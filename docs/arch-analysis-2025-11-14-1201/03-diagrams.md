# Architecture Diagrams

**Analysis Date:** 2025-11-14
**Workspace:** docs/arch-analysis-2025-11-14-1201/
**Analyst:** Claude (System Archaeologist)

This document provides C4 architecture diagrams at Context, Container, and Component levels for the elspeth-simple system, reflecting the current architecture with recent refactorings.

---

## Context Diagram (C4 Level 1)

**Title:** elspeth-simple - Sense/Decide/Act Orchestration Platform

```mermaid
graph TB
    User[("Data Scientist/<br/>ML Engineer")]
    Admin[("Administrator")]

    System["elspeth-simple<br/>SDA Orchestration Platform<br/>(Python CLI Application)"]

    OpenRouter["OpenRouter API<br/>(LLM Gateway)"]
    AzureOpenAI["Azure OpenAI API<br/>(LLM Service)"]
    AzureBlobStorage["Azure Blob Storage<br/>(Cloud Storage)"]
    GitHub["GitHub<br/>(Repository Service)"]
    AzureDevOps["Azure DevOps<br/>(Repository Service)"]
    LocalFS["Local Filesystem<br/>(Storage)"]

    User -->|"Runs SDA cycles<br/>via CLI"| System
    Admin -->|"Configures<br/>via YAML"| System

    System -->|"LLM API calls"| OpenRouter
    System -->|"LLM API calls"| AzureOpenAI
    System -->|"Read input data<br/>Write results"| AzureBlobStorage
    System -->|"Commit artifacts"| GitHub
    System -->|"Commit artifacts"| AzureDevOps
    System -->|"Read config<br/>Read/Write data"| LocalFS

    style System fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style User fill:#95B3D7,stroke:#5B8AB8,color:#000
    style Admin fill:#95B3D7,stroke:#5B8AB8,color:#000
    style OpenRouter fill:#FDB462,stroke:#E89A4D,color:#000
    style AzureOpenAI fill:#FDB462,stroke:#E89A4D,color:#000
    style AzureBlobStorage fill:#B3DE69,stroke:#8FB84E,color:#000
    style GitHub fill:#B3DE69,stroke:#8FB84E,color:#000
    style AzureDevOps fill:#B3DE69,stroke:#8FB84E,color:#000
    style LocalFS fill:#B3DE69,stroke:#8FB84E,color:#000
```

**Description:**

The elspeth-simple system is a Python-based CLI application for running **Sense/Decide/Act (SDA)** cycles on datasets. Users (data scientists and ML engineers) interact through command-line interface, while administrators configure via hierarchical YAML files.

**Key interactions:**
- **SENSE** - Load data from datasources (Azure Blob, local CSV, custom)
- **DECIDE** - Process through LLM providers (OpenRouter, Azure OpenAI) or custom logic
- **ACT** - Output to multiple sinks (GitHub, Azure DevOps, blob storage, local files)

**Security context:** Designed for official-sensitive environments with HMAC signing, input validation, and security-level metadata.

---

## Container Diagram (C4 Level 2)

**Title:** elspeth-simple Internal Subsystems and Dependencies

```mermaid
graph TB
    User[("User")]

    subgraph System["elspeth-simple Platform - 12 Subsystems"]
        CLI["CLI & Configuration<br/>(cli.py, config.py)"]
        ConfigMerger["ConfigurationMerger<br/>(config_merger.py)<br/>[NEW]"]
        Orchestrators["Orchestration Strategies<br/>(orchestrators/)<br/>[NEW]"]
        SDACore["SDA Core<br/>(sda/)"]
        CoreOrch["Core Orchestrator<br/>(orchestrator.py)"]
        Registry["Plugin Registry<br/>(registry.py, interfaces.py)"]
        ArtifactPipe["Artifact Pipeline<br/>(artifact_pipeline.py)"]
        LLMMiddleware["LLM Middleware<br/>(llm/)"]
        PromptEngine["Prompt Engine<br/>(prompts/)"]
        Controls["Control Plane<br/>(controls/)"]
        Security["Security Layer<br/>(security/)"]
        Validation["Validation System<br/>(validation.py)"]
        Plugins["Plugin Implementations<br/>(plugins/)"]
    end

    ExtLLMs["LLM APIs<br/>(OpenRouter, Azure)"]
    ExtStorage["Storage Systems<br/>(Blob, GitHub)"]
    LocalFS["Local Filesystem"]

    User -->|"Executes commands"| CLI

    CLI -->|"Uses"| ConfigMerger
    CLI -->|"Validates"| Validation
    CLI -->|"Single run"| CoreOrch
    CLI -->|"Suite run"| Orchestrators

    Orchestrators -->|"Executes cycles"| SDACore
    Orchestrators -->|"Merges config"| ConfigMerger
    CoreOrch -->|"Delegates to"| SDACore

    SDACore -->|"Creates plugins"| Registry
    SDACore -->|"Compiles prompts"| PromptEngine
    SDACore -->|"Applies middleware"| LLMMiddleware
    SDACore -->|"Rate limits"| Controls
    SDACore -->|"Writes results"| ArtifactPipe

    Registry -->|"Validates schemas"| Validation
    Registry -->|"Instantiates"| Plugins

    ArtifactPipe -->|"Enforces security"| Security
    ArtifactPipe -->|"Executes"| Plugins

    LLMMiddleware -->|"Routes to"| Plugins
    Plugins -->|"Uses signing"| Security

    Plugins -->|"API calls"| ExtLLMs
    Plugins -->|"Read/Write"| ExtStorage
    Plugins -->|"Read/Write"| LocalFS

    style CLI fill:#E8F4F8,stroke:#4A90E2
    style ConfigMerger fill:#C8E6C9,stroke:#4CAF50
    style Orchestrators fill:#FFF9C4,stroke:#FBC02D
    style SDACore fill:#FFE0B2,stroke:#FF9800
    style CoreOrch fill:#FFCCBC,stroke:#FF5722
    style Registry fill:#D5E8D4,stroke:#82B366
    style ArtifactPipe fill:#E1D5E7,stroke:#9673A6
    style LLMMiddleware fill:#DAE8FC,stroke:#6C8EBF
    style PromptEngine fill:#F8CECC,stroke:#B85450
    style Controls fill:#D4E1F5,stroke:#7DA7D9
    style Security fill:#FFD9E6,stroke:#FF6B9D
    style Validation fill:#E6F3E6,stroke:#7CB342
    style Plugins fill:#FFF9E6,stroke:#FFB84D
```

**Description:**

The Container diagram shows the 12 major subsystems with **2 new subsystems** added in recent refactoring:

**New Subsystems (Nov 13-14, 2025):**
1. **ConfigurationMerger** [NEW] - Centralized config merging with merge trace debugging
2. **Orchestration Strategies** [NEW] - Pluggable strategies (Standard vs Experimental)

**Changed Subsystems:**
3. **CLI & Configuration** - Enhanced with --print-config, --explain-config flags
4. **SDA Core** - Renamed from "Experiment", SDASuiteRunner deprecated

**Unchanged Subsystems (8):**
5. Core Orchestrator, 6. Plugin Registry, 7. Artifact Pipeline, 8. LLM Middleware,
9. Prompt Engine, 10. Control Plane, 11. Security Layer, 12. Validation System

**Key architectural change:** Configuration complexity addressed via ConfigurationMerger, orchestration patterns clarified via strategy pattern.

---

## Component Diagram (Level 3) - ConfigurationMerger

**Title:** ConfigurationMerger Internal Structure

```mermaid
graph TB
    subgraph ConfigMergerSubsystem["ConfigurationMerger Subsystem [NEW]"]
        Merger["ConfigurationMerger<br/>(main class)"]

        subgraph MergeStrategies["Merge Strategy Implementations"]
            Override["OVERRIDE Strategy<br/>(scalars)"]
            Append["APPEND Strategy<br/>(lists)"]
            DeepMerge["DEEP_MERGE Strategy<br/>(nested dicts)"]
        end

        MergeTrace["Merge Trace<br/>(_merge_trace list)"]
        StrategyMap["MERGE_STRATEGIES<br/>(key → strategy mapping)"]

        subgraph DataModels["Data Models"]
            ConfigSource["ConfigSource<br/>(name, data, precedence)"]
            MergeStrategyEnum["MergeStrategy<br/>(enum)"]
        end
    end

    CLI["CLI (_run_suite)"]
    Config["config.py"]
    SDAOrch["Orchestration Strategies"]

    CLI -->|"Creates sources<br/>Calls merge()"| Merger
    Config -->|"Uses for profile merging"| Merger
    SDAOrch -->|"Uses for cycle defaults"| Merger

    Merger -->|"Contains"| StrategyMap
    Merger -->|"Records to"| MergeTrace
    Merger -->|"Applies"| Override
    Merger -->|"Applies"| Append
    Merger -->|"Applies"| DeepMerge

    StrategyMap -->|"Maps to"| MergeStrategyEnum
    Merger -->|"Accepts"| ConfigSource

    MergeTrace -->|"Used by"| ExplainMethod["explain(key) method"]

    style Merger fill:#C8E6C9,stroke:#4CAF50
    style Override fill:#E8F5E9,stroke:#4CAF50
    style Append fill:#E8F5E9,stroke:#4CAF50
    style DeepMerge fill:#E8F5E9,stroke:#4CAF50
    style MergeTrace fill:#F1F8E9,stroke:#4CAF50
    style StrategyMap fill:#F1F8E9,stroke:#4CAF50
    style ConfigSource fill:#DCEDC8,stroke:#4CAF50
    style MergeStrategyEnum fill:#DCEDC8,stroke:#4CAF50
```

**Description:**

ConfigurationMerger is a **new subsystem** introduced Nov 13, 2025 to centralize all configuration merging logic.

**Core functionality:**

1. **merge(*sources)** - Main entry point
   - Accepts variable ConfigSource objects with precedence levels
   - Sorts by precedence (1=lowest to 5=highest)
   - Applies appropriate merge strategy per key
   - Returns merged dictionary

2. **Three merge strategies:**
   - **OVERRIDE** - Higher precedence replaces lower (for scalars like strings, ints)
   - **APPEND** - Accumulates from all sources (for lists like plugins)
   - **DEEP_MERGE** - Recursive merge (for nested dicts like llm.options)

3. **Merge trace debugging:**
   - Records every merge operation with source and strategy
   - `explain(key)` method shows configuration provenance
   - Supports --explain-config CLI flag

**Key pattern:** Strategy pattern with three algorithms, precedence-based sorting, trace debugging for transparency.

**Addresses:** Prior architectural concern about "Configuration Complexity and Merging Logic"

---

## Component Diagram (Level 3) - Orchestration Strategies

**Title:** Orchestration Strategies Internal Structure

```mermaid
graph TB
    subgraph OrchSubsystem["Orchestration Strategies Subsystem [NEW]"]
        Standard["StandardOrchestrator<br/>(303 lines)"]
        Experimental["ExperimentalOrchestrator<br/>(217 lines)"]

        subgraph SharedMethods["Common Methods"]
            BuildRunner["build_runner()<br/>(config merging)"]
            CreatePlugins["_create_middlewares()<br/>_create_row_plugins()<br/>etc."]
        end

        subgraph StandardFlow["StandardOrchestrator Flow"]
            StdRun["run(df, defaults, ...)"]
            StdLoop["Sequential cycle execution"]
        end

        subgraph ExpFlow["ExperimentalOrchestrator Flow"]
            ExpRun["run(df, defaults, ...)"]
            ExpBaseline["Run baseline cycle first"]
            ExpVariants["Run variant cycles"]
            ExpCompare["Baseline comparison"]
        end
    end

    CLI["CLI (_run_suite)"]
    SDARunner["SDARunner"]
    ConfigMerger["ConfigurationMerger"]
    Registry["Plugin Registry"]

    CLI -->|"orchestrator_type=standard"| Standard
    CLI -->|"orchestrator_type=experimental"| Experimental

    Standard -->|"Uses"| BuildRunner
    Experimental -->|"Uses"| BuildRunner

    BuildRunner -->|"Merges config"| ConfigMerger
    BuildRunner -->|"Creates runner with"| SDARunner

    CreatePlugins -->|"Instantiates from"| Registry

    StdRun --> StdLoop
    StdLoop -->|"For each cycle"| SDARunner

    ExpRun --> ExpBaseline
    ExpBaseline -->|"Run first"| SDARunner
    ExpBaseline --> ExpVariants
    ExpVariants -->|"Run remaining"| SDARunner
    ExpVariants --> ExpCompare

    style Standard fill:#FFF9C4,stroke:#FBC02D
    style Experimental fill:#FFF59D,stroke:#FBC02D
    style BuildRunner fill:#FFF176,stroke:#FBC02D
    style CreatePlugins fill:#FFF176,stroke:#FBC02D
    style StdRun fill:#FFEE58,stroke:#FBC02D
    style StdLoop fill:#FFEE58,stroke:#FBC02D
    style ExpRun fill:#FFEB3B,stroke:#FBC02D
    style ExpBaseline fill:#FFEB3B,stroke:#FBC02D
    style ExpVariants fill:#FFEB3B,stroke:#FBC02D
    style ExpCompare fill:#FFEB3B,stroke:#FBC02D
```

**Description:**

Orchestration Strategies is a **new subsystem** introduced Nov 13, 2025 to provide pluggable orchestration patterns for multi-cycle execution.

**Two strategies:**

1. **StandardOrchestrator** (303 lines)
   - Simple sequential execution
   - Each cycle independent
   - No cross-cycle dependencies
   - Use case: Multiple unrelated SDA cycles

2. **ExperimentalOrchestrator** (217 lines)
   - A/B testing with baseline comparison
   - First cycle = baseline
   - Remaining cycles = variants
   - Automatic comparison against baseline
   - Use case: Comparing prompts, models, or configurations

**Common patterns:**
- Both use `build_runner()` which:
  - Merges defaults + prompt pack + cycle config via ConfigurationMerger
  - Instantiates plugins via Registry
  - Creates SDARunner for cycle execution
- Both implement `run(df, defaults, sink_factory, preflight_info)` interface
- Sink factory pattern for per-cycle isolation

**Replaces:** Deprecated SDASuiteRunner (was monolithic, now decomposed into strategies)

---

## Component Diagram (Level 3) - SDA Core

**Title:** SDA Core - Sense/Decide/Act Cycle Execution

```mermaid
graph TB
    subgraph SDASubsystem["SDA Core Subsystem"]
        Runner["SDARunner<br/>(cycle execution engine)<br/>(600+ lines)"]

        subgraph Phases["SDA Cycle Phases"]
            Sense["SENSE Phase<br/>(load data from datasource)"]
            Decide["DECIDE Phase<br/>(process via LLM + plugins)"]
            Act["ACT Phase<br/>(write to sinks)"]
        end

        subgraph RunnerMethods["SDARunner Methods"]
            RunMethod["run() - Main template method"]
            ProcessRow["_process_single_row() - Row processing"]
            ParallelRun["_run_parallel() - Concurrent processing"]
            Checkpoint["Checkpoint logic - Resume support"]
            EarlyStop["Early stop - Condition checking"]
        end

        subgraph Config["Configuration Models"]
            Suite["SDASuite"]
            CycleConfig["SDACycleConfig"]
        end

        subgraph PluginProtos["Plugin Protocols"]
            RowPlugin["RowPlugin"]
            AggPlugin["AggregationPlugin"]
            BaselinePlugin["BaselineComparisonPlugin"]
            HaltPlugin["HaltConditionPlugin"]
        end
    end

    Orchestrators["Orchestration Strategies"]
    CoreOrch["Core Orchestrator"]
    PromptEngine["Prompt Engine"]
    LLMMiddleware["LLM Middleware"]
    Controls["Control Plane"]
    ArtifactPipe["Artifact Pipeline"]

    Orchestrators -->|"Creates"| Runner
    CoreOrch -->|"Uses"| Runner

    RunMethod --> Sense
    Sense --> Decide
    Decide --> Act

    Decide -->|"Sequential"| ProcessRow
    Decide -->|"Parallel"| ParallelRun

    RunMethod -->|"Uses"| Checkpoint
    RunMethod -->|"Checks"| EarlyStop

    ProcessRow -->|"Compiles prompts"| PromptEngine
    ProcessRow -->|"Sends requests"| LLMMiddleware
    ProcessRow -->|"Enforces limits"| Controls

    Act -->|"Writes via"| ArtifactPipe

    Runner -->|"Applies"| RowPlugin
    Runner -->|"Applies"| AggPlugin
    Runner -->|"Uses for baseline"| BaselinePlugin
    Runner -->|"Checks"| HaltPlugin

    style Runner fill:#FFE0B2,stroke:#FF9800
    style Sense fill:#FFF3E0,stroke:#FF9800
    style Decide fill:#FFF3E0,stroke:#FF9800
    style Act fill:#FFF3E0,stroke:#FF9800
    style RunMethod fill:#FFE0B2,stroke:#FF9800
    style ProcessRow fill:#FFCC80,stroke:#FF9800
    style ParallelRun fill:#FFCC80,stroke:#FF9800
    style Checkpoint fill:#FFCC80,stroke:#FF9800
    style EarlyStop fill:#FFCC80,stroke:#FF9800
```

**Description:**

SDA Core implements the **Sense/Decide/Act cycle execution pattern** (renamed from "Experiment" terminology Nov 13, 2025).

**Three-phase cycle:**

1. **SENSE** - Load and prepare input data
   - Loads DataFrame from datasource plugin
   - Filters already-processed rows (checkpoint)
   - Prepares for decision-making

2. **DECIDE** - Process data through decision systems
   - Compiles Jinja2 prompt templates
   - Sends requests through LLM middleware to LLM client
   - Applies row plugins for metrics/transformations
   - Sequential or parallel processing (ThreadPoolExecutor)
   - Rate limiting and cost tracking
   - Early stopping condition checks

3. **ACT** - Output results to sinks
   - Applies aggregation plugins
   - Writes results via artifact pipeline
   - Resolves sink dependencies (DAG)

**Key capabilities:**
- Checkpoint/resume for long-running cycles
- Retry logic with exponential backoff
- Parallel row processing
- Plugin lifecycle management
- Early stopping conditions

**Concerns:** SDARunner complexity (600+ lines) - see docs/plans/2025-11-13-refactor-runner-god-class.md for planned refactoring

---

## Diagram Selection Rationale

**Three component diagrams selected:**

1. **ConfigurationMerger** - NEW subsystem showing merge strategies and debugging
2. **Orchestration Strategies** - NEW subsystem showing standard vs experimental patterns
3. **SDA Core** - Core execution showing Sense/Decide/Act cycle pattern

**Why these:**
- Represent the most significant recent architectural changes
- ConfigurationMerger addresses major technical concern from prior analysis
- Orchestration Strategies demonstrates strategy pattern and A/B testing
- SDA Core shows the fundamental execution model

**Why not others:**
- Plugin Registry, Artifact Pipeline, LLM Middleware - Unchanged since prior analysis
- Control Plane, Security, Validation - Smaller, well-understood patterns
- CLI, Core Orchestrator - Thin layers, limited internal complexity

These three diagrams represent the **architectural evolution** and show the system's current state.

---

## Confidence Assessment

**Diagram Confidence Levels:**

- **Context Diagram:** High - External systems verified from plugin implementations and configuration
- **Container Diagram:** High - All 12 subsystems from catalog, dependencies verified through code reading and prior docs
- **ConfigurationMerger Component:** High - Complete file read (211 lines), understand merge strategies, trace pattern
- **Orchestration Strategies Component:** High - Read both implementations (520 total lines), verified interface consistency
- **SDA Core Component:** Medium-High - Based on prior analysis plus verified renaming/deprecation changes

**Overall Confidence:** High - Diagrams accurately reflect current architecture with recent refactorings

---

**Status:** Architecture diagrams complete, ready for validation
