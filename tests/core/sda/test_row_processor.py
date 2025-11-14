"""Tests for RowProcessor."""

import pandas as pd

from elspeth.core.prompts import PromptEngine
from elspeth.core.sda.row_processor import RowProcessor


class MockLLMClient:
    def __init__(self, response: dict | None = None):
        self.response = response or {"content": "mock"}

    def generate(self, system: str, user: str, metadata: dict | None = None) -> dict:
        return self.response


class MockTransform:
    def transform(self, row: dict, responses: dict) -> dict:
        return {"transformed": True}


def test_row_processor_processes_single_row():
    """RowProcessor processes single row with LLM."""
    engine = PromptEngine()
    system_template = engine.compile("System", name="test:system")
    user_template = engine.compile("User: {text}", name="test:user")

    llm_client = MockLLMClient(response={"content": "processed"})
    processor = RowProcessor(
        llm_client=llm_client,
        engine=engine,
        system_template=system_template,
        user_template=user_template,
        criteria_templates={},
        transform_plugins=[],
    )

    row = pd.Series({"text": "hello"})
    context = {"text": "hello"}

    record, failure = processor.process_row(row, context, row_id="1")

    assert record is not None
    assert failure is None
    assert record["response"]["content"] == "processed"
    assert record["row"] == context


def test_row_processor_applies_transforms():
    """RowProcessor applies transform plugins."""
    engine = PromptEngine()
    system_template = engine.compile("System", name="test:system")
    user_template = engine.compile("User", name="test:user")

    processor = RowProcessor(
        llm_client=MockLLMClient(),
        engine=engine,
        system_template=system_template,
        user_template=user_template,
        criteria_templates={},
        transform_plugins=[MockTransform()],
    )

    row = pd.Series({})
    record, _ = processor.process_row(row, {}, row_id="1")

    assert record["metrics"]["transformed"] is True
