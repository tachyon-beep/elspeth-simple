"""Experimental orchestrator for A/B testing with baseline comparison."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable

from elspeth.core.sda.config import SDASuite, SDACycleConfig
from elspeth.core.sda.plugin_registry import create_baseline_plugin
from elspeth.core.interfaces import LLMClientProtocol, ResultSink
from .standard import StandardOrchestrator


@dataclass
class ExperimentalOrchestrator(StandardOrchestrator):
    """Experimental orchestrator with A/B testing and baseline comparison.

    Extends StandardOrchestrator with:
    - Baseline identification from metadata
    - Runs baseline first (before variants)
    - Applies comparison plugins between baseline and variants
    - Includes comparison results in output
    """

    def _identify_baseline(self) -> SDACycleConfig | None:
        """Identify baseline cycle from metadata.

        Looks for cycle with metadata.is_baseline = true.
        Falls back to first cycle if no baseline specified.
        """
        # Check metadata first
        for cycle in self.suite.cycles:
            if cycle.metadata.get("is_baseline"):
                return cycle

        # Fall back to first cycle
        return self.suite.cycles[0] if self.suite.cycles else None

    def _get_variants(self, baseline: SDACycleConfig) -> List[SDACycleConfig]:
        """Get all cycles except baseline."""
        return [c for c in self.suite.cycles if c != baseline]

    def run(
        self,
        df,
        defaults: Dict[str, Any] | None = None,
        sink_factory: Callable[[SDACycleConfig], List[ResultSink]] | None = None,
        preflight_info: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Run suite with baseline-first ordering and comparison logic.

        Execution order:
        1. Identify baseline from metadata
        2. Run baseline first
        3. Run variants
        4. Apply comparison plugins (baseline vs each variant)
        5. Include comparison results in output
        """
        defaults = defaults or {}
        results: Dict[str, Any] = {}
        prompt_packs = defaults.get("prompt_packs", {})

        # Identify baseline and order experiments: baseline first, then variants
        baseline = self._identify_baseline()
        if not baseline:
            # No cycles to run
            return results

        experiments: List[SDACycleConfig] = [baseline]
        experiments.extend(self._get_variants(baseline))

        # Build metadata with is_baseline flag for middlewares
        suite_metadata = [
            {
                "experiment": exp.name,
                "temperature": exp.temperature,
                "max_tokens": exp.max_tokens,
                "is_baseline": (exp == baseline),
            }
            for exp in experiments
        ]

        if preflight_info is None:
            preflight_info = {
                "experiment_count": len(experiments),
                "baseline": baseline.name,
            }

        notified_middlewares: dict[int, Any] = {}
        baseline_payload = None

        for experiment in experiments:
            pack_name = experiment.prompt_pack or defaults.get("prompt_pack")
            pack = prompt_packs.get(pack_name) if pack_name else None

            # Determine sinks
            if experiment.sink_defs:
                sinks = self._instantiate_sinks(experiment.sink_defs)
            elif pack and pack.get("sinks"):
                sinks = self._instantiate_sinks(pack["sinks"])
            elif defaults.get("sink_defs"):
                sinks = self._instantiate_sinks(defaults["sink_defs"])
            else:
                sinks = sink_factory(experiment) if sink_factory else self.sinks

            # Build and run
            runner = self.build_runner(
                experiment,
                {**defaults, "prompt_packs": prompt_packs, "prompt_pack": pack_name},
                sinks,
            )

            # Notify middlewares
            middlewares = list(runner.llm_middlewares or [])
            for mw in middlewares:
                key = id(mw)
                if hasattr(mw, "on_suite_loaded") and key not in notified_middlewares:
                    mw.on_suite_loaded(suite_metadata, preflight_info)
                    notified_middlewares[key] = mw
                if hasattr(mw, "on_experiment_start"):
                    mw.on_experiment_start(
                        experiment.name,
                        {
                            "temperature": experiment.temperature,
                            "max_tokens": experiment.max_tokens,
                            "is_baseline": (experiment == baseline),
                        },
                    )

            # Execute cycle
            payload = runner.run(df)

            # Track baseline payload
            if experiment == baseline:
                baseline_payload = payload

            # Store results
            results[experiment.name] = {
                "payload": payload,
                "config": experiment,
            }

            # Notify completion
            for mw in middlewares:
                if hasattr(mw, "on_experiment_complete"):
                    mw.on_experiment_complete(
                        experiment.name,
                        payload,
                        {
                            "temperature": experiment.temperature,
                            "max_tokens": experiment.max_tokens,
                            "is_baseline": (experiment == baseline),
                        },
                    )

            # Apply baseline comparison for variants
            if baseline_payload and experiment != baseline:
                comparisons = self._compare_with_baseline(
                    baseline_payload,
                    payload,
                    experiment,
                    defaults,
                    pack,
                    middlewares,
                )
                if comparisons:
                    payload["baseline_comparison"] = comparisons
                    results[experiment.name]["baseline_comparison"] = comparisons

        # Suite complete notification
        for mw in notified_middlewares.values():
            if hasattr(mw, "on_suite_complete"):
                mw.on_suite_complete()

        return results

    def _compare_with_baseline(
        self,
        baseline_payload: Dict[str, Any],
        variant_payload: Dict[str, Any],
        experiment: SDACycleConfig,
        defaults: Dict[str, Any],
        pack: Dict[str, Any] | None,
        middlewares: List[Any],
    ) -> Dict[str, Any]:
        """Apply comparison plugins between baseline and variant.

        Comparison plugin precedence:
        1. defaults.baseline_plugin_defs
        2. pack.baseline_plugins (appended)
        3. experiment.metadata.baseline_plugins (appended)
        """
        # Collect comparison plugin definitions
        comp_defs = list(defaults.get("baseline_plugin_defs", []))

        if pack and pack.get("baseline_plugins"):
            comp_defs = list(pack.get("baseline_plugins", [])) + comp_defs

        # Check experiment metadata for baseline plugins
        if experiment.metadata.get("baseline_plugins"):
            comp_defs += experiment.metadata["baseline_plugins"]

        # Execute comparison plugins
        comparisons = {}
        for defn in comp_defs:
            plugin = create_baseline_plugin(defn)
            diff = plugin.compare(baseline_payload, variant_payload)
            if diff:
                comparisons[plugin.name] = diff

        # Notify middlewares of comparison
        if comparisons:
            for mw in middlewares:
                if hasattr(mw, "on_baseline_comparison"):
                    mw.on_baseline_comparison(experiment.name, comparisons)

        return comparisons
