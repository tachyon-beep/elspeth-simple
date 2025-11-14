"""Tests for ResultAggregator."""

from elspeth.core.sda.result_aggregator import ResultAggregator


class MockAggregationPlugin:
    def __init__(self, name: str, aggregated: dict):
        self.name = name
        self.aggregated = aggregated

    def aggregate(self, results: list) -> dict:
        return self.aggregated


def test_result_aggregator_collects_results():
    """ResultAggregator collects results and failures."""
    aggregator = ResultAggregator(aggregation_plugins=[])

    aggregator.add_result({"id": 1}, row_index=0)
    aggregator.add_result({"id": 2}, row_index=1)
    aggregator.add_failure({"error": "test"})

    payload = aggregator.build_payload(security_level="OFFICIAL-SENSITIVE")

    assert len(payload["results"]) == 2
    assert payload["results"][0]["id"] == 1
    assert payload["results"][1]["id"] == 2
    assert len(payload["failures"]) == 1
    assert payload["metadata"]["rows"] == 2


def test_result_aggregator_applies_aggregation_plugins():
    """ResultAggregator applies aggregation plugins."""
    plugin = MockAggregationPlugin("stats", {"mean": 5.0})
    aggregator = ResultAggregator(aggregation_plugins=[plugin])

    aggregator.add_result({"value": 3}, row_index=0)
    aggregator.add_result({"value": 7}, row_index=1)

    payload = aggregator.build_payload()

    assert "aggregates" in payload
    assert payload["aggregates"]["stats"]["mean"] == 5.0
    assert payload["metadata"]["aggregates"]["stats"]["mean"] == 5.0
