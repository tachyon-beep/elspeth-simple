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


def test_explain_simple_override():
    """Test explain method shows configuration source."""
    merger = ConfigurationMerger()
    source1 = ConfigSource(name="pack", data={"rate_limit": 10}, precedence=1)
    source2 = ConfigSource(name="profile", data={"rate_limit": 50}, precedence=2)

    merged = merger.merge(source1, source2)
    explanation = merger.explain("rate_limit", merged)

    assert "rate_limit = 50" in explanation
    assert "profile" in explanation
    assert "override" in explanation


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
  prompts:
    user: "Profile user prompt"
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
        assert settings.orchestrator_config.llm_prompt.get("system") == "Test system prompt"
        assert settings.orchestrator_config.llm_prompt.get("user") == "Profile user prompt"

        # Verify plugins are appended (pack plugins + profile plugins)
        plugin_names = [p["name"] for p in settings.orchestrator_config.transform_plugin_defs]
        assert "plugin1" in plugin_names  # From pack
        assert "plugin2" in plugin_names  # From profile
        # Pack plugins should come first
        assert plugin_names.index("plugin1") < plugin_names.index("plugin2")

    finally:
        Path(config_path).unlink()
