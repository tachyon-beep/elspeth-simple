"""Standard orchestrator for sequential SDA cycle execution."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Callable

from elspeth.core.sda.config import SDASuite, SDACycleConfig
from elspeth.core.sda.runner import SDARunner
from elspeth.core.sda.plugin_registry import (
    create_transform_plugin,
    create_aggregation_transform,
    create_halt_condition_plugin,
    normalize_halt_condition_definitions,
)
from elspeth.core.interfaces import LLMClientProtocol, ResultSink
from elspeth.core.controls import create_rate_limiter, create_cost_tracker
from elspeth.core.llm.registry import create_middleware
from elspeth.core import registry as core_registry
from elspeth.core.security import resolve_security_level
from elspeth.core.validation import ConfigurationError
from elspeth.core.config_merger import ConfigurationMerger, ConfigSource


@dataclass
class StandardOrchestrator:
    """Standard orchestrator - executes SDA cycles sequentially.

    No baseline tracking, no comparison logic.
    Just runs cycles in order as defined in suite.
    """
    suite: SDASuite
    llm_client: LLMClientProtocol
    sinks: List[ResultSink]
    _shared_middlewares: Dict[str, Any] = field(default_factory=dict, init=False)

    def build_runner(
        self,
        config: SDACycleConfig,
        defaults: Dict[str, Any],
        sinks: List[ResultSink],
    ) -> SDARunner:
        """Build runner for single cycle with merged configuration.

        Merging precedence:
        1. defaults (from Settings)
        2. prompt_pack (if specified)
        3. config (cycle-specific)
        """
        merger = ConfigurationMerger()

        # Build sources in precedence order
        sources = []

        # Source 1: defaults
        sources.append(ConfigSource(name="defaults", data=defaults, precedence=1))

        # Source 2: prompt pack (if specified)
        prompt_packs = defaults.get("prompt_packs", {})
        pack_name = config.prompt_pack or defaults.get("prompt_pack")
        if pack_name and pack_name in prompt_packs:
            pack = prompt_packs[pack_name]
            sources.append(ConfigSource(name="prompt_pack", data=pack, precedence=2))

        # Source 3: cycle config
        config_data = {
            k: v for k, v in config.__dict__.items()
            if v is not None and not k.startswith('_')
        }
        sources.append(ConfigSource(name="cycle", data=config_data, precedence=3))

        # Merge all sources
        merged = merger.merge(*sources)

        # Extract merged values with fallbacks
        prompt_system = merged.get("prompt_system", "")
        prompt_template = merged.get("prompt_template", "")

        # Handle prompts dict format
        if prompts := merged.get("prompts"):
            prompt_system = prompt_system or prompts.get("system", "")
            prompt_template = prompt_template or prompts.get("user", "")

        prompt_fields = merged.get("prompt_fields")
        criteria = merged.get("criteria")
        prompt_defaults = merged.get("prompt_defaults", {})
        concurrency_config = merged.get("concurrency_config") or merged.get("concurrency")
        halt_condition_config = merged.get("halt_condition_config") or merged.get("early_stop")

        # Handle middlewares (appended by merger)
        middleware_defs = merged.get("llm_middleware_defs", []) or merged.get("llm_middlewares", [])
        middlewares = self._create_middlewares(middleware_defs)

        # Handle halt condition plugins (appended by merger)
        halt_condition_plugin_defs = merged.get("halt_condition_plugin_defs", []) or merged.get("halt_condition_plugins", [])
        if halt_condition_plugin_defs:
            halt_condition_plugin_defs = normalize_halt_condition_definitions(halt_condition_plugin_defs)
        if not halt_condition_plugin_defs and halt_condition_config:
            halt_condition_plugin_defs = normalize_halt_condition_definitions(halt_condition_config)
        halt_condition_plugins = (
            [create_halt_condition_plugin(defn) for defn in halt_condition_plugin_defs]
            if halt_condition_plugin_defs else None
        )

        # Security level resolution
        pack = prompt_packs.get(pack_name) if pack_name and pack_name in prompt_packs else None
        security_level = resolve_security_level(
            config.security_level,
            (pack.get("security_level") if pack else None),
            defaults.get("security_level"),
        )

        # Transform plugins (appended by merger)
        transform_plugin_defs = (
            merged.get("transform_plugin_defs", [])
            or merged.get("row_plugins", [])
            or merged.get("transform_plugins", [])
        )
        transform_plugins = (
            [create_transform_plugin(defn) for defn in transform_plugin_defs]
            if transform_plugin_defs else None
        )

        # Aggregation transforms (appended by merger)
        aggregation_transform_defs = (
            merged.get("aggregation_transform_defs", [])
            or merged.get("aggregator_plugins", [])
            or merged.get("aggregation_transforms", [])
        )
        aggregation_transforms = (
            [create_aggregation_transform(defn) for defn in aggregation_transform_defs]
            if aggregation_transform_defs else None
        )

        # Rate limiter and cost tracker (override strategy)
        rate_limiter = merged.get("rate_limiter")
        if merged.get("rate_limiter_def"):
            rate_limiter = create_rate_limiter(merged["rate_limiter_def"])

        cost_tracker = merged.get("cost_tracker")
        if merged.get("cost_tracker_def"):
            cost_tracker = create_cost_tracker(merged["cost_tracker_def"])

        # Validate required prompts
        if not (prompt_system or "").strip():
            raise ConfigurationError(
                f"Cycle '{config.name}' has no system prompt defined. Provide one in the cycle, defaults, or prompt pack."
            )
        if not (prompt_template or "").strip():
            raise ConfigurationError(
                f"Cycle '{config.name}' has no user prompt defined. Provide one in the cycle, defaults, or prompt pack."
            )

        runner_kwargs = {
            "llm_client": self.llm_client,
            "sinks": sinks,
            "prompt_system": prompt_system,
            "prompt_template": prompt_template,
            "prompt_fields": prompt_fields,
            "criteria": criteria,
            "prompt_defaults": prompt_defaults or None,
            "transform_plugins": transform_plugins,
            "aggregation_transforms": aggregation_transforms,
            "rate_limiter": rate_limiter,
            "cost_tracker": cost_tracker,
            "cycle_name": config.name,
            "llm_middlewares": middlewares or None,
            "concurrency_config": concurrency_config,
            "security_level": security_level,
            "halt_condition_plugins": halt_condition_plugins,
            "halt_condition_config": halt_condition_config,
        }
        return SDARunner(**runner_kwargs)

    def _create_middlewares(self, definitions: list[Dict[str, Any]] | None) -> list[Any]:
        instances: list[Any] = []
        for defn in definitions or []:
            name = defn.get("name") or defn.get("plugin")
            identifier = f"{name}:{json.dumps(defn.get('options', {}), sort_keys=True)}"
            if identifier not in self._shared_middlewares:
                self._shared_middlewares[identifier] = create_middleware(defn)
            instances.append(self._shared_middlewares[identifier])
        return instances

    def _instantiate_sinks(self, defs: List[Dict[str, Any]]) -> List[ResultSink]:
        sinks: List[ResultSink] = []
        for index, entry in enumerate(defs):
            plugin = entry.get("plugin")
            raw_options = dict(entry.get("options", {}))
            core_registry.registry.validate_sink(plugin, raw_options)
            options = dict(raw_options)
            artifacts_cfg = options.pop("artifacts", None)
            security_level = options.pop("security_level", entry.get("security_level"))
            sink = core_registry.registry.create_sink(plugin, options)
            setattr(sink, "_dmp_artifact_config", artifacts_cfg or {})
            setattr(sink, "_dmp_plugin_name", plugin)
            base_name = entry.get("name") or plugin or f"sink{index}"
            setattr(sink, "_dmp_sink_name", base_name)
            if security_level:
                setattr(sink, "_dmp_security_level", security_level)
            sinks.append(sink)
        return sinks

    def run(
        self,
        df,
        defaults: Dict[str, Any] | None = None,
        sink_factory: Callable[[SDACycleConfig], List[ResultSink]] | None = None,
        preflight_info: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Run all cycles in suite sequentially.

        No baseline tracking, no comparison logic.
        Returns results dict keyed by cycle name.
        """
        defaults = defaults or {}
        results: Dict[str, Any] = {}
        prompt_packs = defaults.get("prompt_packs", {})

        # Build cycle metadata (no is_baseline field)
        cycle_metadata = [
            {
                "cycle": cycle.name,
                "temperature": cycle.temperature,
                "max_tokens": cycle.max_tokens,
            }
            for cycle in self.suite.cycles
        ]

        if preflight_info is None:
            preflight_info = {
                "cycle_count": len(self.suite.cycles),
            }

        notified_middlewares: dict[int, Any] = {}

        # Run cycles in order (no baseline reordering)
        for cycle in self.suite.cycles:
            pack_name = cycle.prompt_pack or defaults.get("prompt_pack")
            pack = prompt_packs.get(pack_name) if pack_name else None

            # Determine sinks
            if cycle.sink_defs:
                sinks = self._instantiate_sinks(cycle.sink_defs)
            elif pack and pack.get("sinks"):
                sinks = self._instantiate_sinks(pack["sinks"])
            elif defaults.get("sink_defs"):
                sinks = self._instantiate_sinks(defaults["sink_defs"])
            else:
                sinks = sink_factory(cycle) if sink_factory else self.sinks

            # Build and run
            runner = self.build_runner(
                cycle,
                {**defaults, "prompt_packs": prompt_packs, "prompt_pack": pack_name},
                sinks,
            )

            # Notify middlewares
            middlewares = list(runner.llm_middlewares or [])
            for mw in middlewares:
                key = id(mw)
                if hasattr(mw, "on_suite_loaded") and key not in notified_middlewares:
                    mw.on_suite_loaded(cycle_metadata, preflight_info)
                    notified_middlewares[key] = mw
                if hasattr(mw, "on_experiment_start"):  # Legacy name for compatibility
                    mw.on_experiment_start(
                        cycle.name,
                        {
                            "temperature": cycle.temperature,
                            "max_tokens": cycle.max_tokens,
                        },
                    )

            # Execute cycle
            payload = runner.run(df)

            # Store results (no baseline comparison)
            results[cycle.name] = {
                "payload": payload,
                "config": cycle,
            }

            # Notify completion
            for mw in middlewares:
                if hasattr(mw, "on_experiment_complete"):  # Legacy name for compatibility
                    mw.on_experiment_complete(
                        cycle.name,
                        payload,
                        {
                            "temperature": cycle.temperature,
                            "max_tokens": cycle.max_tokens,
                        },
                    )

        # Suite complete notification
        for mw in notified_middlewares.values():
            if hasattr(mw, "on_suite_complete"):
                mw.on_suite_complete()

        return results
