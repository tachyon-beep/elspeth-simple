"""SDA plugin interfaces for data transformation."""

from __future__ import annotations

from typing import Any, Protocol


class TransformPlugin(Protocol):
    """Transforms a single data input during the DECIDE phase and returns derived fields."""

    name: str

    def transform(self, row: dict[str, Any], responses: dict[str, Any]) -> dict[str, Any]:
        ...


class AggregationTransform(Protocol):
    """Performs aggregation transformation across all results after individual transforms complete."""

    name: str

    def aggregate(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        ...


class ComparisonPlugin(Protocol):
    """Compares variant payloads against baseline payload."""

    name: str

    def compare(self, baseline: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
        ...


class HaltConditionPlugin(Protocol):
    """Observes row-level results and signals when processing should halt."""

    name: str

    def reset(self) -> None:
        ...

    def check(self, record: dict[str, Any], *, metadata: dict[str, Any] | None = None) -> dict[str, Any] | None:
        ...
