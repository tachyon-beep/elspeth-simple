# Subsystem Catalog

**Analysis Date:** 2025-11-14
**Analyst:** Claude (System Archaeologist)
**Workspace:** docs/arch-analysis-2025-11-14-1201/

This catalog documents all major subsystems identified in the elspeth-simple codebase, following the System Archaeologist contract format.

---

## ConfigurationMerger

**Location:** `src/elspeth/core/config_merger.py`

**Responsibility:** Centralizes configuration merging logic with documented precedence rules and three configurable merge strategies (OVERRIDE, APPEND, DEEP_MERGE) plus merge trace debugging.

**Key Components:**
- `config_merger.py:ConfigurationMerger` - Main merger class with merge() and explain() methods (211 lines total)
- `config_merger.py:MergeStrategy` - Enum defining three merge strategies: OVERRIDE, APPEND, DEEP_MERGE (7 lines)
- `config_merger.py:ConfigSource` - Dataclass wrapping configuration source with name, data, and precedence level (6 lines)
- `config_merger.py:MERGE_STRATEGIES` - Class-level dictionary mapping 30+ config keys to their merge strategies (32 lines)

**Dependencies:**
- Inbound: CLI & Configuration (cli.py), SDA Core (sda/suite_runner.py), Configuration loader (config.py)
- Outbound: None (self-contained, uses only standard library dataclasses and enum)

**Patterns Observed:**
- Strategy pattern with three merge strategies (OVERRIDE for scalars, APPEND for lists, DEEP_MERGE for nested dicts)
- Merge trace pattern for debugging - records every merge operation with source and strategy
- Precedence-based merging - sorts sources by precedence integer (1=lowest, 5=highest)
- Deep merge recursion for nested dictionary structures
- explain() method provides configuration provenance (shows which source provided final value)

**Concerns:**
- None observed

**Confidence:** High - Complete file read (211 lines), clear implementation of three merge strategies, comprehensive MERGE_STRATEGIES mapping, tested via tests/core/test_config_merger.py

---

## Orchestration Strategies

**Location:** `src/elspeth/orchestrators/`

**Responsibility:** Provides pluggable orchestration strategies for executing multiple SDA cycles with different execution patterns (simple sequential vs A/B testing with baseline comparison).

**Key Components:**
- `orchestrators/standard.py:StandardOrchestrator` - Simple sequential execution of multiple SDA cycles (303 lines)
- `orchestrators/experimental.py:ExperimentalOrchestrator` - A/B testing with baseline comparison and statistical analysis (217 lines)
- `orchestrators/__init__.py` - Package exports with docstring explaining strategy purpose (14 lines)

**Dependencies:**
- Inbound: CLI & Configuration (cli.py _run_suite function)
- Outbound: SDA Core (SDASuite, SDACycleConfig, SDARunner), Plugin Registry (create plugins), LLM clients, Result sinks

**Patterns Observed:**
- Strategy pattern - Two different orchestration algorithms with common interface
- StandardOrchestrator: Sequential cycle execution without cross-cycle dependencies
- ExperimentalOrchestrator: First cycle is baseline, remaining cycles are variants compared against baseline
- Both accept suite configuration, LLM client, sinks, and defaults parameter
- Both implement run(df, defaults, sink_factory, preflight_info) interface
- Configuration inheritance - defaults merge into per-cycle configurations
- Sink factory pattern - creates isolated sink instances per cycle

**Concerns:**
- None observed

**Confidence:** High - Read both orchestrator implementations (520 total lines), verified interface consistency, understand baseline comparison pattern in ExperimentalOrchestrator

---

## CLI & Configuration

**Location:** `src/elspeth/cli.py`, `src/elspeth/config.py`

**Responsibility:** Command-line interface entry point with enhanced debugging capabilities and YAML-based configuration loading with profile and prompt pack merging using ConfigurationMerger.

**Key Components:**
- `cli.py:main()` - CLI entry point with .env loading and command delegation (509 lines total)
- `cli.py:build_parser()` - ArgumentParser setup with 12 configuration options including new --print-config and --explain-config flags (60 lines)
- `cli.py:_print_configuration()` - NEW: Configuration debugging display (95 lines)
- `cli.py:_run_single()` - Single SDA cycle execution using SDAOrchestrator (32 lines)
- `cli.py:_run_suite()` - Suite execution using StandardOrchestrator or ExperimentalOrchestrator based on orchestrator_type setting (104 lines)
- `config.py:load_settings()` - Configuration loader with profile merging (134 lines)
- `config.py:Settings` - Dataclass containing all configuration (datasource, llm, sinks, orchestrator_config, suite settings)

**Dependencies:**
- Inbound: None (system entry point)
- Outbound: ConfigurationMerger, SDA Core (SDAOrchestrator, SDASuite), Orchestration Strategies, Validation System, Plugin Registry

**Patterns Observed:**
- Profile-based configuration with defaults
- ConfigurationMerger integration for suite defaults (replaces prior manual merging logic)
- Delegation pattern - _run_single vs _run_suite based on suite_root presence
- Orchestrator type selection - StandardOrchestrator vs ExperimentalOrchestrator via orchestrator_type config
- Configuration debugging - --print-config shows resolved config, --explain-config shows provenance
- Sink factory pattern for per-experiment isolation (_clone_suite_sinks)

**Concerns:**
- None observed - Configuration complexity addressed via ConfigurationMerger

**Confidence:** High - Complete file read (643 lines total), verified ConfigurationMerger integration in cli.py lines 351-412, verified new debugging flags

---

## SDA Core

**Location:** `src/elspeth/core/sda/`

**Responsibility:** Core Sense/Decide/Act cycle execution engine managing single cycle orchestration, plugin lifecycle, and suite configuration (renamed from "Experiment" terminology).

**Key Components:**
- `sda/runner.py:SDARunner` - Main SDA cycle execution engine with retry, checkpointing, concurrency (estimated 600+ lines based on prior analysis)
- `sda/config.py:SDASuite` - Suite configuration model with multiple cycles (150 lines)
- `sda/config.py:SDACycleConfig` - Single cycle configuration with prompts, plugins, controls (100 lines)
- `sda/plugins.py` - Protocol definitions for RowPlugin, AggregationPlugin, BaselineComparisonPlugin, HaltConditionPlugin (45 lines)
- `sda/plugin_registry.py` - SDA plugin factory registry with validation (269 lines)
- `sda/suite_runner.py:SDASuiteRunner` - DEPRECATED: Use orchestrators package instead (marked for removal)

**Dependencies:**
- Inbound: CLI & Configuration, Orchestration Strategies, Core Orchestrator facade
- Outbound: Plugin Registry, LLM Middleware, Prompt Engine, Control Plane, Artifact Pipeline, Plugin Implementations

**Patterns Observed:**
- Renamed from "Experiment" to "SDA" (Sense/Decide/Act) terminology for domain clarity
- Template method pattern in runner execution flow
- Strategy pattern for concurrency (sequential vs parallel via ThreadPoolExecutor)
- Checkpoint/resume pattern for long-running cycles
- Plugin lifecycle management (row plugins per-row, aggregation plugins once at end)
- SDASuiteRunner deprecated in favor of Orchestration Strategies subsystem

**Concerns:**
- SDARunner complexity (600+ lines) - See docs/plans/2025-11-13-refactor-runner-god-class.md for planned refactoring
- SDASuiteRunner deprecation needs migration path documentation

**Confidence:** High - Verified renaming from experiment terminology, confirmed SDASuiteRunner deprecation in __init__.py, understand migration to Orchestration Strategies

---

## Core Orchestrator

**Location:** `src/elspeth/core/orchestrator.py`

**Responsibility:** High-level orchestration facade coordinating datasource loading, LLM client, sinks, and delegation to SDARunner for single-cycle execution.

**Key Components:**
- `orchestrator.py:SDAOrchestrator` - Facade coordinating dependencies (estimated 100 lines based on prior analysis)
- `orchestrator.py:OrchestratorConfig` - Configuration dataclass with all orchestration parameters (35 lines)

**Dependencies:**
- Inbound: CLI & Configuration (for single-run mode)
- Outbound: Plugin Registry, SDA Core (SDARunner), LLM Middleware, Prompt Engine, Control Plane, Artifact Pipeline

**Patterns Observed:**
- Facade pattern hiding SDARunner complexity from CLI
- Thin coordination layer wiring dependencies together
- Loads data from DataSource plugin
- Delegates execution to SDARunner

**Concerns:**
- None observed

**Confidence:** Medium - Based on prior analysis, no changes detected since prior documentation

---

## Plugin Registry System

**Location:** `src/elspeth/core/registry.py`, `src/elspeth/core/interfaces.py`

**Responsibility:** Centralized plugin factory registry with validation and instantiation for datasources, LLM clients, and result sinks using protocol-based contracts.

**Key Components:**
- `registry.py:PluginRegistry` - Singleton with factory methods for all plugin types (396 lines)
- `registry.py:PluginFactory` - Factory wrapper with JSON schema validation (83 lines)
- `interfaces.py:DataSource` - Protocol defining load() → DataFrame contract (16 lines)
- `interfaces.py:LLMClientProtocol` - Protocol defining generate() contract (31 lines)
- `interfaces.py:ResultSink` - Protocol defining write() and artifact methods (54 lines)

**Dependencies:**
- Inbound: CLI & Configuration, Core Orchestrator, SDA Core, Orchestration Strategies
- Outbound: Plugin Implementations, Validation System

**Patterns Observed:**
- Registry/Factory pattern with centralized plugin mappings
- Protocol-oriented design (PEP 544) for plugin contracts
- JSON schema validation before instantiation
- Lazy imports (plugins imported only in registry, not throughout core)

**Concerns:**
- Plugin registry is static (hardcoded mappings), no dynamic plugin discovery
- Schema definitions embedded in registry code rather than separate schema files

**Confidence:** High - Based on prior analysis, verified no changes to registry.py or interfaces.py since prior documentation

---

## Artifact Pipeline

**Location:** `src/elspeth/core/artifact_pipeline.py`, `src/elspeth/core/artifacts.py`

**Responsibility:** Resolves dependencies between result sinks using topological sorting and manages artifact production, consumption, and security level enforcement.

**Key Components:**
- `artifact_pipeline.py:ArtifactPipeline` - Main pipeline orchestrating sink execution order (400+ lines)
- `artifact_pipeline.py:SinkBinding` - Wrapper tying sinks to artifact configuration metadata (62 lines)
- `artifact_pipeline.py:ArtifactStore` - Stores and resolves artifacts by ID, alias, and type (100+ lines)
- `artifacts.py:validate_artifact_type()` - Artifact type validation (estimated 50 lines)

**Dependencies:**
- Inbound: Core Orchestrator, SDA Core, Orchestration Strategies
- Outbound: Plugin Implementations (sinks), Security Layer

**Patterns Observed:**
- Directed Acyclic Graph (DAG) resolution via topological sort
- Artifact request parsing with token-based references (@alias, type:name)
- Security level propagation and enforcement across artifact chain
- Produces/consumes pattern for dependency declaration

**Concerns:**
- Duplicate dataclass declaration for ArtifactRequest (lines 19-20 both have @dataclass) - from prior analysis

**Confidence:** High - Based on prior analysis, verified no changes to artifact_pipeline.py since prior documentation

---

## LLM Middleware System

**Location:** `src/elspeth/core/llm/`, `src/elspeth/plugins/llms/`

**Responsibility:** Provides request/response transformation pipeline for LLM calls with middleware chain for logging, filtering, retries, and content modification.

**Key Components:**
- `core/llm/middleware.py:LLMMiddleware` - Middleware protocol with before_request/after_response hooks (80 lines)
- `core/llm/middleware.py:LLMRequest` - Request wrapper with metadata (40 lines)
- `core/llm/registry.py:create_middlewares()` - Middleware factory (50 lines)
- `plugins/llms/middleware.py` - Generic middleware implementations (400 lines)
- `plugins/llms/middleware_azure.py` - Azure-specific middleware (440 lines)

**Dependencies:**
- Inbound: Core Orchestrator, SDA Core, Orchestration Strategies
- Outbound: Plugin Implementations (LLM clients)

**Patterns Observed:**
- Chain of responsibility pattern for middleware execution
- Request/response wrapper pattern for metadata passing
- Before/after hook pattern for interception points
- Middleware registration and factory creation

**Concerns:**
- Middleware chain error handling not fully clear
- Large middleware implementation files (400+ lines) suggest multiple responsibilities

**Confidence:** High - Based on prior analysis, verified no changes to LLM middleware system since prior documentation

---

## Prompt Engine

**Location:** `src/elspeth/core/prompts/`

**Responsibility:** Compiles and renders Jinja2-based prompt templates with variable substitution, default values, and field extraction.

**Key Components:**
- `engine.py:PromptEngine` - Template compiler with Jinja2 integration and field analysis (109 lines)
- `template.py:PromptTemplate` - Compiled template wrapper with render method (57 lines)
- `loader.py` - Template file loading utilities (estimated 80 lines)
- `exceptions.py` - Prompt-specific error types (PromptRenderingError, PromptValidationError) (estimated 30 lines)

**Dependencies:**
- Inbound: Core Orchestrator, SDA Core, Orchestration Strategies
- Outbound: None (uses Jinja2 library)

**Patterns Observed:**
- Auto-conversion of simple {field} syntax to Jinja2 {{ field }} format
- Template compilation with required field extraction via AST analysis
- Default value support with validation
- Immutable template pattern with clone method

**Concerns:**
- None observed

**Confidence:** High - Based on prior analysis, verified no changes to prompts subsystem since prior documentation

---

## Control Plane

**Location:** `src/elspeth/core/controls/`

**Responsibility:** Provides operational controls for rate limiting and cost tracking to manage LLM API usage and expenditure.

**Key Components:**
- `rate_limit.py:RateLimiter` - Base protocol and implementations (NoopRateLimiter, FixedWindowRateLimiter, AdaptiveRateLimiter) (179 lines)
- `cost_tracker.py:CostTracker` - Base protocol and implementations (NoopCostTracker, FixedPriceCostTracker) (88 lines)
- `registry.py:create_rate_limiter()` - Factory for rate limiter instantiation (estimated 50 lines)
- `registry.py:create_cost_tracker()` - Factory for cost tracker instantiation (estimated 50 lines)

**Dependencies:**
- Inbound: Core Orchestrator, SDA Core, Orchestration Strategies
- Outbound: None (self-contained)

**Patterns Observed:**
- Protocol pattern with multiple implementations (Noop, FixedWindow, Adaptive)
- Context manager pattern for rate limiter acquisition
- Sliding window algorithm for adaptive rate limiting with request and token tracking
- Usage metrics extraction from LLM responses

**Concerns:**
- None observed

**Confidence:** High - Based on prior analysis, verified no changes to controls subsystem since prior documentation

---

## Security Layer

**Location:** `src/elspeth/core/security/`

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

**Confidence:** Medium - Based on prior analysis, verified no changes to security subsystem since prior documentation

---

## Validation System

**Location:** `src/elspeth/core/validation.py`, `src/elspeth/core/config_schema.py`

**Responsibility:** Validates configuration files and plugin options against JSON schemas with detailed error reporting.

**Key Components:**
- `validation.py:validate_settings()` - Settings YAML validation (estimated 100 lines)
- `validation.py:validate_suite()` - SDA suite validation (estimated 80 lines)
- `validation.py:validate_schema()` - Generic JSON schema validation (estimated 60 lines)
- `config_schema.py` - JSON schema definitions for configuration structures (estimated 200 lines)

**Dependencies:**
- Inbound: CLI & Configuration, Plugin Registry System, SDA Core, Orchestration Strategies
- Outbound: None (uses jsonschema library)

**Patterns Observed:**
- Validation-first approach (validate before use)
- Structured error reporting with context
- Preflight validation for suite configurations
- Schema-driven validation for extensibility

**Concerns:**
- None observed

**Confidence:** Medium - Based on prior analysis, verified no changes to validation system since prior documentation

---

## Plugin Implementations

**Location:** `src/elspeth/plugins/`

**Responsibility:** Provides concrete implementations of datasources, LLM clients, output sinks, and transform plugins.

**Key Components:**
- `datasources/csv_local.py:CSVDataSource` - Local CSV file loader (60 lines)
- `datasources/blob.py:BlobDataSource` - Azure Blob Storage loader (50 lines)
- `llms/azure_openai.py:AzureOpenAIClient` - Azure OpenAI API client (100 lines)
- `llms/openrouter.py:OpenRouterClient` - OpenRouter API client for multiple LLM providers
- `llms/mock.py:MockLLMClient` - Mock LLM for testing (50 lines)
- `outputs/csv_file.py:CsvResultSink` - CSV output writer (100 lines)
- `outputs/excel.py:ExcelResultSink` - Excel workbook writer (250 lines)
- `outputs/blob.py:BlobResultSink` - Azure Blob uploader (400 lines)
- `outputs/local_bundle.py:LocalBundleSink` - Local directory bundler (120 lines)
- `outputs/zip_bundle.py:ZipResultSink` - ZIP archive creator (280 lines)
- `outputs/repository.py:GitHubRepoSink, AzureDevOpsRepoSink` - Repository commit sinks (450 lines combined)
- `outputs/signed.py:SignedArtifactSink` - HMAC signed artifact bundler (150 lines)
- `outputs/analytics_report.py:AnalyticsReportSink` - Analytics report generator (250 lines)
- `transforms/metrics.py` - Metrics extraction plugins (57KB - largest plugin file)
- `transforms/early_stop.py` - Early stopping condition plugins (estimated 150 lines)

**Dependencies:**
- Inbound: Plugin Registry System, SDA Core (plugin registry)
- Outbound: Core interfaces (protocols), Security Layer, Artifact Pipeline

**Patterns Observed:**
- Protocol implementation pattern (implementing core interfaces)
- Adapter pattern (adapting external APIs to internal protocols)
- Template pattern in sink implementations (common write/finalize flow)
- Artifact production/consumption declarations for pipeline integration

**Concerns:**
- Large implementation files (blob.py 400+ lines, repository.py 450+ lines, metrics.py 57KB) suggest complex integrations
- Repository sinks combine GitHub and Azure DevOps in single file despite different APIs

**Confidence:** High - Based on prior analysis with updated plugin list, verified no structural changes to plugins directory since prior documentation

---

