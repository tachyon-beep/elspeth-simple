# Subsystem Catalog

This catalog documents all major subsystems identified in the elspeth-simple codebase.

## CLI & Configuration

**Location:** `cli.py`, `config.py`

**Responsibility:** Provides command-line interface for experiment execution and loads YAML-based configuration with profile and prompt pack merging.

**Key Components:**
- `cli.py:main()` - CLI entry point that parses arguments and delegates to single or suite runners (367 lines)
- `cli.py:build_parser()` - Argument parser setup with settings path, profile, output options (77 lines)
- `config.py:load_settings()` - Configuration loader that merges profiles and prompt packs into Settings object (134 lines)
- `config.py:Settings` - Data model containing datasource, LLM, sinks, orchestrator config, and suite settings (29 lines)

**Dependencies:**
- Inbound: None (system entry point)
- Outbound: Core Orchestration, Plugin Registry System, Validation System, Experiment Framework

**Patterns Observed:**
- Profile-based configuration with default fallback
- Prompt pack merging with precedence rules (pack → profile → suite defaults)
- Builder pattern for constructing complex settings objects
- Validation-first approach (validate before instantiation)

**Concerns:**
- Complex configuration merging logic spread across multiple functions in cli.py (lines 204-358)
- Precedence rules for prompt packs, suite defaults, and profile settings not well-documented

**Confidence:** High - Clear entry points, comprehensive argument parsing, verified configuration loading flow

---

## Core Orchestration

**Location:** `core/orchestrator.py`, `core/experiments/runner.py`

**Responsibility:** Orchestrates the main experiment execution flow from data loading through LLM processing to result output.

**Key Components:**
- `orchestrator.py:ExperimentOrchestrator` - High-level orchestrator that coordinates datasource, LLM, and sinks (100 lines)
- `orchestrator.py:OrchestratorConfig` - Configuration dataclass with all orchestration parameters (35 lines)
- `experiments/runner.py:ExperimentRunner` - Low-level runner handling row processing, retries, checkpointing, concurrency (600+ lines)
- `experiments/runner.py:run()` - Main execution loop with early stopping, parallel processing support (150+ lines)

**Dependencies:**
- Inbound: CLI & Configuration, Experiment Framework (suite runner)
- Outbound: Plugin Registry System, LLM Middleware System, Prompt Engine, Control Plane, Artifact Pipeline, Experiment Framework (plugins)

**Patterns Observed:**
- Template method pattern in runner execution flow
- Strategy pattern for concurrency (sequential vs parallel execution)
- Checkpoint/resume pattern for long-running experiments
- ThreadPoolExecutor for parallel row processing

**Concerns:**
- ExperimentRunner class is large (600+ lines) with many responsibilities (prompts, retries, checkpointing, concurrency, early stopping)
- Complexity in parallel execution error handling and state management

**Confidence:** High - Core execution path verified through file reads, clear orchestration responsibilities

---

## Plugin Registry System

**Location:** `core/registry.py`, `core/interfaces.py`

**Responsibility:** Centralized plugin factory registry that validates and instantiates datasource, LLM, and sink plugins with schema enforcement.

**Key Components:**
- `registry.py:PluginRegistry` - Main registry with factory methods for all plugin types (396 lines)
- `registry.py:PluginFactory` - Factory wrapper with JSON schema validation (83 lines)
- `interfaces.py:DataSource` - Protocol defining load() → DataFrame contract (16 lines)
- `interfaces.py:LLMClientProtocol` - Protocol defining generate() contract (31 lines)
- `interfaces.py:ResultSink` - Protocol defining write() and artifact methods (54 lines)

**Dependencies:**
- Inbound: CLI & Configuration, Core Orchestration, Experiment Framework
- Outbound: Plugin Implementations, Validation System

**Patterns Observed:**
- Registry/Factory pattern with centralized plugin mappings
- Protocol-oriented design (PEP 544) for plugin contracts
- JSON schema validation before instantiation
- Lazy imports (plugins imported only in registry, not throughout core)

**Concerns:**
- Plugin registry is static (hardcoded mappings), no dynamic plugin discovery
- Schema definitions embedded in registry code rather than separate schema files

**Confidence:** High - Verified all plugin registrations and factory methods, clear protocol definitions

---

## Experiment Framework

**Location:** `core/experiments/`

**Responsibility:** Manages experiment suites, coordinates multiple experiment runs, and provides plugin extension points for row processing, aggregation, baseline comparison, and early stopping.

**Key Components:**
- `suite_runner.py:ExperimentSuiteRunner` - Orchestrates multiple experiments with shared configuration (280 lines)
- `config.py:ExperimentSuite` - Suite configuration model with experiments list (150 lines)
- `config.py:ExperimentConfig` - Single experiment configuration (100 lines)
- `plugins.py` - Protocol definitions for RowExperimentPlugin, AggregationExperimentPlugin, BaselineComparisonPlugin, EarlyStopPlugin (45 lines)
- `plugin_registry.py` - Experiment plugin factory registry with validation (269 lines)

**Dependencies:**
- Inbound: CLI & Configuration, Core Orchestration
- Outbound: Plugin Implementations (experiments), Core Orchestration (runner), LLM Middleware System, Control Plane

**Patterns Observed:**
- Suite-level configuration inheritance with per-experiment overrides
- Plugin protocol pattern for extensible experiment behaviors
- Builder pattern for constructing runners with merged configurations
- Baseline comparison pattern for A/B testing

**Concerns:**
- Configuration merging complexity between suite defaults, prompt packs, and experiment configs (suite_runner.py lines 34-100)
- Early stop plugin normalization logic is complex with multiple input formats

**Confidence:** High - Verified suite loading, experiment configuration, and plugin protocols through file reads

---

## Artifact Pipeline

**Location:** `core/artifact_pipeline.py`, `core/artifacts.py`

**Responsibility:** Resolves dependencies between result sinks using topological sorting and manages artifact production, consumption, and security level enforcement.

**Key Components:**
- `artifact_pipeline.py:ArtifactPipeline` - Main pipeline orchestrating sink execution order (400+ lines)
- `artifact_pipeline.py:SinkBinding` - Wrapper tying sinks to artifact configuration metadata (62 lines)
- `artifact_pipeline.py:ArtifactStore` - Stores and resolves artifacts by ID, alias, and type (100+ lines)
- `artifacts.py:validate_artifact_type()` - Artifact type validation (estimated 50 lines)

**Dependencies:**
- Inbound: Core Orchestration, Experiment Framework
- Outbound: Plugin Implementations (sinks), Security Layer

**Patterns Observed:**
- Directed Acyclic Graph (DAG) resolution via topological sort
- Artifact request parsing with token-based references (@alias, type:name)
- Security level propagation and enforcement across artifact chain
- Produces/consumes pattern for dependency declaration

**Concerns:**
- Duplicate dataclass declaration for ArtifactRequest (lines 19-20 both have @dataclass)
- Complexity in artifact resolution with multiple lookup mechanisms (ID, alias, type)

**Confidence:** High - Verified topological sort logic, artifact store operations, and dependency resolution patterns

---

## LLM Middleware System

**Location:** `core/llm/`, `plugins/llms/`

**Responsibility:** Provides request/response transformation pipeline for LLM calls with middleware chain for logging, filtering, retries, and content modification.

**Key Components:**
- `core/llm/middleware.py:LLMMiddleware` - Middleware protocol with before_request/after_response hooks (80 lines)
- `core/llm/middleware.py:LLMRequest` - Request wrapper with metadata (40 lines)
- `core/llm/registry.py:create_middlewares()` - Middleware factory (50 lines)
- `plugins/llms/azure_openai.py:AzureOpenAIClient` - Azure OpenAI implementation (100 lines)
- `plugins/llms/middleware.py` - Generic middleware implementations (400 lines)
- `plugins/llms/middleware_azure.py` - Azure-specific middleware (440 lines)

**Dependencies:**
- Inbound: Core Orchestration, Experiment Framework
- Outbound: Plugin Implementations (LLM clients)

**Patterns Observed:**
- Chain of responsibility pattern for middleware execution
- Request/response wrapper pattern for metadata passing
- Before/after hook pattern for interception points
- Middleware registration and factory creation

**Concerns:**
- Middleware chain error handling not fully clear (what happens if middleware fails?)
- Large middleware implementation files (400+ lines) suggest multiple responsibilities

**Confidence:** High - Verified middleware protocol, factory creation, and Azure OpenAI integration

---

## Prompt Engine

**Location:** `core/prompts/`

**Responsibility:** Compiles and renders Jinja2-based prompt templates with variable substitution, default values, and field extraction.

**Key Components:**
- `engine.py:PromptEngine` - Template compiler with Jinja2 integration and field analysis (109 lines)
- `template.py:PromptTemplate` - Compiled template wrapper with render method (57 lines)
- `loader.py` - Template file loading utilities (estimated 80 lines)
- `exceptions.py` - Prompt-specific error types (PromptRenderingError, PromptValidationError) (estimated 30 lines)

**Dependencies:**
- Inbound: Core Orchestration, Experiment Framework
- Outbound: None (uses Jinja2 library)

**Patterns Observed:**
- Auto-conversion of simple {field} syntax to Jinja2 {{ field }} format
- Template compilation with required field extraction via AST analysis
- Default value support with validation
- Immutable template pattern with clone method

**Concerns:**
- None observed

**Confidence:** High - Verified template compilation, rendering logic, and Jinja2 integration

---

## Control Plane

**Location:** `core/controls/`

**Responsibility:** Provides operational controls for rate limiting and cost tracking to manage LLM API usage and expenditure.

**Key Components:**
- `rate_limit.py:RateLimiter` - Base protocol and implementations (NoopRateLimiter, FixedWindowRateLimiter, AdaptiveRateLimiter) (179 lines)
- `cost_tracker.py:CostTracker` - Base protocol and implementations (NoopCostTracker, FixedPriceCostTracker) (88 lines)
- `registry.py:create_rate_limiter()` - Factory for rate limiter instantiation (estimated 50 lines)
- `registry.py:create_cost_tracker()` - Factory for cost tracker instantiation (estimated 50 lines)

**Dependencies:**
- Inbound: Core Orchestration, Experiment Framework
- Outbound: None (self-contained)

**Patterns Observed:**
- Protocol pattern with multiple implementations (Noop, FixedWindow, Adaptive)
- Context manager pattern for rate limiter acquisition
- Sliding window algorithm for adaptive rate limiting with request and token tracking
- Usage metrics extraction from LLM responses

**Concerns:**
- None observed

**Confidence:** High - Verified rate limiter and cost tracker implementations, clear protocol definitions

---

## Security Layer

**Location:** `core/security/`

**Responsibility:** Handles artifact signing with HMAC and manages security level normalization and enforcement across the system.

**Key Components:**
- `signing.py:generate_signature()` - HMAC signature generation (SHA256/SHA512) (36 lines)
- `signing.py:verify_signature()` - Signature verification with timing-safe comparison (36 lines)
- `__init__.py:normalize_security_level()` - Security level string normalization (estimated 20 lines)
- `__init__.py:resolve_security_level()` - Security level resolution from multiple sources (estimated 30 lines)

**Dependencies:**
- Inbound: Artifact Pipeline, Plugin Implementations (signed artifact sink)
- Outbound: None (uses standard library hashlib/hmac)

**Patterns Observed:**
- HMAC-based signing with configurable hash algorithms
- Timing-safe comparison (hmac.compare_digest) for signature verification
- Security level propagation through artifact chain
- Key normalization (string/bytes handling)

**Concerns:**
- Security level enforcement logic distributed across artifact pipeline rather than centralized

**Confidence:** Medium - Verified signing implementation, security level normalization logic inferred from usage patterns

---

## Validation System

**Location:** `core/validation.py`, `core/config_schema.py`

**Responsibility:** Validates configuration files and plugin options against JSON schemas with detailed error reporting.

**Key Components:**
- `validation.py:validate_settings()` - Settings YAML validation (estimated 100 lines)
- `validation.py:validate_suite()` - Experiment suite validation (estimated 80 lines)
- `validation.py:validate_schema()` - Generic JSON schema validation (estimated 60 lines)
- `config_schema.py` - JSON schema definitions for configuration structures (estimated 200 lines)

**Dependencies:**
- Inbound: CLI & Configuration, Plugin Registry System, Experiment Framework
- Outbound: None (uses jsonschema library likely)

**Patterns Observed:**
- Validation-first approach (validate before use)
- Structured error reporting with context
- Preflight validation for suite configurations
- Schema-driven validation for extensibility

**Concerns:**
- None observed

**Confidence:** Medium - Verified validation entry points and error handling patterns, detailed implementation not fully read

---

## Plugin Implementations

**Location:** `plugins/`

**Responsibility:** Provides concrete implementations of datasources, LLM clients, output sinks, and experiment plugins.

**Key Components:**
- `datasources/csv_local.py:CSVDataSource` - Local CSV file loader (60 lines)
- `datasources/blob.py:BlobDataSource` - Azure Blob Storage loader (50 lines)
- `llms/azure_openai.py:AzureOpenAIClient` - Azure OpenAI API client (100 lines)
- `llms/mock.py:MockLLMClient` - Mock LLM for testing (50 lines)
- `outputs/csv_file.py:CsvResultSink` - CSV output writer (100 lines)
- `outputs/excel.py:ExcelResultSink` - Excel workbook writer (250 lines)
- `outputs/blob.py:BlobResultSink` - Azure Blob uploader (400 lines)
- `outputs/local_bundle.py:LocalBundleSink` - Local directory bundler (120 lines)
- `outputs/zip_bundle.py:ZipResultSink` - ZIP archive creator (280 lines)
- `outputs/repository.py:GitHubRepoSink, AzureDevOpsRepoSink` - Repository commit sinks (450 lines combined)
- `outputs/signed.py:SignedArtifactSink` - HMAC signed artifact bundler (150 lines)
- `outputs/analytics_report.py:AnalyticsReportSink` - Analytics report generator (250 lines)
- `experiments/metrics.py` - Metrics extraction plugins (estimated 200 lines)
- `experiments/early_stop.py` - Early stopping condition plugins (estimated 150 lines)

**Dependencies:**
- Inbound: Plugin Registry System, Experiment Framework (plugin registry)
- Outbound: Core interfaces (protocols), Security Layer, Artifact Pipeline

**Patterns Observed:**
- Protocol implementation pattern (implementing core interfaces)
- Adapter pattern (adapting external APIs to internal protocols)
- Template pattern in sink implementations (common write/finalize flow)
- Artifact production/consumption declarations for pipeline integration

**Concerns:**
- Large implementation files (blob.py 400+ lines, repository.py 450+ lines) suggest complex integrations
- Repository sinks combine GitHub and Azure DevOps in single file despite different APIs

**Confidence:** High - Sampled multiple plugin implementations across all categories, verified protocol compliance

---
