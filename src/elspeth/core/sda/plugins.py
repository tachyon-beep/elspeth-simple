"""SDA plugin interfaces for data transformation."""

from __future__ import annotations

from typing import Dict, Protocol, Any, List, Optional


class TransformPlugin(Protocol):
    """Transforms a single data input during the DECIDE phase and returns derived fields."""

    name: str

    def transform(self, row: Dict[str, Any], responses: Dict[str, Any]) -> Dict[str, Any]:
        ...


class AggregationTransform(Protocol):
    """Performs aggregation transformation across all results after individual transforms complete."""

    name: str

    def aggregate(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        ...


class ComparisonPlugin(Protocol):
    """Compares variant payloads against baseline payload."""

    name: str

    def compare(self, baseline: Dict[str, Any], variant: Dict[str, Any]) -> Dict[str, Any]:
        ...


class HaltConditionPlugin(Protocol):
    """Observes row-level results and signals when processing should halt."""

    name: str

    def reset(self) -> None:
        ...

    def check(self, record: Dict[str, Any], *, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        ...
