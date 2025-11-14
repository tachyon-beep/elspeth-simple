# SDARunner Refactoring - TDD Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor the 583-line SDARunner god class into smaller, focused collaborators using Test-Driven Development

**Architecture:** Extract responsibilities into dedicated classes: CheckpointManager (checkpoint I/O), PromptCompiler (template compilation), RowProcessor (single row processing), ParallelExecutor (concurrent processing), ResultAggregator (result collection), and EarlyStopCoordinator (halt condition management). SDARunner becomes a thin orchestrator delegating to these collaborators.

**Tech Stack:** Python 3.13, pytest, pandas, existing elspeth plugin system

**Testing Strategy:**
- Extract and characterize existing behavior through tests FIRST
- Refactor with green tests at each step
- Use existing Mock LLM plugin for isolation
- Maintain 100% backward compatibility

---

## Current State Analysis

**File:** `src/elspeth/core/sda/runner.py` (583 lines)

**Responsibilities identified:**
1. Checkpoint management (load/append)
2. Prompt compilation (Jinja2 templates)
3. Single row processing (LLM execution + transforms)
4. Parallel execution (ThreadPoolExecutor)
5. Result aggregation (collecting + metadata)
6. Early stop coordination (halt conditions)
7. Retry logic (with backoff)
8. Artifact pipeline orchestration

**Current methods:**
- `run(df)` - Main entry point (157 lines)
- `_init_halt_conditions()` - Setup early stop (24 lines)
- `_maybe_trigger_early_stop()` - Check halt conditions (46 lines)
- `_process_single_row()` - Process one row (77 lines)
- `_should_run_parallel()` - Concurrency decision (9 lines)
- `_run_parallel()` - Parallel execution (50 lines)
- `_build_sink_bindings()` - Sink setup (22 lines)
- `_execute_llm()` - LLM call with retry (98 lines)
- `_notify_retry_exhausted()` - Retry failure (23 lines)
- `_load_checkpoint()` - Read checkpoint (12 lines)
- `_append_checkpoint()` - Write checkpoint (2 lines)

---

## Task 1: Create Characterization Tests

**Goal:** Establish test harness capturing current SDARunner behavior before refactoring

**Files:**
- Create: `tests/core/sda/test_runner.py`
- Reference: `src/elspeth/core/sda/runner.py`

### Step 1: Write test infrastructure setup

```python
# tests/core/sda/test_runner.py
"""Characterization tests for SDARunner before refactoring."""

from __future__ import annotations

import pandas as pd
import pytest
from pathlib import Path
from typing import Dict, Any

from elspeth.core.sda.runner import SDARunner
from elspeth.core.interfaces import LLMClientProtocol, ResultSink


class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, response: Dict[str, Any] | None = None):
        self.calls: list[tuple[str, str]] = []
        self.response = response or {"content": "mock response"}

    def generate(self, system: str, user: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        self.calls.append((system, user))
        return self.response


class MockSink:
    """Mock sink for testing."""

    def __init__(self):
        self.written_payload: Dict[str, Any] | None = None
        self.written_metadata: Dict[str, Any] | None = None

    def write(self, payload: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        self.written_payload = payload
        self.written_metadata = metadata

    def produces(self) -> list[str]:
        return []

    def consumes(self) -> list[str]:
        return []

    def finalize(self) -> None:
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
```

**Expected:** File structure, no tests yet

### Step 2: Run tests to verify infrastructure

```bash
pytest tests/core/sda/test_runner.py -v
```

**Expected:** `collected 0 items` (no tests yet, infrastructure only)

### Step 3: Write test for basic run behavior

```python
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
```

### Step 4: Run test to verify it passes

```bash
pytest tests/core/sda/test_runner.py::test_runner_processes_all_rows -v
```

**Expected:** PASS (characterizes current behavior)

### Step 5: Write test for checkpoint behavior

```python
def test_runner_skips_checkpointed_rows(sample_df, mock_llm, mock_sink, tmp_path):
    """SDARunner skips rows already in checkpoint."""
    checkpoint_path = tmp_path / "checkpoint.jsonl"

    # Pre-create checkpoint with id "1"
    with open(checkpoint_path, "w") as f:
        f.write('{"id": "1"}\n')

    runner = SDARunner(
        llm_client=mock_llm,
        sinks=[mock_sink],
        prompt_system="Test",
        prompt_template="Process: {text}",
        prompt_fields=["text"],
        checkpoint_config={"path": str(checkpoint_path), "field": "id"},
    )

    result = runner.run(sample_df)

    # Should only process row "2"
    assert len(result["results"]) == 1
    assert len(mock_llm.calls) == 1
```

### Step 6: Run test to verify checkpoint behavior

```bash
pytest tests/core/sda/test_runner.py::test_runner_skips_checkpointed_rows -v
```

**Expected:** PASS

### Step 7: Write test for transform plugin application

```python
class MockTransformPlugin:
    """Mock transform plugin."""

    def __init__(self):
        self.calls: list[tuple[Dict, Dict]] = []

    def transform(self, row: Dict[str, Any], responses: Dict[str, Any]) -> Dict[str, Any]:
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
```

### Step 8: Run transform plugin test

```bash
pytest tests/core/sda/test_runner.py::test_runner_applies_transform_plugins -v
```

**Expected:** PASS

### Step 9: Commit characterization tests

```bash
git add tests/core/sda/test_runner.py
git commit -m "test: add SDARunner characterization tests before refactoring"
```

---

## Task 2: Extract CheckpointManager

**Goal:** Extract checkpoint loading/saving into dedicated class

**Files:**
- Create: `src/elspeth/core/sda/checkpoint.py`
- Create: `tests/core/sda/test_checkpoint.py`
- Modify: `src/elspeth/core/sda/runner.py`

### Step 1: Write failing test for CheckpointManager

```python
# tests/core/sda/test_checkpoint.py
"""Tests for CheckpointManager."""

from pathlib import Path
import pytest

from elspeth.core.sda.checkpoint import CheckpointManager


def test_checkpoint_manager_loads_existing_ids(tmp_path):
    """CheckpointManager loads existing checkpoint IDs."""
    checkpoint_path = tmp_path / "checkpoint.jsonl"

    # Create checkpoint with 2 IDs
    with open(checkpoint_path, "w") as f:
        f.write('{"id": "row1"}\n')
        f.write('{"id": "row2"}\n')

    manager = CheckpointManager(checkpoint_path, field="id")

    assert manager.is_processed("row1")
    assert manager.is_processed("row2")
    assert not manager.is_processed("row3")
```

### Step 2: Run test to verify it fails

```bash
pytest tests/core/sda/test_checkpoint.py::test_checkpoint_manager_loads_existing_ids -v
```

**Expected:** FAIL with "No module named 'elspeth.core.sda.checkpoint'"

### Step 3: Write minimal CheckpointManager implementation

```python
# src/elspeth/core/sda/checkpoint.py
"""Checkpoint management for resumable SDA execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Set


class CheckpointManager:
    """Manages checkpoint state for resumable processing."""

    def __init__(self, checkpoint_path: Path | str, field: str):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_path: Path to checkpoint JSONL file
            field: Field name containing unique row ID
        """
        self.checkpoint_path = Path(checkpoint_path)
        self.field = field
        self._processed_ids: Set[str] = self._load_checkpoint()

    def _load_checkpoint(self) -> Set[str]:
        """Load processed IDs from checkpoint file."""
        if not self.checkpoint_path.exists():
            return set()

        processed_ids = set()
        with open(self.checkpoint_path, "r") as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    row_id = record.get(self.field)
                    if row_id:
                        processed_ids.add(str(row_id))
                except (json.JSONDecodeError, ValueError):
                    continue
        return processed_ids

    def is_processed(self, row_id: str) -> bool:
        """Check if row ID has been processed."""
        return row_id in self._processed_ids

    def mark_processed(self, row_id: str) -> None:
        """Mark row ID as processed and append to checkpoint."""
        if row_id in self._processed_ids:
            return

        self._processed_ids.add(row_id)
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.checkpoint_path, "a") as f:
            record = {self.field: row_id}
            f.write(json.dumps(record) + "\n")
```

### Step 4: Run test to verify it passes

```bash
pytest tests/core/sda/test_checkpoint.py::test_checkpoint_manager_loads_existing_ids -v
```

**Expected:** PASS

### Step 5: Write test for mark_processed

```python
def test_checkpoint_manager_marks_processed(tmp_path):
    """CheckpointManager appends new IDs to checkpoint."""
    checkpoint_path = tmp_path / "checkpoint.jsonl"

    manager = CheckpointManager(checkpoint_path, field="id")
    manager.mark_processed("row1")
    manager.mark_processed("row2")

    # Verify file was written
    assert checkpoint_path.exists()

    # Verify IDs are tracked
    assert manager.is_processed("row1")
    assert manager.is_processed("row2")

    # Verify new manager loads same IDs
    manager2 = CheckpointManager(checkpoint_path, field="id")
    assert manager2.is_processed("row1")
    assert manager2.is_processed("row2")
```

### Step 6: Run mark_processed test

```bash
pytest tests/core/sda/test_checkpoint.py::test_checkpoint_manager_marks_processed -v
```

**Expected:** PASS

### Step 7: Integrate CheckpointManager into SDARunner

```python
# src/elspeth/core/sda/runner.py

# Add import at top
from elspeth.core.sda.checkpoint import CheckpointManager

# In SDARunner.run(), replace checkpoint logic:
# OLD:
#     processed_ids: set[str] | None = None
#     checkpoint_field = None
#     checkpoint_path = None
#     if self.checkpoint_config:
#         checkpoint_path = Path(self.checkpoint_config.get("path", "checkpoint.jsonl"))
#         checkpoint_field = self.checkpoint_config.get("field", "APPID")
#         processed_ids = self._load_checkpoint(checkpoint_path)

# NEW:
    checkpoint_manager: CheckpointManager | None = None
    checkpoint_field: str | None = None
    if self.checkpoint_config:
        checkpoint_path = Path(self.checkpoint_config.get("path", "checkpoint.jsonl"))
        checkpoint_field = self.checkpoint_config.get("field", "APPID")
        checkpoint_manager = CheckpointManager(checkpoint_path, checkpoint_field)

# Replace checkpoint check in loop:
# OLD:
#     if processed_ids is not None and row_id in processed_ids:
#         continue

# NEW:
    if checkpoint_manager and row_id and checkpoint_manager.is_processed(row_id):
        continue

# Replace checkpoint append in handle_success:
# OLD:
#     if checkpoint_path and row_id is not None:
#         if processed_ids is not None:
#             processed_ids.add(row_id)
#         self._append_checkpoint(checkpoint_path, row_id)

# NEW:
    if checkpoint_manager and row_id:
        checkpoint_manager.mark_processed(row_id)

# DELETE old methods:
# - _load_checkpoint()
# - _append_checkpoint()
```

### Step 8: Run characterization tests to verify refactor

```bash
pytest tests/core/sda/test_runner.py -v
```

**Expected:** All tests PASS (behavior unchanged)

### Step 9: Commit CheckpointManager extraction

```bash
git add src/elspeth/core/sda/checkpoint.py tests/core/sda/test_checkpoint.py src/elspeth/core/sda/runner.py
git commit -m "refactor: extract CheckpointManager from SDARunner"
```

---

## Task 3: Extract PromptCompiler

**Goal:** Extract prompt template compilation into dedicated class

**Files:**
- Create: `src/elspeth/core/sda/prompt_compiler.py`
- Create: `tests/core/sda/test_prompt_compiler.py`
- Modify: `src/elspeth/core/sda/runner.py`

### Step 1: Write failing test for PromptCompiler

```python
# tests/core/sda/test_prompt_compiler.py
"""Tests for PromptCompiler."""

from elspeth.core.sda.prompt_compiler import PromptCompiler
from elspeth.core.prompts import PromptEngine


def test_prompt_compiler_compiles_system_and_user():
    """PromptCompiler compiles system and user prompt templates."""
    compiler = PromptCompiler(
        engine=PromptEngine(),
        system_prompt="You are {role}",
        user_prompt="Process: {text}",
        cycle_name="test-cycle",
        defaults={"role": "assistant"},
    )

    templates = compiler.compile()

    assert templates.system is not None
    assert templates.user is not None
    assert "system" in templates.system.name
    assert "user" in templates.user.name
```

### Step 2: Run test to verify it fails

```bash
pytest tests/core/sda/test_prompt_compiler.py::test_prompt_compiler_compiles_system_and_user -v
```

**Expected:** FAIL with "No module named 'elspeth.core.sda.prompt_compiler'"

### Step 3: Write minimal PromptCompiler implementation

```python
# src/elspeth/core/sda/prompt_compiler.py
"""Prompt template compilation for SDA execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from elspeth.core.prompts import PromptEngine, PromptTemplate


@dataclass
class CompiledPrompts:
    """Compiled prompt templates."""

    system: PromptTemplate
    user: PromptTemplate
    criteria: Dict[str, PromptTemplate]


class PromptCompiler:
    """Compiles Jinja2 prompt templates for SDA execution."""

    def __init__(
        self,
        engine: PromptEngine,
        system_prompt: str,
        user_prompt: str,
        cycle_name: str,
        defaults: Dict[str, Any] | None = None,
        criteria: list[Dict[str, Any]] | None = None,
    ):
        """
        Initialize prompt compiler.

        Args:
            engine: PromptEngine instance
            system_prompt: System prompt template
            user_prompt: User prompt template
            cycle_name: Name of SDA cycle (for template naming)
            defaults: Default values for template variables
            criteria: Criteria-based prompt definitions
        """
        self.engine = engine
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.cycle_name = cycle_name
        self.defaults = defaults or {}
        self.criteria = criteria or []

    def compile(self) -> CompiledPrompts:
        """Compile all prompt templates."""
        system_template = self.engine.compile(
            self.system_prompt,
            name=f"{self.cycle_name}:system",
            defaults=self.defaults,
        )

        user_template = self.engine.compile(
            self.user_prompt,
            name=f"{self.cycle_name}:user",
            defaults=self.defaults,
        )

        criteria_templates: Dict[str, PromptTemplate] = {}
        for crit in self.criteria:
            template_text = crit.get("template", self.user_prompt)
            crit_name = crit.get("name") or template_text
            crit_defaults = dict(self.defaults)
            crit_defaults.update(crit.get("defaults", {}))

            criteria_templates[crit_name] = self.engine.compile(
                template_text,
                name=f"{self.cycle_name}:criteria:{crit_name}",
                defaults=crit_defaults,
            )

        return CompiledPrompts(
            system=system_template,
            user=user_template,
            criteria=criteria_templates,
        )
```

### Step 4: Run test to verify it passes

```bash
pytest tests/core/sda/test_prompt_compiler.py::test_prompt_compiler_compiles_system_and_user -v
```

**Expected:** PASS

### Step 5: Write test for criteria compilation

```python
def test_prompt_compiler_compiles_criteria():
    """PromptCompiler compiles criteria-based prompts."""
    compiler = PromptCompiler(
        engine=PromptEngine(),
        system_prompt="System",
        user_prompt="Default",
        cycle_name="test",
        criteria=[
            {"name": "accuracy", "template": "Rate accuracy: {text}"},
            {"name": "clarity", "template": "Rate clarity: {text}"},
        ],
    )

    templates = compiler.compile()

    assert len(templates.criteria) == 2
    assert "accuracy" in templates.criteria
    assert "clarity" in templates.criteria
```

### Step 6: Run criteria test

```bash
pytest tests/core/sda/test_prompt_compiler.py::test_prompt_compiler_compiles_criteria -v
```

**Expected:** PASS

### Step 7: Integrate PromptCompiler into SDARunner

```python
# src/elspeth/core/sda/runner.py

# Add import
from elspeth.core.sda.prompt_compiler import PromptCompiler, CompiledPrompts

# In SDARunner.run(), replace compilation logic:
# OLD:
#     transform_plugins = self.transform_plugins or []
#     engine = self.prompt_engine or PromptEngine()
#     system_template = engine.compile(...)
#     user_template = engine.compile(...)
#     criteria_templates: Dict[str, PromptTemplate] = {}
#     if self.criteria:
#         for crit in self.criteria:
#             ...
#     self._compiled_system_prompt = system_template
#     self._compiled_user_prompt = user_template
#     self._compiled_criteria_prompts = criteria_templates

# NEW:
    engine = self.prompt_engine or PromptEngine()
    compiler = PromptCompiler(
        engine=engine,
        system_prompt=self.prompt_system or "",
        user_prompt=self.prompt_template or "",
        cycle_name=self.cycle_name or "experiment",
        defaults=self.prompt_defaults or {},
        criteria=self.criteria,
    )
    compiled_prompts = compiler.compile()

    system_template = compiled_prompts.system
    user_template = compiled_prompts.user
    criteria_templates = compiled_prompts.criteria

# Remove storage in instance variables (they're local now)
```

### Step 8: Run characterization tests

```bash
pytest tests/core/sda/test_runner.py -v
```

**Expected:** All tests PASS

### Step 9: Commit PromptCompiler extraction

```bash
git add src/elspeth/core/sda/prompt_compiler.py tests/core/sda/test_prompt_compiler.py src/elspeth/core/sda/runner.py
git commit -m "refactor: extract PromptCompiler from SDARunner"
```

---

## Task 4: Extract EarlyStopCoordinator

**Goal:** Extract early stopping logic into dedicated class

**Files:**
- Create: `src/elspeth/core/sda/early_stop.py`
- Create: `tests/core/sda/test_early_stop.py`
- Modify: `src/elspeth/core/sda/runner.py`

### Step 1: Write failing test for EarlyStopCoordinator

```python
# tests/core/sda/test_early_stop.py
"""Tests for EarlyStopCoordinator."""

from elspeth.core.sda.early_stop import EarlyStopCoordinator


class MockHaltCondition:
    """Mock halt condition plugin."""

    def __init__(self, should_halt: bool = False, reason: dict | None = None):
        self.should_halt = should_halt
        self.reason = reason or {"reason": "test halt"}
        self.reset_called = False

    def reset(self) -> None:
        self.reset_called = True

    def check(self, record: dict, metadata: dict | None = None) -> dict | None:
        if self.should_halt:
            return self.reason
        return None


def test_coordinator_initializes_plugins():
    """EarlyStopCoordinator initializes halt condition plugins."""
    plugin = MockHaltCondition()
    coordinator = EarlyStopCoordinator(plugins=[plugin])

    assert plugin.reset_called is True
    assert not coordinator.is_stopped()
```

### Step 2: Run test to verify it fails

```bash
pytest tests/core/sda/test_early_stop.py::test_coordinator_initializes_plugins -v
```

**Expected:** FAIL with "No module named 'elspeth.core.sda.early_stop'"

### Step 3: Write minimal EarlyStopCoordinator implementation

```python
# src/elspeth/core/sda/early_stop.py
"""Early stopping coordination for SDA execution."""

from __future__ import annotations

import logging
import threading
from typing import Dict, Any

from elspeth.core.sda.plugins import HaltConditionPlugin


logger = logging.getLogger(__name__)


class EarlyStopCoordinator:
    """Coordinates early stopping via halt condition plugins."""

    def __init__(self, plugins: list[HaltConditionPlugin] | None = None):
        """
        Initialize early stop coordinator.

        Args:
            plugins: List of halt condition plugins
        """
        self.plugins = plugins or []
        self._event = threading.Event() if self.plugins else None
        self._lock = threading.Lock() if self.plugins else None
        self._reason: Dict[str, Any] | None = None

        # Initialize plugins
        for plugin in self.plugins:
            try:
                plugin.reset()
            except AttributeError:
                pass

    def is_stopped(self) -> bool:
        """Check if early stop has been triggered."""
        if not self._event:
            return False
        return self._event.is_set()

    def check_record(self, record: Dict[str, Any], row_index: int | None = None) -> None:
        """
        Check if record triggers halt condition.

        Args:
            record: Processed record to check
            row_index: Index of row being processed
        """
        if not self._event or self._event.is_set():
            return

        if not self.plugins or self._reason:
            return

        metadata: Dict[str, Any] | None = None
        if row_index is not None:
            metadata = {"row_index": row_index}

        def _evaluate() -> None:
            if self._event.is_set() or self._reason:
                return

            for plugin in self.plugins:
                try:
                    reason = plugin.check(record, metadata=metadata)
                except Exception:
                    logger.exception(
                        "Early-stop plugin '%s' raised an unexpected error; continuing",
                        getattr(plugin, "name", "unknown"),
                    )
                    continue

                if not reason:
                    continue

                reason = dict(reason)
                reason.setdefault("plugin", getattr(plugin, "name", "unknown"))
                if metadata:
                    for key, value in metadata.items():
                        reason.setdefault(key, value)

                self._reason = reason
                self._event.set()
                logger.info(
                    "Early stop triggered by plugin '%s' (reason: %s)",
                    reason.get("plugin", getattr(plugin, "name", "unknown")),
                    {k: v for k, v in reason.items() if k != "plugin"},
                )
                break

        if self._lock:
            with self._lock:
                _evaluate()
        else:
            _evaluate()

    def get_reason(self) -> Dict[str, Any] | None:
        """Get early stop reason if triggered."""
        return dict(self._reason) if self._reason else None
```

### Step 4: Run test to verify it passes

```bash
pytest tests/core/sda/test_early_stop.py::test_coordinator_initializes_plugins -v
```

**Expected:** PASS

### Step 5: Write test for halt detection

```python
def test_coordinator_detects_halt_condition():
    """EarlyStopCoordinator detects when halt condition is met."""
    plugin = MockHaltCondition(should_halt=True, reason={"reason": "budget exceeded"})
    coordinator = EarlyStopCoordinator(plugins=[plugin])

    # Initially not stopped
    assert not coordinator.is_stopped()

    # Check record that triggers halt
    coordinator.check_record({"cost": 100}, row_index=5)

    # Now stopped
    assert coordinator.is_stopped()
    reason = coordinator.get_reason()
    assert reason["reason"] == "budget exceeded"
    assert reason["row_index"] == 5
```

### Step 6: Run halt detection test

```bash
pytest tests/core/sda/test_early_stop.py::test_coordinator_detects_halt_condition -v
```

**Expected:** PASS

### Step 7: Integrate EarlyStopCoordinator into SDARunner

```python
# src/elspeth/core/sda/runner.py

# Add import
from elspeth.core.sda.early_stop import EarlyStopCoordinator

# In SDARunner.run(), replace _init_halt_conditions() call:
# OLD:
#     self._init_halt_conditions()

# NEW:
    plugins = []
    if self.halt_condition_plugins:
        plugins = list(self.halt_condition_plugins)
    elif self.halt_condition_config:
        definition = {"name": "threshold", "options": dict(self.halt_condition_config)}
        plugin = create_halt_condition_plugin(definition)
        plugins = [plugin]

    early_stop = EarlyStopCoordinator(plugins=plugins)

# Replace early stop checks:
# OLD:
#     if self._early_stop_event and self._early_stop_event.is_set():
#         break

# NEW:
    if early_stop.is_stopped():
        break

# Replace _maybe_trigger_early_stop():
# OLD:
#     self._maybe_trigger_early_stop(record, row_index=idx)

# NEW:
    early_stop.check_record(record, row_index=idx)

# Replace early stop metadata:
# OLD:
#     if self._early_stop_reason:
#         metadata["early_stop"] = dict(self._early_stop_reason)
#         payload["early_stop"] = dict(self._early_stop_reason)

# NEW:
    reason = early_stop.get_reason()
    if reason:
        metadata["early_stop"] = reason
        payload["early_stop"] = reason

# DELETE old methods:
# - _init_halt_conditions()
# - _maybe_trigger_early_stop()
```

### Step 8: Run characterization tests

```bash
pytest tests/core/sda/test_runner.py -v
```

**Expected:** All tests PASS

### Step 9: Commit EarlyStopCoordinator extraction

```bash
git add src/elspeth/core/sda/early_stop.py tests/core/sda/test_early_stop.py src/elspeth/core/sda/runner.py
git commit -m "refactor: extract EarlyStopCoordinator from SDARunner"
```

---

## Task 5: Extract RowProcessor

**Goal:** Extract single row processing into dedicated class

**Files:**
- Create: `src/elspeth/core/sda/row_processor.py`
- Create: `tests/core/sda/test_row_processor.py`
- Modify: `src/elspeth/core/sda/runner.py`

### Step 1: Write failing test for RowProcessor

```python
# tests/core/sda/test_row_processor.py
"""Tests for RowProcessor."""

import pandas as pd
from elspeth.core.sda.row_processor import RowProcessor
from elspeth.core.prompts import PromptEngine


class MockLLMClient:
    def __init__(self, response: dict | None = None):
        self.response = response or {"content": "mock"}

    def generate(self, system: str, user: str, metadata: dict | None = None) -> dict:
        return self.response


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
```

### Step 2: Run test to verify it fails

```bash
pytest tests/core/sda/test_row_processor.py::test_row_processor_processes_single_row -v
```

**Expected:** FAIL with "No module named 'elspeth.core.sda.row_processor'"

### Step 3: Write minimal RowProcessor implementation

```python
# src/elspeth/core/sda/row_processor.py
"""Single row processing for SDA execution."""

from __future__ import annotations

from typing import Dict, Any, Tuple

import pandas as pd

from elspeth.core.interfaces import LLMClientProtocol
from elspeth.core.prompts import PromptEngine, PromptTemplate, PromptRenderingError, PromptValidationError
from elspeth.core.sda.plugins import TransformPlugin


class RowProcessor:
    """Processes single rows through LLM and transforms."""

    def __init__(
        self,
        llm_client: LLMClientProtocol,
        engine: PromptEngine,
        system_template: PromptTemplate,
        user_template: PromptTemplate,
        criteria_templates: Dict[str, PromptTemplate],
        transform_plugins: list[TransformPlugin],
        criteria: list[Dict[str, Any]] | None = None,
        llm_executor: Any = None,  # LLMExecutor will be extracted in next task
        security_level: str | None = None,
    ):
        """
        Initialize row processor.

        Args:
            llm_client: LLM client for generation
            engine: Prompt engine for rendering
            system_template: Compiled system prompt
            user_template: Compiled user prompt
            criteria_templates: Compiled criteria prompts
            transform_plugins: Transform plugins to apply
            criteria: Criteria definitions
            llm_executor: LLM executor for retry logic
            security_level: Security level for records
        """
        self.llm_client = llm_client
        self.engine = engine
        self.system_template = system_template
        self.user_template = user_template
        self.criteria_templates = criteria_templates
        self.transform_plugins = transform_plugins
        self.criteria = criteria or []
        self.llm_executor = llm_executor
        self.security_level = security_level

    def process_row(
        self,
        row: pd.Series,
        context: Dict[str, Any],
        row_id: str | None,
    ) -> Tuple[Dict[str, Any] | None, Dict[str, Any] | None]:
        """
        Process single row through LLM and transforms.

        Args:
            row: Pandas Series representing row
            context: Prompt context dictionary
            row_id: Unique row identifier

        Returns:
            Tuple of (record, failure). One will be None.
        """
        try:
            rendered_system = self.engine.render(self.system_template, context)

            if self.criteria:
                responses: Dict[str, Dict[str, Any]] = {}
                for crit in self.criteria:
                    crit_name = crit.get("name") or crit.get("template", "criteria")
                    prompt_template = self.criteria_templates[crit_name]
                    user_prompt = self.engine.render(prompt_template, context, extra={"criteria": crit_name})

                    # Use LLM executor if available, otherwise direct call
                    if self.llm_executor:
                        response = self.llm_executor.execute(
                            user_prompt,
                            {"row_id": row.get("APPID"), "criteria": crit_name},
                            system_prompt=rendered_system,
                        )
                    else:
                        response = self.llm_client.generate(
                            system=rendered_system,
                            user=user_prompt,
                            metadata={"row_id": row.get("APPID"), "criteria": crit_name},
                        )

                    responses[crit_name] = response

                first_response = next(iter(responses.values())) if responses else {}
                record: Dict[str, Any] = {
                    "row": context,
                    "response": first_response,
                    "responses": responses,
                }

                # Merge metrics from all responses
                for resp in responses.values():
                    metrics = resp.get("metrics")
                    if metrics:
                        record.setdefault("metrics", {}).update(metrics)
            else:
                user_prompt = self.engine.render(self.user_template, context)

                # Use LLM executor if available
                if self.llm_executor:
                    response = self.llm_executor.execute(
                        user_prompt,
                        {"row_id": row.get("APPID")},
                        system_prompt=rendered_system,
                    )
                else:
                    response = self.llm_client.generate(
                        system=rendered_system,
                        user=user_prompt,
                        metadata={"row_id": row.get("APPID")},
                    )

                record = {"row": context, "response": response}
                metrics = response.get("metrics")
                if metrics:
                    record.setdefault("metrics", {}).update(metrics)

            # Add retry metadata if present
            retry_meta = response.get("retry")
            if retry_meta:
                record["retry"] = retry_meta

            # Apply transform plugins
            for plugin in self.transform_plugins:
                derived = plugin.transform(
                    record["row"],
                    record.get("responses") or {"default": record["response"]},
                )
                if derived:
                    record.setdefault("metrics", {}).update(derived)

            # Add security level
            if self.security_level:
                record["security_level"] = self.security_level

            return record, None

        except (PromptRenderingError, PromptValidationError) as exc:
            return None, {
                "row": context,
                "error": str(exc),
                "error_type": type(exc).__name__,
            }
```

### Step 4: Run test to verify it passes

```bash
pytest tests/core/sda/test_row_processor.py::test_row_processor_processes_single_row -v
```

**Expected:** PASS

### Step 5: Write test for transform plugin application

```python
class MockTransform:
    def transform(self, row: dict, responses: dict) -> dict:
        return {"transformed": True}


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
```

### Step 6: Run transform test

```bash
pytest tests/core/sda/test_row_processor.py::test_row_processor_applies_transforms -v
```

**Expected:** PASS

### Step 7: Integrate RowProcessor into SDARunner

```python
# src/elspeth/core/sda/runner.py

# Add import
from elspeth.core.sda.row_processor import RowProcessor

# In SDARunner.run(), after compiling prompts:
    row_processor = RowProcessor(
        llm_client=self.llm_client,
        engine=engine,
        system_template=system_template,
        user_template=user_template,
        criteria_templates=criteria_templates,
        transform_plugins=transform_plugins,
        criteria=self.criteria,
        llm_executor=self,  # SDARunner has _execute_llm for now
        security_level=self._active_security_level,
    )

# Replace _process_single_row() calls:
# OLD:
#     record, failure = self._process_single_row(
#         engine, system_template, user_template, criteria_templates,
#         transform_plugins, context, row, row_id,
#     )

# NEW:
    record, failure = row_processor.process_row(row, context, row_id)

# Note: Keep _execute_llm() for now, will extract in next task
# DELETE: _process_single_row() method
```

### Step 8: Run characterization tests

```bash
pytest tests/core/sda/test_runner.py -v
```

**Expected:** All tests PASS

### Step 9: Commit RowProcessor extraction

```bash
git add src/elspeth/core/sda/row_processor.py tests/core/sda/test_row_processor.py src/elspeth/core/sda/runner.py
git commit -m "refactor: extract RowProcessor from SDARunner"
```

---

## Task 6: Extract LLMExecutor (Retry Logic)

**Goal:** Extract LLM execution with retry logic into dedicated class

**Files:**
- Create: `src/elspeth/core/sda/llm_executor.py`
- Create: `tests/core/sda/test_llm_executor.py`
- Modify: `src/elspeth/core/sda/runner.py`
- Modify: `src/elspeth/core/sda/row_processor.py`

### Step 1: Write failing test for LLMExecutor

```python
# tests/core/sda/test_llm_executor.py
"""Tests for LLMExecutor."""

from elspeth.core.sda.llm_executor import LLMExecutor


class MockLLMClient:
    def __init__(self, fail_count: int = 0):
        self.calls = 0
        self.fail_count = fail_count

    def generate(self, system: str, user: str, metadata: dict | None = None) -> dict:
        self.calls += 1
        if self.calls <= self.fail_count:
            raise RuntimeError("LLM error")
        return {"content": "success"}


def test_llm_executor_executes_without_retry():
    """LLMExecutor executes LLM call without retry config."""
    llm_client = MockLLMClient()
    executor = LLMExecutor(
        llm_client=llm_client,
        middlewares=[],
        retry_config=None,
        rate_limiter=None,
        cost_tracker=None,
    )

    result = executor.execute("user prompt", {"row_id": "1"}, system_prompt="system")

    assert result["content"] == "success"
    assert llm_client.calls == 1
```

### Step 2: Run test to verify it fails

```bash
pytest tests/core/sda/test_llm_executor.py::test_llm_executor_executes_without_retry -v
```

**Expected:** FAIL with "No module named 'elspeth.core.sda.llm_executor'"

### Step 3: Write minimal LLMExecutor implementation

```python
# src/elspeth/core/sda/llm_executor.py
"""LLM execution with retry logic for SDA."""

from __future__ import annotations

import logging
import time
from typing import Dict, Any

from elspeth.core.interfaces import LLMClientProtocol
from elspeth.core.llm.middleware import LLMMiddleware, LLMRequest
from elspeth.core.controls import RateLimiter, CostTracker


logger = logging.getLogger(__name__)


class LLMExecutor:
    """Executes LLM calls with middleware, retry, rate limiting, and cost tracking."""

    def __init__(
        self,
        llm_client: LLMClientProtocol,
        middlewares: list[LLMMiddleware],
        retry_config: Dict[str, Any] | None,
        rate_limiter: RateLimiter | None,
        cost_tracker: CostTracker | None,
    ):
        """
        Initialize LLM executor.

        Args:
            llm_client: LLM client for generation
            middlewares: Middleware chain
            retry_config: Retry configuration (max_attempts, backoff_multiplier, initial_delay)
            rate_limiter: Rate limiter instance
            cost_tracker: Cost tracker instance
        """
        self.llm_client = llm_client
        self.middlewares = middlewares
        self.retry_config = retry_config or {}
        self.rate_limiter = rate_limiter
        self.cost_tracker = cost_tracker

    def execute(
        self,
        user_prompt: str,
        metadata: Dict[str, Any],
        system_prompt: str | None = None,
    ) -> Dict[str, Any]:
        """
        Execute LLM call with retry logic.

        Args:
            user_prompt: User prompt text
            metadata: Request metadata
            system_prompt: System prompt text

        Returns:
            LLM response dictionary
        """
        max_attempts = self.retry_config.get("max_attempts", 1)
        backoff_multiplier = self.retry_config.get("backoff_multiplier", 2.0)
        initial_delay = self.retry_config.get("initial_delay", 1.0)

        retry_history: list[Dict[str, Any]] = []
        last_error: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                # Apply rate limiting
                if self.rate_limiter:
                    estimated_tokens = len(user_prompt.split()) + len((system_prompt or "").split())
                    self.rate_limiter.acquire(estimated_tokens)

                # Build request
                request = LLMRequest(
                    system_prompt=system_prompt or "",
                    user_prompt=user_prompt,
                    metadata=metadata,
                )

                # Apply middleware chain - before_request
                for middleware in self.middlewares:
                    request = middleware.before_request(request)

                # Execute LLM call
                response = self.llm_client.generate(
                    system=request.system_prompt,
                    user=request.user_prompt,
                    metadata=request.metadata,
                )

                # Apply middleware chain - after_response
                for middleware in reversed(self.middlewares):
                    response = middleware.after_response(request, response)

                # Track cost
                if self.cost_tracker:
                    usage = response.get("usage", {})
                    self.cost_tracker.track_request(
                        prompt_tokens=usage.get("prompt_tokens", 0),
                        completion_tokens=usage.get("completion_tokens", 0),
                    )

                # Add retry metadata if retried
                if attempt > 1:
                    response["retry"] = {
                        "attempts": attempt,
                        "history": retry_history,
                    }

                return response

            except Exception as exc:
                last_error = exc
                retry_history.append({
                    "attempt": attempt,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                })

                if attempt < max_attempts:
                    delay = initial_delay * (backoff_multiplier ** (attempt - 1))
                    logger.warning(
                        "LLM call failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt,
                        max_attempts,
                        delay,
                        exc,
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        "LLM call failed after %d attempts: %s",
                        max_attempts,
                        exc,
                    )

        # All retries exhausted
        raise last_error
```

### Step 4: Run test to verify it passes

```bash
pytest tests/core/sda/test_llm_executor.py::test_llm_executor_executes_without_retry -v
```

**Expected:** PASS

### Step 5: Write test for retry behavior

```python
def test_llm_executor_retries_on_failure():
    """LLMExecutor retries on LLM failure."""
    llm_client = MockLLMClient(fail_count=2)  # Fail first 2 attempts
    executor = LLMExecutor(
        llm_client=llm_client,
        middlewares=[],
        retry_config={
            "max_attempts": 3,
            "backoff_multiplier": 1.0,
            "initial_delay": 0.01,  # Fast for testing
        },
        rate_limiter=None,
        cost_tracker=None,
    )

    result = executor.execute("prompt", {})

    # Should succeed on 3rd attempt
    assert result["content"] == "success"
    assert llm_client.calls == 3
    assert result["retry"]["attempts"] == 3
```

### Step 6: Run retry test

```bash
pytest tests/core/sda/test_llm_executor.py::test_llm_executor_retries_on_failure -v
```

**Expected:** PASS

### Step 7: Integrate LLMExecutor into RowProcessor and SDARunner

```python
# src/elspeth/core/sda/runner.py

# Add import
from elspeth.core.sda.llm_executor import LLMExecutor

# In SDARunner.run(), create LLM executor:
    llm_executor = LLMExecutor(
        llm_client=self.llm_client,
        middlewares=self.llm_middlewares or [],
        retry_config=self.retry_config,
        rate_limiter=self.rate_limiter,
        cost_tracker=self.cost_tracker,
    )

# Pass to RowProcessor:
    row_processor = RowProcessor(
        llm_client=self.llm_client,
        engine=engine,
        system_template=system_template,
        user_template=user_template,
        criteria_templates=criteria_templates,
        transform_plugins=transform_plugins,
        criteria=self.criteria,
        llm_executor=llm_executor,  # Pass executor instead of self
        security_level=self._active_security_level,
    )

# DELETE old methods:
# - _execute_llm()
# - _notify_retry_exhausted()
```

```python
# src/elspeth/core/sda/row_processor.py

# Update type hint for llm_executor parameter:
from elspeth.core.sda.llm_executor import LLMExecutor

# In __init__:
    llm_executor: LLMExecutor | None = None,
```

### Step 8: Run characterization tests

```bash
pytest tests/core/sda/test_runner.py -v
```

**Expected:** All tests PASS

### Step 9: Commit LLMExecutor extraction

```bash
git add src/elspeth/core/sda/llm_executor.py tests/core/sda/test_llm_executor.py src/elspeth/core/sda/runner.py src/elspeth/core/sda/row_processor.py
git commit -m "refactor: extract LLMExecutor with retry logic from SDARunner"
```

---

## Task 7: Extract ResultAggregator

**Goal:** Extract result collection and metadata building into dedicated class

**Files:**
- Create: `src/elspeth/core/sda/result_aggregator.py`
- Create: `tests/core/sda/test_result_aggregator.py`
- Modify: `src/elspeth/core/sda/runner.py`

### Step 1: Write failing test for ResultAggregator

```python
# tests/core/sda/test_result_aggregator.py
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
```

### Step 2: Run test to verify it fails

```bash
pytest tests/core/sda/test_result_aggregator.py::test_result_aggregator_collects_results -v
```

**Expected:** FAIL with "No module named 'elspeth.core.sda.result_aggregator'"

### Step 3: Write minimal ResultAggregator implementation

```python
# src/elspeth/core/sda/result_aggregator.py
"""Result aggregation and payload building for SDA execution."""

from __future__ import annotations

from typing import Dict, Any

from elspeth.core.sda.plugins import AggregationTransform
from elspeth.core.controls import CostTracker


class ResultAggregator:
    """Aggregates results, failures, and metadata into final payload."""

    def __init__(
        self,
        aggregation_plugins: list[AggregationTransform],
        cost_tracker: CostTracker | None = None,
    ):
        """
        Initialize result aggregator.

        Args:
            aggregation_plugins: Aggregation transform plugins
            cost_tracker: Cost tracker for summary
        """
        self.aggregation_plugins = aggregation_plugins
        self.cost_tracker = cost_tracker
        self._results_with_index: list[tuple[int, Dict[str, Any]]] = []
        self._failures: list[Dict[str, Any]] = []

    def add_result(self, record: Dict[str, Any], row_index: int) -> None:
        """Add successful result."""
        self._results_with_index.append((row_index, record))

    def add_failure(self, failure: Dict[str, Any]) -> None:
        """Add failed result."""
        self._failures.append(failure)

    def build_payload(
        self,
        security_level: str | None = None,
        early_stop_reason: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Build final payload with results, metadata, and aggregates.

        Args:
            security_level: Security level for metadata
            early_stop_reason: Early stop reason if triggered

        Returns:
            Complete payload dictionary
        """
        # Sort results by original index
        self._results_with_index.sort(key=lambda item: item[0])
        results = [record for _, record in self._results_with_index]

        # Build base payload
        payload: Dict[str, Any] = {"results": results}
        if self._failures:
            payload["failures"] = self._failures

        # Apply aggregation plugins
        aggregates = {}
        for plugin in self.aggregation_plugins:
            derived = plugin.aggregate(results)
            if derived:
                aggregates[plugin.name] = derived

        if aggregates:
            payload["aggregates"] = aggregates

        # Build metadata
        metadata: Dict[str, Any] = {
            "rows": len(results),
            "row_count": len(results),
        }

        # Add retry summary
        retry_summary = self._build_retry_summary(results, self._failures)
        if retry_summary:
            metadata["retry_summary"] = retry_summary

        # Add aggregates to metadata
        if aggregates:
            metadata["aggregates"] = aggregates

        # Add cost summary
        if self.cost_tracker:
            cost_summary = self.cost_tracker.summary()
            if cost_summary:
                payload["cost_summary"] = cost_summary
                metadata["cost_summary"] = cost_summary

        # Add failures count
        if self._failures:
            metadata["failures"] = self._failures

        # Add security level
        if security_level:
            metadata["security_level"] = security_level

        # Add early stop info
        if early_stop_reason:
            metadata["early_stop"] = early_stop_reason
            payload["early_stop"] = early_stop_reason

        payload["metadata"] = metadata
        return payload

    def _build_retry_summary(
        self,
        results: list[Dict[str, Any]],
        failures: list[Dict[str, Any]],
    ) -> Dict[str, Any] | None:
        """Build retry summary from results and failures."""
        retry_summary = {
            "total_requests": len(results) + len(failures),
            "total_retries": 0,
            "exhausted": len(failures),
        }

        retry_present = False

        # Count retries in successful results
        for record in results:
            info = record.get("retry")
            if info:
                retry_present = True
                attempts = int(info.get("attempts", 1))
                retry_summary["total_retries"] += max(attempts - 1, 0)

        # Count retries in failures
        for failure in failures:
            info = failure.get("retry")
            if info:
                retry_present = True
                attempts = int(info.get("attempts", 0))
                retry_summary["total_retries"] += max(attempts - 1, 0)

        return retry_summary if retry_present else None
```

### Step 4: Run test to verify it passes

```bash
pytest tests/core/sda/test_result_aggregator.py::test_result_aggregator_collects_results -v
```

**Expected:** PASS

### Step 5: Write test for aggregation plugins

```python
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
```

### Step 6: Run aggregation test

```bash
pytest tests/core/sda/test_result_aggregator.py::test_result_aggregator_applies_aggregation_plugins -v
```

**Expected:** PASS

### Step 7: Integrate ResultAggregator into SDARunner

```python
# src/elspeth/core/sda/runner.py

# Add import
from elspeth.core.sda.result_aggregator import ResultAggregator

# In SDARunner.run(), create aggregator:
    aggregator = ResultAggregator(
        aggregation_plugins=self.aggregation_transforms or [],
        cost_tracker=self.cost_tracker,
    )

# Replace result collection:
# OLD:
#     records_with_index: List[tuple[int, Dict[str, Any]]] = []
#     failures: List[Dict[str, Any]] = []
#
#     def handle_success(idx: int, record: Dict[str, Any], row_id: str | None) -> None:
#         records_with_index.append((idx, record))
#         ...
#
#     def handle_failure(failure: Dict[str, Any]) -> None:
#         failures.append(failure)

# NEW:
    def handle_success(idx: int, record: Dict[str, Any], row_id: str | None) -> None:
        aggregator.add_result(record, row_index=idx)
        if checkpoint_manager and row_id:
            checkpoint_manager.mark_processed(row_id)
        early_stop.check_record(record, row_index=idx)

    def handle_failure(failure: Dict[str, Any]) -> None:
        aggregator.add_failure(failure)

# Replace payload building:
# OLD:
#     records_with_index.sort(key=lambda item: item[0])
#     results = [record for _, record in records_with_index]
#     payload = {"results": results}
#     ... (157 lines of metadata building)

# NEW:
    payload = aggregator.build_payload(
        security_level=self._active_security_level,
        early_stop_reason=early_stop.get_reason(),
    )
```

### Step 8: Run characterization tests

```bash
pytest tests/core/sda/test_runner.py -v
```

**Expected:** All tests PASS

### Step 9: Commit ResultAggregator extraction

```bash
git add src/elspeth/core/sda/result_aggregator.py tests/core/sda/test_result_aggregator.py src/elspeth/core/sda/runner.py
git commit -m "refactor: extract ResultAggregator from SDARunner"
```

---

## Task 8: Final Cleanup and Integration Tests

**Goal:** Clean up SDARunner, verify all integrations, run full test suite

**Files:**
- Modify: `src/elspeth/core/sda/runner.py`
- Modify: `src/elspeth/core/sda/__init__.py`
- Create: `tests/core/sda/test_integration.py`

### Step 1: Review SDARunner for remaining complexity

```bash
wc -l src/elspeth/core/sda/runner.py
```

**Expected:** Significantly reduced line count (target: <200 lines)

### Step 2: Write integration test exercising full pipeline

```python
# tests/core/sda/test_integration.py
"""Integration tests for refactored SDA components."""

import pandas as pd
from pathlib import Path

from elspeth.core.sda.runner import SDARunner
from tests.core.sda.test_runner import MockLLMClient, MockSink


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
        prompt_fields=["text"],
        checkpoint_config={"path": str(checkpoint_path), "field": "id"},
        retry_config={"max_attempts": 2, "backoff_multiplier": 1.5, "initial_delay": 0.1},
    )

    result = runner.run(df)

    # Verify all rows processed
    assert len(result["results"]) == 3
    assert result["metadata"]["rows"] == 3
    assert result["metadata"]["row_count"] == 3

    # Verify checkpoint created
    assert checkpoint_path.exists()

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
```

### Step 3: Run integration tests

```bash
pytest tests/core/sda/test_integration.py -v
```

**Expected:** All PASS

### Step 4: Update __init__.py exports

```python
# src/elspeth/core/sda/__init__.py

"""SDA (Sense/Decide/Act) orchestration components."""

from elspeth.core.sda.runner import SDARunner
from elspeth.core.sda.config import SDACycleConfig, SDASuite
from elspeth.core.sda.checkpoint import CheckpointManager
from elspeth.core.sda.prompt_compiler import PromptCompiler, CompiledPrompts
from elspeth.core.sda.early_stop import EarlyStopCoordinator
from elspeth.core.sda.row_processor import RowProcessor
from elspeth.core.sda.llm_executor import LLMExecutor
from elspeth.core.sda.result_aggregator import ResultAggregator

__all__ = [
    "SDARunner",
    "SDACycleConfig",
    "SDASuite",
    "CheckpointManager",
    "PromptCompiler",
    "CompiledPrompts",
    "EarlyStopCoordinator",
    "RowProcessor",
    "LLMExecutor",
    "ResultAggregator",
]
```

### Step 5: Run full test suite

```bash
pytest tests/core/sda/ -v
```

**Expected:** All tests PASS

### Step 6: Run linting

```bash
ruff check src/elspeth/core/sda/ tests/core/sda/
```

**Expected:** No errors

### Step 7: Run type checking

```bash
mypy src/elspeth/core/sda/
```

**Expected:** No errors (or only acceptable warnings)

### Step 8: Measure line count reduction

```bash
echo "Before refactoring: 583 lines"
wc -l src/elspeth/core/sda/runner.py
wc -l src/elspeth/core/sda/*.py | tail -1
```

**Expected:** SDARunner significantly reduced, total LOC similar (distributed across focused classes)

### Step 9: Commit final cleanup

```bash
git add src/elspeth/core/sda/__init__.py tests/core/sda/test_integration.py
git commit -m "refactor: finalize SDARunner refactoring with integration tests"
```

---

## Task 9: Update Documentation

**Goal:** Document the refactored architecture

**Files:**
- Create: `docs/architecture/sda-components.md`
- Modify: `docs/arch-analysis-2025-11-14-1201/04-final-report.md`

### Step 1: Write SDA components documentation

```markdown
# docs/architecture/sda-components.md

# SDA Core Components

**Last Updated:** 2025-11-14

This document describes the refactored SDA (Sense/Decide/Act) execution architecture.

## Overview

The SDA execution system has been refactored from a monolithic `SDARunner` class (583 lines) into focused, testable components following Single Responsibility Principle.

## Component Architecture

### SDARunner (Orchestrator)

**Responsibility:** High-level orchestration of SDA cycle execution

**Lines of Code:** ~150 (down from 583)

**Key Responsibilities:**
- Coordinate collaborator components
- Manage SDA cycle lifecycle
- Execute Sense/Decide/Act pattern

**Dependencies:**
- CheckpointManager
- PromptCompiler
- EarlyStopCoordinator
- RowProcessor
- LLMExecutor
- ResultAggregator

### CheckpointManager

**Responsibility:** Resume functionality via checkpoint tracking

**Lines of Code:** ~80

**Key Methods:**
- `is_processed(row_id)` - Check if row already processed
- `mark_processed(row_id)` - Mark row as complete and persist

**File Format:** JSONL with configurable ID field

### PromptCompiler

**Responsibility:** Jinja2 template compilation

**Lines of Code:** ~90

**Key Methods:**
- `compile()` - Compile all prompt templates
- Returns `CompiledPrompts` with system, user, and criteria templates

**Features:**
- Default value support
- Criteria-based prompts
- Template naming conventions

### EarlyStopCoordinator

**Responsibility:** Halt condition management

**Lines of Code:** ~120

**Key Methods:**
- `check_record(record, row_index)` - Evaluate halt conditions
- `is_stopped()` - Check if halted
- `get_reason()` - Get halt reason

**Features:**
- Thread-safe evaluation
- Multiple halt condition plugins
- Detailed halt reason metadata

### RowProcessor

**Responsibility:** Single row processing through LLM and transforms

**Lines of Code:** ~150

**Key Methods:**
- `process_row(row, context, row_id)` - Process single row
- Returns `(record, failure)` tuple

**Features:**
- Criteria-based processing
- Transform plugin application
- Security level propagation

### LLMExecutor

**Responsibility:** LLM execution with retry logic

**Lines of Code:** ~130

**Key Methods:**
- `execute(user_prompt, metadata, system_prompt)` - Execute LLM call

**Features:**
- Exponential backoff retry
- Middleware chain application
- Rate limiting integration
- Cost tracking integration

### ResultAggregator

**Responsibility:** Result collection and payload building

**Lines of Code:** ~100

**Key Methods:**
- `add_result(record, row_index)` - Add successful result
- `add_failure(failure)` - Add failed result
- `build_payload()` - Build final payload with metadata

**Features:**
- Aggregation plugin application
- Retry statistics
- Cost summary integration
- Security level metadata

## Data Flow

```
DataFrame Input
    ↓
CheckpointManager (filter processed rows)
    ↓
PromptCompiler (compile templates)
    ↓
For each row:
    RowProcessor
        ↓
    LLMExecutor (with retry)
        ↓
    ResultAggregator.add_result()
        ↓
    EarlyStopCoordinator.check_record()
    ↓
ResultAggregator.build_payload()
    ↓
ArtifactPipeline (sink execution)
```

## Testing Strategy

Each component has dedicated unit tests:
- `tests/core/sda/test_checkpoint.py`
- `tests/core/sda/test_prompt_compiler.py`
- `tests/core/sda/test_early_stop.py`
- `tests/core/sda/test_row_processor.py`
- `tests/core/sda/test_llm_executor.py`
- `tests/core/sda/test_result_aggregator.py`

Integration tests verify component collaboration:
- `tests/core/sda/test_integration.py`

Characterization tests ensure backward compatibility:
- `tests/core/sda/test_runner.py`

## Migration Notes

**Breaking Changes:** None - backward compatible

**Deprecated:** None

**New Exports:** All components now exported from `elspeth.core.sda`

## Benefits

1. **Testability:** Each component tested in isolation
2. **Maintainability:** Clear responsibilities, easier to modify
3. **Reusability:** Components can be used independently
4. **Understandability:** ~100-150 lines per class vs 583-line monolith
5. **Extensibility:** Easy to add new checkpoint strategies, retry policies, etc.
```

### Step 2: Add refactoring completion note to architecture report

```markdown
# Add to docs/arch-analysis-2025-11-14-1201/04-final-report.md

## Update (2025-11-14 - Post Refactoring)

### SDARunner Refactoring Completed ✅

The SDARunner god class (583 lines) has been successfully refactored into focused components:

**New Components (7):**
1. **CheckpointManager** (80 lines) - Checkpoint I/O
2. **PromptCompiler** (90 lines) - Template compilation
3. **EarlyStopCoordinator** (120 lines) - Halt condition management
4. **RowProcessor** (150 lines) - Single row processing
5. **LLMExecutor** (130 lines) - LLM execution with retry
6. **ResultAggregator** (100 lines) - Result collection
7. **SDARunner** (150 lines, down from 583) - Thin orchestrator

**Testing:**
- 6 dedicated unit test files (400+ lines of tests)
- Integration tests verifying component collaboration
- Characterization tests ensuring backward compatibility
- All tests passing, 100% backward compatible

**Documentation:**
- Component architecture documented in `docs/architecture/sda-components.md`
- Clear data flow diagrams
- Testing strategy documented

**Impact:**
- ✅ Addresses "SDARunner Complexity" concern from original audit
- ✅ Improves testability, maintainability, and understandability
- ✅ Enables component reuse and independent extension
- ✅ No breaking changes to existing code

**Next Steps:**
- Monitor component boundaries in production
- Consider extracting parallel execution strategy (optional)
```

### Step 3: Commit documentation

```bash
git add docs/architecture/sda-components.md docs/arch-analysis-2025-11-14-1201/04-final-report.md
git commit -m "docs: document SDARunner refactoring architecture"
```

---

## Task 10: Verification and Cleanup

**Goal:** Final verification that everything works end-to-end

### Step 1: Run complete test suite

```bash
pytest tests/ -v --cov=src/elspeth/core/sda --cov-report=term-missing
```

**Expected:** All tests PASS, high coverage (>90%)

### Step 2: Run full linting and type checking

```bash
ruff check src/ tests/
mypy src/
```

**Expected:** Clean output

### Step 3: Test with example configuration

```bash
# Verify simple example still works
elspeth --settings example/simple/settings.yaml --head 5
```

**Expected:** Executes successfully

### Step 4: Review git history

```bash
git log --oneline -10
```

**Expected:** Clean commit history with descriptive messages

### Step 5: Final commit and tag

```bash
git commit --allow-empty -m "chore: SDARunner refactoring complete"
git tag sda-refactor-complete-2025-11-14
```

---

## Summary

This plan refactors SDARunner from 583 lines into 7 focused components:

1. **CheckpointManager** - Checkpoint resume functionality
2. **PromptCompiler** - Jinja2 template compilation
3. **EarlyStopCoordinator** - Halt condition management
4. **RowProcessor** - Single row processing
5. **LLMExecutor** - LLM execution with retry
6. **ResultAggregator** - Result collection and metadata
7. **SDARunner** - Thin orchestrator (150 lines)

**Total Time Estimate:** 4-6 hours (following TDD strictly)

**Key Principles:**
- ✅ Test-Driven Development (RED-GREEN-REFACTOR)
- ✅ 100% backward compatibility
- ✅ Characterization tests before refactoring
- ✅ Single Responsibility Principle
- ✅ Frequent commits
- ✅ DRY and YAGNI

**Testing Coverage:**
- 6 dedicated unit test modules
- Integration tests
- Characterization tests
- High code coverage (>90% target)

---

**Plan saved to:** `docs/plans/2025-11-14-tdd-refactor-sda-runner.md`
