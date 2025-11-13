# src/elspeth/core/config_merger.py
"""Centralized configuration merging with documented precedence."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class MergeStrategy(Enum):
    """Configuration merge strategies."""
    OVERRIDE = "override"  # Higher precedence replaces lower
    APPEND = "append"      # Accumulate from all sources (lists)
    DEEP_MERGE = "deep_merge"  # Recursive merge (nested dicts)


@dataclass
class ConfigSource:
    """Configuration source with metadata."""
    name: str  # "system_default", "prompt_pack", "profile", "suite", "experiment"
    data: Dict[str, Any]
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

    def __init__(self):
        """Initialize merger."""
        pass

    def merge(self, *sources: ConfigSource) -> Dict[str, Any]:
        """Merge configuration sources with defined precedence.

        Args:
            sources: Configuration sources in any order (sorted by precedence)

        Returns:
            Merged configuration dictionary
        """
        # For now, just return data from first source
        if sources:
            return dict(sources[0].data)
        return {}
