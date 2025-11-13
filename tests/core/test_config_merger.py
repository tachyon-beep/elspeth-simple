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
