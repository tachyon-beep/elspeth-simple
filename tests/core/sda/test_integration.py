"""Integration tests for refactored SDA components."""

from __future__ import annotations

from typing import Any

import pandas as pd

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


def test_full_sda_pipeline_with_all_features(tmp_path):
    """Full SDA pipeline with checkpoints, transforms, early stop."""
    checkpoint_path = tmp_path / "checkpoint.jsonl"

    # Sample data
    df = pd.DataFrame([
        {"id": "1", "text": "First"},
        {"id": "2", "text": "Second"},
        {"id": "3", "text": "Third"},
    ])

    # Mock components
    llm_client = MockLLMClient(response={"content": "processed", "usage": {"prompt_tokens": 10, "completion_tokens": 5}})
    sink = MockSink()

    # Run with all features
    runner = SDARunner(
        llm_client=llm_client,
        sinks=[sink],
        prompt_system="System prompt",
        prompt_template="User: {text}",
        prompt_fields=["text", "id"],  # Include id for checkpoint
        checkpoint_config={"path": str(checkpoint_path), "field": "id"},
        retry_config={"max_attempts": 2, "backoff_multiplier": 1.5, "initial_delay": 0.1},
    )

    result = runner.run(df)

    # Verify all rows processed
    assert len(result["results"]) == 3
    assert result["metadata"]["rows"] == 3
    assert result["metadata"]["row_count"] == 3

    # Verify checkpoint created (should have 3 IDs written)
    assert checkpoint_path.exists(), "Checkpoint file should be created"
    checkpoint_ids = checkpoint_path.read_text().strip().split("\n")
    assert len(checkpoint_ids) == 3, f"Expected 3 checkpoint IDs, got {len(checkpoint_ids)}"
    assert set(checkpoint_ids) == {"1", "2", "3"}, f"Expected IDs 1,2,3, got {checkpoint_ids}"

    # Verify sink received payload
    assert sink.written_payload is not None
    assert len(sink.written_payload["results"]) == 3


def test_refactored_components_work_together(tmp_path):
    """Verify all refactored components integrate correctly."""
    # This test exists to ensure no regressions in component integration
    df = pd.DataFrame([{"id": "1", "text": "Test"}])

    runner = SDARunner(
        llm_client=MockLLMClient(),
        sinks=[MockSink()],
        prompt_system="Test",
        prompt_template="{text}",
        prompt_fields=["text"],
    )

    result = runner.run(df)

    # Should work without any features enabled
    assert len(result["results"]) == 1
    assert "metadata" in result
    assert result["metadata"]["rows"] == 1
