# Remove Deprecated SDASuiteRunner - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove deprecated SDASuiteRunner module since we're pre-release with only one customer (no backward compatibility needed)

**Architecture:** Clean deletion of 339-line deprecated module and all references. The functionality has been replaced by StandardOrchestrator and ExperimentalOrchestrator in the orchestrators package.

**Tech Stack:** Python 3.13, pytest for verification

**Context:** SDASuiteRunner was deprecated during the orchestration refactoring (commit e53a97b). It has been replaced by the orchestrators package with clearer separation of concerns. Since the project is pre-release with only one customer, we can make breaking changes without a deprecation period.

---

## Current State Analysis

**File to remove:**
- `src/elspeth/core/sda/suite_runner.py` (339 lines)

**References to update:**
- `src/elspeth/core/sda/__init__.py` - Remove import and export
- Documentation files (arch-analysis reports, etc.) - No code changes needed

**Actual usage:**
- ✅ **NONE** - No code currently uses SDASuiteRunner
- Only exists in __init__.py for backward compatibility (not needed)

**Replacement:**
- `src/elspeth/orchestrators/standard.py` - StandardOrchestrator
- `src/elspeth/orchestrators/experimental.py` - ExperimentalOrchestrator

---

## Task 1: Verify No Active Usage

**Goal:** Confirm SDASuiteRunner has no active references before deletion

**Files:**
- Check: All Python files in `src/`, `tests/`, `example/`

### Step 1: Search for SDASuiteRunner usage

```bash
grep -r "SDASuiteRunner" --include="*.py" --exclude-dir=docs src/ tests/ example/
```

**Expected:** Only matches in:
- `src/elspeth/core/sda/suite_runner.py` (the file itself)
- `src/elspeth/core/sda/__init__.py` (import/export)

### Step 2: Search for suite_runner imports

```bash
grep -r "from.*suite_runner\|import.*suite_runner" --include="*.py" src/ tests/ example/
```

**Expected:** Only match in `src/elspeth/core/sda/__init__.py`

### Step 3: Verify orchestrators are available

```bash
ls -la src/elspeth/orchestrators/
```

**Expected:** Should show `standard.py` and `experimental.py` with StandardOrchestrator and ExperimentalOrchestrator

### Step 4: Document findings

Create verification notes that no code depends on SDASuiteRunner.

**Note:** No commit needed - this is verification only

---

## Task 2: Remove SDASuiteRunner from Exports

**Goal:** Remove SDASuiteRunner from module exports in __init__.py

**Files:**
- Modify: `src/elspeth/core/sda/__init__.py`

### Step 1: Remove import statement

**File:** `src/elspeth/core/sda/__init__.py`

**Remove lines 12-15:**
```python
# DEPRECATED: SDASuiteRunner moved to orchestrators package
# Use StandardOrchestrator or ExperimentalOrchestrator instead
# Kept for backward compatibility - will be removed in future version
from .suite_runner import SDASuiteRunner
```

### Step 2: Remove from __all__ export list

**File:** `src/elspeth/core/sda/__init__.py`

**Remove from __all__ list (line 28):**
```python
"SDASuiteRunner",  # Deprecated
```

**After removal, __all__ should be:**
```python
__all__ = [
    "CheckpointManager",
    "CompiledPrompts",
    "EarlyStopCoordinator",
    "LLMExecutor",
    "PromptCompiler",
    "ResultAggregator",
    "RowProcessor",
    "SDACycleConfig",
    "SDARunner",
    "SDASuite",
]
```

### Step 3: Verify __init__.py is valid

```bash
python -c "from elspeth.core.sda import SDARunner; print('Import successful')"
```

**Expected:** "Import successful" (no import errors)

### Step 4: Run tests to verify no breakage

```bash
pytest tests/core/sda/ -v
```

**Expected:** All tests PASS (should be 17 tests)

### Step 5: Commit changes

```bash
git add src/elspeth/core/sda/__init__.py
git commit -m "refactor: remove SDASuiteRunner from sda module exports

SDASuiteRunner is deprecated and replaced by orchestrators package.
Since we're pre-release with one customer, removing without deprecation period.

Use StandardOrchestrator or ExperimentalOrchestrator instead."
```

---

## Task 3: Delete suite_runner.py Module

**Goal:** Delete the deprecated 339-line module file

**Files:**
- Delete: `src/elspeth/core/sda/suite_runner.py`

### Step 1: Verify file is no longer imported

```bash
grep -r "suite_runner" --include="*.py" src/ tests/ example/
```

**Expected:** No matches (we removed the import in Task 2)

### Step 2: Delete the file

```bash
git rm src/elspeth/core/sda/suite_runner.py
```

**Expected:** File staged for deletion

### Step 3: Verify Python can still import sda module

```bash
python -c "from elspeth.core import sda; print(dir(sda))"
```

**Expected:** Module loads successfully, SDASuiteRunner not in list

### Step 4: Run full test suite

```bash
pytest tests/ -v
```

**Expected:** All 33 tests PASS

### Step 5: Commit deletion

```bash
git commit -m "refactor: delete deprecated suite_runner.py module (339 lines)

The SDASuiteRunner class has been fully replaced by:
- StandardOrchestrator (orchestrators.standard)
- ExperimentalOrchestrator (orchestrators.experimental)

Removed 339 lines of deprecated code."
```

---

## Task 4: Verify Orchestrators Work Correctly

**Goal:** Ensure the replacement orchestrators function properly

**Files:**
- Test: `src/elspeth/orchestrators/standard.py`
- Test: `src/elspeth/orchestrators/experimental.py`

### Step 1: Verify orchestrator imports

```python
# Test in Python REPL or temporary test file
from elspeth.orchestrators import StandardOrchestrator, ExperimentalOrchestrator
print("StandardOrchestrator:", StandardOrchestrator)
print("ExperimentalOrchestrator:", ExperimentalOrchestrator)
```

**Expected:** Both classes import successfully

### Step 2: Check example configurations

```bash
ls example/experimental/
```

**Expected:** Should contain experimental orchestrator examples

### Step 3: Verify example can run (if configured)

```bash
# Only if you have example data configured
elspeth --settings example/simple/settings.yaml --head 1
```

**Expected:** Executes without errors (uses StandardOrchestrator by default)

### Step 4: Document verification

All orchestrators work correctly and SDASuiteRunner removal causes no issues.

**Note:** No commit needed - this is verification only

---

## Task 5: Update Documentation References

**Goal:** Update architecture documentation to reflect removal

**Files:**
- Modify: `docs/architecture/sda-components.md`

### Step 1: Add note about SDASuiteRunner removal

**File:** `docs/architecture/sda-components.md`

**Add to "Migration Notes" section:**

```markdown
### SDASuiteRunner Removal (2025-11-14)

**Removed:** `SDASuiteRunner` class from `core/sda/suite_runner.py` (339 lines)

**Reason:** Pre-release status allows breaking changes without deprecation period.

**Migration:** Use orchestrators package instead:
- For sequential cycle execution: `orchestrators.StandardOrchestrator`
- For A/B testing with baseline: `orchestrators.ExperimentalOrchestrator`

**Example:**
```python
# Old (removed):
from elspeth.core.sda import SDASuiteRunner
runner = SDASuiteRunner(suite, llm_client, sinks)

# New:
from elspeth.orchestrators import StandardOrchestrator
orchestrator = StandardOrchestrator()
# Use through suite execution, not directly instantiated
```

No code changes needed for existing users (only one customer: project maintainer).
```

### Step 2: Run linting on documentation

```bash
ruff check docs/architecture/sda-components.md || echo "Markdown file, linting may not apply"
```

**Expected:** No issues (or tool doesn't apply to markdown)

### Step 3: Commit documentation update

```bash
git add docs/architecture/sda-components.md
git commit -m "docs: document SDASuiteRunner removal in architecture guide"
```

---

## Task 6: Final Verification and Cleanup

**Goal:** Comprehensive verification that removal is complete and clean

**Files:**
- Verify: All test files
- Verify: All source files
- Verify: Git history

### Step 1: Run complete test suite with coverage

```bash
pytest tests/ -v --cov=src/elspeth/core/sda --cov-report=term-missing
```

**Expected:** All 33 tests PASS, no import errors

### Step 2: Run linting on modified files

```bash
ruff check src/elspeth/core/sda/ tests/core/sda/
```

**Expected:** No new linting errors

### Step 3: Verify git status is clean

```bash
git status
```

**Expected:** "nothing to commit, working tree clean"

### Step 4: Review commit log

```bash
git log --oneline -5
```

**Expected:** Should show the 3 commits from this plan:
1. Remove SDASuiteRunner from exports
2. Delete suite_runner.py module
3. Update documentation

### Step 5: Count lines removed

```bash
git diff HEAD~3..HEAD --stat | grep suite_runner
```

**Expected:** Shows ~339 lines deleted from suite_runner.py

### Step 6: Create summary commit (optional)

```bash
git commit --allow-empty -m "chore: SDASuiteRunner removal complete

Removed 339 lines of deprecated code:
- Deleted suite_runner.py module
- Removed from sda package exports
- Updated architecture documentation

Replaced by orchestrators.StandardOrchestrator and orchestrators.ExperimentalOrchestrator.

Since pre-release (1 customer), no backward compatibility period needed."
```

---

## Task 7: Test Example Configuration (Optional)

**Goal:** Ensure example configurations still work after removal

**Files:**
- Test: `example/simple/settings.yaml`
- Test: `example/experimental/` (if exists)

### Step 1: Test simple example

```bash
elspeth --settings example/simple/settings.yaml --head 5
```

**Expected:** Processes 5 rows successfully without errors

### Step 2: Verify orchestrator selection works

```bash
grep -r "orchestrator" example/*/settings.yaml || echo "No orchestrator config (uses default)"
```

**Expected:** Either finds orchestrator config or uses default StandardOrchestrator

### Step 3: Document test results

All examples work correctly with SDASuiteRunner removed.

**Note:** No commit needed - this is verification only

---

## Summary

This plan removes the deprecated SDASuiteRunner module cleanly:

**Deletions:**
- `suite_runner.py` - 339 lines

**Modifications:**
- `__init__.py` - Remove import and export (4 lines)
- `sda-components.md` - Add migration note

**Total lines removed:** ~343 lines

**Breaking changes:** None for production users (pre-release, 1 customer)

**Replacement:** `orchestrators.StandardOrchestrator` and `orchestrators.ExperimentalOrchestrator`

**Timeline:** 15-30 minutes for complete execution

---

**Plan saved to:** `docs/plans/2025-11-14-remove-deprecated-suite-runner.md`
