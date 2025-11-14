# Holistic Assessment - Discovery Findings

**Analysis Date:** 2025-11-14 12:01
**Workspace:** docs/arch-analysis-2025-11-14-1201/
**Analyst:** Claude (System Archaeologist)

---

## Executive Summary

el speth-simple is a Python-based **Sense/Decide/Act (SDA) orchestration framework** for running LLM-powered data transformation and decision-making workflows. The system has recently undergone significant architectural refactoring, introducing:
- New orchestration layer with pluggable strategies (StandardOrchestrator, ExperimentalOrchestrator)
- Centralized configuration merging system (ConfigurationMerger)
- Enhanced CLI with configuration debugging capabilities
- Formalized SDA terminology throughout codebase

**Codebase Stats:**
- **61 Python files** totaling **~10,338 LOC**
- **11 major subsystems** (1 new since prior analysis)
- **Recent architectural changes:** 5 major refactorings in past 24 hours

**Architecture Maturity:** High - Protocol-oriented design, extensive plugin system, production controls (rate limiting, cost tracking, security)

---

## Entry Points

### Primary Entry Point
- **Script:** `elspeth = "elspeth.cli:main"` (defined in pyproject.toml)
- **Module:** `src/elspeth/cli.py:main()` function
- **Invocation:** `elspeth --settings config/settings.yaml [options]`

### CLI Capabilities (Recent Enhancements)
The CLI has been significantly enhanced with debugging features:

**Execution Modes:**
- `--settings PATH` - Path to YAML configuration file
- `--profile NAME` - Profile selection (default, production, dev, etc.)
- `--suite-root PATH` - Run experiment suite vs single run
- `--single-run` - Force single execution even if suite configured

**New Debugging Features (Added Nov 13, 2025):**
- `--print-config` - Print resolved configuration and exit (no execution)
- `--explain-config KEY` - Explain source of specific config key (e.g., 'rate_limiter' or 'llm.options.temperature')

**Operational Controls:**
- `--disable-metrics` - Disable metrics/statistical plugins
- `--live-outputs` - Enable live writes to remote sinks (disables dry-run)
- `--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}` - Logging verbosity

**Output Options:**
- `--head N` - Preview N rows of results
- `--output-csv PATH` - Save results to CSV file

### Configuration Loading Flow
```
main()
  → load_settings(settings_path, profile)
    → YAML parsing with profile selection
    → Prompt pack merging (if configured)
    → ConfigurationMerger for multi-source merging [NEW]
  → validate_settings(args.settings, profile)
  → Delegation to run strategy:
    → _run_single() for single experiments
    → _run_suite() for experiment suites
```

---

## Technology Stack

### Language & Runtime
- **Python 3.13** (requires-python = ">=3.13")
- Modern Python features:
  - `from __future__ import annotations` (PEP 563)
  - Protocol-based structural typing (PEP 544)
  - Dataclasses for configuration models
  - Type hints throughout

### Core Dependencies
**Data Processing:**
- `pandas>=2.2.0` - DataFrame-based data handling
- `numpy>=1.26.0` - Numerical operations (via pandas)

**Configuration & Templates:**
- `pyyaml>=6.0.1` - YAML configuration parsing
- `jinja2>=3.1.3` - Prompt template engine

**LLM Integration:**
- `openai>=1.12.0` - OpenAI/Azure OpenAI client
- `requests>=2.31.0` - HTTP requests for API calls

**Cloud Storage:**
- `azure-storage-blob>=12.19.0` - Azure Blob Storage integration
- `azure-identity>=1.15.0` - Azure authentication

### Development Tools
- `ruff>=0.3.0` - Linting and formatting
- `mypy>=1.9.0` - Static type checking
- `pytest>=8.0.0` - Testing framework
- `pytest-cov>=4.1.0` - Code coverage
- `pytest-asyncio>=0.23.0` - Async test support

### Architectural Patterns
- **Protocol-oriented design** - PEP 544 structural typing for plugin contracts
- **Registry/Factory pattern** - Centralized plugin management
- **Middleware chain** - LLM request/response transformation
- **DAG resolution** - Topological sort for artifact dependencies
- **Strategy pattern** - Pluggable orchestration strategies [NEW]
- **Template method** - SDA cycle execution flow

---

## Directory Structure

### Top-Level Organization
```
/home/john/elspeth-simple/
├── src/elspeth/              # Main source code (src layout migration complete)
│   ├── cli.py                # Command-line entry point
│   ├── config.py             # Configuration loading and Settings model
│   ├── core/                 # Core framework subsystems
│   ├── orchestrators/        # Orchestration strategies [NEW SUBSYSTEM]
│   ├── plugins/              # Plugin implementations
│   └── datasources/          # Data source implementations
├── tests/                    # Test suite
│   └── core/                 # Core subsystem tests
├── docs/                     # Documentation
│   ├── architecture/         # Architecture documentation (prior analysis)
│   ├── plans/                # Implementation plans
│   └── configuration-precedence.md  # Config merging guide [NEW DOC]
├── example/                  # Example configurations
│   ├── simple/               # Simple example
│   ├── complex/              # Complex example
│   └── experimental/         # Experimental features (A/B testing) [NEW]
└── pyproject.toml            # Project metadata and dependencies
```

### Core Subsystems (`src/elspeth/core/`)
```
core/
├── artifact_pipeline.py      # Artifact dependency resolution (DAG)
├── artifacts.py              # Artifact models and validation
├── config_merger.py          # Centralized configuration merging [NEW - 211 lines]
├── config_schema.py          # JSON schema definitions
├── interfaces.py             # Protocol definitions (DataSource, LLMClient, ResultSink)
├── orchestrator.py           # High-level orchestration facade
├── processing.py             # Processing utilities
├── registry.py               # Plugin factory registry (17KB, 396 lines)
├── validation.py             # Configuration and schema validation (23KB, 600+ lines)
├── controls/                 # Rate limiting and cost tracking
│   ├── cost_tracker.py       # Cost tracking implementations
│   ├── rate_limit.py         # Rate limiter implementations
│   └── registry.py           # Control plane registry
├── llm/                      # LLM middleware system
│   ├── middleware.py         # Middleware protocol and base
│   └── registry.py           # Middleware factory
├── prompts/                  # Prompt engine
│   ├── engine.py             # Jinja2 template compiler
│   ├── template.py           # Template wrapper
│   ├── loader.py             # Template file loading
│   └── exceptions.py         # Prompt-specific exceptions
├── sda/                      # Sense/Decide/Act cycle orchestration [RENAMED]
│   ├── __init__.py           # Exports SDASuite, SDARunner, SDACycleConfig
│   ├── config.py             # SDA cycle configuration models
│   ├── runner.py             # SDA cycle runner (execution engine)
│   ├── suite_runner.py       # DEPRECATED: Use orchestrators instead
│   ├── plugins.py            # SDA plugin protocols
│   └── plugin_registry.py    # SDA plugin factory
└── security/                 # Security and signing
    ├── signing.py            # HMAC signature generation/verification
    └── __init__.py           # Security level normalization
```

### New Orchestrators Subsystem (`src/elspeth/orchestrators/`)
```
orchestrators/                # [NEW SUBSYSTEM - Nov 13, 2025]
├── __init__.py               # Exports StandardOrchestrator, ExperimentalOrchestrator
├── standard.py               # Simple sequential execution (303 lines)
└── experimental.py           # A/B testing with baseline comparison (217 lines)
```

**Purpose:** Pluggable orchestration strategies for different SDA cycle execution patterns.

**Strategies:**
1. **StandardOrchestrator** - Simple sequential execution of multiple cycles
2. **ExperimentalOrchestrator** - A/B testing with baseline comparison and statistical analysis

**Migration:** Replaces deprecated `SDASuiteRunner` with clearer separation of concerns.

### Plugin Implementations (`src/elspeth/plugins/`)
```
plugins/
├── datasources/              # Data source plugins (2 implementations)
│   ├── blob.py               # Azure Blob Storage loader
│   └── csv_local.py          # Local CSV file loader
├── llms/                     # LLM client plugins (5 implementations)
│   ├── azure_openai.py       # Azure OpenAI client
│   ├── middleware.py         # Generic middleware implementations (400 lines)
│   ├── middleware_azure.py   # Azure-specific middleware (440 lines)
│   ├── mock.py               # Mock LLM for testing
│   └── openrouter.py         # OpenRouter API client
├── outputs/                  # Result sink plugins (10 implementations)
│   ├── analytics_report.py   # Analytics report generator (7.3KB)
│   ├── archive_bundle.py     # Archive bundler (11.4KB)
│   ├── blob.py               # Azure Blob uploader (13.6KB)
│   ├── csv_file.py           # CSV file writer (3.2KB)
│   ├── excel.py              # Excel workbook generator (7.8KB)
│   ├── file_copy.py          # File copy sink (4KB)
│   ├── local_bundle.py       # Local directory bundler (3.5KB)
│   ├── repository.py         # GitHub/Azure DevOps sinks (12.5KB)
│   ├── signed.py             # HMAC signed artifact bundler (4.5KB)
│   └── zip_bundle.py         # ZIP archive creator (8.6KB)
└── transforms/               # Transform plugins (2 implementations)
    ├── early_stop.py         # Early stopping conditions (4KB)
    └── metrics.py            # Metrics extraction (57KB - largest plugin)
```

---

## Subsystem Identification

Based on directory structure, cohesion analysis, and architectural boundaries, I've identified **12 major subsystems** (1 new since prior analysis):

### 1. **CLI & Configuration**
- **Location:** `cli.py` (509 lines), `config.py` (134 lines)
- **New features:** `--print-config`, `--explain-config` CLI flags
- **Dependencies:** ConfigurationMerger [NEW], Validation, Orchestrators

### 2. **Configuration Merger** [NEW SUBSYSTEM]
- **Location:** `core/config_merger.py` (211 lines)
- **Responsibility:** Centralized configuration merging with documented precedence
- **Key Features:**
  - Three merge strategies: OVERRIDE, APPEND, DEEP_MERGE
  - Merge trace for debugging
  - `explain()` method for configuration provenance
- **Addresses:** Prior concern about "Configuration Complexity and Merging Logic"

### 3. **Orchestration Strategies** [NEW SUBSYSTEM]
- **Location:** `orchestrators/` (520 lines total)
- **Implementations:**
  - StandardOrchestrator (303 lines) - Sequential execution
  - ExperimentalOrchestrator (217 lines) - A/B testing with baseline
- **Migration:** Replaces deprecated SDASuiteRunner

### 4. **SDA Core** (formerly "Experiment Framework")
- **Location:** `core/sda/` (~1200 lines)
- **Renamed from:** Experiment terminology → Sense/Decide/Act terminology
- **Components:**
  - SDACycleConfig - Cycle configuration
  - SDARunner - Cycle execution engine
  - SDASuite - Suite configuration
  - SDASuiteRunner - DEPRECATED (use Orchestrators instead)

### 5. **Core Orchestrator** (Facade)
- **Location:** `core/orchestrator.py` (100 lines)
- **Responsibility:** High-level coordination facade
- **Delegates to:** SDARunner or Orchestrators

### 6. **Plugin Registry System**
- **Location:** `core/registry.py` (396 lines), `core/interfaces.py` (56 lines)
- **No major changes since prior analysis**

### 7. **Artifact Pipeline**
- **Location:** `core/artifact_pipeline.py` (400+ lines)
- **No major changes since prior analysis**

### 8. **LLM Middleware System**
- **Location:** `core/llm/` + `plugins/llms/middleware*.py`
- **No major changes since prior analysis**

### 9. **Prompt Engine**
- **Location:** `core/prompts/`
- **No major changes since prior analysis**

### 10. **Control Plane**
- **Location:** `core/controls/`
- **No major changes since prior analysis**

### 11. **Security Layer**
- **Location:** `core/security/`
- **No major changes since prior analysis**

### 12. **Validation System**
- **Location:** `core/validation.py` (23KB, 600+ lines)
- **No major changes since prior analysis**

### 13. **Plugin Implementations**
- **Location:** `plugins/`
- **No major structural changes, but metrics.py remains large (57KB)**

**Total:** 12 subsystems (2 new: ConfigurationMerger, Orchestration Strategies)

---

## Changes Since Prior Analysis (Nov 13, 2025)

The codebase underwent **major architectural refactoring** between the prior analysis (Nov 13 AM) and current state (Nov 14):

### 1. New Orchestration Layer (Commit e53a97b)
**Impact:** HIGH - New architectural layer

**Changes:**
- Created `src/elspeth/orchestrators/` package
- StandardOrchestrator (303 lines) - Simple sequential execution
- ExperimentalOrchestrator (217 lines) - A/B testing with baseline comparison
- Deprecated `SDASuiteRunner` in favor of orchestrators

**Rationale:** Clearer separation between:
- **SDA cycle execution** (core/sda/) - Single cycle operations
- **Orchestration strategies** (orchestrators/) - Multi-cycle coordination

**Example configurations added:**
- `example/experimental/` - A/B testing examples with baseline/variant cycles

### 2. Centralized Configuration Merging (Multiple commits)
**Impact:** HIGH - Addresses major technical concern

**Changes:**
- New `ConfigurationMerger` class in `core/config_merger.py` (211 lines)
- Documented merge strategies (OVERRIDE, APPEND, DEEP_MERGE)
- Merge trace for debugging configuration provenance
- `explain()` method for understanding config resolution

**Migration:**
- `config.py` refactored to use ConfigurationMerger
- `cli.py` suite defaults migrated to ConfigurationMerger
- `sda/suite_runner.py` refactored to use ConfigurationMerger

**Tests added:**
- `tests/core/test_config_merger.py` (340 lines of integration tests)

**Documentation added:**
- `docs/configuration-precedence.md` (285 lines) - Comprehensive guide

**Addresses:** Prior architecture concern "Configuration Complexity and Merging Logic"

### 3. CLI Configuration Debugging (Commit 2c5d150)
**Impact:** MEDIUM - Improved developer experience

**Changes:**
- `--print-config` flag - Print resolved configuration and exit
- `--explain-config KEY` flag - Explain source of specific config key
- Enables debugging complex multi-source configurations

**Implementation:**
- `cli.py:_print_configuration()` function (95 new lines)

### 4. SDA Terminology Standardization (Commit 73813a4)
**Impact:** MEDIUM - Naming consistency

**Changes:**
- Renamed from "experiment" to "Sense/Decide/Act" (SDA) terminology
- `ExperimentSuite` → `SDASuite`
- `ExperimentRunner` → `SDARunner`
- `ExperimentConfig` → `SDACycleConfig`

**Scope:** Comprehensive rename across codebase, docs, and examples

### 5. Implementation Plans Documented (Commit 4d44753)
**Impact:** LOW - Documentation

**New documentation:**
- `docs/plans/2025-11-13-centralize-config-merging.md` (1545 lines)
- `docs/plans/2025-11-13-refactor-runner-god-class.md` (848 lines)

**Content:** Detailed implementation plans for refactorings (some already completed)

---

## Initial Architectural Observations

### Strengths Maintained
1. **Protocol-oriented design** - Clean abstraction via PEP 544 protocols
2. **Plugin extensibility** - 22 plugin implementations across 4 categories
3. **Production controls** - Rate limiting, cost tracking, security, validation
4. **Comprehensive testing** - pytest with coverage, async support

### New Strengths
5. **Centralized configuration** - ConfigurationMerger addresses prior complexity concern
6. **Pluggable orchestration** - Strategy pattern for different execution modes
7. **Configuration debugging** - `--print-config` and `--explain-config` improve DX
8. **Clear terminology** - SDA nomenclature more domain-appropriate than "experiment"

### Areas Requiring Investigation
1. **SDARunner complexity** - Prior concern about "god class" (600+ lines)
   - Check if refactoring plan (`docs/plans/2025-11-13-refactor-runner-god-class.md`) has been executed
2. **Large plugin files** - metrics.py (57KB), middleware files (400-440 lines)
3. **Orchestrator relationship** - How do StandardOrchestrator and ExperimentalOrchestrator relate to SDARunner?
4. **Migration path** - Is SDASuiteRunner truly deprecated or still used?
5. **Test coverage** - Does ConfigurationMerger refactoring have adequate tests?

### Architectural Evolution Summary
The system has evolved from:
- **Before:** Monolithic configuration merging, single suite runner, experiment terminology
- **After:** Pluggable orchestration strategies, centralized config merging, SDA terminology, enhanced debugging

This represents **significant architectural maturity improvement** in a short timeframe.

---

## Recommended Subsystem Analysis Approach

### Parallel Analysis Strategy
Given:
- 12 subsystems total
- 2 new/changed subsystems requiring deep analysis
- 10 existing subsystems with prior documentation available

**Proposed approach:**
1. **New subsystems** (deep analysis via subagents):
   - ConfigurationMerger - Analyze merge strategies, trace logic, integration
   - Orchestration Strategies - Analyze StandardOrchestrator vs ExperimentalOrchestrator

2. **Changed subsystems** (update analysis):
   - CLI & Configuration - Document new flags, integration with ConfigurationMerger
   - SDA Core - Document renaming, deprecation of SDASuiteRunner

3. **Unchanged subsystems** (verify prior analysis still accurate):
   - Plugin Registry, Artifact Pipeline, LLM Middleware, Prompt Engine, Controls, Security, Validation, Plugin Implementations

**Parallelization:**
- Spawn 4 parallel subagents:
  - Subagent 1: ConfigurationMerger (new)
  - Subagent 2: Orchestration Strategies (new)
  - Subagent 3: CLI & SDA Core (changed)
  - Subagent 4: Verify unchanged subsystems against prior docs

**Estimated time:**
- Sequential: ~3 hours
- Parallel: ~1 hour

---

## Next Steps

1. **Finalize orchestration strategy** - Parallel with 4 subagents (documented above)
2. **Create task specifications** - Write `temp/task-*.md` for each subagent
3. **Spawn parallel subagents** - Execute subsystem analysis
4. **Validate catalog** - Systematic validation against contract
5. **Generate diagrams** - C4 diagrams reflecting new architecture
6. **Synthesize final report** - Comprehensive architecture documentation

---

**Confidence:** High - Based on systematic file reading, git log analysis, and comparison to prior documentation

**Analysis Time:** 25 minutes

**Status:** Holistic assessment complete, ready for subsystem analysis phase
