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
