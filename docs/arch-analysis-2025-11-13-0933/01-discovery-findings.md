# Discovery Findings - Holistic Assessment

**Analysis Date:** 2025-11-13
**Codebase:** elspeth-simple (DMP - Data/ML Platform)
**Total LOC:** ~9,283 Python lines
**Complexity:** Medium

## System Overview

**elspeth-simple** is a Python-based framework for orchestrating LLM (Large Language Model) experiments. The system loads input data, processes it through configurable LLM pipelines with middleware, applies plugins for metrics and transformations, and outputs results to various sinks (CSV, blob storage, repositories, etc.).

**Primary Use Case:** Running structured experiments on datasets using LLMs with configurable prompt templates, metrics collection, and result persistence.

**Key Characteristics:**
- Plugin-based extensibility architecture
- Protocol-driven interfaces (DataSource, LLMClientProtocol, ResultSink)
- Support for experiment suites with baseline comparisons
- Artifact dependency resolution between sinks
- Security level enforcement for data handling
- Rate limiting and cost tracking controls

## Directory Structure & Organization Pattern

**Organization Pattern:** Layered architecture with clear separation between core framework and plugins

```
elspeth-simple/
├── cli.py                    # CLI entry point
├── config.py                 # Configuration loader
├── __init__.py
├── core/                     # Core framework
│   ├── interfaces.py         # Protocol definitions
│   ├── registry.py           # Plugin factory registry
│   ├── orchestrator.py       # Main orchestration logic
│   ├── artifact_pipeline.py  # Sink dependency resolution
│   ├── artifacts.py          # Artifact type validation
│   ├── validation.py         # Config validation
│   ├── processing.py         # Data preparation utilities
│   ├── config_schema.py      # Configuration schemas
│   ├── experiments/          # Experiment execution engine
│   │   ├── runner.py         # Single experiment runner
│   │   ├── suite_runner.py   # Multi-experiment orchestration
│   │   ├── config.py         # Experiment config models
│   │   ├── plugins.py        # Experiment plugin protocols
│   │   └── plugin_registry.py # Experiment plugin factory
│   ├── llm/                  # LLM middleware system
│   │   ├── middleware.py     # Middleware protocol
│   │   └── registry.py       # Middleware factory
│   ├── prompts/              # Prompt template engine
│   │   ├── engine.py         # Template compiler
│   │   ├── template.py       # Template renderer
│   │   ├── loader.py         # Template loading
│   │   └── exceptions.py     # Prompt errors
│   ├── controls/             # Operational controls
│   │   ├── rate_limit.py     # Rate limiting
│   │   ├── cost_tracker.py   # Cost tracking
│   │   └── registry.py       # Control factories
│   └── security/             # Security features
│       └── signing.py        # Artifact signing
├── plugins/                  # Plugin implementations
│   ├── datasources/          # Data input plugins
│   │   ├── csv_local.py      # Local CSV loader
│   │   └── blob.py           # Azure Blob loader
│   ├── llms/                 # LLM client plugins
│   │   ├── azure_openai.py   # Azure OpenAI client
│   │   ├── mock.py           # Mock client for testing
│   │   ├── middleware.py     # Generic middleware impls
│   │   └── middleware_azure.py # Azure-specific middleware
│   ├── outputs/              # Result sink plugins
│   │   ├── csv_file.py       # CSV output
│   │   ├── excel.py          # Excel workbook output
│   │   ├── blob.py           # Azure Blob output
│   │   ├── local_bundle.py   # Local bundle output
│   │   ├── zip_bundle.py     # Zip archive output
│   │   ├── archive_bundle.py # Advanced bundling
│   │   ├── file_copy.py      # File copy sink
│   │   ├── repository.py     # GitHub/Azure DevOps sinks
│   │   ├── signed.py         # Signed artifact output
│   │   └── analytics_report.py # Analytics report generation
│   └── experiments/          # Experiment plugins
│       ├── metrics.py        # Metrics collection
│       └── early_stop.py     # Early stopping logic
└── datasources/              # (appears empty or legacy)
```

**Observations:**
- Clear separation of concerns: core framework vs plugins
- Core modules are cohesive and focused
- Plugin categories align with extension points (datasources, llms, outputs, experiments)

## Entry Points

### Primary Entry Point
**File:** `cli.py:main()`
**Line:** 360-367

**Flow:**
1. Parse CLI arguments (settings file, profile, output options)
2. Validate settings against schema (`validation.py`)
3. Load settings from YAML via `config.py`
4. Decide between single experiment or suite execution
5. For single: Create `ExperimentOrchestrator` and run
6. For suite: Load `ExperimentSuite` and use `ExperimentSuiteRunner`

### Configuration Entry Point
**File:** `config.py:load_settings()`
**Line:** 37-134

**Responsibilities:**
- Parse YAML configuration files
- Merge prompt packs with profile settings
- Instantiate plugins via registry
- Build `OrchestratorConfig` with all settings

### API/Library Entry Point
Not explicitly exposed. System appears designed primarily as CLI tool, but core components (`ExperimentOrchestrator`, `ExperimentRunner`) could be imported and used programmatically.

## Technology Stack

**Language:** Python 3.x (uses modern features like `from __future__ import annotations`, Protocol)

**Core Dependencies:**
- **pandas** - DataFrame-based data processing
- **PyYAML** - Configuration file parsing
- **Standard library:**
  - `concurrent.futures` - Parallel execution
  - `dataclasses` - Data models
  - `typing` - Type hints with Protocol
  - `logging` - Structured logging
  - `pathlib` - Path handling

**External Integrations:**
- Azure OpenAI API (for LLM calls)
- Azure Blob Storage (for data I/O)
- GitHub API (for repository sinks)
- Azure DevOps API (for repository sinks)

**Testing Framework:** Not visible in current scan (likely pytest based on Python conventions)

**Architectural Patterns:**
- Protocol-oriented design (PEP 544)
- Plugin/Registry pattern
- Pipeline pattern (artifact dependencies)
- Middleware pattern (LLM request/response)
- Factory pattern (plugin creation)

## Subsystem Identification

### 1. CLI & Configuration
**Location:** `cli.py`, `config.py`
**Responsibility:** Command-line interface, YAML configuration loading, settings validation, entry point orchestration
**Key Components:**
- `cli.py:main()` - CLI entry point
- `cli.py:build_parser()` - Argument parsing
- `config.py:load_settings()` - Configuration loader
- `config.py:Settings` - Settings data model
**Confidence:** HIGH

### 2. Core Orchestration
**Location:** `core/orchestrator.py`, `core/experiments/runner.py`
**Responsibility:** Main experiment execution flow, coordinates datasource → LLM → sinks pipeline
**Key Components:**
- `orchestrator.py:ExperimentOrchestrator` - High-level orchestrator
- `orchestrator.py:OrchestratorConfig` - Configuration model
- `experiments/runner.py:ExperimentRunner` - Low-level execution engine
- `experiments/runner.py:run()` - Main execution loop with retry, checkpointing, concurrency
**Dependencies:** Registry, LLM clients, datasources, sinks, controls, artifact pipeline
**Confidence:** HIGH

### 3. Plugin Registry System
**Location:** `core/registry.py`, `core/interfaces.py`
**Responsibility:** Plugin discovery, instantiation, validation via factory pattern
**Key Components:**
- `registry.py:PluginRegistry` - Central registry with factory methods
- `registry.py:PluginFactory` - Factory with schema validation
- `interfaces.py:DataSource` - Protocol for data sources
- `interfaces.py:LLMClientProtocol` - Protocol for LLM clients
- `interfaces.py:ResultSink` - Protocol for result sinks
**Registered Plugins:**
- Datasources: `azure_blob`, `local_csv`
- LLMs: `azure_openai`, `mock`
- Sinks: `azure_blob`, `csv`, `local_bundle`, `excel_workbook`, `zip_bundle`, `file_copy`, `github_repo`, `azure_devops_repo`, `signed_artifact`, `analytics_report`
**Confidence:** HIGH

### 4. Experiment Framework
**Location:** `core/experiments/`
**Responsibility:** Experiment suite management, plugin execution (row/aggregation/baseline/early-stop), experiment configuration
**Key Components:**
- `suite_runner.py:ExperimentSuiteRunner` - Runs multiple experiments
- `config.py:ExperimentSuite` - Suite configuration model
- `config.py:ExperimentConfig` - Single experiment config
- `plugins.py:RowExperimentPlugin` - Per-row plugin protocol
- `plugins.py:AggregationExperimentPlugin` - Aggregation plugin protocol
- `plugins.py:EarlyStopPlugin` - Early stopping plugin protocol
- `plugin_registry.py` - Experiment plugin factories
**Confidence:** HIGH

### 5. Artifact Pipeline
**Location:** `core/artifact_pipeline.py`, `core/artifacts.py`
**Responsibility:** Dependency resolution between sinks, artifact passing, security level enforcement
**Key Components:**
- `artifact_pipeline.py:ArtifactPipeline` - Topological sort and execution orchestration
- `artifact_pipeline.py:SinkBinding` - Sink wrapper with metadata
- `artifact_pipeline.py:ArtifactStore` - Artifact storage and lookup
- `artifacts.py` - Artifact type validation
**Patterns:** Directed Acyclic Graph (DAG) resolution for sink dependencies
**Confidence:** HIGH

### 6. LLM Middleware System
**Location:** `core/llm/`, `plugins/llms/`
**Responsibility:** Request/response transformation, content filtering, logging, retries
**Key Components:**
- `core/llm/middleware.py:LLMMiddleware` - Middleware protocol
- `core/llm/middleware.py:LLMRequest` - Request wrapper
- `core/llm/registry.py:create_middlewares()` - Middleware factory
- `plugins/llms/azure_openai.py:AzureOpenAIClient` - Azure OpenAI implementation
- `plugins/llms/middleware.py` - Generic middleware implementations
- `plugins/llms/middleware_azure.py` - Azure-specific middleware
**Confidence:** HIGH

### 7. Prompt Engine
**Location:** `core/prompts/`
**Responsibility:** Template compilation, rendering with variable substitution, validation
**Key Components:**
- `engine.py:PromptEngine` - Template compiler
- `template.py:PromptTemplate` - Rendered template
- `loader.py` - Template file loading
- `exceptions.py` - Prompt-specific errors
**Features:** Jinja2-like templating, defaults, field extraction
**Confidence:** HIGH

### 8. Control Plane
**Location:** `core/controls/`
**Responsibility:** Rate limiting, cost tracking, resource management
**Key Components:**
- `rate_limit.py:RateLimiter` - Rate limiting implementation
- `cost_tracker.py:CostTracker` - Cost tracking implementation
- `registry.py:create_rate_limiter()` - Rate limiter factory
- `registry.py:create_cost_tracker()` - Cost tracker factory
**Confidence:** HIGH

### 9. Security Layer
**Location:** `core/security/`
**Responsibility:** Data signing, security level normalization and enforcement
**Key Components:**
- `signing.py` - Artifact signing with HMAC
- `__init__.py:normalize_security_level()` - Security level parsing
- `__init__.py:resolve_security_level()` - Security level resolution
**Confidence:** MEDIUM (smaller subsystem, may be part of broader security story)

### 10. Validation System
**Location:** `core/validation.py`, `core/config_schema.py`
**Responsibility:** Configuration validation, schema enforcement, error reporting
**Key Components:**
- `validation.py:validate_settings()` - Settings validation
- `validation.py:validate_suite()` - Suite validation
- `validation.py:validate_schema()` - JSON schema validation
- `config_schema.py` - Configuration schemas
**Confidence:** HIGH

### 11. Plugin Implementations
**Location:** `plugins/`
**Responsibility:** Concrete implementations of datasources, LLMs, outputs, experiment plugins
**Subcategories:**
- **Datasources** (`plugins/datasources/`): CSV local, Azure Blob
- **LLMs** (`plugins/llms/`): Azure OpenAI, Mock, Middleware implementations
- **Outputs** (`plugins/outputs/`): 11 different sink types (CSV, Excel, Blob, ZIP, GitHub, Azure DevOps, etc.)
- **Experiments** (`plugins/experiments/`): Metrics, Early stopping
**Confidence:** HIGH

## Architectural Patterns

### 1. Protocol-Oriented Design
All plugin extension points use Python Protocols (PEP 544) for structural typing:
- `DataSource.load() -> pd.DataFrame`
- `LLMClientProtocol.generate(...) -> Dict`
- `ResultSink.write(...) -> None`

**Benefits:** Duck typing, flexible plugin implementation, clear contracts

### 2. Registry/Factory Pattern
`PluginRegistry` maintains mappings from plugin names to factory functions with schema validation.

**Flow:** `config.yaml` → `load_settings()` → `registry.create_X(name, options)` → Validated plugin instance

### 3. Pipeline/DAG Pattern
Artifact dependencies form a DAG, topologically sorted for execution order.

**Example:** Sink A produces artifact X → Sink B consumes X → Sink C consumes X → Execution order: A, then B & C in parallel

### 4. Middleware/Chain of Responsibility
LLM requests pass through middleware chain for transformation, logging, filtering.

**Flow:** Request → Middleware 1 → Middleware 2 → ... → LLM Client → ... → Middleware 2 → Middleware 1 → Response

### 5. Template Method
`ExperimentRunner.run()` defines the template flow:
1. Load checkpoint (if enabled)
2. Compile prompt templates
3. Process rows (sequential or parallel)
4. Apply row plugins
5. Call LLM via middleware chain
6. Apply aggregation plugins
7. Write to sinks via artifact pipeline

### 6. Strategy Pattern
Concurrency strategy, retry strategy, early stop strategy all configurable via plugin definitions.

## Key Dependencies & Data Flow

### Primary Data Flow

```
1. CLI Entry Point (cli.py)
     ↓
2. Configuration Loading (config.py)
     ↓
3. Plugin Instantiation (registry.py)
     ↓
4. Orchestrator Creation (orchestrator.py)
     ↓
5. Data Loading (DataSource plugin)
     ↓
6. Experiment Execution (ExperimentRunner)
     ├─→ Prompt Compilation (prompts/engine.py)
     ├─→ Row Processing Loop
     │    ├─→ Row Plugins (experiments/plugins.py)
     │    ├─→ LLM Call via Middleware (llm/middleware.py)
     │    └─→ Checkpointing
     ├─→ Aggregation Plugins
     └─→ Baseline Comparison (if suite)
     ↓
7. Result Writing (artifact_pipeline.py)
     ├─→ Topological Sort of Sinks
     ├─→ Artifact Production
     ├─→ Artifact Consumption
     └─→ Finalization
     ↓
8. Output Artifacts (ResultSink plugins)
```

### Module Dependencies

**Core → Core:** Internal dependencies are well-structured
- `orchestrator` depends on `experiments/runner`, `registry`, `controls`, `llm/registry`
- `experiments/runner` depends on `interfaces`, `prompts`, `llm/middleware`, `controls`, `artifact_pipeline`
- `artifact_pipeline` depends on `interfaces`, `artifacts`, `security`

**Core → Plugins:** Core imports plugin implementations only in `registry.py` (centralized)
- `registry.py` imports all plugin classes for factory registration
- Other core modules depend only on protocols, not concrete implementations

**Plugins → Core:** Plugins import interfaces and utilities from core
- Plugin implementations import `interfaces.py` for protocol definitions
- Some plugins use `security`, `validation`, `artifacts` utilities

**Configuration:** Uses YAML with profile-based selection and prompt pack merging

## Plugin Ecosystem

### Datasource Plugins (2)
1. **local_csv** - Load CSV from local filesystem
2. **azure_blob** - Load CSV/data from Azure Blob Storage

### LLM Plugins (2 + middleware)
1. **azure_openai** - Azure OpenAI API client
2. **mock** - Mock client for testing
3. **Middleware implementations** - Generic and Azure-specific

### Output/Sink Plugins (10)
1. **csv** - Write results to CSV file
2. **excel_workbook** - Write to Excel with multiple sheets
3. **azure_blob** - Upload to Azure Blob Storage
4. **local_bundle** - Create local directory bundle
5. **zip_bundle** - Create ZIP archive with results
6. **archive_bundle** - Advanced bundling with metadata
7. **file_copy** - Copy artifacts to destination
8. **github_repo** - Commit results to GitHub repository
9. **azure_devops_repo** - Commit to Azure DevOps repository
10. **signed_artifact** - Sign and bundle artifacts with HMAC
11. **analytics_report** - Generate analytics reports (JSON/Markdown)

### Experiment Plugins (2 visible)
1. **metrics** - Extract and compute metrics from LLM responses
2. **early_stop** - Implement early stopping conditions

## Observations & Insights

### Strengths
- **Clean architecture** with clear layer separation
- **Extensibility** via protocol-based plugins
- **Type safety** with extensive use of type hints and protocols
- **Configurability** via YAML with validation
- **Security-aware** with security levels and artifact signing
- **Production-ready features**: checkpointing, retries, rate limiting, cost tracking

### Potential Complexity Areas
- **Configuration merging** (profiles, prompt packs, suite defaults) has complex precedence rules in `config.py` and `suite_runner.py`
- **Artifact pipeline** topological sort and security level enforcement adds complexity
- **Prompt template compilation** with defaults and field extraction
- **Middleware chain** execution order and error handling

### Missing/Unclear Areas
- **Testing infrastructure** not visible (may exist outside scanned files)
- **Documentation** minimal (only README.md visible)
- **Plugin discovery** is static (hardcoded in registry), no dynamic loading
- **Error handling** strategies not fully clear from high-level scan

## Subsystem Summary

**Identified Subsystems: 11**

1. CLI & Configuration
2. Core Orchestration
3. Plugin Registry System
4. Experiment Framework
5. Artifact Pipeline
6. LLM Middleware System
7. Prompt Engine
8. Control Plane
9. Security Layer
10. Validation System
11. Plugin Implementations (with 4 subcategories)

**Recommendation for Detailed Analysis:**
Focus on subsystems 2-7 as they form the core execution path. Subsystems 1, 8-11 are supporting infrastructure.
