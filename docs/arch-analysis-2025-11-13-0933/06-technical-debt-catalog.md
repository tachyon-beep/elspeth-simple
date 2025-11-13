# Technical Debt Catalog

**Document Version:** 1.0
**Catalog Date:** November 13, 2025
**Codebase Version:** Git commit 73813a4 (main branch)
**Analysis Scope:** High-priority architectural issues requiring immediate remediation
**Status:** 2 critical work packages defined, ready for execution

---

## Work Package 1: Refactor ExperimentRunner God Class

**Priority:** HIGH (Critical Path for Development Velocity)
**Category:** Architecture / Code Quality
**ID:** TD-001
**Status:** Ready for Development

### Problem Statement

The `ExperimentRunner` class violates Single Responsibility Principle with 600+ lines and 10+ distinct responsibilities. This god class anti-pattern constrains development velocity, increases defect risk, and blocks parallel development.

### Evidence

**File:** `src/core/experiments/runner.py` (600+ lines)

**Responsibilities identified:**
1. Prompt template compilation and caching
2. LLM request/response handling
3. Row-by-row processing logic
4. Parallel execution orchestration (ThreadPoolExecutor)
5. Retry logic with exponential backoff
6. Checkpoint/resume state management
7. Early stopping condition evaluation
8. Plugin lifecycle coordination (row plugins, aggregation plugins)
9. Rate limiting integration
10. Cost tracking integration

**Supporting evidence from codebase:**
- Single class handles concurrent.futures.ThreadPoolExecutor orchestration
- Checkpoint logic embedded in execution flow
- Retry policy logic mixed with business logic
- Plugin coordination spread throughout runner methods

### Business Impact

**Current state:**
- Sequential development (cannot parallelize work on different concerns)
- New features require understanding 600+ lines before making changes
- Developer onboarding time increased by steep learning curve

**6-month projection without fix:**
- Feature development velocity decreases 30-40%
- Defect rate increases as changes have unpredictable side effects
- Team productivity constrained by single-threaded development on runner

**12-month projection without fix:**
- ExperimentRunner becomes untouchable (too risky to modify)
- Feature development effectively frozen on core orchestration
- Technical debt forces workarounds, creating more technical debt

### Technical Impact

**Maintainability:**
- Change fragility: Modifying retry logic risks breaking checkpoint logic
- Every change has blast radius across unrelated functionality
- Code navigation difficult (finding relevant logic in 600+ lines)

**Testability:**
- Cannot unit test individual concerns in isolation
- Unit tests become integration tests (require full setup)
- Test complexity increases with every responsibility added

**Extensibility:**
- Adding new execution strategies requires modifying large class
- Risk of regression with every modification
- Parallel development blocked by merge conflicts

### Effort Estimate

**Total:** 7 weeks (35 working days)

**Breakdown:**
- Week 1: Extract RetryPolicy class + unit tests (5 days)
- Week 2: Extract CheckpointManager class + unit tests (5 days)
- Week 3: Extract ParallelExecutor class + unit tests (5 days)
- Week 4: Extract EarlyStopCoordinator class + unit tests (5 days)
- Week 5: Extract PluginLifecycle class + unit tests (5 days)
- Week 6: Refactor ExperimentRunner to use extracted classes (5 days)
- Week 7: Integration testing and verification (5 days)

**Resources:** 1 senior engineer (full-time)

**Dependencies:** None (can start immediately)

### Technical Approach

**Target architecture:**

```
ExperimentRunner (coordination only, <300 lines)
├─ RetryPolicy (retry logic with configurable strategies)
├─ CheckpointManager (state persistence and resume)
├─ ParallelExecutor (ThreadPoolExecutor orchestration)
├─ EarlyStopCoordinator (plugin-based condition checking)
└─ PluginLifecycle (row plugin and aggregation plugin execution)
```

**Extraction sequence (sequential, one per week):**

**Week 1: RetryPolicy**
- Extract: Retry logic with exponential backoff
- Location: New file `src/core/experiments/retry_policy.py`
- Interface:
  ```python
  class RetryPolicy:
      def execute_with_retry(self, fn: Callable, metadata: Dict) -> Any:
          """Execute function with retry logic."""
  ```
- Tests: Unit tests for retry strategies (immediate, exponential, max attempts)
- Validation: All existing retry behavior preserved

**Week 2: CheckpointManager**
- Extract: Checkpoint/resume state management
- Location: New file `src/core/experiments/checkpoint_manager.py`
- Interface:
  ```python
  class CheckpointManager:
      def load_checkpoint(self, path: Path) -> Optional[CheckpointState]:
          """Load checkpoint state from file."""

      def save_checkpoint(self, path: Path, state: CheckpointState) -> None:
          """Save checkpoint state to file."""

      def filter_processed_rows(self, df: pd.DataFrame, checkpoint: CheckpointState) -> pd.DataFrame:
          """Filter already-processed rows from dataframe."""
  ```
- Tests: Unit tests for checkpoint I/O, state management, row filtering
- Validation: Resume functionality works identically

**Week 3: ParallelExecutor**
- Extract: ThreadPoolExecutor orchestration and parallel processing
- Location: New file `src/core/experiments/parallel_executor.py`
- Interface:
  ```python
  class ParallelExecutor:
      def execute_parallel(
          self,
          fn: Callable,
          items: List[Any],
          max_workers: int
      ) -> List[Any]:
          """Execute function on items in parallel."""
  ```
- Tests: Unit tests for parallel execution, error handling, worker pool management
- Validation: Parallel mode produces identical results, performance unchanged

**Week 4: EarlyStopCoordinator**
- Extract: Early stopping condition evaluation
- Location: New file `src/core/experiments/early_stop_coordinator.py`
- Interface:
  ```python
  class EarlyStopCoordinator:
      def check_early_stop(
          self,
          record: Dict,
          metadata: Dict,
          plugins: List[EarlyStopPlugin]
      ) -> Optional[Dict]:
          """Check if early stop conditions met."""
  ```
- Tests: Unit tests for condition checking, plugin coordination
- Validation: Early stop behavior identical

**Week 5: PluginLifecycle**
- Extract: Row plugin and aggregation plugin execution
- Location: New file `src/core/experiments/plugin_lifecycle.py`
- Interface:
  ```python
  class PluginLifecycle:
      def apply_row_plugins(
          self,
          row: pd.Series,
          response: Dict,
          plugins: List[RowExperimentPlugin]
      ) -> Dict:
          """Apply row plugins to single result."""

      def apply_aggregation_plugins(
          self,
          records: List[Dict],
          plugins: List[AggregationExperimentPlugin]
      ) -> Dict:
          """Apply aggregation plugins to all results."""
  ```
- Tests: Unit tests for plugin application, error handling
- Validation: Plugin behavior identical

**Week 6: Refactor ExperimentRunner**
- Refactor: ExperimentRunner to use all extracted classes
- Goal: Reduce to <300 lines, coordination logic only
- Changes:
  ```python
  class ExperimentRunner:
      def __init__(
          self,
          retry_policy: RetryPolicy,
          checkpoint_manager: CheckpointManager,
          parallel_executor: ParallelExecutor,
          early_stop_coordinator: EarlyStopCoordinator,
          plugin_lifecycle: PluginLifecycle,
          ...
      ):
          # Dependency injection of extracted components

      def run(self, df: pd.DataFrame) -> List[Dict]:
          # Coordination only - delegates to components
          checkpoint = self.checkpoint_manager.load_checkpoint(...)
          df = self.checkpoint_manager.filter_processed_rows(df, checkpoint)

          if self.config.parallel:
              results = self.parallel_executor.execute_parallel(...)
          else:
              results = [self._process_row(row) for row in df.itertuples()]

          for record in results:
              early_stop = self.early_stop_coordinator.check_early_stop(...)
              if early_stop:
                  break

          aggregated = self.plugin_lifecycle.apply_aggregation_plugins(results, ...)
          return results
  ```
- Tests: Update existing runner tests to use new architecture
- Validation: All integration tests pass

**Week 7: Integration Testing**
- Run full test suite (unit + integration)
- Performance benchmarking (ensure no regression)
- End-to-end testing with real experiments
- Code review and documentation updates
- Validation criteria:
  - All existing tests pass (zero behavior changes)
  - ExperimentRunner class <300 lines
  - Each extracted class has 100% unit test coverage
  - Performance unchanged (±5% acceptable variance)
  - No new linter or type checker errors

### Success Criteria

**Must achieve:**
1. ✅ ExperimentRunner class reduced to <300 lines
2. ✅ Each extracted class has dedicated unit tests (100% coverage)
3. ✅ All existing integration tests pass (zero breaking changes)
4. ✅ Performance benchmarks unchanged (±5% variance)
5. ✅ No new type checker errors (mypy/pyright pass)
6. ✅ Each extracted class has single, clear responsibility

**Quality gates:**
- Code review by senior engineer (not implementer)
- Architecture review confirms SRP compliance
- Performance testing on realistic dataset (1000+ rows)

### Risks and Mitigation

**Risk 1: Breaking existing behavior**
- Mitigation: Comprehensive test suite, incremental extraction (one class per week)
- Contingency: Each week's extraction can be reverted independently

**Risk 2: Performance regression from additional abstraction**
- Mitigation: Benchmark before/after each extraction
- Contingency: Profile and optimize hot paths if needed

**Risk 3: Incomplete understanding of responsibilities**
- Mitigation: Code reading + existing test analysis before extraction
- Contingency: Pair programming with original implementer

### Post-Completion

**Immediate benefits:**
- Parallel development enabled (different developers on different components)
- New execution strategies can be added without modifying ExperimentRunner
- Testing becomes easier (unit test individual components)

**Long-term benefits:**
- Development velocity increases (smaller, focused classes)
- Defect rate decreases (isolated concerns)
- Onboarding time decreases (easier to understand)

**Maintenance:**
- Update architecture documentation with new component diagram
- Add docstrings explaining responsibility of each component
- Document dependency injection pattern for future reference

---

## Work Package 2: Centralize Configuration Merging Logic

**Priority:** HIGH (User Experience and Operational Risk)
**Category:** Architecture / Code Quality
**ID:** TD-002
**Status:** Ready for Development

### Problem Statement

Configuration merging logic is distributed across 300+ lines in three files (`cli.py`, `config.py`, `core/experiments/suite_runner.py`) with undocumented precedence rules across 5 hierarchy levels. Users cannot predict final configuration values, creating operational risk and support burden.

### Evidence

**Files affected:**
- `src/cli.py` (lines 204-358, ~150 lines of merging logic)
- `src/config.py` (134 lines total, includes merging)
- `src/core/experiments/suite_runner.py` (lines 34-100, suite-level merging)

**Total:** 300+ lines of configuration merging spread across 3 files

**Configuration hierarchy (5 levels):**
1. System defaults (hardcoded)
2. Prompt pack settings (reusable configurations)
3. Profile settings (environment-specific)
4. Suite defaults (suite-level shared config)
5. Experiment settings (per-experiment overrides)

**Merge strategies vary by key:**
- Scalar values: Override (higher precedence replaces lower)
- Lists (plugins): Append (accumulate from all sources)
- Nested dicts: Deep merge with complex rules

**Evidence of user confusion:**
- Archaeologist report: "Precedence rules for prompt packs, suite defaults, and profile settings not well-documented"
- Configuration debugging requires reading 300+ lines across 3 files

### Business Impact

**Current state:**
- Users cannot predict configuration behavior
- Support burden for "why isn't my config working?"
- Configuration errors discovered at runtime (not validation time)

**6-month projection without fix:**
- Configuration complexity limits user adoption
- Production incidents from configuration errors increase
- Users create workarounds (bypassing safety mechanisms like rate limits)

### Technical Impact

**Unpredictability:**
- Users set rate_limit in profile, prompt pack overrides it, user doesn't understand why
- No visibility into final merged configuration
- Silent overrides create unexpected behavior

**Debugging difficulty:**
- Must read 300+ lines across 3 files to understand precedence
- No trace of merge decisions (which value came from where)
- Error messages don't explain configuration source

**Maintenance burden:**
- Changing merge logic requires coordinated updates in 3 locations
- Risk of inconsistency between files
- New configuration keys require updates in multiple places

### Effort Estimate

**Total:** 2 weeks (10 working days)

**Breakdown:**
- Days 1-2: Design ConfigurationMerger class (2 days)
- Days 3-5: Implementation + unit tests (3 days)
- Days 6-7: Migration + integration testing (2 days)
- Days 8-9: Add --print-config CLI flag (2 days)
- Day 10: Documentation + code review (1 day)

**Resources:** 1 senior engineer (full-time)

**Dependencies:** None (can start immediately or after TD-001)

### Technical Approach

**Target architecture:**

Create new file: `src/core/config_merger.py` with centralized merging logic

**Implementation:**

```python
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

class MergeStrategy(Enum):
    """Configuration merge strategies."""
    OVERRIDE = "override"  # Higher precedence replaces lower
    APPEND = "append"      # Accumulate from all sources (lists)
    DEEP_MERGE = "deep_merge"  # Recursive merge (nested dicts)

@dataclass
class ConfigSource:
    """Configuration source with metadata."""
    name: str  # "system_default", "prompt_pack", "profile", "suite", "experiment"
    data: Dict[str, Any]
    precedence: int  # Lower number = lower precedence

class ConfigurationMerger:
    """Centralized configuration merging with documented precedence.

    Precedence levels (lowest to highest):
    1. System defaults (precedence=1)
    2. Prompt pack (precedence=2)
    3. Profile (precedence=3)
    4. Suite defaults (precedence=4)
    5. Experiment config (precedence=5)

    Merge strategies by key:
    - Scalar values (str, int, bool): OVERRIDE
    - Lists (*_plugins, *_sinks): APPEND
    - Nested dicts (llm.options, datasource.options): DEEP_MERGE
    """

    # Define merge strategies for known keys
    MERGE_STRATEGIES = {
        "row_plugins": MergeStrategy.APPEND,
        "aggregation_plugins": MergeStrategy.APPEND,
        "sinks": MergeStrategy.APPEND,
        "llm": MergeStrategy.DEEP_MERGE,
        "datasource": MergeStrategy.DEEP_MERGE,
        "orchestrator": MergeStrategy.DEEP_MERGE,
        # All other keys: OVERRIDE (default)
    }

    def merge(self, *sources: ConfigSource) -> Dict[str, Any]:
        """Merge configuration sources with defined precedence.

        Args:
            sources: Configuration sources in any order (sorted by precedence)

        Returns:
            Merged configuration dictionary
        """
        # Sort by precedence (lowest first)
        sorted_sources = sorted(sources, key=lambda s: s.precedence)

        merged = {}
        self._merge_trace = []  # Track merge decisions for debugging

        for source in sorted_sources:
            merged = self._merge_source(merged, source)

        return merged

    def explain(self, key: str, merged_config: Dict) -> str:
        """Explain why a configuration value is what it is.

        Args:
            key: Configuration key (e.g., "rate_limit.requests_per_minute")

        Returns:
            Explanation string showing source and precedence

        Example:
            >>> merger.explain("rate_limit.requests_per_minute", config)
            "rate_limit.requests_per_minute = 50
             Source: profile (precedence 3)
             Overrides: prompt_pack=100 (precedence 2), system_default=10 (precedence 1)"
        """
        # Implementation traces merge history
        pass

    def _merge_source(self, base: Dict, source: ConfigSource) -> Dict:
        """Merge single source into base configuration."""
        result = base.copy()

        for key, value in source.data.items():
            strategy = self.MERGE_STRATEGIES.get(key, MergeStrategy.OVERRIDE)

            if strategy == MergeStrategy.OVERRIDE:
                result[key] = value
                self._merge_trace.append({
                    "key": key,
                    "strategy": "override",
                    "source": source.name,
                    "value": value
                })

            elif strategy == MergeStrategy.APPEND:
                if key not in result:
                    result[key] = []
                result[key] = result[key] + value
                self._merge_trace.append({
                    "key": key,
                    "strategy": "append",
                    "source": source.name,
                    "appended": value
                })

            elif strategy == MergeStrategy.DEEP_MERGE:
                if key not in result:
                    result[key] = {}
                result[key] = self._deep_merge_dict(result[key], value)
                self._merge_trace.append({
                    "key": key,
                    "strategy": "deep_merge",
                    "source": source.name,
                    "merged_keys": list(value.keys())
                })

        return result

    def _deep_merge_dict(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge nested dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dict(result[key], value)
            else:
                result[key] = value
        return result
```

**Migration plan:**

**Day 1-2: Design and skeleton**
- Create `src/core/config_merger.py` with classes above
- Define MERGE_STRATEGIES dictionary for all known keys
- Write comprehensive class docstring with examples

**Day 3: Replace cli.py merging**
- Refactor `cli.py:load_settings()` to use ConfigurationMerger
- Remove old merging logic (lines 204-358)
- Keep same API (no breaking changes)

**Day 4: Replace config.py merging**
- Refactor config.py to use ConfigurationMerger
- Centralize prompt pack merging logic

**Day 5: Replace suite_runner.py merging**
- Refactor `suite_runner.py` to use ConfigurationMerger
- Remove suite-level merging logic (lines 34-100)

**Day 6-7: Testing and validation**
- Unit tests for ConfigurationMerger (all merge strategies)
- Integration tests: Load 10+ real-world configurations
- Validation: Before/after configs must be identical (byte-for-byte)
- Add tests for edge cases:
  - Conflicting keys across all 5 levels
  - List appending with duplicates
  - Deep merge with nested 3+ levels
  - Missing keys in some sources

**Day 8-9: Add --print-config flag**
- Implement CLI flag: `elspeth --settings config.yaml --print-config`
- Output format:
  ```yaml
  # Resolved Configuration
  # Generated from: config.yaml (profile: production)
  # Merge sources: system_defaults → prompt_pack:quality-eval → profile:production → suite_defaults → experiment:exp1

  llm:
    plugin: azure_openai  # Source: profile:production (overrides prompt_pack:mock)
    options:
      deployment_name: gpt-4  # Source: profile:production
      temperature: 0.7  # Source: prompt_pack:quality-eval

  rate_limit:
    requests_per_minute: 50  # Source: suite_defaults (overrides profile:100, prompt_pack:10)
    max_workers: 10  # Source: experiment:exp1

  row_plugins:  # Strategy: APPEND from all sources
    - name: extract_score  # Source: prompt_pack:quality-eval
    - name: custom_metric  # Source: experiment:exp1
  ```
- Add `--explain-config KEY` flag for single key explanation

**Day 10: Documentation**
- Create `docs/configuration-precedence.md` with:
  - Precedence level table
  - Merge strategy table
  - Examples for each level
  - Troubleshooting section
- Update class docstrings
- Code review with team

### Success Criteria

**Must achieve:**
1. ✅ All configuration merging logic in single file (`config_merger.py`)
2. ✅ All existing configurations produce identical results (byte-for-byte)
3. ✅ 100% unit test coverage for ConfigurationMerger
4. ✅ `--print-config` flag shows resolved configuration
5. ✅ Documentation explains all precedence rules
6. ✅ Zero breaking changes (existing configs work identically)

**Quality gates:**
- Integration test: Load 10+ real configs, compare before/after
- User testing: 3 users create configs using only new documentation
- Code review: Senior engineer confirms centralization complete

### Risks and Mitigation

**Risk 1: Breaking existing configurations**
- Mitigation: Comprehensive before/after testing, incremental migration
- Contingency: Each file migration can be reverted independently

**Risk 2: Missed edge cases in merge logic**
- Mitigation: Extract current behavior as tests before refactoring
- Contingency: Add specific tests for discovered edge cases

**Risk 3: Performance impact from tracing**
- Mitigation: Make tracing optional (only for --print-config)
- Contingency: Profile and optimize if needed

### Post-Completion

**Immediate benefits:**
- Users can predict configuration behavior (--print-config)
- Configuration debugging simplified (explain() method)
- Support burden reduced (users self-serve)

**Long-term benefits:**
- Single source of truth for merging logic
- Easy to add new configuration keys (define merge strategy once)
- Testable in isolation (unit tests for merge scenarios)

**Maintenance:**
- Document merge strategy for new config keys
- Update MERGE_STRATEGIES dict when adding keys
- Keep precedence rules consistent

---

## Immediate Actions (Before Starting Work Packages)

### Documentation Sprint (12 hours total)

**Can be done in parallel with work packages or before starting:**

#### Action 1: Document Configuration Precedence (6 hours)

**Deliverable:** `docs/configuration-precedence.md`

**Must include:**
- Table showing all 5 hierarchy levels with precedence order (system → prompt_pack → profile → suite → experiment)
- Merge strategy table (override vs append vs deep_merge) for each config section
- 5 examples showing each level overriding previous level
- Common mistakes section ("Why is my rate limit not working?")
- Troubleshooting flowchart

**Validation:** 3 users create complex configs following only the docs

#### Action 2: Document ExperimentRunner Architecture (3 hours)

**Deliverable:** Enhanced docstring in `src/core/experiments/runner.py`

**Must include:**
- ASCII diagram of execution flow
- Line number references for each responsibility
- Known issues section (size, SRP violations)
- Reference to this technical debt catalog

**Validation:** Code review by team member unfamiliar with runner

#### Action 3: Add Debug Logging (3 hours)

**Deliverable:** Configuration debug logging

**Implementation:**
```python
# In cli.py or config_merger.py
logger.info("Configuration merge: rate_limit.requests_per_minute = 50")
logger.info("  Source: profile:production (precedence 3)")
logger.info("  Overrides: prompt_pack=100 (precedence 2)")
```

**Validation:** Run experiment with `--debug`, verify merge decisions logged

---

## Execution Plan

### Option A: Sequential (Conservative)

```
Week 1-2:   TD-002 (Configuration merging - lower risk)
Week 3-9:   TD-001 (ExperimentRunner refactoring)
Week 10:    Buffer for issues
```

**Rationale:** Configuration merging is lower risk, shorter duration. Success builds confidence for larger refactoring.

### Option B: Parallel (Aggressive)

```
Week 1-2:   TD-002 (Engineer A: Configuration merging)
Week 1-7:   TD-001 (Engineer B: ExperimentRunner refactoring)
```

**Rationale:** Two independent engineers can work in parallel. TD-002 completion provides immediate user value while TD-001 is in progress.

**Conflicts:** Minimal (TD-002 touches cli.py, config.py; TD-001 touches runner.py, creates new files)

### Recommended: Option B (Parallel)

Both work packages are independent and can be executed in parallel by different engineers. This delivers value faster:
- TD-002 completes in 2 weeks (immediate user experience improvement)
- TD-001 completes in 7 weeks (development velocity improvement)
- Total calendar time: 7 weeks (vs 10 weeks sequential)

---

## Summary

**2 work packages defined:**
- TD-001: Refactor ExperimentRunner god class (7 weeks, HIGH priority)
- TD-002: Centralize configuration merging (2 weeks, HIGH priority)

**Combined effort:** 9 weeks (sequential) or 7 weeks (parallel)

**Resources required:** 1-2 senior engineers

**Business value:**
- Increased development velocity (30-40% improvement after TD-001)
- Reduced user confusion and support burden (after TD-002)
- Lower defect rate (isolated concerns after TD-001)
- Improved operational stability (predictable config after TD-002)

**Risk level:** LOW (comprehensive testing, incremental approach, clear success criteria)

**Ready to start:** Both work packages have sufficient detail for immediate execution.

---

**End of Catalog**
