"""Characterization tests for SDARunner before refactoring."""

from __future__ import annotations

from typing import Any

import pandas as pd
import pytest

from elspeth.core.sda.runner import SDARunner


class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, response: dict[str, Any] | None = None):
        self.calls: list[tuple[str, str]] = []
        self.response = response or {"content": "mock response"}

    def generate(self, system_prompt: str, user_prompt: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        self.calls.append((system_prompt, user_prompt))
        return self.response


class MockSink:
    """Mock sink for testing."""

    def __init__(self):
        self.written_payload: dict[str, Any] | None = None
        self.written_metadata: dict[str, Any] | None = None

    def write(self, payload: dict[str, Any], metadata: dict[str, Any] | None = None) -> None:
        self.written_payload = payload
        self.written_metadata = metadata

    def produces(self) -> list[str]:
        return []

    def consumes(self) -> list[str]:
        return []

    def finalize(self, artifacts: dict[str, Any] | None = None, metadata: dict[str, Any] | None = None) -> None:
        pass


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Sample DataFrame for testing."""
    return pd.DataFrame([
        {"id": "1", "text": "Hello world"},
        {"id": "2", "text": "Test data"},
    ])


@pytest.fixture
def mock_llm() -> MockLLMClient:
    """Mock LLM client fixture."""
    return MockLLMClient()


@pytest.fixture
def mock_sink() -> MockSink:
    """Mock sink fixture."""
    return MockSink()


def test_runner_processes_all_rows(sample_df, mock_llm, mock_sink):
    """SDARunner processes all rows in DataFrame."""
    runner = SDARunner(
        llm_client=mock_llm,
        sinks=[mock_sink],
        prompt_system="You are a test assistant",
        prompt_template="Process: {text}",
        prompt_fields=["text"],
    )

    result = runner.run(sample_df)

    # Should process 2 rows
    assert len(result["results"]) == 2
    assert len(mock_llm.calls) == 2
    assert mock_sink.written_payload is not None


def test_runner_skips_checkpointed_rows(sample_df, mock_llm, mock_sink, tmp_path):
    """SDARunner skips rows already in checkpoint."""
    checkpoint_path = tmp_path / "checkpoint.jsonl"

    # Pre-create checkpoint with id "1"
    with open(checkpoint_path, "w") as f:
        f.write('1\n')

    runner = SDARunner(
        llm_client=mock_llm,
        sinks=[mock_sink],
        prompt_system="Test",
        prompt_template="Process: {text}",
        prompt_fields=["text", "id"],
        checkpoint_config={"path": str(checkpoint_path), "field": "id"},
    )

    result = runner.run(sample_df)

    # Should only process row "2"
    assert len(result["results"]) == 1
    assert len(mock_llm.calls) == 1


class MockTransformPlugin:
    """Mock transform plugin."""

    def __init__(self):
        self.calls: list[tuple[dict, dict]] = []

    def transform(self, row: dict[str, Any], responses: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((row, responses))
        return {"transformed": True}


def test_runner_applies_transform_plugins(sample_df, mock_llm, mock_sink):
    """SDARunner applies transform plugins to each row."""
    mock_plugin = MockTransformPlugin()

    runner = SDARunner(
        llm_client=mock_llm,
        sinks=[mock_sink],
        prompt_system="Test",
        prompt_template="Process: {text}",
        prompt_fields=["text"],
        transform_plugins=[mock_plugin],
    )

    result = runner.run(sample_df)

    # Transform plugin should be called for each row
    assert len(mock_plugin.calls) == 2
    # Results should include transformed metrics
    assert result["results"][0]["metrics"]["transformed"] is True
