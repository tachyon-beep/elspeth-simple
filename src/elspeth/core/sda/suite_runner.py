"""Suite runner orchestrating multiple SDA cycles.

DEPRECATED: This module is deprecated and will be removed in a future version.
Use orchestrators.StandardOrchestrator or orchestrators.ExperimentalOrchestrator instead.

This module is kept for backward compatibility only.
"""

from __future__ import annotations

import json
import warnings
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from elspeth.core import registry as core_registry
from elspeth.core.config_merger import ConfigSource, ConfigurationMerger
from elspeth.core.controls import create_cost_tracker, create_rate_limiter
from elspeth.core.interfaces import LLMClientProtocol, ResultSink
from elspeth.core.llm.registry import create_middleware
from elspeth.core.sda.config import SDACycleConfig, SDASuite
from elspeth.core.sda.plugin_registry import (
    create_aggregation_transform,
    create_baseline_plugin,
    create_halt_condition_plugin,
    create_transform_plugin,
    normalize_halt_condition_definitions,
)
from elspeth.core.sda.runner import SDARunner
from elspeth.core.security import resolve_security_level
from elspeth.core.validation import ConfigurationError


@dataclass
class SDASuiteRunner:
    """DEPRECATED: Use ExperimentalOrchestrator from orchestrators package instead."""
    suite: SDASuite
    llm_client: LLMClientProtocol
    sinks: list[ResultSink]
    _shared_middlewares: dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self):
        warnings.warn(
            "SDASuiteRunner is deprecated. Use orchestrators.ExperimentalOrchestrator instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def build_runner(
        self,
        config: SDACycleConfig,
        defaults: dict[str, Any],
        sinks: list[ResultSink],
    ) -> SDARunner:
        """Build runner for single experiment with merged configuration.

        Merging precedence:
        1. defaults (from Settings)
        2. prompt_pack (if specified)
        3. config (experiment-specific)
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

        # Source 3: experiment config
        config_data = {
            k: v for k, v in config.__dict__.items()
            if v is not None and not k.startswith('_')
        }
        sources.append(ConfigSource(name="experiment", data=config_data, precedence=3))

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

        # Security level resolution (still uses special resolution logic)
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
                f"Experiment '{config.name}' has no system prompt defined. Provide one in the experiment, defaults, or prompt pack."
            )
        if not (prompt_template or "").strip():
            raise ConfigurationError(
                f"Experiment '{config.name}' has no user prompt defined. Provide one in the experiment, defaults, or prompt pack."
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

    def _create_middlewares(self, definitions: list[dict[str, Any]] | None) -> list[Any]:
        instances: list[Any] = []
        for defn in definitions or []:
            name = defn.get("name") or defn.get("plugin")
            identifier = f"{name}:{json.dumps(defn.get('options', {}), sort_keys=True)}"
            if identifier not in self._shared_middlewares:
                self._shared_middlewares[identifier] = create_middleware(defn)
            instances.append(self._shared_middlewares[identifier])
        return instances

    def _instantiate_sinks(self, defs: list[dict[str, Any]]) -> list[ResultSink]:
        sinks: list[ResultSink] = []
        for index, entry in enumerate(defs):
            plugin = entry.get("plugin")
            raw_options = dict(entry.get("options", {}))
            core_registry.registry.validate_sink(plugin, raw_options)
            options = dict(raw_options)
            artifacts_cfg = options.pop("artifacts", None)
            security_level = options.pop("security_level", entry.get("security_level"))
            sink = core_registry.registry.create_sink(plugin, options)
            sink._dmp_artifact_config = artifacts_cfg or {}
            sink._dmp_plugin_name = plugin
            base_name = entry.get("name") or plugin or f"sink{index}"
            sink._dmp_sink_name = base_name
            if security_level:
                sink._dmp_security_level = security_level
            sinks.append(sink)
        return sinks

    def run(
        self,
        df,
        defaults: dict[str, Any] | None = None,
        sink_factory: Callable[[SDACycleConfig], list[ResultSink]] | None = None,
        preflight_info: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        defaults = defaults or {}
        results: dict[str, Any] = {}
        prompt_packs = defaults.get("prompt_packs", {})

        # Note: This code is deprecated. For new code use ExperimentalOrchestrator.
        # Legacy baseline detection for backward compatibility
        experiments: list[SDACycleConfig] = []
        baseline = None
        for cycle in self.suite.cycles:
            if cycle.metadata.get("is_baseline"):
                baseline = cycle
                break
        if baseline is None and self.suite.cycles:
            baseline = self.suite.cycles[0]

        if baseline:
            experiments.append(baseline)
        experiments.extend(exp for exp in self.suite.cycles if exp != baseline)

        baseline_payload = None
        suite_metadata = [
            {
                "experiment": exp.name,
                "temperature": exp.temperature,
                "max_tokens": exp.max_tokens,
                "is_baseline": exp.metadata.get("is_baseline", False),
            }
            for exp in experiments
        ]
        if preflight_info is None:
            preflight_info = {
                "experiment_count": len(experiments),
                "baseline": baseline.name if baseline else None,
            }
        notified_middlewares: dict[int, Any] = {}

        for experiment in experiments:
            pack_name = experiment.prompt_pack or defaults.get("prompt_pack")
            pack = prompt_packs.get(pack_name) if pack_name else None

            if experiment.sink_defs:
                sinks = self._instantiate_sinks(experiment.sink_defs)
            elif pack and pack.get("sinks"):
                sinks = self._instantiate_sinks(pack["sinks"])
            elif defaults.get("sink_defs"):
                sinks = self._instantiate_sinks(defaults["sink_defs"])
            else:
                sinks = sink_factory(experiment) if sink_factory else self.sinks

            runner = self.build_runner(
                experiment,
                {**defaults, "prompt_packs": prompt_packs, "prompt_pack": pack_name},
                sinks,
            )
            middlewares = list(runner.llm_middlewares or [])
            suite_notified = []
            for mw in middlewares:
                key = id(mw)
                if hasattr(mw, "on_suite_loaded") and key not in notified_middlewares:
                    mw.on_suite_loaded(suite_metadata, preflight_info)
                    notified_middlewares[key] = mw
                    suite_notified.append(mw)
                if hasattr(mw, "on_experiment_start"):
                    mw.on_experiment_start(
                        experiment.name,
                        {
                            "temperature": experiment.temperature,
                            "max_tokens": experiment.max_tokens,
                            "is_baseline": experiment.metadata.get("is_baseline", False),
                        },
                    )
            payload = runner.run(df)

            if baseline_payload is None and (experiment.metadata.get("is_baseline") or experiment == baseline):
                baseline_payload = payload

            results[experiment.name] = {
                "payload": payload,
                "config": experiment,
            }
            for mw in middlewares:
                if hasattr(mw, "on_experiment_complete"):
                    mw.on_experiment_complete(
                        experiment.name,
                        payload,
                        {
                            "temperature": experiment.temperature,
                            "max_tokens": experiment.max_tokens,
                            "is_baseline": experiment.metadata.get("is_baseline", False),
                        },
                    )

            if baseline_payload and experiment != baseline:
                comp_defs = list(defaults.get("baseline_plugin_defs", []))
                if pack and pack.get("baseline_plugins"):
                    comp_defs = list(pack.get("baseline_plugins", [])) + comp_defs
                if experiment.metadata.get("baseline_plugins"):
                    comp_defs += experiment.metadata["baseline_plugins"]
                comparisons = {}
                for defn in comp_defs:
                    plugin = create_baseline_plugin(defn)
                    diff = plugin.compare(baseline_payload, payload)
                    if diff:
                        comparisons[plugin.name] = diff
                if comparisons:
                    payload["baseline_comparison"] = comparisons
                    results[experiment.name]["baseline_comparison"] = comparisons
                    for mw in middlewares:
                        if hasattr(mw, "on_baseline_comparison"):
                            mw.on_baseline_comparison(experiment.name, comparisons)

        for mw in notified_middlewares.values():
            if hasattr(mw, "on_suite_complete"):
                mw.on_suite_complete()

        return results
