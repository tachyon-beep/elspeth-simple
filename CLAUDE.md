# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

elspeth-simple is a Python 3.13+ Sense/Decide/Act (SDA) orchestration framework for building auditable data workflows designed for official-sensitive environments. It orchestrates data transformation pipelines combining datasources, LLM processing, and output sinks with production features (retry logic, checkpointing, rate limiting, cost tracking).

## Development Commands

### Environment Setup
```bash
# Create virtual environment (Python 3.13+ required)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Install dev dependencies
uv pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/core/test_config_merger.py -v

# Run specific test function
pytest tests/core/test_config_merger.py::test_merge_append_strategy -v

# Run and skip slow tests
pytest -m "not slow"

# Run only unit tests
pytest -m unit
```

### Code Quality
```bash
# Linting (check only)
ruff check src/ tests/

# Linting (auto-fix)
ruff check --fix src/ tests/

# Format code
ruff format src/ tests/

# Type checking
mypy src/

# Run all quality checks
ruff check src/ tests/ && mypy src/ && pytest
```

### Running the CLI
```bash
# Basic usage
elspeth --settings config/settings.yaml

# Using specific profile
elspeth --settings config.yaml --profile production

# Preview first N rows
elspeth --settings config.yaml --head 20

# Save results to CSV
elspeth --settings config.yaml --output-csv results.csv

# Debug configuration
elspeth --settings config.yaml --print-config
elspeth --settings config.yaml --explain-config llm.options.temperature

# Force single run (not suite)
elspeth --settings config.yaml --single-run

# Enable live outputs (disable dry-run)
elspeth --settings config.yaml --live-outputs

# Disable metrics plugins
elspeth --settings config.yaml --disable-metrics
```

## Architecture

### Sense/Decide/Act Pattern
The framework follows a three-phase pipeline:
1. **SENSE** - Load data via datasources (CSV, Azure Blob, custom)
2. **DECIDE** - Process rows through LLM clients and transform plugins
3. **ACT** - Write results to multiple sinks (CSV, Excel, Blob, Git repos)

### Core Architecture Layers

#### 1. Orchestration Layer (`src/elspeth/core/orchestrator.py`, `src/elspeth/orchestrators/`)
- **SDAOrchestrator**: Single-run orchestrator coordinating SENSE→DECIDE→ACT
- **StandardOrchestrator**: Sequential multi-cycle execution (independent runs)
- **ExperimentalOrchestrator**: A/B testing with baseline comparison
- Orchestrator type selected via `orchestrator_type: standard|experimental` in config

#### 2. SDA Execution (`src/elspeth/core/sda/`)
- **SDARunner**: Core execution engine for one complete SDA cycle
- **RowProcessor**: Per-row LLM invocation with retry logic
- **LLMExecutor**: LLM client interaction with middleware support
- **ResultAggregator**: Post-processing aggregation transforms
- **CheckpointManager**: Resume interrupted processing
- **EarlyStopCoordinator**: Halt conditions (budget, quality gates)

#### 3. Configuration System (`src/elspeth/config.py`, `src/elspeth/core/config_merger.py`)
- **ConfigurationMerger**: Centralized merge logic with precedence (critical component!)
- **Merge strategies**: OVERRIDE (scalars), APPEND (lists), DEEP_MERGE (nested dicts)
- **Precedence levels**: 1=system defaults, 2=prompt pack, 3=profile, 4=suite defaults, 5=experiment
- **Debug tooling**: `--print-config`, `--explain-config KEY`
- Configuration merging is CRITICAL - always use ConfigurationMerger for consistency

#### 4. Plugin System (`src/elspeth/core/registry.py`, `src/elspeth/plugins/`)
Protocol-based extensibility (22 implementations):
- **Datasources**: `local_csv`, `azure_blob`
- **LLM Clients**: `openrouter`, `azure_openai`, `mock`
- **Sinks**: `csv`, `excel`, `azure_blob`, `github_repo`, `azure_devops_repo`, `zip_bundle`, `signed`
- **Transforms**: `early_stop`, `metrics`, custom row/aggregation plugins
- **Rate Limiters**: `fixed_window`, `adaptive`
- **Cost Trackers**: `fixed_price`, `azure_openai`

#### 5. Prompting (`src/elspeth/core/prompts/`)
- **PromptEngine**: Jinja2-based templating with field substitution
- **PromptCompiler**: Compiles system/user/criteria prompts with defaults
- **Prompt packs**: Reusable configurations (precedence=2)
- **Prompt aliases**: Field name remapping

#### 6. Controls (`src/elspeth/core/controls/`)
- **RateLimiter**: Token bucket rate limiting
- **CostTracker**: Token usage and cost monitoring

#### 7. Security (`src/elspeth/core/security/`)
- **HMAC Signing**: SHA-256/SHA-512 artifact signing
- **Security levels**: Classification metadata (OFFICIAL, OFFICIAL:SENSITIVE, etc.)

### Suite Execution Model
- **SDASuite**: Multi-cycle execution defined in YAML (`suite_root`)
- **Cycles**: Independent SDA runs with per-cycle configuration overrides
- **Orchestrator strategies**: StandardOrchestrator (sequential) vs ExperimentalOrchestrator (baseline comparison)
- Suite configs merge experiment-level overrides into defaults using ConfigurationMerger

## Key Implementation Patterns

### Configuration Merging
**ALWAYS use ConfigurationMerger** - never implement custom merge logic:
```python
from elspeth.core.config_merger import ConfigurationMerger, ConfigSource

merger = ConfigurationMerger()
sources = [
    ConfigSource(name="defaults", data=defaults_dict, precedence=1),
    ConfigSource(name="overrides", data=overrides_dict, precedence=2),
]
merged = merger.merge(*sources)
```

### Plugin Registration
Plugins use factory pattern via registry:
```python
from elspeth.core.registry import registry

# Register plugin
@registry.register_datasource("my_source")
class MyDataSource:
    def load(self) -> pd.DataFrame: ...

# Create instance
datasource = registry.create_datasource("my_source", {"option": "value"})
```

### Protocol-Based Design
Use PEP 544 structural typing (protocols) for interfaces:
- `DataSource`: `load() -> pd.DataFrame`
- `LLMClientProtocol`: `send(messages, **kwargs) -> dict`
- `ResultSink`: `write(results: dict) -> None`
- `TransformPlugin`: `transform(row, context) -> dict`

### Retry Logic
Retry configuration via `retry_config`:
```yaml
retry:
  max_attempts: 3
  initial_delay_seconds: 1.0
  max_delay_seconds: 60.0
  backoff_multiplier: 2.0
```

### Checkpointing
Resume processing via `checkpoint_config`:
```yaml
checkpoint:
  path: checkpoint.jsonl
  field: APPID  # unique row identifier
```

## Testing Guidelines

### Test Structure
- **Unit tests**: `tests/core/`, `tests/plugins/`
- **Integration tests**: Mark with `@pytest.mark.integration`
- **Slow tests**: Mark with `@pytest.mark.slow`
- Use pytest fixtures for common setup
- pythonpath is `src/` (configured in pyproject.toml)

### Test Execution Paths
```python
# Correct way to run tests with PYTHONPATH
pytest tests/core/test_config_merger.py -v

# Or with explicit PYTHONPATH
PYTHONPATH=src pytest tests/
```

### Key Test Files
- `tests/core/test_config_merger.py`: ConfigurationMerger (340 lines, comprehensive)
- `tests/core/test_orchestrator.py`: SDAOrchestrator
- `tests/core/test_sda_runner.py`: SDARunner
- `tests/plugins/`: Plugin implementations

## Configuration Hierarchy

**Precedence order** (higher wins):
1. System defaults (precedence=1)
2. Prompt packs (precedence=2) - via `prompt_pack: pack_name`
3. Profile config (precedence=3) - via `--profile PROFILE`
4. Suite defaults (precedence=4) - `suite_defaults` section
5. Experiment config (precedence=5) - per-cycle overrides in suite

**Merge strategies by key type**:
- Scalars (strings, numbers, bools): OVERRIDE
- Lists (plugins, criteria): APPEND
- Nested dicts (llm.options): DEEP_MERGE

**Debug configuration**:
```bash
# See full resolved config
elspeth --settings config.yaml --print-config

# Explain specific key provenance
elspeth --settings config.yaml --explain-config llm.options.temperature
```

## Common Development Tasks

### Adding a New Plugin
1. Create plugin class implementing appropriate protocol
2. Register with `@registry.register_TYPE("plugin_name")`
3. Add to `src/elspeth/plugins/TYPE/__init__.py`
4. Create tests in `tests/plugins/test_TYPE_plugin.py`
5. Document in README if it's a major plugin

### Adding a New Transform Plugin
1. Implement `TransformPlugin` protocol with `transform(row, context)`
2. Register via `@registry.register_transform("plugin_name")`
3. Add configuration in YAML under `row_plugins:`

### Modifying Configuration Merge Logic
- **NEVER modify ConfigurationMerger directly without understanding precedence**
- Read `docs/configuration-precedence.md` (285 lines)
- Add comprehensive tests to `tests/core/test_config_merger.py`
- Update `ConfigSource` precedence constants if adding new layer

### Working with Suites
- Suite definition: `suite_root/suite.yaml`
- Experiment definitions: `suite_root/EXPERIMENT_NAME.yaml`
- Use ConfigurationMerger for defaults merging
- Test with `--single-run` to skip suite execution

## Important Implementation Notes

### ConfigurationMerger is Critical
- Introduced Nov 13, 2025 to centralize all merge logic
- Replaced scattered manual merging across 3 files
- All configuration merging MUST go through ConfigurationMerger
- Has comprehensive test coverage (340 lines)
- Provides `explain()` for debugging

### Orchestrator Type Selection
- `orchestrator_type: standard` - Simple sequential cycles
- `orchestrator_type: experimental` - A/B testing with baseline (default)
- Set in YAML `suite:` section or top-level config

### Environment Variables
- Load `.env` file automatically via `cli.py:load_dotenv()`
- Common vars: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `AZURE_OPENAI_KEY`
- Reference in YAML: `${VARIABLE_NAME}`

### Dry-Run Mode
- Repository sinks (GitHub, Azure DevOps) default to dry-run
- Enable live writes: `--live-outputs`
- Check `dry_run` attribute on sink instances

### Recent Refactoring (Nov 13-14, 2025)
- ConfigurationMerger introduced (addresses major technical debt)
- SDASuiteRunner deprecated → StandardOrchestrator/ExperimentalOrchestrator
- Terminology: "experiment" → "SDA cycle"
- CLI enhancements: `--print-config`, `--explain-config`

## File Organization

```
src/elspeth/
├── cli.py                    # CLI entry point
├── config.py                 # Settings loader
├── core/
│   ├── orchestrator.py       # SDAOrchestrator
│   ├── config_merger.py      # ConfigurationMerger (critical!)
│   ├── interfaces.py         # Protocol definitions
│   ├── registry.py           # Plugin registry
│   ├── sda/                  # SDA execution engine
│   │   ├── runner.py         # SDARunner
│   │   ├── row_processor.py  # Per-row processing
│   │   ├── llm_executor.py   # LLM interaction
│   │   ├── checkpoint.py     # Checkpointing
│   │   └── early_stop.py     # Halt conditions
│   ├── prompts/              # Jinja2 templating
│   ├── controls/             # Rate limiting, cost tracking
│   └── security/             # HMAC signing
├── orchestrators/            # Suite orchestration strategies
│   ├── standard.py           # Sequential execution
│   └── experimental.py       # A/B testing
└── plugins/                  # Plugin implementations
    ├── datasources/
    ├── llms/
    ├── sinks/
    └── transforms/

tests/                        # Test suite (mirrors src/)
docs/                         # Documentation
example/                      # Example configurations
```

## Documentation References

- Architecture analysis: `docs/arch-analysis-2025-11-14-1201/04-final-report.md`
- Configuration precedence: `docs/configuration-precedence.md`
- OpenRouter setup: `docs/OPENROUTER_SETUP.md`
- Environment variables: `docs/ENVIRONMENT_VARIABLES.md`
- Examples: `example/simple/`, `example/complex/`, `example/experimental/`