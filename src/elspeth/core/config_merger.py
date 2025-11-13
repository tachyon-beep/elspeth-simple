# src/elspeth/core/config_merger.py
"""Centralized configuration merging with documented precedence."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar


class MergeStrategy(Enum):
    """Configuration merge strategies."""
    OVERRIDE = "override"  # Higher precedence replaces lower
    APPEND = "append"      # Accumulate from all sources (lists)
    DEEP_MERGE = "deep_merge"  # Recursive merge (nested dicts)


@dataclass
class ConfigSource:
    """Configuration source with metadata."""
    name: str  # "system_default", "prompt_pack", "profile", "suite", "experiment"
    data: dict[str, Any]
    precedence: int  # Lower number = lower precedence


class ConfigurationMerger:
    """Centralized configuration merging with documented precedence.

    Precedence levels (lowest to highest):
    1. System defaults (precedence=1)
    2. Prompt pack (precedence=2)
    3. Profile (precedence=3)
    4. Suite defaults (precedence=4)
    5. Experiment config (precedence=5)

    Merge strategies by key:
    - Scalar values (str, int, bool): OVERRIDE
    - Lists (*_plugins, *_sinks): APPEND
    - Nested dicts (llm.options, datasource.options): DEEP_MERGE
    """

    # Define merge strategies for known keys
    MERGE_STRATEGIES: ClassVar[dict[str, MergeStrategy]] = {
        # Lists use APPEND strategy
        "row_plugins": MergeStrategy.APPEND,
        "aggregator_plugins": MergeStrategy.APPEND,
        "baseline_plugins": MergeStrategy.APPEND,
        "llm_middlewares": MergeStrategy.APPEND,
        "sinks": MergeStrategy.APPEND,
        "early_stop_plugins": MergeStrategy.APPEND,

        # Nested dicts use DEEP_MERGE
        "llm": MergeStrategy.DEEP_MERGE,
        "datasource": MergeStrategy.DEEP_MERGE,
        "orchestrator": MergeStrategy.DEEP_MERGE,
        "concurrency": MergeStrategy.DEEP_MERGE,
        "retry": MergeStrategy.DEEP_MERGE,
        "checkpoint": MergeStrategy.DEEP_MERGE,
        "early_stop": MergeStrategy.DEEP_MERGE,
        "prompts": MergeStrategy.DEEP_MERGE,

        # All other keys: OVERRIDE (default)
    }

    def __init__(self):
        """Initialize merger with empty trace."""
        self._merge_trace: list[dict[str, Any]] = []

    def merge(self, *sources: ConfigSource) -> dict[str, Any]:
        """Merge configuration sources with defined precedence.

        Args:
            sources: Configuration sources in any order (sorted by precedence)

        Returns:
            Merged configuration dictionary
        """
        # Sort by precedence (lowest first)
        sorted_sources = sorted(sources, key=lambda s: s.precedence)

        merged: dict[str, Any] = {}
        self._merge_trace = []  # Reset trace

        for source in sorted_sources:
            merged = self._merge_source(merged, source)

        return merged

    def _merge_source(self, base: dict[str, Any], source: ConfigSource) -> dict[str, Any]:
        """Merge single source into base configuration.

        Args:
            base: Base configuration dictionary
            source: Configuration source to merge

        Returns:
            Merged configuration dictionary
        """
        result = base.copy()

        for key, value in source.data.items():
            strategy = self.MERGE_STRATEGIES.get(key, MergeStrategy.OVERRIDE)

            if strategy == MergeStrategy.OVERRIDE:
                result[key] = value
                self._merge_trace.append({
                    "key": key,
                    "strategy": "override",
                    "source": source.name,
                    "value": value
                })

            elif strategy == MergeStrategy.APPEND:
                if key not in result:
                    result[key] = []
                # Append new items to existing list
                if isinstance(value, list):
                    result[key] = result[key] + value
                else:
                    result[key].append(value)
                self._merge_trace.append({
                    "key": key,
                    "strategy": "append",
                    "source": source.name,
                    "appended": value
                })

        return result
