# SDA (Sense/Decide/Act) Renaming Plan

**Version:** 1.0
**Date:** 2025-11-13
**Status:** Draft for Review
**Approach:** Fix-on-fail (no backward compatibility)

---

## Executive Summary

This document outlines a comprehensive plan to rebrand the elspeth-simple codebase from experimentation-focused terminology to a generic **Sense/Decide/Act (SDA) orchestrator** framework.

**Scope:** 57 Python files, documentation, and all references to "experiment" terminology

**Estimated Effort:** 3-5 days of focused work

**Risk Level:** Medium-High (breaking changes across entire codebase)

---

## 1. Conceptual Framework

### 1.1 SDA Paradigm Mapping

| **SDA Phase** | **Current System** | **Renamed System** |
|---------------|--------------------|--------------------|
| **SENSE** | `DataSource` loads input data | `DataSource` (keep - data sources) |
| **DECIDE** | LLM processes prompts, plugins transform | `LLMClientProtocol` (keep), `TransformPlugin` (data transforms) |
| **ACT** | `ResultSink` writes outputs | `ResultSink` (keep - data sinks/effectors) |
| **Orchestration** | `ExperimentRunner` coordinates | `SDARunner` coordinates full sense→decide→act cycle |

### 1.2 Terminology Map

| **Old Term** | **New Term** | **Context** |
|--------------|--------------|-------------|
| Experiment | SDA Cycle | One complete sense→decide→act execution |
| Experiment Suite | SDA Suite | Collection of multiple SDA cycles |
| Experiment Runner | SDA Runner | Execution engine for one cycle |
| Row Plugin | Transform Plugin | Per-input data transformation during decide phase |
| Aggregation Plugin | Aggregation Transform | Post-processing transformation across all results |
| Experiment Context | SDA Context | Runtime context for one cycle |
| Experiment Name | Cycle Name | Identifier for the cycle |
| Row/Experiment Plugins | Data Transforms | Plugins that transform data during decide phase |

---

## 2. Directory & File Structure Changes

### 2.1 Directory Renames

| **Current Path** | **New Path** | **Reason** |
|------------------|--------------|------------|
| `core/experiments/` | `core/sda/` | Central SDA orchestration logic |
| `plugins/experiments/` | `plugins/processors/` | Generic decision/synthesis processors |

### 2.2 File Moves

**Phase A: Rename `core/experiments/` → `core/sda/`**

- `core/experiments/__init__.py` → `core/sda/__init__.py`
- `core/experiments/runner.py` → `core/sda/runner.py`
- `core/experiments/suite_runner.py` → `core/sda/suite_runner.py`
- `core/experiments/plugins.py` → `core/sda/plugins.py`
- `core/experiments/plugin_registry.py` → `core/sda/plugin_registry.py`
- `core/experiments/config.py` → `core/sda/config.py`

**Phase B: Rename `plugins/experiments/` → `plugins/transforms/`**

- `plugins/experiments/__init__.py` → `plugins/transforms/__init__.py`
- `plugins/experiments/metrics.py` → `plugins/transforms/metrics.py`
- `plugins/experiments/early_stop.py` → `plugins/transforms/early_stop.py`

---

## 3. Core Class & Function Renames

### 3.1 Primary Orchestration Classes

#### **File: `core/orchestrator.py`**

| **Current Name** | **New Name** | **Type** |
|------------------|--------------|----------|
| `ExperimentOrchestrator` | `SDAOrchestrator` | Class |
| `OrchestratorConfig` | `SDAConfig` | Class |
| `experiment_runner` (field) | `sda_runner` | Attribute |
| `experiment_name` (parameter) | `cycle_name` | Parameter |

**Docstring Update:**
```python
# OLD: """Experiment orchestrator bridging datasource, LLM, and sinks."""
# NEW: """SDA (Sense/Decide/Act) orchestrator coordinating data input, decision-making, and action execution."""
```

---

#### **File: `core/sda/runner.py` (formerly `core/experiments/runner.py`)**

| **Current Name** | **New Name** | **Type** |
|------------------|--------------|----------|
| `ExperimentRunner` | `SDARunner` | Class |
| `experiment_name` (field) | `cycle_name` | Attribute |
| `row_plugins` (field) | `transform_plugins` | Attribute |
| `aggregator_plugins` (field) | `aggregation_transforms` | Attribute |
| `_process_single_row()` | `_process_single_input()` | Method |

**Docstring Update:**
```python
# OLD: """Simplified experiment runner ported from legacy implementation."""
# NEW: """SDA (Sense/Decide/Act) runner executing one complete orchestration cycle."""
```

**Internal Variables to Rename:**
- `row_plugins` → `transform_plugins` (all occurrences)
- `aggregator_plugins` → `aggregation_transforms` (all occurrences)
- `experiment_name` → `cycle_name` (all occurrences)
- `rows_to_process` → `inputs_to_process`
- `processed_ids` → `processed_inputs`

---

#### **File: `core/sda/suite_runner.py` (formerly `core/experiments/suite_runner.py`)**

| **Current Name** | **New Name** | **Type** |
|------------------|--------------|----------|
| `ExperimentSuiteRunner` | `SDASuiteRunner` | Class |
| `ExperimentSuite` | `SDASuite` | Class (imported) |
| `baseline_experiment` | `baseline_cycle` | Variable |
| `variant_experiments` | `variant_cycles` | Variable |

---

#### **File: `core/sda/config.py` (formerly `core/experiments/config.py`)**

| **Current Name** | **New Name** | **Type** |
|------------------|--------------|----------|
| `ExperimentSuite` | `SDASuite` | Class |
| `ExperimentConfig` | `SDACycleConfig` | Class |
| `suite_defaults` (field) | `suite_defaults` | Attribute (keep) |
| `experiments` (field) | `cycles` | Attribute |

---

### 3.2 Plugin Protocol Definitions

#### **File: `core/sda/plugins.py` (formerly `core/experiments/plugins.py`)**

| **Current Name** | **New Name** | **Type** |
|------------------|--------------|----------|
| `RowExperimentPlugin` | `TransformPlugin` | Protocol |
| `AggregationExperimentPlugin` | `AggregationTransform` | Protocol |
| `BaselineComparisonPlugin` | `ComparisonPlugin` | Protocol |
| `EarlyStopPlugin` | `HaltConditionPlugin` | Protocol |

**Method Renames:**
- `RowExperimentPlugin.process_row()` → `TransformPlugin.transform()`
- `AggregationExperimentPlugin.finalize()` → `AggregationTransform.aggregate()` or keep `finalize()`

**Docstring Updates:**

```python
# OLD: """Processes a single experiment row and returns derived fields."""
# NEW: """Transforms a single data input during the DECIDE phase and returns derived fields."""

# OLD: """Runs after all rows to compute aggregated outputs."""
# NEW: """Performs aggregation transformation across all results after individual transforms complete."""
```

---

#### **File: `core/sda/plugin_registry.py` (formerly `core/experiments/plugin_registry.py`)**

| **Current Name** | **New Name** | **Type** |
|------------------|--------------|----------|
| `create_row_plugin()` | `create_decision_plugin()` | Function |
| `create_aggregation_plugin()` | `create_synthesis_plugin()` | Function |
| `create_early_stop_plugin()` | `create_halt_condition_plugin()` | Function |
| `row_plugin_defs` (parameter names) | `decision_plugin_defs` | Parameter |
| `aggregator_plugin_defs` | `synthesis_plugin_defs` | Parameter |

---

### 3.3 Interface Definitions

#### **File: `core/interfaces.py`**

| **Current Name** | **New Name** | **Type** |
|------------------|--------------|----------|
| `ExperimentContext` | `SDAContext` | Class |
| `DataSource` | `DataSource` (keep) | Protocol |
| `LLMClientProtocol` | `LLMClientProtocol` (keep) | Protocol |
| `ResultSink` | `ResultSink` (keep) | Protocol |

**Decision:** Keep `DataSource`, `LLMClientProtocol`, and `ResultSink` as-is. They align perfectly with:
- **SENSE phase**: Data Sources provide inputs
- **DECIDE phase**: LLM + Transform Plugins process data
- **ACT phase**: Result Sinks (data sinks/effectors) output results

---

### 3.4 CLI & Configuration Loading

#### **File: `cli.py`**

| **Current Name** | **New Name** | **Type** |
|------------------|--------------|----------|
| `ExperimentOrchestrator` (import) | `SDAOrchestrator` | Class reference |
| `ExperimentSuiteRunner` (import) | `SDASuiteRunner` | Class reference |
| `ExperimentSuite` (import) | `SDASuite` | Class reference |
| `--single-run` (arg) | `--single-cycle` | CLI argument |

**String Updates in Help Text:**
- "experiment" → "SDA cycle"
- "suite of experiments" → "suite of cycles"
- "Force single experiment run" → "Force single SDA cycle execution"

**Function Names:**
- `_run_single()` → `_run_single_cycle()`
- Consider: `run()` → `run_orchestration()`

---

#### **File: `config.py`**

| **Current Name** | **New Name** | **Type** |
|------------------|--------------|----------|
| `prompt_pack` → | `prompt_pack` (keep) or `decision_template` | Field name |

**Note:** This file primarily loads settings; main impact is field name changes in Settings dataclass if they reference "experiment".

---

### 3.5 Plugin Implementations

#### **File: `plugins/transforms/metrics.py` (formerly `plugins/experiments/metrics.py`)**

Review and rename any classes/functions with "experiment" in the name:
- Internal class names likely have "Experiment" → change to "Transform" or remove
- Ensure implements `TransformPlugin` protocol

#### **File: `plugins/transforms/early_stop.py` (formerly `plugins/experiments/early_stop.py`)**

Review and rename:
- Classes implementing `EarlyStopPlugin` → update to implement `HaltConditionPlugin`

---

## 4. Import Statement Updates

**Every Python file** that imports from `core.experiments` or `plugins.experiments` needs updates:

### 4.1 Core Imports

**Old:**
```python
from dmp.core.experiments.runner import ExperimentRunner
from dmp.core.experiments import ExperimentSuiteRunner, ExperimentSuite
from dmp.core.experiments.plugins import RowExperimentPlugin, AggregationExperimentPlugin
from dmp.core.experiments.plugin_registry import create_row_plugin, create_aggregation_plugin
```

**New:**

```python
from dmp.core.sda.runner import SDARunner
from dmp.core.sda import SDASuiteRunner, SDASuite
from dmp.core.sda.plugins import TransformPlugin, AggregationTransform
from dmp.core.sda.plugin_registry import create_transform_plugin, create_aggregation_transform
```

### 4.2 Files Requiring Import Updates

**Confirmed files with imports:**
1. `core/orchestrator.py`
2. `cli.py`
3. `core/sda/__init__.py` (formerly experiments/__init__.py)
4. `core/sda/suite_runner.py`
5. `plugins/transforms/metrics.py`
6. `plugins/transforms/early_stop.py`
7. Any other files importing from these modules

**Strategy:** Use automated find/replace after directory rename:
```bash
# Find all imports
rg "from dmp\.core\.experiments" --type py
rg "from dmp\.plugins\.experiments" --type py
```

---

## 5. Configuration Schema & Validation

### 5.1 Configuration File Updates

#### **File: `core/config_schema.py`**

Review JSON schemas that reference:
- `"experiment"` → `"cycle"` or `"sda_cycle"`
- `"experiments"` (array) → `"cycles"`
- `"experiment_defaults"` → `"cycle_defaults"`
- `"row_plugins"` → `"transform_plugins"`
- `"aggregator_plugins"` → `"aggregation_transforms"`

**Example Schema Change:**
```json
// OLD
{
  "experiments": {
    "type": "array",
    "items": { "type": "object" }
  }
}

// NEW
{
  "cycles": {
    "type": "array",
    "items": { "type": "object" }
  }
}
```

### 5.2 Validation Functions

#### **File: `core/validation.py`**

- `validate_suite()` - Update internal logic referencing "experiments"
- Error messages: Change "experiment" → "SDA cycle"

---

## 6. Documentation Updates

### 6.1 Architecture Documentation

#### **File: `docs/architecture/README.md`**

**Search/Replace:**
- "experiment" → "SDA cycle"
- "Experiment Framework" → "SDA Framework"
- "ExperimentRunner" → "SDARunner"
- "experiment suite" → "SDA suite"
- "row plugin" → "transform plugin"
- "data processors" → "data transforms"
- Update all diagrams with new terminology

#### **File: `docs/architecture/subsystems.md`**

- Rename "Experiment Framework" section → "SDA Framework"
- Update all class names and file paths
- Update component descriptions

#### **File: `docs/architecture/diagrams.md`**

- Update all Mermaid diagrams with new component names
- "Experiment Framework" boxes → "SDA Framework"
- Update legend/descriptions

### 6.2 README

#### **File: `README.md`**

Review for:
- "experiment" references → "SDA cycle"
- System description: emphasize sense/decide/act paradigm
- Example usage: update command-line examples

---

## 7. Variable & Field Name Updates (Detailed)

### 7.1 OrchestratorConfig Fields

#### **File: `core/orchestrator.py`**

```python
@dataclass
class SDAConfig:  # renamed from OrchestratorConfig
    llm_prompt: Dict[str, str]  # keep
    prompt_fields: List[str] | None = None  # keep
    prompt_aliases: Dict[str, str] | None = None  # keep
    criteria: List[Dict[str, str]] | None = None  # keep
    row_plugin_defs: List[Dict[str, Any]] | None = None  # → decision_plugin_defs
    aggregator_plugin_defs: List[Dict[str, Any]] | None = None  # → synthesis_plugin_defs
    sink_defs: List[Dict[str, Any]] | None = None  # keep
    prompt_pack: str | None = None  # keep
    baseline_plugin_defs: List[Dict[str, Any]] | None = None  # keep
    retry_config: Dict[str, Any] | None = None  # keep
    checkpoint_config: Dict[str, Any] | None = None  # keep
    llm_middleware_defs: List[Dict[str, Any]] | None = None  # keep
    prompt_defaults: Dict[str, Any] | None = None  # keep
    concurrency_config: Dict[str, Any] | None = None  # keep
    early_stop_config: Dict[str, Any] | None = None  # keep
    early_stop_plugin_defs: List[Dict[str, Any]] | None = None  # → halt_condition_plugin_defs
```

**Renames:**
- `row_plugin_defs` → `transform_plugin_defs`
- `aggregator_plugin_defs` → `aggregation_transform_defs`
- `early_stop_plugin_defs` → `halt_condition_plugin_defs`

### 7.2 SDARunner Fields

#### **File: `core/sda/runner.py`**

```python
@dataclass
class SDARunner:  # renamed from ExperimentRunner
    llm_client: LLMClientProtocol  # keep
    sinks: List[ResultSink]  # keep
    prompt_system: str  # keep
    prompt_template: str  # keep
    prompt_fields: List[str] | None = None  # keep
    criteria: List[Dict[str, str]] | None = None  # keep
    row_plugins: List[RowExperimentPlugin] | None = None  # → transform_plugins: List[TransformPlugin]
    aggregator_plugins: List[AggregationExperimentPlugin] | None = None  # → aggregation_transforms: List[AggregationTransform]
    rate_limiter: RateLimiter | None = None  # keep
    cost_tracker: CostTracker | None = None  # keep
    experiment_name: str | None = None  # → cycle_name
    retry_config: Dict[str, Any] | None = None  # keep
    checkpoint_config: Dict[str, Any] | None = None  # keep
    _checkpoint_ids: set[str] | None = None  # keep or → _checkpoint_inputs
    prompt_defaults: Dict[str, Any] | None = None  # keep
    prompt_engine: PromptEngine | None = None  # keep
    _compiled_system_prompt: PromptTemplate | None = None  # keep
    _compiled_user_prompt: PromptTemplate | None = None  # keep
    _compiled_criteria_prompts: Dict[str, PromptTemplate] | None = None  # keep
    llm_middlewares: list[LLMMiddleware] | None = None  # keep
    concurrency_config: Dict[str, Any] | None = None  # keep
    security_level: str | None = None  # keep
    _active_security_level: str | None = None  # keep
    early_stop_plugins: List[EarlyStopPlugin] | None = None  # → halt_condition_plugins
    early_stop_config: Dict[str, Any] | None = None  # → halt_condition_config
```

**Renames:**
- `row_plugins` → `transform_plugins`
- `aggregator_plugins` → `aggregation_transforms`
- `experiment_name` → `cycle_name`
- `early_stop_plugins` → `halt_condition_plugins`
- `early_stop_config` → `halt_condition_config`

---

## 8. Method & Function Renames (Detailed)

### 8.1 Core Methods

#### **File: `core/sda/runner.py`**

| **Current Method** | **New Method** | **Notes** |
|--------------------|----------------|-----------|
| `run(df: pd.DataFrame)` | `run(df: pd.DataFrame)` | Keep - clear method name |
| `_process_single_row(idx, row, context, row_id)` | `_process_single_input(idx, input_data, context, input_id)` | More generic |
| `_run_parallel(rows_to_process)` | `_run_parallel(inputs_to_process)` | Parameter rename |
| `_load_checkpoint(path)` | `_load_checkpoint(path)` | Keep |
| `_save_checkpoint(checkpoint_path, row_id)` | `_save_checkpoint(checkpoint_path, input_id)` | Parameter rename |
| `_init_early_stop()` | `_init_halt_conditions()` | Consistent terminology |

**Internal Variable Renames in Methods:**
- `row` → `input_data` or `input_row` (context-dependent)
- `row_id` → `input_id`
- `row_plugins` → `transform_plugins`
- `aggregator_plugins` → `aggregation_transforms`

### 8.2 Plugin Registry Functions

#### **File: `core/sda/plugin_registry.py`**

| **Current Function** | **New Function** |
|----------------------|------------------|
| `create_row_plugin(defn)` | `create_transform_plugin(defn)` |
| `create_aggregation_plugin(defn)` | `create_aggregation_transform(defn)` |
| `create_early_stop_plugin(defn)` | `create_halt_condition_plugin(defn)` |
| `create_baseline_comparison_plugin(defn)` | `create_comparison_plugin(defn)` |

### 8.3 Suite Runner Methods

#### **File: `core/sda/suite_runner.py`**

| **Current Method** | **New Method** | **Notes** |
|--------------------|----------------|-----------|
| `run_suite()` | `run_suite()` | Keep |
| `_run_baseline_experiment()` | `_run_baseline_cycle()` | Terminology |
| `_run_variant_experiment()` | `_run_variant_cycle()` | Terminology |

---

## 9. String Literal Updates

### 9.1 Logging Messages

**Search for strings containing:**
- `"experiment"` → `"SDA cycle"` or `"cycle"`
- `"Running experiment"` → `"Running SDA cycle"`
- `"Experiment completed"` → `"Cycle completed"`
- `"row processing"` → `"input processing"`

**Files to check:**
- `core/sda/runner.py`
- `core/sda/suite_runner.py`
- `core/orchestrator.py`
- `cli.py`

### 9.2 Error Messages

Update exception messages:
- `"Experiment configuration invalid"` → `"SDA cycle configuration invalid"`
- `"No experiments found in suite"` → `"No cycles found in suite"`

---

## 10. Test File Updates

**Note:** Test files not visible in current file list, but if they exist:

### 10.1 Test Directory Structure
- `tests/test_experiments/` → `tests/test_sda/`
- `tests/test_experiment_runner.py` → `tests/test_sda_runner.py`

### 10.2 Test Class Names
- `TestExperimentRunner` → `TestSDARunner`
- `TestExperimentOrchestrator` → `TestSDAOrchestrator`

### 10.3 Test Method Names
- `test_experiment_runs_successfully` → `test_sda_cycle_runs_successfully`

---

## 11. Execution Plan (Phased Approach)

### **Phase 1: Preparation & Backup** (30 minutes)
1. **Create git branch:** `git checkout -b feature/sda-renaming`
2. **Backup current state:** `git tag pre-sda-rename`
3. **Run existing tests:** Establish baseline (if tests exist)
4. **Create execution checklist:** Copy this document sections as todos

### **Phase 2: Directory Renames** (15 minutes)

1. **Rename directories:**

   ```bash
   git mv core/experiments core/sda
   git mv plugins/experiments plugins/transforms
   ```

2. **Commit:** `git commit -m "Phase 2: Rename directories experiments→sda, plugins/experiments→transforms"`

### **Phase 3: Update Imports** (30 minutes)
1. **Update all import statements** in files:
   - `core/orchestrator.py`
   - `cli.py`
   - `core/sda/__init__.py`
   - `core/sda/suite_runner.py`
   - `plugins/transforms/metrics.py`
   - `plugins/transforms/early_stop.py`
   - Any files importing from `core.experiments` or `plugins.experiments`

2. **Find all imports:**
   ```bash
   rg "from dmp\.core\.experiments" --type py -l
   rg "from dmp\.plugins\.experiments" --type py -l
   ```

3. **Commit:** `git commit -m "Phase 3: Update import paths"`

### **Phase 4: Core Class Renames** (1-2 hours)
1. **File: `core/orchestrator.py`**
   - Rename `ExperimentOrchestrator` → `SDAOrchestrator`
   - Rename `OrchestratorConfig` → `SDAConfig`
   - Update field names: `experiment_runner` → `sda_runner`, etc.
   - Update docstrings

2. **File: `core/sda/runner.py`**
   - Rename `ExperimentRunner` → `SDARunner`
   - Update all field names per Section 7.2
   - Rename methods per Section 8.1
   - Update docstrings and comments

3. **File: `core/sda/suite_runner.py`**
   - Rename `ExperimentSuiteRunner` → `SDASuiteRunner`
   - Update variables: `baseline_experiment` → `baseline_cycle`
   - Update method names per Section 8.3

4. **File: `core/sda/config.py`**
   - Rename `ExperimentSuite` → `SDASuite`
   - Rename `ExperimentConfig` → `SDACycleConfig`
   - Update field: `experiments` → `cycles`

5. **Commit:** `git commit -m "Phase 4: Rename core orchestration classes"`

### **Phase 5: Plugin Protocol Renames** (1 hour)

1. **File: `core/sda/plugins.py`**
   - `RowExperimentPlugin` → `TransformPlugin`
   - `AggregationExperimentPlugin` → `AggregationTransform`
   - `BaselineComparisonPlugin` → `ComparisonPlugin`
   - `EarlyStopPlugin` → `HaltConditionPlugin`
   - Update method names: `process_row()` → `transform()`
   - Update docstrings

2. **File: `core/sda/plugin_registry.py`**
   - Rename all factory functions per Section 8.2
   - Update parameter names

3. **File: `core/interfaces.py`**
   - Rename `ExperimentContext` → `SDAContext`
   - Keep `DataSource`, `LLMClientProtocol`, `ResultSink` as-is

4. **Commit:** `git commit -m "Phase 5: Rename plugin protocols to Transform/AggregationTransform"`

### **Phase 6: Plugin Implementations** (1 hour)

1. **File: `plugins/transforms/metrics.py`**
   - Update class names and protocol implementations
   - Update imports to use `TransformPlugin`

2. **File: `plugins/transforms/early_stop.py`**
   - Update class names and protocol implementations
   - Update imports to use `HaltConditionPlugin`

3. **Commit:** `git commit -m "Phase 6: Update transform plugin implementations"`

### **Phase 7: CLI & Configuration** (1 hour)
1. **File: `cli.py`**
   - Update imports
   - Rename CLI arguments: `--single-run` → `--single-cycle`
   - Update help text strings
   - Rename functions: `_run_single()` → `_run_single_cycle()`

2. **File: `config.py`**
   - Update field names if they reference experiments

3. **File: `core/config_schema.py`**
   - Update JSON schemas per Section 5.1

4. **File: `core/validation.py`**
   - Update error messages

5. **Commit:** `git commit -m "Phase 7: Update CLI and configuration"`

### **Phase 8: Documentation** (2-3 hours)
1. **Update architecture docs:**
   - `docs/architecture/README.md`
   - `docs/architecture/subsystems.md`
   - `docs/architecture/diagrams.md`

2. **Update README.md**

3. **Update all Mermaid diagrams** with new component names

4. **Commit:** `git commit -m "Phase 8: Update documentation"`

### **Phase 9: String Literals & Messages** (1 hour)
1. **Search and replace logging messages:**
   ```bash
   rg '".*experiment.*"' --type py -l
   ```

2. **Update error messages**

3. **Update docstrings and comments**

4. **Commit:** `git commit -m "Phase 9: Update string literals"`

### **Phase 10: Testing & Fix-on-Fail** (2-4 hours)
1. **Run Python syntax check:**
   ```bash
   python -m py_compile $(find . -name "*.py")
   ```

2. **Run import checks:**
   ```bash
   python -c "from dmp.core.sda import SDARunner"
   python -c "from dmp.core.orchestrator import SDAOrchestrator"
   ```

3. **Run tests (if they exist):**
   ```bash
   pytest
   ```

4. **Fix any errors** discovered:
   - Import errors → check file paths
   - Name errors → check class/function renames
   - Type errors → check protocol implementations

5. **Manual smoke test:**
   - Run CLI with sample configuration
   - Verify basic functionality

6. **Commit fixes:** `git commit -m "Phase 10: Fix-on-fail corrections"`

### **Phase 11: Final Review & Merge** (30 minutes)
1. **Review all changes:**
   ```bash
   git diff main..feature/sda-renaming --stat
   ```

2. **Check for any missed "experiment" references:**
   ```bash
   rg -i "experiment" --type py -l
   # Review results, exclude acceptable cases
   ```

3. **Final commit:** `git commit -m "Phase 11: Final cleanup"`

4. **Merge to main:**
   ```bash
   git checkout main
   git merge feature/sda-renaming
   ```

5. **Tag release:**
   ```bash
   git tag v2.0.0-sda
   ```

---

## 12. Rollback Plan

If critical issues arise:

1. **Immediate rollback:**
   ```bash
   git checkout main
   git reset --hard pre-sda-rename
   ```

2. **Selective revert:**
   ```bash
   git revert <commit-hash>
   ```

---

## 13. Risk Assessment

| **Risk** | **Likelihood** | **Impact** | **Mitigation** |
|----------|----------------|------------|----------------|
| Missed references | High | Medium | Comprehensive search before merge |
| Import errors | Medium | High | Automated import checks in Phase 10 |
| Plugin breakage | Medium | Medium | Update all plugin implementations |
| Config file incompatibility | High | High | Update validation schemas, test with sample configs |
| Documentation drift | Medium | Low | Update all docs in Phase 8 |

---

## 14. Success Criteria

- [ ] All Python files import successfully
- [ ] No references to "Experiment" in class/function names
- [ ] CLI runs without errors
- [ ] Configuration files can be loaded
- [ ] All tests pass (if they exist)
- [ ] Documentation reflects new terminology
- [ ] Grep search for "experiment" returns only acceptable cases (comments, historical notes)

---

## 15. Post-Rename Checklist

After completion, verify:

- [ ] `rg -i "ExperimentRunner" --type py` returns 0 results
- [ ] `rg -i "ExperimentOrchestrator" --type py` returns 0 results
- [ ] `rg -i "ExperimentSuite" --type py` returns 0 results
- [ ] `rg -i "RowExperimentPlugin" --type py` returns 0 results
- [ ] `rg -i "core\.experiments" --type py` returns 0 results
- [ ] All imports resolve successfully
- [ ] Sample configuration loads without errors
- [ ] Documentation uses SDA terminology consistently

---

## 16. Resolved Terminology Decisions

Based on user feedback, the following decisions have been finalized:

1. **DataSource/ResultSink:** ✅ **KEEP AS-IS**
   - Aligns with Sense (data sources) and Act (data sinks/effectors)

2. **LLMClientProtocol:** ✅ **KEEP AS-IS**
   - LLM terminology is clear and widely understood

3. **Plugin directory:** ✅ **plugins/transforms/** (not processors)
   - Aligns with Decide phase: data transforms

4. **Plugin protocols:**
   - `RowExperimentPlugin` → `TransformPlugin`
   - `AggregationExperimentPlugin` → `AggregationTransform`

5. **Method naming:**
   - `process_row()` → `transform()` (data transformation)
   - `finalize()` → `aggregate()` or keep `finalize()`

6. **Config field names:** ✅ **YES, change all for consistency**
   - `row_plugin_defs` → `transform_plugin_defs`
   - `aggregator_plugin_defs` → `aggregation_transform_defs`

**Final SDA Alignment:**

- **SENSE:** DataSource (data sources)
- **DECIDE:** LLMClientProtocol + TransformPlugin (data transforms)
- **ACT:** ResultSink (data sinks to effectors)

---

## 17. Summary of Files Modified

### **High-Impact Files (Core Changes)**
1. `core/orchestrator.py` - Main orchestrator class
2. `core/sda/runner.py` - Core execution engine
3. `core/sda/suite_runner.py` - Suite orchestration
4. `core/sda/plugins.py` - Plugin protocols
5. `core/sda/plugin_registry.py` - Plugin factories
6. `core/sda/config.py` - Configuration models
7. `core/interfaces.py` - Core interfaces

### **Medium-Impact Files (Imports & Usage)**
8. `cli.py` - CLI entry point
9. `config.py` - Settings loader
10. `core/config_schema.py` - JSON schemas
11. `core/validation.py` - Validation logic
12. `plugins/transforms/metrics.py` - Transform plugin for metrics
13. `plugins/transforms/early_stop.py` - Halt condition plugin
14. `core/sda/__init__.py` - Module exports

### **Low-Impact Files (Documentation)**
15. `README.md`
16. `docs/architecture/README.md`
17. `docs/architecture/subsystems.md`
18. `docs/architecture/diagrams.md`

### **File Moves**

- 6 files in `core/experiments/` → `core/sda/`
- 3 files in `plugins/experiments/` → `plugins/transforms/`

**Total Files Affected:** ~20 Python files + 4 documentation files = **24 files**

---

## 18. Estimated Timeline

| **Phase** | **Duration** | **Cumulative** |
|-----------|--------------|----------------|
| Phase 1: Preparation | 30 min | 0.5 hrs |
| Phase 2: Directory renames | 15 min | 0.75 hrs |
| Phase 3: Update imports | 30 min | 1.25 hrs |
| Phase 4: Core class renames | 2 hrs | 3.25 hrs |
| Phase 5: Plugin protocols | 1 hr | 4.25 hrs |
| Phase 6: Plugin implementations | 1 hr | 5.25 hrs |
| Phase 7: CLI & config | 1 hr | 6.25 hrs |
| Phase 8: Documentation | 2.5 hrs | 8.75 hrs |
| Phase 9: String literals | 1 hr | 9.75 hrs |
| Phase 10: Testing & fixes | 3 hrs | 12.75 hrs |
| Phase 11: Final review | 30 min | 13.25 hrs |

**Total Estimated Time:** 13-14 hours (~2 working days)

---

## 19. Version Control Strategy

```bash
# Initial setup
git checkout -b feature/sda-renaming
git tag pre-sda-rename

# After each phase
git add .
git commit -m "Phase N: [description]"

# Final merge
git checkout main
git merge feature/sda-renaming
git tag v2.0.0-sda
git push origin main --tags
```

---

## 20. Final Terminology Summary

| **Concept** | **Old Name** | **New Name** | **SDA Phase** |
|-------------|--------------|--------------|---------------|
| Input providers | DataSource | DataSource (keep) | **SENSE** |
| Decision engine | LLMClientProtocol | LLMClientProtocol (keep) | **DECIDE** |
| Per-input transforms | RowExperimentPlugin | TransformPlugin | **DECIDE** |
| Aggregation transforms | AggregationExperimentPlugin | AggregationTransform | **DECIDE** |
| Output handlers | ResultSink | ResultSink (keep) | **ACT** |
| Orchestration unit | ExperimentRunner | SDARunner | All phases |
| Collection | ExperimentSuite | SDASuite | All phases |
| Plugin directory | plugins/experiments/ | plugins/transforms/ | **DECIDE** |
| Core directory | core/experiments/ | core/sda/ | All phases |

---

## END OF PLAN

**Next Steps:**
1. Review this plan with team/stakeholders
2. Answer open questions (Section 16)
3. Schedule execution window (2-day block recommended)
4. Execute phases sequentially
5. Fix-on-fail approach: address errors as they arise in Phase 10
