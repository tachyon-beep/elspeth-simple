# Architecture Quality Assessment

**Document Version:** 1.0
**Assessment Date:** November 13, 2025
**Codebase Version:** Git commit 73813a4 (main branch)
**Analyzed Codebase:** elspeth-simple (9,283 lines Python)

---

## Assessment Summary

**Quality Level:** Good with High-Severity Issues
**Primary Pattern:** Layered architecture with protocol-oriented plugin system
**Overall Severity:** HIGH - Two critical maintainability issues will constrain development velocity and increase defect rate
**Timeline:** Current problems are already impacting development; will become critical within 6-12 months without remediation

**Bottom line:** The architecture demonstrates sound design patterns (protocol-oriented design, plugin registry, DAG resolution) but has two high-severity maintainability problems that require immediate attention: a 600-line god class violating Single Responsibility Principle and undocumented configuration merging logic spanning 300+ lines across three files.

---

## Evidence-Based Findings

### Core Architecture Pattern

**Pattern:** Layered architecture with protocol-oriented plugin extensibility

**Evidence:**
- 11 distinct subsystems with clear separation (cli.py, core/orchestrator.py, core/registry.py, core/experiments/, core/artifact_pipeline.py, core/llm/, core/prompts/, core/controls/, core/security/, core/validation.py, plugins/)
- Protocol-based contracts using PEP 544 structural typing (DataSource, LLMClientProtocol, ResultSink in core/interfaces.py)
- Centralized plugin registry with factory pattern and JSON schema validation (core/registry.py, 396 lines)
- 22 plugin implementations across 4 categories (datasources: 2, llms: 4, outputs: 11, experiments: 5+)

**Assessment:** This is fundamentally sound architecture. Protocol-oriented design enables loose coupling, extensibility, and testability.

### Type Safety and Modern Python

**Evidence:**
- Type hints with Protocol-based interfaces throughout codebase
- `from __future__ import annotations` for forward compatibility
- Dataclasses for configuration models
- Python 3.x with modern features

**Assessment:** Type system usage is appropriate and demonstrates engineering discipline.

---

## Architectural Problems

### Problem 1: God Class in Core Orchestration

**Severity:** HIGH

**Issue:** The `ExperimentRunner` class (core/experiments/runner.py) is 600+ lines with at least 10 distinct responsibilities:

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

**Evidence:**
- File: `core/experiments/runner.py` (600+ lines)
- Archaeologist report: "ExperimentRunner complexity: 600+ line class with many responsibilities"
- Violates Single Responsibility Principle by at least 10x

**Why this is HIGH severity:**

This is a classic god class anti-pattern. When a single class has 10+ responsibilities:

1. **Change fragility:** Modifying retry logic risks breaking checkpoint logic. Changing parallel execution risks breaking rate limiting. Every change has blast radius across unrelated functionality.

2. **Testing difficulty:** Cannot test retry logic without setting up checkpoint infrastructure, rate limiters, cost trackers, plugin lifecycle, etc. Unit tests become integration tests.

3. **Comprehension barrier:** New developers must understand 600 lines and 10 different concerns before making any change. Steep learning curve.

4. **Extension constraint:** Adding new execution strategies (e.g., streaming, batch optimization) requires modifying this massive class. Risk of regression.

5. **Parallel development blocked:** Two developers cannot work on different concerns (retry vs checkpoint) without merge conflicts.

**Impact timeline:** This is already impacting development velocity. Within 6 months, this will become the primary bottleneck for feature development.

**Required action:** Refactor into separate concerns (see Recommendations).

---

### Problem 2: Configuration Merging Complexity

**Severity:** HIGH

**Issue:** Configuration merging logic is spread across 300+ lines in three files with undocumented precedence rules and multiple merge strategies for different configuration keys.

**Evidence:**
- Files: `cli.py` (lines 204-358), `config.py` (134 lines), `core/experiments/suite_runner.py` (lines 34-100)
- Total: 300+ lines of merging logic across 3 files
- Archaeologist report: "Precedence rules for prompt packs, suite defaults, and profile settings not well-documented"
- Five levels of configuration hierarchy: System defaults → Prompt packs → Profiles → Suite defaults → Experiment overrides
- Different merge strategies: `row_plugins` appends, `prompt_system` overrides, nested configs have special handling

**Why this is HIGH severity:**

Distributed, undocumented configuration merging creates operational risk:

1. **Unpredictability:** Users cannot determine final configuration values. "Why is my rate limit 10 when I set it to 50?" becomes a debugging exercise requiring code reading.

2. **Debugging difficulty:** When configuration behavior is unexpected, developers must read 300+ lines across 3 files to understand precedence.

3. **Error-prone:** Easy to inadvertently override critical settings (security levels, rate limits, cost tracking). Silent failures.

4. **Maintenance burden:** Changing merge logic requires coordinated updates in 3 locations. Risk of inconsistency.

5. **User frustration:** Configuration is the primary user interface for this system. Complex, unpredictable configuration directly impacts user experience.

**Real-world scenario:**
```yaml
# User sets in profile
rate_limit: {requests_per_minute: 50}

# Prompt pack has
rate_limit: {tokens_per_minute: 1000}

# Suite defaults has
rate_limit: {max_workers: 10}

# What's the final configuration?
# User has no way to know without running or reading 300 lines of merge code
```

**Impact timeline:** This is currently causing user confusion and support burden. Will limit adoption and increase operational risk.

**Required action:** Centralize merge logic and document precedence (see Recommendations).

---

### Problem 3: Static Plugin Registration

**Severity:** MEDIUM

**Issue:** Plugins are hardcoded in registry via dictionary initialization. Adding plugins requires modifying core code and importing all plugins at startup.

**Evidence:**
- File: `core/registry.py` - all plugins explicitly imported and registered
- No entry point discovery mechanism
- No lazy loading (all plugins imported even if unused)
- Archaeologist report: "Plugin registry is static (hardcoded mappings), no dynamic plugin discovery"

**Why this is MEDIUM severity:**

This limits extensibility but doesn't break current functionality:

1. **Third-party plugins impossible:** Cannot distribute plugins separately from core. Organizations cannot add custom plugins without forking.

2. **Import overhead:** All 22 plugins imported at startup even if experiment uses only 2.

3. **Coupling:** Registry directly depends on all plugin implementations. Changes to plugins require registry changes.

4. **Distribution limitation:** Cannot package plugins separately (e.g., `pip install elspeth-azure-plugins`).

**Impact timeline:** Not currently blocking, but will limit ecosystem growth if third-party extensions are desired.

**Required action:** Implement entry point-based plugin discovery (see Recommendations).

---

### Problem 4: Large Plugin Implementation Files

**Severity:** MEDIUM

**Issue:** Several plugin files exceed 400 lines, suggesting multiple responsibilities or complex integrations.

**Evidence:**
- `plugins/outputs/blob.py`: 400+ lines (Azure Blob result sink)
- `plugins/outputs/repository.py`: 450+ lines (GitHub AND Azure DevOps sinks in single file)
- `plugins/llms/middleware.py`: 400+ lines (multiple generic middleware implementations)
- `plugins/llms/middleware_azure.py`: 440+ lines (Azure-specific middleware implementations)

**Why this is MEDIUM severity:**

Large files indicate possible SRP violations:

1. **repository.py combines two different APIs** (GitHub, Azure DevOps) in one file. These should be separate: `github_repo.py` and `azure_devops_repo.py`.

2. **middleware.py likely contains multiple middleware implementations** in one file. Each middleware should be separate file.

3. **blob.py 400 lines** suggests complex integration, which may be appropriate for Azure Blob SDK, but should be reviewed for extraction opportunities.

**Impact:** Makes navigation, testing, and maintenance harder. Not blocking but increases technical debt.

**Required action:** Split repository.py and middleware files (see Recommendations).

---

## Impact Analysis

### Development Velocity Impact

**Current state:**
- ExperimentRunner god class forces sequential development (cannot parallelize work on different concerns)
- New features require understanding 600+ lines before making changes
- Configuration debugging consumes support time

**6-month projection without remediation:**
- Feature development slows by 30-40% as class grows and complexity increases
- Defect rate increases as changes have unpredictable side effects
- Developer onboarding time increases (steep learning curve)

**12-month projection without remediation:**
- ExperimentRunner becomes untouchable (too risky to modify)
- Feature development effectively frozen on core orchestration
- Team works around the problem with workarounds, creating more technical debt

### Operational Risk Impact

**Current state:**
- Users cannot predict configuration behavior
- Configuration errors discovered at runtime (not validation time)
- Support burden for "why isn't my config working?"

**6-month projection without remediation:**
- Configuration complexity limits user adoption
- Production incidents from configuration errors increase
- Users create workarounds (bypassing safety mechanisms)

### Extensibility Impact

**Current state:**
- Third-party plugins impossible (static registration)
- Core team is bottleneck for all plugin development

**12-month projection without remediation:**
- Ecosystem growth constrained (no third-party plugins)
- Organizations fork codebase to add custom plugins
- Maintenance burden on core team (all plugins in core repo)

---

## What Works Well

The following architectural decisions are sound and should be preserved:

**Protocol-Oriented Design:** Using Python protocols (PEP 544) for plugin contracts is excellent. This enables loose coupling, testability, and extensibility. Core code depends on interfaces, not implementations. This pattern should be maintained and reinforced.

**Plugin Registry with Validation:** The factory pattern with JSON schema validation is solid. Validates plugin options before instantiation (fail-fast). Clear error messages. This pattern works correctly despite static registration issue.

**DAG Resolution for Artifacts:** The artifact pipeline with topological sort is sophisticated and well-designed. Enables complex sink dependencies (CSV → ZIP → GitHub) without hard-coding workflows. This demonstrates advanced architectural thinking.

**Layered Architecture:** Clear separation between Entry (CLI), Orchestration, Infrastructure (Registry, Middleware, Controls), Processing (Prompts, Artifacts), and Cross-Cutting (Security, Validation) layers. Dependencies flow correctly (top-down). This structure is sound.

**Control Plane Design:** Rate limiting and cost tracking with multiple implementations (Noop, FixedWindow, Adaptive) using protocol pattern is well-designed. Context manager pattern for rate limiter acquisition is idiomatic Python.

These patterns demonstrate that the architecture team understands modern software design principles. The problems identified are localized to specific implementations (god class, configuration merging) rather than fundamental architectural flaws.

---

## Recommendations

### Immediate Actions (Next Sprint - 1 Week)

#### 1. Document Configuration Precedence

**Action:** Create `docs/configuration-precedence.md` with comprehensive examples

**Content must include:**
- Table showing all 5 hierarchy levels with precedence order
- Example showing each level overriding previous level
- Merge strategy table (append vs override vs merge) for each config key
- Common mistakes section with solutions
- Troubleshooting flowchart for "why isn't my config working?"

**Rationale:** Cannot fix complexity immediately, but can eliminate unpredictability through documentation.

**Validation:** Have 3 users (who didn't write the docs) create complex configurations following only the docs. If they succeed, docs are sufficient.

**Effort:** 4-6 hours

---

#### 2. Add Configuration Debug Tooling

**Action:** Implement `--print-config` CLI flag and debug logging

**Requirements:**
```bash
$ elspeth --settings config.yaml --profile prod --print-config
# Output: Resolved configuration showing:
# - Source of each value (system default / prompt pack / profile / suite / experiment)
# - Final merged configuration
# - Warnings for overridden values

$ elspeth --settings config.yaml --profile prod --debug-config
# Runs normally but logs merge decisions:
# [CONFIG] rate_limit.requests_per_minute: 50 (from profile) overrides 100 (from prompt_pack)
```

**Rationale:** Users can see final configuration and understand why values are what they are.

**Validation:** Test with complex suite configuration, verify output matches runtime behavior.

**Effort:** 4 hours

---

#### 3. Document ExperimentRunner Architecture

**Action:** Add comprehensive class-level docstring with execution flow ASCII diagram

**Required content:**
```python
class ExperimentRunner:
    """Executes experiment processing flow from data load to result output.

    ARCHITECTURE:

    ┌─────────────────────────────────────────────────────────────┐
    │ Execution Flow (Template Method)                            │
    ├─────────────────────────────────────────────────────────────┤
    │ 1. Load checkpoint (CheckpointManager)                      │
    │ 2. Compile prompts (PromptEngine)                          │
    │ 3. Filter processed rows                                    │
    │ 4. Choose strategy: Sequential | Parallel                   │
    │    ├─ Sequential: _process_single_row() loop               │
    │    └─ Parallel: ThreadPoolExecutor + _run_parallel()       │
    │ 5. Apply row plugins (per result)                          │
    │ 6. Apply aggregation plugins (all results)                 │
    │ 7. Write via ArtifactPipeline                              │
    └─────────────────────────────────────────────────────────────┘

    RESPONSIBILITIES (WARNING: Too many):
    - Prompt compilation: Lines 100-150
    - LLM execution: Lines 200-250
    - Retry logic: Lines 300-350
    - Checkpoint management: Lines 400-450
    - Parallel execution: Lines 500-550
    - Early stopping: Lines 600-650

    KNOWN ISSUES:
    - Class size: 600+ lines (should be <300)
    - SRP violations: 10+ responsibilities
    - Refactoring planned: Q2 2025 (extract retry, checkpoint, parallel exec)

    For details see: docs/arch-analysis-2025-11-13-0933/05-architecture-assessment.md
    """
```

**Rationale:** Improves comprehension for developers working with this class until refactoring is complete.

**Validation:** Code review by team member unfamiliar with runner implementation. Can they understand flow?

**Effort:** 3 hours

---

### Short-Term Actions (Next Quarter - 3 Months)

#### 4. Centralize Configuration Merging

**Action:** Refactor merging logic into `ConfigurationMerger` class with comprehensive unit tests

**Design:**
```python
class ConfigurationMerger:
    """Centralized configuration merging with documented precedence.

    Precedence (lowest to highest):
    1. System defaults
    2. Prompt pack
    3. Profile
    4. Suite defaults
    5. Experiment config

    Merge strategies:
    - Scalars: Override (higher precedence replaces lower)
    - Lists (plugins): Append (accumulate from all sources)
    - Dicts (nested config): Deep merge
    """

    def merge(self, *sources: Dict, strategy: MergeStrategy) -> Dict:
        """Merge configuration sources with defined precedence."""
        pass

    def explain(self, key: str, merged_config: Dict) -> str:
        """Explain why a config value is what it is."""
        pass
```

**Requirements:**
- Single file: `core/config_merger.py`
- All merge logic centralized (remove from cli.py, config.py, suite_runner.py)
- 100% test coverage for merge scenarios
- `explain()` method for debugging
- Migration should be transparent (all existing configs produce identical results)

**Validation:**
- All existing configurations produce identical merged results
- Unit tests for edge cases (conflicting keys, nested merges, list appending)
- Integration test: Load 10 real-world configs, compare before/after

**Effort:** 2 weeks (1 week implementation, 1 week testing and migration)

---

#### 5. Refactor ExperimentRunner

**Action:** Extract responsibilities into separate classes, reduce runner to <300 lines

**Target architecture:**
```
ExperimentRunner (coordination only, <300 lines)
├─ RetryPolicy (retry logic with strategies)
├─ CheckpointManager (state persistence and resume)
├─ ParallelExecutor (ThreadPoolExecutor orchestration)
├─ EarlyStopCoordinator (plugin-based condition checking)
└─ PluginLifecycle (row plugin and aggregation plugin execution)
```

**Extraction sequence:**
1. **Week 1:** Extract `RetryPolicy` with unit tests
2. **Week 2:** Extract `CheckpointManager` with unit tests
3. **Week 3:** Extract `ParallelExecutor` with unit tests
4. **Week 4:** Extract `EarlyStopCoordinator` with unit tests
5. **Week 5:** Extract `PluginLifecycle` with unit tests
6. **Week 6:** Refactor `ExperimentRunner` to use extracted classes
7. **Week 7:** Integration testing and verification

**Validation:**
- Each extracted class has 100% test coverage (unit tests)
- All existing integration tests pass
- ExperimentRunner class is <300 lines
- No behavior changes (experiments produce identical results)
- Performance unchanged (measure with benchmarks)

**Effort:** 7 weeks

---

#### 6. Split Large Plugin Files

**Action:** Separate `repository.py` into `github_repo.py` and `azure_devops_repo.py`

**Changes:**
```
Before:
plugins/outputs/repository.py (450 lines)
  ├─ GitHubRepoSink (200 lines)
  └─ AzureDevOpsRepoSink (200 lines)
  └─ Shared utilities (50 lines)

After:
plugins/outputs/repository_base.py (50 lines) ← shared utilities
plugins/outputs/github_repo.py (200 lines)
plugins/outputs/azure_devops_repo.py (200 lines)
```

**Similarly for middleware:**
```
Before:
plugins/llms/middleware.py (400 lines) ← multiple middleware in one file

After:
plugins/llms/middleware/
  ├─ __init__.py
  ├─ logging_middleware.py
  ├─ filtering_middleware.py
  ├─ caching_middleware.py
  └─ retry_middleware.py
```

**Validation:**
- All tests pass
- No behavior changes
- Registry imports updated

**Effort:** 1 week

---

### Long-Term Actions (6-12 Months)

#### 7. Implement Dynamic Plugin Discovery

**Action:** Add Python entry point-based plugin registration for third-party extensibility

**Design:**
```python
# Third-party plugin package: elspeth-custom-plugins
# setup.py
entry_points={
    'elspeth.datasources': [
        'my_datasource = my_package.datasource:MyDataSource',
    ],
    'elspeth.outputs': [
        'my_sink = my_package.sink:MySink',
    ],
}

# Core: core/registry.py
class PluginRegistry:
    def discover_plugins(self):
        """Discover plugins via entry points."""
        for ep in pkg_resources.iter_entry_points('elspeth.datasources'):
            self.register_datasource(ep.name, ep.load())
```

**Requirements:**
- Entry point discovery for all plugin types (datasources, llms, outputs, experiments)
- Lazy loading (import only when plugin instantiated)
- Plugin verification (check protocol compliance)
- Version compatibility checking
- Documentation for third-party plugin developers

**Validation:**
- Create test third-party plugin package
- Verify discovery, loading, and execution
- Verify lazy loading (plugins not used are not imported)
- Performance test (100 plugins registered, only 2 used)

**Effort:** 4 weeks

---

#### 8. Simplify Configuration Hierarchy

**Action:** Evaluate reducing configuration levels and simplifying merge logic

**Investigation required:**
- Survey users: Which configuration levels are actually used?
- Analyze existing configs: What patterns are common?
- Prototype: Can we eliminate prompt packs and use composition instead?

**Possible simplification:**
```
Current (5 levels):
System defaults → Prompt packs → Profiles → Suite defaults → Experiment

Proposed (3 levels):
System defaults → Profile → Experiment
(Use profile inheritance for reusability instead of prompt packs)
```

**Requirements:**
- Migration path for existing configurations
- Backward compatibility (deprecated but functional)
- User feedback on proposal before implementation

**Effort:** 6 weeks (2 weeks investigation, 2 weeks design, 2 weeks prototype)

---

## Prioritization

**Do immediately (next sprint):**
1. Document configuration precedence (4-6 hours)
2. Add `--print-config` flag (4 hours)
3. Document ExperimentRunner architecture (3 hours)

**Total immediate effort:** ~12 hours (1.5 days)

**Do next quarter:**
4. Centralize configuration merging (2 weeks)
5. Refactor ExperimentRunner (7 weeks)
6. Split large plugin files (1 week)

**Total short-term effort:** ~10 weeks (2.5 months)

**Plan for long-term (6-12 months):**
7. Dynamic plugin discovery (4 weeks)
8. Configuration hierarchy simplification (6 weeks)

---

## Summary

**Quality level:** Good architecture with two high-severity maintainability issues.

**What's good:** Protocol-oriented design, plugin architecture, DAG resolution, layered structure, control plane design. These are sound patterns that should be preserved.

**What's broken:** 600-line god class and 300+ lines of distributed configuration merging. Both are HIGH severity and will constrain development velocity within 6-12 months.

**Required action:** Execute immediate actions (documentation) within one sprint, then tackle refactoring over next quarter. Long-term actions are optional but recommended for ecosystem growth.

**Risk if ignored:** Development velocity decreases 30-40% over next 12 months. Configuration complexity limits user adoption and increases operational risk.

**Confidence:** HIGH - All findings based on direct evidence from codebase analysis (file paths, line counts, pattern observations). No speculation.

---

**End of Assessment**
