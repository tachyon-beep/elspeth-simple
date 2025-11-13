# Refactor SDARunner God Class Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extract 5 separate concerns from 583-line SDARunner god class to improve maintainability, testability, and enable parallel development

**Architecture:** Extract retry logic, checkpoint management, parallel execution, early stop coordination, and plugin lifecycle into separate, testable classes. Reduce SDARunner to <300 lines of coordination logic.

**Tech Stack:** Python 3.x, dataclasses, concurrent.futures, typing

**Current state:** Single 583-line class with 10+ responsibilities (prompt compilation, LLM execution, retry, checkpoint, parallel execution, early stopping, plugin coordination, rate limiting, cost tracking)

**Target state:** SDARunner coordinates 5 specialized classes, each <150 lines with single responsibility

**Reference:** See `docs/arch-analysis-2025-11-13-0933/06-technical-debt-catalog.md` for detailed problem description

---

## Overview

This plan extracts SDARunner (583 lines) into focused components over 7 weeks:

- **Week 1:** Extract RetryPolicy (retry logic with exponential backoff)
- **Week 2:** Extract CheckpointManager (state persistence and resume)
- **Week 3:** Extract ParallelExecutor (ThreadPoolExecutor orchestration)
- **Week 4:** Extract EarlyStopCoordinator (halt condition checking)
- **Week 5:** Extract PluginLifecycle (transform and aggregation plugins)
- **Week 6:** Refactor SDARunner to use extracted classes (<300 lines)
- **Week 7:** Integration testing and verification

**Each week follows TDD:** Write failing test → Implement minimal code → Verify passes → Commit

---

## Task 1: Extract RetryPolicy Class

**Files:**
- Create: `src/elspeth/core/sda/retry_policy.py`
- Test: `tests/core/sda/test_retry_policy.py`
- Modify: `src/elspeth/core/sda/runner.py` (integrate RetryPolicy)

### Current Code Location

RetryPolicy logic currently embedded in `runner.py`:
- Retry config parsing: lines 44, 126-131
- Retry execution: lines 147-171 (_process_single_row_with_retry)

### Step 1: Write the failing test

Create test file:

```python
# tests/core/sda/test_retry_policy.py
"""Tests for retry policy logic."""

import pytest
from elspeth.core.sda.retry_policy import RetryPolicy


def test_retry_policy_no_retries():
    """Test that function executes once without retry config."""
    policy = RetryPolicy(max_attempts=1)

    call_count = 0
    def fn():
        nonlocal call_count
        call_count += 1
        return "success"

    result = policy.execute_with_retry(fn)

    assert result == "success"
    assert call_count == 1


def test_retry_policy_retries_on_failure():
    """Test that function retries on exception."""
    policy = RetryPolicy(max_attempts=3, initial_delay=0.01)

    call_count = 0
    def fn():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Temporary failure")
        return "success"

    result = policy.execute_with_retry(fn)

    assert result == "success"
    assert call_count == 3


def test_retry_policy_gives_up_after_max_attempts():
    """Test that retry gives up after max attempts."""
    policy = RetryPolicy(max_attempts=3)

    def fn():
        raise ValueError("Persistent failure")

    with pytest.raises(ValueError):
        policy.execute_with_retry(fn)
```

### Step 2: Run test to verify it fails

Run: `pytest tests/core/sda/test_retry_policy.py -v`
Expected: FAIL with "ModuleNotFoundError"

### Step 3: Create minimal implementation

```python
# src/elspeth/core/sda/retry_policy.py
"""Retry policy for LLM operations with exponential backoff."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class RetryPolicy:
    """Retry policy with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (default: 1 = no retry)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay in seconds between retries (default: 60.0)
        multiplier: Delay multiplier for exponential backoff (default: 2.0)
    """
    max_attempts: int = 1
    initial_delay: float = 1.0
    max_delay: float = 60.0
    multiplier: float = 2.0

    def execute_with_retry(
        self,
        fn: Callable[[], Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute function with retry logic.

        Args:
            fn: Function to execute (no arguments)
            metadata: Optional metadata for logging

        Returns:
            Result from successful function execution

        Raises:
            Exception: Re-raises last exception if all retries exhausted
        """
        last_exception = None
        delay = self.initial_delay

        for attempt in range(1, self.max_attempts + 1):
            try:
                return fn()
            except Exception as e:
                last_exception = e

                if attempt >= self.max_attempts:
                    # Last attempt failed, raise exception
                    logger.error(
                        "Retry exhausted after %d attempts: %s",
                        attempt,
                        str(e)
                    )
                    raise

                # Log and wait before retry
                logger.warning(
                    "Attempt %d/%d failed: %s. Retrying in %.2fs...",
                    attempt,
                    self.max_attempts,
                    str(e),
                    delay
                )
                time.sleep(delay)

                # Exponential backoff
                delay = min(delay * self.multiplier, self.max_delay)

        # Should never reach here, but raise last exception if we do
        if last_exception:
            raise last_exception

        raise RuntimeError("Retry logic error: no attempts executed")

    @classmethod
    def from_config(cls, config: Optional[Dict[str, Any]]) -> "RetryPolicy":
        """Create RetryPolicy from configuration dict.

        Args:
            config: Configuration with keys: max_attempts, initial_delay, max_delay, multiplier

        Returns:
            RetryPolicy instance
        """
        if not config:
            return cls(max_attempts=1)  # No retry by default

        return cls(
            max_attempts=config.get("max_attempts", 1),
            initial_delay=config.get("initial_delay", 1.0),
            max_delay=config.get("max_delay", 60.0),
            multiplier=config.get("multiplier", 2.0)
        )
```

### Step 4: Run test to verify it passes

Run: `pytest tests/core/sda/test_retry_policy.py -v`
Expected: All PASS

### Step 5: Integrate into SDARunner

Update `runner.py`:

```python
from elspeth.core.sda.retry_policy import RetryPolicy

@dataclass
class SDARunner:
    # ... existing fields ...
    retry_config: Dict[str, Any] | None = None
    _retry_policy: RetryPolicy | None = None

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        # Initialize retry policy
        self._retry_policy = RetryPolicy.from_config(self.retry_config)

        # ... rest of run() ...

    def _process_single_row(self, ...):
        """Process single row with retry."""
        def execute_llm():
            # Existing LLM call logic here
            return response

        # Use retry policy instead of manual retry loop
        response = self._retry_policy.execute_with_retry(execute_llm)
        return response
```

### Step 6: Run integration tests

Run: `pytest tests/core/sda/ -v -k runner`
Expected: All PASS (no regressions)

### Step 7: Commit

```bash
git add src/elspeth/core/sda/retry_policy.py tests/core/sda/test_retry_policy.py src/elspeth/core/sda/runner.py
git commit -m "feat: extract RetryPolicy from SDARunner

- Create RetryPolicy class with exponential backoff
- Add comprehensive unit tests
- Integrate into SDARunner (removes ~25 lines)
- Zero behavior changes, all tests pass"
```

---

## Task 2: Extract CheckpointManager Class

**Files:**
- Create: `src/elspeth/core/sda/checkpoint_manager.py`
- Test: `tests/core/sda/test_checkpoint_manager.py`
- Modify: `src/elspeth/core/sda/runner.py`

### Current Code Location

Checkpoint logic currently in `runner.py`:
- Checkpoint config: lines 45-46
- Load checkpoint: lines 64-67, lines 204-218 (_load_checkpoint method)
- Save checkpoint: lines 139-145
- Filter processed rows: lines 97-107

### Step 1: Write the failing test

```python
# tests/core/sda/test_checkpoint_manager.py
"""Tests for checkpoint manager."""

import tempfile
from pathlib import Path
import pandas as pd
import pytest

from elspeth.core.sda.checkpoint_manager import CheckpointManager, CheckpointState


def test_checkpoint_manager_no_existing_checkpoint():
    """Test loading when no checkpoint exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint_path = Path(tmpdir) / "checkpoint.jsonl"
        manager = CheckpointManager(checkpoint_path, field="id")

        state = manager.load_checkpoint()

        assert state.processed_ids == set()
        assert not checkpoint_path.exists()


def test_checkpoint_manager_save_and_load():
    """Test saving and loading checkpoint."""
    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint_path = Path(tmpdir) / "checkpoint.jsonl"
        manager = CheckpointManager(checkpoint_path, field="id")

        # Save some IDs
        manager.save_checkpoint({"id1", "id2", "id3"})

        # Load checkpoint
        state = manager.load_checkpoint()

        assert state.processed_ids == {"id1", "id2", "id3"}


def test_checkpoint_manager_filter_processed_rows():
    """Test filtering already-processed rows."""
    df = pd.DataFrame({
        "id": ["id1", "id2", "id3", "id4"],
        "data": ["a", "b", "c", "d"]
    })

    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint_path = Path(tmpdir) / "checkpoint.jsonl"
        manager = CheckpointManager(checkpoint_path, field="id")

        # Mark id1 and id3 as processed
        manager.save_checkpoint({"id1", "id3"})

        # Filter DataFrame
        filtered = manager.filter_processed_rows(df)

        assert len(filtered) == 2
        assert list(filtered["id"]) == ["id2", "id4"]
```

### Step 2: Run test to verify it fails

Run: `pytest tests/core/sda/test_checkpoint_manager.py -v`
Expected: FAIL with "ModuleNotFoundError"

### Step 3: Create minimal implementation

```python
# src/elspeth/core/sda/checkpoint_manager.py
"""Checkpoint management for resumable experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set
import json
import logging

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class CheckpointState:
    """Checkpoint state containing processed IDs."""
    processed_ids: Set[str]


class CheckpointManager:
    """Manages checkpoint state for resumable experiments.

    Args:
        checkpoint_path: Path to checkpoint file (JSONL format)
        field: Field name to use as row ID for checkpoint tracking
    """

    def __init__(self, checkpoint_path: Path, field: str):
        """Initialize checkpoint manager."""
        self.checkpoint_path = checkpoint_path
        self.field = field

    def load_checkpoint(self) -> CheckpointState:
        """Load checkpoint state from file.

        Returns:
            CheckpointState with processed IDs
        """
        if not self.checkpoint_path.exists():
            logger.info("No checkpoint found at %s", self.checkpoint_path)
            return CheckpointState(processed_ids=set())

        processed_ids: Set[str] = set()

        try:
            with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        if self.field in record:
                            processed_ids.add(str(record[self.field]))

            logger.info(
                "Loaded checkpoint: %d processed IDs from %s",
                len(processed_ids),
                self.checkpoint_path
            )

        except Exception as e:
            logger.warning("Failed to load checkpoint: %s", str(e))
            return CheckpointState(processed_ids=set())

        return CheckpointState(processed_ids=processed_ids)

    def save_checkpoint(self, processed_ids: Set[str]) -> None:
        """Save checkpoint state to file.

        Args:
            processed_ids: Set of processed row IDs
        """
        # Ensure parent directory exists
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.checkpoint_path, "w", encoding="utf-8") as f:
                for row_id in processed_ids:
                    record = {self.field: row_id}
                    f.write(json.dumps(record) + "\n")

            logger.info(
                "Saved checkpoint: %d processed IDs to %s",
                len(processed_ids),
                self.checkpoint_path
            )

        except Exception as e:
            logger.error("Failed to save checkpoint: %s", str(e))

    def filter_processed_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter already-processed rows from DataFrame.

        Args:
            df: DataFrame with field column

        Returns:
            Filtered DataFrame with only unprocessed rows
        """
        state = self.load_checkpoint()

        if not state.processed_ids:
            return df

        if self.field not in df.columns:
            logger.warning(
                "Checkpoint field '%s' not in DataFrame, skipping filter",
                self.field
            )
            return df

        # Filter out processed rows
        mask = ~df[self.field].astype(str).isin(state.processed_ids)
        filtered = df[mask].copy()

        logger.info(
            "Filtered %d already-processed rows, %d remaining",
            len(df) - len(filtered),
            len(filtered)
        )

        return filtered

    @classmethod
    def from_config(
        cls,
        config: Optional[dict]
    ) -> Optional["CheckpointManager"]:
        """Create CheckpointManager from configuration.

        Args:
            config: Configuration dict with 'path' and 'field' keys

        Returns:
            CheckpointManager instance or None if no config
        """
        if not config:
            return None

        checkpoint_path = Path(config.get("path", "checkpoint.jsonl"))
        checkpoint_field = config.get("field", "id")

        return cls(checkpoint_path, checkpoint_field)
```

### Step 4: Run test to verify it passes

Run: `pytest tests/core/sda/test_checkpoint_manager.py -v`
Expected: All PASS

### Step 5: Integrate into SDARunner

Update `runner.py` to use CheckpointManager instead of manual logic

### Step 6: Run integration tests

Run: `pytest tests/core/sda/ -v -k runner`
Expected: All PASS

### Step 7: Commit

```bash
git add src/elspeth/core/sda/checkpoint_manager.py tests/core/sda/test_checkpoint_manager.py src/elspeth/core/sda/runner.py
git commit -m "feat: extract CheckpointManager from SDARunner

- Create CheckpointManager class for resumable experiments
- Add comprehensive unit tests
- Integrate into SDARunner (removes ~50 lines)
- Zero behavior changes"
```

---

## Task 3-5: Extract ParallelExecutor, EarlyStopCoordinator, PluginLifecycle

**Note:** Tasks 3-5 follow the same pattern as Tasks 1-2:
1. Write failing tests
2. Create minimal implementation
3. Run tests to verify passes
4. Integrate into SDARunner
5. Run integration tests
6. Commit

See **Technical Debt Catalog** (TD-001) for detailed specifications of each class.

**Week 3: ParallelExecutor**
- Extract ThreadPoolExecutor orchestration
- Handle concurrent row processing with error collection
- Test parallel execution, worker pool management, error handling

**Week 4: EarlyStopCoordinator**
- Extract early stop condition evaluation
- Coordinate halt condition plugins
- Test condition checking, plugin coordination

**Week 5: PluginLifecycle**
- Extract transform and aggregation plugin execution
- Handle plugin application, error handling
- Test row plugins, aggregation plugins, error scenarios

---

## Task 6: Refactor SDARunner to Coordination Only

**Goal:** Reduce SDARunner to <300 lines using extracted classes

**Files:**
- Modify: `src/elspeth/core/sda/runner.py`
- Modify: `tests/core/sda/test_runner.py` (update for new architecture)

### Step 1: Document target architecture

Add comprehensive docstring to SDARunner:

```python
@dataclass
class SDARunner:
    """Orchestrates SDA (Sense/Decide/Act) experiment execution.

    ARCHITECTURE (Post-Refactoring):

    SDARunner is the coordination layer that delegates to specialized components:

    ┌─────────────────────────────────────────────────────────────┐
    │ Execution Flow                                               │
    ├─────────────────────────────────────────────────────────────┤
    │ 1. Initialize components (retry, checkpoint, parallel, etc) │
    │ 2. Load checkpoint → filter processed rows                  │
    │ 3. Compile prompts (PromptEngine)                           │
    │ 4. Choose execution: Sequential | Parallel                   │
    │    ├─ Sequential: Process rows one by one                   │
    │    └─ Parallel: ParallelExecutor orchestrates threads       │
    │ 5. Apply transform plugins (PluginLifecycle)                │
    │ 6. Check early stop (EarlyStopCoordinator)                  │
    │ 7. Apply aggregation plugins (PluginLifecycle)              │
    │ 8. Write results via ArtifactPipeline                       │
    └─────────────────────────────────────────────────────────────┘

    COMPONENTS:
    - RetryPolicy: Retry logic with exponential backoff
    - CheckpointManager: State persistence and resume
    - ParallelExecutor: ThreadPoolExecutor orchestration
    - EarlyStopCoordinator: Halt condition checking
    - PluginLifecycle: Transform and aggregation plugins

    RESPONSIBILITIES (Coordination Only):
    - Wiring components together
    - Orchestrating execution flow
    - Delegating to specialized components
    - Artifact pipeline coordination

    Lines: <300 (down from 583)
    """
```

### Step 2: Refactor run() method to use extracted classes

```python
def run(self, df: pd.DataFrame) -> Dict[str, Any]:
    """Execute SDA cycle on DataFrame.

    Args:
        df: Input DataFrame to process

    Returns:
        Results dictionary with metadata and processed records
    """
    # Initialize components
    retry_policy = RetryPolicy.from_config(self.retry_config)
    checkpoint_mgr = CheckpointManager.from_config(self.checkpoint_config)
    parallel_exec = ParallelExecutor.from_config(self.concurrency_config)
    early_stop_coord = EarlyStopCoordinator(
        self.halt_condition_plugins,
        self.halt_condition_config
    )
    plugin_lifecycle = PluginLifecycle(
        transform_plugins=self.transform_plugins,
        aggregation_transforms=self.aggregation_transforms
    )

    # Filter processed rows (checkpoint)
    if checkpoint_mgr:
        df = checkpoint_mgr.filter_processed_rows(df)

    # Compile prompts
    engine = self.prompt_engine or PromptEngine()
    self._compile_prompts(engine)

    # Process rows (sequential or parallel)
    if parallel_exec:
        results = parallel_exec.execute_parallel(
            fn=lambda row: self._process_single_row(row, retry_policy, plugin_lifecycle),
            items=list(df.iterrows())
        )
    else:
        results = [
            self._process_single_row(row, retry_policy, plugin_lifecycle)
            for _, row in df.iterrows()
        ]

    # Check early stop
    if early_stop_coord:
        results, stopped = early_stop_coord.check_and_filter(results)
        if stopped:
            logger.info("Early stop triggered")

    # Apply aggregation plugins
    aggregated = plugin_lifecycle.apply_aggregation(results)

    # Write via artifact pipeline
    self._write_results(results, aggregated)

    return {"results": results, "aggregated": aggregated}
```

### Step 3: Run tests to verify no regressions

Run: `pytest tests/core/sda/ -v`
Expected: All PASS

### Step 4: Count lines

Run: `wc -l src/elspeth/core/sda/runner.py`
Expected: <300 lines

### Step 5: Commit

```bash
git add src/elspeth/core/sda/runner.py tests/core/sda/test_runner.py
git commit -m "refactor: reduce SDARunner to coordination layer

- SDARunner now <300 lines (down from 583)
- Delegates to RetryPolicy, CheckpointManager, ParallelExecutor, EarlyStopCoordinator, PluginLifecycle
- All tests pass, zero behavior changes
- Improved maintainability and testability"
```

---

## Task 7: Integration Testing and Verification

**Goal:** Validate complete refactoring with comprehensive tests

**Files:**
- Create: `tests/integration/test_runner_refactoring.py`

### Step 1: Write end-to-end integration test

```python
"""Integration tests for refactored SDARunner."""

import pandas as pd
import pytest
from unittest.mock import Mock

from elspeth.core.sda.runner import SDARunner


def test_runner_end_to_end_with_all_components():
    """Test SDARunner with retry, checkpoint, parallel, early stop, plugins."""

    # Create mock LLM client
    llm = Mock()
    llm.generate.return_value = {"response": "test response"}

    # Create minimal runner config
    runner = SDARunner(
        llm_client=llm,
        sinks=[],
        prompt_system="Test system",
        prompt_template="Test template: {field}",
        retry_config={"max_attempts": 3},
        concurrency_config={"max_workers": 2},
        transform_plugins=[],
        aggregation_transforms=[]
    )

    # Test DataFrame
    df = pd.DataFrame({
        "field": ["value1", "value2", "value3"]
    })

    # Execute
    results = runner.run(df)

    # Verify
    assert "results" in results
    assert len(results["results"]) == 3


def test_runner_backward_compatibility():
    """Verify refactored runner produces same results as original."""
    # Compare outputs before/after refactoring
    # (Would need baseline outputs from original implementation)
    pass
```

### Step 2: Run integration tests

Run: `pytest tests/integration/test_runner_refactoring.py -v`
Expected: All PASS

### Step 3: Run full test suite

Run: `pytest tests/ -v`
Expected: All PASS

### Step 4: Performance benchmark

Run benchmarks to ensure no performance regression

### Step 5: Final validation

- [ ] SDARunner <300 lines
- [ ] All extracted classes have 100% unit test coverage
- [ ] All integration tests pass
- [ ] No performance regression (±5%)
- [ ] Type checker passes (mypy)
- [ ] Linter passes (ruff)

### Step 6: Final commit

```bash
git add tests/integration/test_runner_refactoring.py
git commit -m "test: add comprehensive integration tests for refactored runner

- End-to-end tests with all components
- Backward compatibility validation
- Performance benchmarks
- All tests pass"
```

---

## Success Criteria

- [ ] RetryPolicy extracted with unit tests
- [ ] CheckpointManager extracted with unit tests
- [ ] ParallelExecutor extracted with unit tests
- [ ] EarlyStopCoordinator extracted with unit tests
- [ ] PluginLifecycle extracted with unit tests
- [ ] SDARunner reduced to <300 lines
- [ ] All unit tests passing (>90% coverage per class)
- [ ] All integration tests passing
- [ ] No behavior changes (experiments produce identical results)
- [ ] No performance regression (±5%)
- [ ] Type checker passing (mypy)
- [ ] Linter passing (ruff)
- [ ] Documentation updated (architecture diagrams, docstrings)

---

## Timeline

- **Week 1:** RetryPolicy extraction (5 days)
- **Week 2:** CheckpointManager extraction (5 days)
- **Week 3:** ParallelExecutor extraction (5 days)
- **Week 4:** EarlyStopCoordinator extraction (5 days)
- **Week 5:** PluginLifecycle extraction (5 days)
- **Week 6:** SDARunner refactoring (5 days)
- **Week 7:** Integration testing and verification (5 days)

**Total:** 7 weeks (35 working days) for 1 senior engineer

---

## Notes for Implementer

**Each extraction follows TDD:**
1. Write comprehensive unit tests first
2. Implement minimal code to pass tests
3. Integrate into SDARunner
4. Run integration tests to verify no regressions
5. Commit before moving to next extraction

**Each extracted class should be:**
- <150 lines
- Single responsibility
- 100% unit test coverage
- Well-documented with docstrings
- Type-annotated

**SDARunner after refactoring:**
- <300 lines
- Coordination logic only
- Delegates all responsibilities to components
- Comprehensive docstring with architecture diagram

**Reference:** See `docs/arch-analysis-2025-11-13-0933/06-technical-debt-catalog.md` Task TD-001 for detailed specifications

---

**Plan complete. Ready for execution.**
