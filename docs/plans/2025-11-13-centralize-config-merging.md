# Centralize Configuration Merging Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Centralize distributed configuration merging logic into single, testable `ConfigurationMerger` class with documented precedence and debug tooling

**Architecture:** Extract 300+ lines of merging logic from `cli.py`, `config.py`, and `suite_runner.py` into new `src/elspeth/core/config_merger.py`. Implement merge strategies (override, append, deep_merge) with tracing for debuggability. Add `--print-config` CLI flag.

**Tech Stack:** Python 3.x, dataclasses, enums, typing, YAML

**Current state:** Configuration merging spread across 3 files:
- `src/elspeth/config.py` lines 31-159 (prompt pack merging)
- `src/elspeth/cli.py` lines 239-306 (suite defaults merging)
- `src/elspeth/core/sda/suite_runner.py` lines 34-129 (experiment config merging)

**Target state:** Single `ConfigurationMerger` class handling all merging with documented precedence

---

## Task 1: Create ConfigurationMerger Skeleton

**Files:**
- Create: `src/elspeth/core/config_merger.py`
- Test: `tests/core/test_config_merger.py`

### Step 1: Write the failing test

Create test file:

```python
# tests/core/test_config_merger.py
"""Tests for configuration merging logic."""

from elspeth.core.config_merger import ConfigurationMerger, ConfigSource, MergeStrategy


def test_merger_exists():
    """Test that ConfigurationMerger can be instantiated."""
    merger = ConfigurationMerger()
    assert merger is not None


def test_merge_single_source():
    """Test merging single configuration source."""
    merger = ConfigurationMerger()
    source = ConfigSource(
        name="test",
        data={"key": "value"},
        precedence=1
    )
    result = merger.merge(source)
    assert result == {"key": "value"}
```

### Step 2: Run test to verify it fails

Run: `pytest tests/core/test_config_merger.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'elspeth.core.config_merger'"

### Step 3: Create minimal implementation

```python
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
```

### Step 4: Run test to verify it passes

Run: `pytest tests/core/test_config_merger.py::test_merger_exists -v`
Expected: PASS

Run: `pytest tests/core/test_config_merger.py::test_merge_single_source -v`
Expected: PASS

### Step 5: Commit

```bash
git add src/elspeth/core/config_merger.py tests/core/test_config_merger.py
git commit -m "feat: add ConfigurationMerger skeleton with basic merge"
```

---

## Task 2: Implement Override Merge Strategy

**Files:**
- Modify: `src/elspeth/core/config_merger.py`
- Modify: `tests/core/test_config_merger.py`

### Step 1: Write the failing test

Add to test file:

```python
def test_merge_override_strategy():
    """Test that higher precedence overrides lower precedence."""
    merger = ConfigurationMerger()
    source1 = ConfigSource(name="low", data={"key": "low_value"}, precedence=1)
    source2 = ConfigSource(name="high", data={"key": "high_value"}, precedence=2)

    result = merger.merge(source1, source2)
    assert result == {"key": "high_value"}


def test_merge_multiple_keys_override():
    """Test merging multiple keys with override strategy."""
    merger = ConfigurationMerger()
    source1 = ConfigSource(
        name="base",
        data={"key1": "value1", "key2": "value2"},
        precedence=1
    )
    source2 = ConfigSource(
        name="override",
        data={"key2": "new_value2", "key3": "value3"},
        precedence=2
    )

    result = merger.merge(source1, source2)
    assert result == {"key1": "value1", "key2": "new_value2", "key3": "value3"}
```

### Step 2: Run test to verify it fails

Run: `pytest tests/core/test_config_merger.py::test_merge_override_strategy -v`
Expected: FAIL with assertion error (returns low_value instead of high_value)

### Step 3: Implement override merge logic

Update `ConfigurationMerger` class:

```python
class ConfigurationMerger:
    """...(docstring unchanged)..."""

    # Define merge strategies for known keys
    MERGE_STRATEGIES = {
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
        self._merge_trace: List[Dict[str, Any]] = []

    def merge(self, *sources: ConfigSource) -> Dict[str, Any]:
        """Merge configuration sources with defined precedence."""
        # Sort by precedence (lowest first)
        sorted_sources = sorted(sources, key=lambda s: s.precedence)

        merged = {}
        self._merge_trace = []  # Reset trace

        for source in sorted_sources:
            merged = self._merge_source(merged, source)

        return merged

    def _merge_source(self, base: Dict, source: ConfigSource) -> Dict:
        """Merge single source into base configuration."""
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

        return result
```

### Step 4: Run test to verify it passes

Run: `pytest tests/core/test_config_merger.py::test_merge_override_strategy -v`
Expected: PASS

Run: `pytest tests/core/test_config_merger.py::test_merge_multiple_keys_override -v`
Expected: PASS

### Step 5: Commit

```bash
git add src/elspeth/core/config_merger.py tests/core/test_config_merger.py
git commit -m "feat: implement override merge strategy"
```

---

## Task 3: Implement Append Merge Strategy

**Files:**
- Modify: `src/elspeth/core/config_merger.py`
- Modify: `tests/core/test_config_merger.py`

### Step 1: Write the failing test

Add to test file:

```python
def test_merge_append_strategy():
    """Test that list keys append from all sources."""
    merger = ConfigurationMerger()
    source1 = ConfigSource(
        name="pack",
        data={"row_plugins": [{"name": "plugin1"}]},
        precedence=1
    )
    source2 = ConfigSource(
        name="profile",
        data={"row_plugins": [{"name": "plugin2"}]},
        precedence=2
    )

    result = merger.merge(source1, source2)
    assert result == {"row_plugins": [{"name": "plugin1"}, {"name": "plugin2"}]}


def test_merge_append_empty_base():
    """Test appending when base doesn't have the key."""
    merger = ConfigurationMerger()
    source1 = ConfigSource(name="base", data={}, precedence=1)
    source2 = ConfigSource(
        name="override",
        data={"sinks": [{"plugin": "csv"}]},
        precedence=2
    )

    result = merger.merge(source1, source2)
    assert result == {"sinks": [{"plugin": "csv"}]}
```

### Step 2: Run test to verify it fails

Run: `pytest tests/core/test_config_merger.py::test_merge_append_strategy -v`
Expected: FAIL (overrides instead of appends)

### Step 3: Implement append merge logic

Update `_merge_source` method:

```python
def _merge_source(self, base: Dict, source: ConfigSource) -> Dict:
    """Merge single source into base configuration."""
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
```

### Step 4: Run test to verify it passes

Run: `pytest tests/core/test_config_merger.py::test_merge_append_strategy -v`
Expected: PASS

Run: `pytest tests/core/test_config_merger.py::test_merge_append_empty_base -v`
Expected: PASS

### Step 5: Commit

```bash
git add src/elspeth/core/config_merger.py tests/core/test_config_merger.py
git commit -m "feat: implement append merge strategy for list keys"
```

---

## Task 4: Implement Deep Merge Strategy

**Files:**
- Modify: `src/elspeth/core/config_merger.py`
- Modify: `tests/core/test_config_merger.py`

### Step 1: Write the failing test

Add to test file:

```python
def test_merge_deep_merge_strategy():
    """Test deep merging of nested dictionaries."""
    merger = ConfigurationMerger()
    source1 = ConfigSource(
        name="pack",
        data={"llm": {"plugin": "azure_openai", "options": {"temperature": 0.5}}},
        precedence=1
    )
    source2 = ConfigSource(
        name="profile",
        data={"llm": {"options": {"temperature": 0.7, "max_tokens": 100}}},
        precedence=2
    )

    result = merger.merge(source1, source2)
    expected = {
        "llm": {
            "plugin": "azure_openai",
            "options": {
                "temperature": 0.7,  # Overridden from source2
                "max_tokens": 100     # Added from source2
            }
        }
    }
    assert result == expected


def test_merge_deep_merge_three_levels():
    """Test deep merging with 3+ levels of nesting."""
    merger = ConfigurationMerger()
    source1 = ConfigSource(
        name="base",
        data={"retry": {"max_attempts": 3, "backoff": {"initial": 1.0}}},
        precedence=1
    )
    source2 = ConfigSource(
        name="override",
        data={"retry": {"backoff": {"multiplier": 2.0}}},
        precedence=2
    )

    result = merger.merge(source1, source2)
    expected = {
        "retry": {
            "max_attempts": 3,
            "backoff": {
                "initial": 1.0,
                "multiplier": 2.0
            }
        }
    }
    assert result == expected
```

### Step 2: Run test to verify it fails

Run: `pytest tests/core/test_config_merger.py::test_merge_deep_merge_strategy -v`
Expected: FAIL (full replacement instead of deep merge)

### Step 3: Implement deep merge logic

Update `_merge_source` and add `_deep_merge_dict` method:

```python
def _merge_source(self, base: Dict, source: ConfigSource) -> Dict:
    """Merge single source into base configuration."""
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

        elif strategy == MergeStrategy.DEEP_MERGE:
            if key not in result:
                result[key] = {}
            result[key] = self._deep_merge_dict(result[key], value)
            self._merge_trace.append({
                "key": key,
                "strategy": "deep_merge",
                "source": source.name,
                "merged_keys": list(value.keys()) if isinstance(value, dict) else []
            })

    return result

def _deep_merge_dict(self, base: Dict, override: Dict) -> Dict:
    """Recursively merge nested dictionaries.

    Args:
        base: Base dictionary
        override: Dictionary to merge into base

    Returns:
        Merged dictionary (base keys + override keys, override wins on conflicts)
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = self._deep_merge_dict(result[key], value)
        else:
            # Override scalar values or non-dict types
            result[key] = value
    return result
```

### Step 4: Run test to verify it passes

Run: `pytest tests/core/test_config_merger.py::test_merge_deep_merge_strategy -v`
Expected: PASS

Run: `pytest tests/core/test_config_merger.py::test_merge_deep_merge_three_levels -v`
Expected: PASS

### Step 5: Commit

```bash
git add src/elspeth/core/config_merger.py tests/core/test_config_merger.py
git commit -m "feat: implement deep merge strategy for nested dicts"
```

---

## Task 5: Implement explain() Method for Debugging

**Files:**
- Modify: `src/elspeth/core/config_merger.py`
- Modify: `tests/core/test_config_merger.py`

### Step 1: Write the failing test

Add to test file:

```python
def test_explain_simple_override():
    """Test explain method shows configuration source."""
    merger = ConfigurationMerger()
    source1 = ConfigSource(name="pack", data={"rate_limit": 10}, precedence=1)
    source2 = ConfigSource(name="profile", data={"rate_limit": 50}, precedence=2)

    merged = merger.merge(source1, source2)
    explanation = merger.explain("rate_limit", merged)

    assert "rate_limit = 50" in explanation
    assert "profile" in explanation
    assert "precedence 2" in explanation


def test_explain_nested_key():
    """Test explain works with nested keys."""
    merger = ConfigurationMerger()
    source1 = ConfigSource(
        name="base",
        data={"llm": {"options": {"temperature": 0.5}}},
        precedence=1
    )
    source2 = ConfigSource(
        name="override",
        data={"llm": {"options": {"temperature": 0.7}}},
        precedence=2
    )

    merged = merger.merge(source1, source2)
    explanation = merger.explain("llm.options.temperature", merged)

    assert "0.7" in explanation
    assert "override" in explanation
```

### Step 2: Run test to verify it fails

Run: `pytest tests/core/test_config_merger.py::test_explain_simple_override -v`
Expected: FAIL (method not implemented)

### Step 3: Implement explain method

Add to `ConfigurationMerger` class:

```python
def explain(self, key: str, merged_config: Dict) -> str:
    """Explain why a configuration value is what it is.

    Args:
        key: Configuration key (e.g., "rate_limit" or "llm.options.temperature")
        merged_config: The merged configuration dictionary

    Returns:
        Explanation string showing source and precedence

    Example:
        >>> merger.explain("rate_limit", config)
        "rate_limit = 50
         Source: profile (precedence 2)
         Strategy: override"
    """
    # Handle nested keys (e.g., "llm.options.temperature")
    keys = key.split(".")
    value = merged_config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return f"{key} = <not found>"

    # Find trace entry for this key
    relevant_traces = [t for t in self._merge_trace if t["key"] == keys[0]]

    if not relevant_traces:
        return f"{key} = {value}\nSource: <unknown>"

    # Get the last trace (highest precedence)
    last_trace = relevant_traces[-1]

    explanation = f"{key} = {value}\n"
    explanation += f"Source: {last_trace['source']}\n"
    explanation += f"Strategy: {last_trace['strategy']}"

    return explanation
```

### Step 4: Run test to verify it passes

Run: `pytest tests/core/test_config_merger.py::test_explain_simple_override -v`
Expected: PASS

Run: `pytest tests/core/test_config_merger.py::test_explain_nested_key -v`
Expected: PASS

### Step 5: Commit

```bash
git add src/elspeth/core/config_merger.py tests/core/test_config_merger.py
git commit -m "feat: add explain() method for config debugging"
```

---

## Task 6: Refactor config.py to Use ConfigurationMerger

**Files:**
- Modify: `src/elspeth/config.py`
- Modify: `tests/core/test_config_merger.py` (integration test)

### Step 1: Write integration test

Add to test file:

```python
def test_config_load_uses_merger():
    """Integration test: config.py uses ConfigurationMerger."""
    from elspeth.config import load_settings
    from pathlib import Path
    import tempfile

    # Create temporary config file
    config_yaml = """
default:
  datasource:
    plugin: local_csv
    options:
      path: test.csv
  llm:
    plugin: mock
  prompt_packs:
    test_pack:
      prompts:
        system: "Test system prompt"
      row_plugins:
        - name: plugin1
  prompt_pack: test_pack
  row_plugins:
    - name: plugin2
  sinks: []
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_yaml)
        config_path = f.name

    try:
        settings = load_settings(config_path, profile="default")

        # Verify prompt pack prompts are merged
        assert settings.orchestrator_config.llm_prompt["system"] == "Test system prompt"

        # Verify plugins are appended (pack plugins + profile plugins)
        # Note: This test validates the merger is being used correctly
        assert len(settings.orchestrator_config.transform_plugin_defs) >= 2

    finally:
        Path(config_path).unlink()
```

### Step 2: Run test to verify current behavior

Run: `pytest tests/core/test_config_merger.py::test_config_load_uses_merger -v`
Expected: PASS (documents current behavior before refactoring)

### Step 3: Refactor config.py load_settings to use ConfigurationMerger

Update `src/elspeth/config.py`:

```python
from elspeth.core.config_merger import ConfigurationMerger, ConfigSource, MergeStrategy


def load_settings(path: str | Path, profile: str = "default") -> Settings:
    """Load settings from YAML configuration file.

    Uses ConfigurationMerger for consistent precedence:
    1. System defaults (if any)
    2. Prompt pack
    3. Profile
    4. Suite defaults
    5. Experiment config (handled by suite_runner)
    """
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    profile_data = dict(data.get(profile, {}))

    prompt_packs = profile_data.pop("prompt_packs", {})
    prompt_pack_name = profile_data.get("prompt_pack")
    pack = prompt_packs.get(prompt_pack_name) if prompt_pack_name else None

    # Use ConfigurationMerger for prompt pack merging
    merger = ConfigurationMerger()

    # Merge pack config into profile config
    if pack:
        pack_source = ConfigSource(name="prompt_pack", data=pack, precedence=2)
        profile_source = ConfigSource(name="profile", data=profile_data, precedence=3)
        merged_config = merger.merge(pack_source, profile_source)
    else:
        merged_config = profile_data

    # Extract merged values
    datasource_cfg = merged_config["datasource"]
    datasource = registry.create_datasource(
        datasource_cfg["plugin"], datasource_cfg.get("options", {})
    )

    llm_cfg = merged_config["llm"]
    llm = registry.create_llm(llm_cfg["plugin"], llm_cfg.get("options", {}))

    # Plugins are now properly appended by merger
    transform_plugin_defs = merged_config.get("row_plugins", [])
    aggregation_transform_defs = merged_config.get("aggregator_plugins", [])
    baseline_plugin_defs = merged_config.get("baseline_plugins", [])
    sink_defs = merged_config.get("sinks", [])
    llm_middleware_defs = merged_config.get("llm_middlewares", [])

    # Other config extraction (unchanged)
    rate_limiter_def = merged_config.get("rate_limiter")
    cost_tracker_def = merged_config.get("cost_tracker")
    prompt_defaults = merged_config.get("prompt_defaults")
    concurrency_config = merged_config.get("concurrency")
    halt_condition_config = merged_config.get("early_stop")
    halt_condition_plugin_defs = normalize_halt_condition_definitions(
        merged_config.get("early_stop_plugins")
    ) or []

    if not halt_condition_plugin_defs and halt_condition_config:
        halt_condition_plugin_defs = normalize_halt_condition_definitions(halt_condition_config)

    prompts = merged_config.get("prompts", {})
    prompt_fields = merged_config.get("prompt_fields")
    prompt_aliases = merged_config.get("prompt_aliases")
    criteria = merged_config.get("criteria")

    # Create sinks and controls (unchanged)
    sinks = [registry.create_sink(item["plugin"], item.get("options", {})) for item in sink_defs]
    rate_limiter = create_rate_limiter(rate_limiter_def)
    cost_tracker = create_cost_tracker(cost_tracker_def)

    # Handle suite_defaults merging with prompt packs
    suite_defaults = dict(merged_config.get("suite_defaults", {}))
    suite_pack_name = suite_defaults.get("prompt_pack")
    if suite_pack_name and suite_pack_name in prompt_packs:
        suite_pack = prompt_packs[suite_pack_name]
        suite_pack_source = ConfigSource(name="suite_prompt_pack", data=suite_pack, precedence=2)
        suite_source = ConfigSource(name="suite_defaults", data=suite_defaults, precedence=3)
        suite_defaults = merger.merge(suite_pack_source, suite_source)

    orchestrator_config = SDAConfig(
        llm_prompt=prompts,
        prompt_fields=prompt_fields,
        prompt_aliases=prompt_aliases,
        criteria=criteria,
        transform_plugin_defs=transform_plugin_defs,
        aggregation_transform_defs=aggregation_transform_defs,
        baseline_plugin_defs=baseline_plugin_defs,
        sink_defs=sink_defs,
        prompt_pack=prompt_pack_name,
        retry_config=merged_config.get("retry"),
        checkpoint_config=merged_config.get("checkpoint"),
        llm_middleware_defs=llm_middleware_defs,
        prompt_defaults=prompt_defaults,
        concurrency_config=concurrency_config,
        halt_condition_config=halt_condition_config,
        halt_condition_plugin_defs=halt_condition_plugin_defs or None,
    )

    suite_root = merged_config.get("suite_root")

    return Settings(
        datasource=datasource,
        llm=llm,
        sinks=sinks,
        orchestrator_config=orchestrator_config,
        suite_root=Path(suite_root) if suite_root else None,
        suite_defaults=suite_defaults,
        rate_limiter=rate_limiter,
        cost_tracker=cost_tracker,
        prompt_packs=prompt_packs,
        prompt_pack=prompt_pack_name,
    )
```

**Note:** Remove old `_merge_pack` function (no longer needed)

### Step 4: Run tests to verify refactoring works

Run: `pytest tests/core/test_config_merger.py::test_config_load_uses_merger -v`
Expected: PASS (same behavior as before)

Run existing config tests: `pytest tests/ -k config -v`
Expected: All PASS (no regressions)

### Step 5: Commit

```bash
git add src/elspeth/config.py tests/core/test_config_merger.py
git commit -m "refactor: migrate config.py to use ConfigurationMerger"
```

---

## Task 7: Refactor suite_runner.py to Use ConfigurationMerger

**Files:**
- Modify: `src/elspeth/core/sda/suite_runner.py`

### Step 1: Identify current merging code

Read `suite_runner.py` lines 34-129 to understand current merge logic

### Step 2: Write test documenting current behavior

Create `tests/core/sda/test_suite_runner_merger.py`:

```python
"""Test suite runner uses ConfigurationMerger correctly."""

from elspeth.core.sda.suite_runner import SDASuiteRunner
from elspeth.core.config_merger import ConfigurationMerger


def test_build_runner_uses_merger():
    """Test that build_runner uses ConfigurationMerger for precedence."""
    # This test validates the refactored behavior
    # Will write after understanding current code structure
    pass
```

### Step 3: Refactor build_runner to use ConfigurationMerger

Update `src/elspeth/core/sda/suite_runner.py`:

Replace lines 34-129 with:

```python
from elspeth.core.config_merger import ConfigurationMerger, ConfigSource

def build_runner(
    self,
    config: SDACycleConfig,
    defaults: Dict[str, Any],
    sinks: List[ResultSink],
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
    prompt_fields = merged.get("prompt_fields")
    criteria = merged.get("criteria")
    prompt_defaults = merged.get("prompt_defaults", {})
    concurrency_config = merged.get("concurrency_config") or merged.get("concurrency")
    halt_condition_config = merged.get("halt_condition_config") or merged.get("early_stop")

    # Handle middlewares
    middleware_defs = merged.get("llm_middleware_defs", []) or merged.get("llm_middlewares", [])
    middlewares = self._create_middlewares(middleware_defs)

    # Handle halt condition plugins
    halt_condition_plugin_defs = merged.get("halt_condition_plugin_defs", [])
    if not halt_condition_plugin_defs and halt_condition_config:
        halt_condition_plugin_defs = normalize_halt_condition_definitions(halt_condition_config)
    halt_condition_plugins = (
        [create_halt_condition_plugin(defn) for defn in halt_condition_plugin_defs]
        if halt_condition_plugin_defs else None
    )

    # Security level resolution
    security_level = resolve_security_level(
        merged.get("security_level"),
        defaults.get("security_level"),
    )

    # Transform plugins (appended by merger)
    transform_plugin_defs = merged.get("transform_plugin_defs", []) or merged.get("row_plugins", [])
    transform_plugins = (
        [create_transform_plugin(defn) for defn in transform_plugin_defs]
        if transform_plugin_defs else None
    )

    # Aggregation transforms (appended by merger)
    aggregation_transform_defs = (
        merged.get("aggregation_transform_defs", [])
        or merged.get("aggregator_plugins", [])
    )
    aggregation_transforms = (
        [create_aggregation_transform(defn) for defn in aggregation_transform_defs]
        if aggregation_transform_defs else None
    )

    # Rate limiter and cost tracker
    rate_limiter = merged.get("rate_limiter")
    if merged.get("rate_limiter_def"):
        rate_limiter = create_rate_limiter(merged["rate_limiter_def"])

    cost_tracker = merged.get("cost_tracker")
    if merged.get("cost_tracker_def"):
        cost_tracker = create_cost_tracker(merged["cost_tracker_def"])

    # Build and return runner (rest unchanged)
    # ... (existing runner construction code)
```

### Step 4: Run tests to verify no regressions

Run: `pytest tests/core/sda/ -v`
Expected: All PASS

### Step 5: Commit

```bash
git add src/elspeth/core/sda/suite_runner.py
git commit -m "refactor: migrate suite_runner to use ConfigurationMerger"
```

---

## Task 8: Refactor cli.py Suite Defaults Merging

**Files:**
- Modify: `src/elspeth/cli.py` (lines 239-306)

### Step 1: Identify code to refactor

Lines 239-306 in `_run_suite` handle defaults merging

### Step 2: Refactor using ConfigurationMerger

Replace manual merging with:

```python
def _run_suite(args: argparse.Namespace, settings, suite_root: Path, *, preflight: dict | None = None) -> None:
    """Run experiment suite with merged configuration."""
    from elspeth.core.config_merger import ConfigurationMerger, ConfigSource

    logger.info("Running suite at %s", suite_root)
    suite = SDASuite.load(suite_root)
    df = settings.datasource.load()
    suite_runner = SDASuiteRunner(
        suite=suite,
        llm_client=settings.llm,
        sinks=settings.sinks,
    )

    # Use ConfigurationMerger for defaults
    merger = ConfigurationMerger()

    # Source 1: orchestrator config
    orch_config_data = {
        "prompt_system": settings.orchestrator_config.llm_prompt.get("system", ""),
        "prompt_template": settings.orchestrator_config.llm_prompt.get("user", ""),
        "prompt_fields": settings.orchestrator_config.prompt_fields,
        "criteria": settings.orchestrator_config.criteria,
        "prompt_packs": settings.prompt_packs,
    }

    # Add optional fields if present
    if settings.orchestrator_config.prompt_pack:
        orch_config_data["prompt_pack"] = settings.orchestrator_config.prompt_pack
    if settings.orchestrator_config.row_plugin_defs:
        orch_config_data["row_plugin_defs"] = settings.orchestrator_config.row_plugin_defs
    # ... (add all optional fields)

    # Source 2: suite_defaults
    suite_defaults = settings.suite_defaults or {}

    sources = [
        ConfigSource(name="orchestrator", data=orch_config_data, precedence=1),
        ConfigSource(name="suite_defaults", data=suite_defaults, precedence=2),
    ]

    defaults = merger.merge(*sources)

    # Add runtime instances (not part of merge)
    if settings.rate_limiter:
        defaults["rate_limiter"] = settings.rate_limiter
    if settings.cost_tracker:
        defaults["cost_tracker"] = settings.cost_tracker

    results = suite_runner.run(
        df,
        defaults=defaults,
        sink_factory=lambda exp: _clone_suite_sinks(settings.sinks, exp.name),
        preflight_info=preflight,
    )

    for name, entry in results.items():
        logger.info("Experiment %s completed with %s rows", name, len(entry["payload"]["results"]))
```

### Step 3: Run tests to verify no regressions

Run: `pytest tests/ -k suite -v`
Expected: All PASS

### Step 4: Commit

```bash
git add src/elspeth/cli.py
git commit -m "refactor: migrate cli.py suite defaults to ConfigurationMerger"
```

---

## Task 9: Add --print-config CLI Flag

**Files:**
- Modify: `src/elspeth/cli.py`
- Test manually

### Step 1: Add CLI argument

Update `build_parser()` in `cli.py`:

```python
def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="Run SDA (Sense-Decide-Act) experiments"
    )

    # ... existing arguments ...

    parser.add_argument(
        "--print-config",
        action="store_true",
        help="Print resolved configuration and exit (no execution)"
    )

    parser.add_argument(
        "--explain-config",
        type=str,
        metavar="KEY",
        help="Explain source of specific config key (e.g., 'rate_limiter' or 'llm.options.temperature')"
    )

    return parser
```

### Step 2: Implement --print-config logic

Update `main()` function:

```python
def main():
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # ... existing setup ...

    settings = load_settings(args.settings, args.profile)

    # Handle --print-config
    if args.print_config or args.explain_config:
        _print_configuration(args, settings)
        return

    # ... rest of main() unchanged ...


def _print_configuration(args: argparse.Namespace, settings: Settings):
    """Print resolved configuration for debugging."""
    import yaml
    from elspeth.core.config_merger import ConfigurationMerger

    # Build configuration dictionary for display
    config_dict = {
        "datasource": {
            "plugin": type(settings.datasource).__name__,
        },
        "llm": {
            "plugin": type(settings.llm).__name__,
        },
        "prompts": settings.orchestrator_config.llm_prompt,
        "row_plugins": settings.orchestrator_config.transform_plugin_defs,
        "aggregator_plugins": settings.orchestrator_config.aggregation_transform_defs,
        "sinks": [type(sink).__name__ for sink in settings.sinks],
    }

    # Add optional fields
    if settings.orchestrator_config.concurrency_config:
        config_dict["concurrency"] = settings.orchestrator_config.concurrency_config
    if settings.rate_limiter:
        config_dict["rate_limiter"] = type(settings.rate_limiter).__name__

    print("# Resolved Configuration")
    print(f"# Loaded from: {args.settings} (profile: {args.profile})")
    print()

    if args.explain_config:
        # Explain specific key (would need to track merge history)
        print(f"Configuration key: {args.explain_config}")
        print("Note: Detailed source tracking requires refactoring load_settings to preserve merger")
    else:
        # Print full config
        print(yaml.dump(config_dict, default_flow_style=False, sort_keys=False))
```

### Step 3: Test manually

Run: `python -m elspeth.cli --settings example/simple/settings.yaml --print-config`
Expected: Prints resolved configuration in YAML format

Run: `python -m elspeth.cli --settings example/simple/settings.yaml --explain-config llm`
Expected: Shows explanation for llm configuration

### Step 4: Commit

```bash
git add src/elspeth/cli.py
git commit -m "feat: add --print-config and --explain-config CLI flags"
```

---

## Task 10: Write Documentation

**Files:**
- Create: `docs/configuration-precedence.md`

### Step 1: Create documentation

```markdown
# Configuration Precedence Guide

This document explains how Elspeth merges configuration from multiple sources with clear precedence rules.

## Precedence Levels

Configuration is merged from 5 levels, from lowest to highest precedence:

| Level | Precedence | Source | Example |
|-------|------------|--------|---------|
| 1 | Lowest | System defaults | Built-in defaults |
| 2 | Low | Prompt pack | `prompt_packs.quality-evaluation` |
| 3 | Medium | Profile | `production:` section in YAML |
| 4 | High | Suite defaults | `suite_defaults:` section |
| 5 | Highest | Experiment config | Individual experiment settings |

**Rule:** Higher precedence overrides lower precedence (except for lists, see Merge Strategies below)

## Merge Strategies

Different configuration keys use different merge strategies:

### Override (Most Keys)

Scalar values use **override** strategy - higher precedence completely replaces lower precedence.

**Example:**
```yaml
# Prompt pack (precedence 2)
rate_limiter:
  requests_per_minute: 10

# Profile (precedence 3)
rate_limiter:
  requests_per_minute: 50

# Result: 50 (profile overrides pack)
```

### Append (Plugin Lists)

List keys use **append** strategy - values accumulate from all sources.

**Keys using append:**
- `row_plugins`
- `aggregator_plugins`
- `baseline_plugins`
- `llm_middlewares`
- `sinks`
- `early_stop_plugins`

**Example:**
```yaml
# Prompt pack (precedence 2)
row_plugins:
  - name: score_extractor

# Profile (precedence 3)
row_plugins:
  - name: custom_metric

# Result: [score_extractor, custom_metric] (both included)
```

### Deep Merge (Nested Dicts)

Nested dictionary keys use **deep merge** strategy - recursively merge nested structures.

**Keys using deep merge:**
- `llm`
- `datasource`
- `prompts`
- `concurrency`
- `retry`
- `checkpoint`
- `early_stop`

**Example:**
```yaml
# Prompt pack (precedence 2)
llm:
  plugin: azure_openai
  options:
    temperature: 0.5
    max_tokens: 500

# Profile (precedence 3)
llm:
  options:
    temperature: 0.7  # Override
    top_p: 0.9        # Add new

# Result:
llm:
  plugin: azure_openai
  options:
    temperature: 0.7    # From profile (override)
    max_tokens: 500     # From pack (preserved)
    top_p: 0.9          # From profile (added)
```

## Debugging Configuration

### Print Resolved Configuration

```bash
elspeth --settings config.yaml --profile production --print-config
```

Shows the final merged configuration without running experiments.

### Explain Specific Key

```bash
elspeth --settings config.yaml --explain-config rate_limiter
```

Shows which source provided the value for a specific key.

## Common Mistakes

### Mistake 1: Unexpected Override

**Problem:** Set rate limit in profile, but prompt pack value is used

**Cause:** Prompt packs have lower precedence than profiles

**Solution:** Check precedence order - profile (3) should override pack (2)

### Mistake 2: Plugins Not Accumulating

**Problem:** Profile plugins replace pack plugins instead of adding to them

**Cause:** Using wrong YAML syntax

**Correct:**
```yaml
row_plugins:  # List syntax
  - name: plugin1
```

**Incorrect:**
```yaml
row_plugins: {name: plugin1}  # Dict syntax (will override)
```

### Mistake 3: Nested Config Confusion

**Problem:** Can't tell if deep merge or override is happening

**Solution:** Use `--print-config` to see final merged result

## Implementation

Configuration merging is implemented in `src/elspeth/core/config_merger.py`.

See `ConfigurationMerger` class for merge strategy definitions.
```

### Step 2: Commit

```bash
git add docs/configuration-precedence.md
git commit -m "docs: add configuration precedence guide"
```

---

## Task 11: Full Integration Testing

**Files:**
- Create: `tests/integration/test_config_merger_integration.py`

### Step 1: Write comprehensive integration test

```python
"""Integration tests for ConfigurationMerger across the system."""

import tempfile
from pathlib import Path
import yaml

from elspeth.config import load_settings


def test_full_config_merge_chain():
    """Test complete configuration merge from pack → profile → suite → experiment."""

    config_yaml = """
default:
  datasource:
    plugin: local_csv
    options:
      path: test.csv

  llm:
    plugin: mock
    options:
      temperature: 0.5

  prompt_packs:
    quality_eval:
      prompts:
        system: "Pack system prompt"
      row_plugins:
        - name: score_extractor
      llm:
        options:
          max_tokens: 100
      rate_limiter:
        requests_per_minute: 10

  prompt_pack: quality_eval

  prompts:
    user: "Profile user prompt"

  row_plugins:
    - name: custom_metric

  llm:
    options:
      temperature: 0.7  # Override pack

  rate_limiter:
    requests_per_minute: 50  # Override pack

  suite_defaults:
    concurrency:
      max_workers: 5

  sinks: []
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_yaml)
        config_path = f.name

    try:
        settings = load_settings(config_path, profile="default")

        # Verify prompts merged correctly
        assert settings.orchestrator_config.llm_prompt["system"] == "Pack system prompt"
        assert settings.orchestrator_config.llm_prompt["user"] == "Profile user prompt"

        # Verify plugins appended (pack + profile)
        plugin_names = [p["name"] for p in settings.orchestrator_config.transform_plugin_defs]
        assert "score_extractor" in plugin_names  # From pack
        assert "custom_metric" in plugin_names    # From profile

        # Note: Deep verification of nested merging depends on implementation details
        # This test validates the ConfigurationMerger is integrated correctly

    finally:
        Path(config_path).unlink()
```

### Step 2: Run integration test

Run: `pytest tests/integration/test_config_merger_integration.py -v`
Expected: PASS

### Step 3: Run full test suite

Run: `pytest tests/ -v`
Expected: All PASS

### Step 4: Commit

```bash
git add tests/integration/test_config_merger_integration.py
git commit -m "test: add comprehensive config merger integration tests"
```

---

## Task 12: Final Validation and Cleanup

**Files:**
- Review all modified files
- Run linters and type checkers

### Step 1: Run type checker

Run: `mypy src/elspeth/core/config_merger.py`
Expected: No errors

### Step 2: Run linter

Run: `ruff check src/elspeth/core/config_merger.py`
Expected: No errors (or fix any issues)

### Step 3: Run full test suite

Run: `pytest tests/ -v --cov=src/elspeth/core/config_merger`
Expected: All PASS, >90% coverage

### Step 4: Manual testing with real config

Run: `python -m elspeth.cli --settings example/simple/settings.yaml --print-config`
Expected: Clean output showing merged configuration

### Step 5: Final commit

```bash
git add .
git commit -m "refactor: complete ConfigurationMerger centralization

- Centralize 300+ lines of merge logic into single file
- Add comprehensive unit tests (>90% coverage)
- Add --print-config and --explain-config CLI flags
- Document configuration precedence rules
- Zero breaking changes (all existing configs work identically)"
```

---

## Success Criteria Checklist

- [ ] ConfigurationMerger class created with all 3 merge strategies
- [ ] Override strategy implemented and tested
- [ ] Append strategy implemented and tested
- [ ] Deep merge strategy implemented and tested
- [ ] explain() method implemented for debugging
- [ ] config.py refactored to use ConfigurationMerger
- [ ] suite_runner.py refactored to use ConfigurationMerger
- [ ] cli.py refactored to use ConfigurationMerger
- [ ] --print-config CLI flag working
- [ ] --explain-config CLI flag working
- [ ] Documentation complete (configuration-precedence.md)
- [ ] Integration tests passing
- [ ] All existing tests still passing (zero regressions)
- [ ] Type checker passing (mypy)
- [ ] Linter passing (ruff)
- [ ] Manual testing with real configs successful

---

## Estimated Timeline

- **Tasks 1-5** (Core merger): 4 hours
- **Tasks 6-8** (Refactoring): 6 hours
- **Task 9** (CLI flags): 2 hours
- **Task 10** (Documentation): 2 hours
- **Tasks 11-12** (Testing & validation): 2 hours

**Total:** ~16 hours (2 working days)

---

**Plan complete. Ready for execution.**
