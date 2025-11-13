# Migration to src Layout

This document describes the migration from the flat `dmp/` package structure to the modern `src/elspeth/` layout.

## Summary of Changes

### Package Name
- **Old**: `dmp`
- **New**: `elspeth`

### Directory Structure
- **Old**: `dmp/` (flat layout at project root)
- **New**: `src/elspeth/` (src layout)

## What Changed

### 1. Directory Reorganization

**Before:**
```
elspeth-simple/
├── dmp/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── core/
│   ├── plugins/
│   └── datasources/
├── pyproject.toml
└── ...
```

**After:**
```
elspeth-simple/
├── src/
│   └── elspeth/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── core/
│       ├── plugins/
│       └── datasources/
├── pyproject.toml
└── ...
```

### 2. Import Statements

All imports updated throughout the codebase:

**Before:**
```python
from dmp.core.orchestrator import SDAOrchestrator
from dmp.config import load_settings
from dmp.plugins.llms import OpenRouterClient
```

**After:**
```python
from elspeth.core.orchestrator import SDAOrchestrator
from elspeth.config import load_settings
from elspeth.plugins.llms import OpenRouterClient
```

### 3. Configuration Updates

#### pyproject.toml

**CLI Entry Point:**
- Old: `elspeth = "dmp.cli:main"`
- New: `elspeth = "elspeth.cli:main"`

**Build Configuration:**
- Old: `packages = ["dmp"]`
- New: `packages = ["src/elspeth"]`

**Version Path:**
- Old: `path = "dmp/__init__.py"`
- New: `path = "src/elspeth/__init__.py"`

**Import Sorting:**
- Old: `known-first-party = ["dmp"]`
- New: `known-first-party = ["elspeth"]`

**Test Configuration:**
- Old: `pythonpath = ["."]`
- New: `pythonpath = ["src"]`

**Coverage:**
- Old: `--cov=dmp` and `source = ["dmp"]`
- New: `--cov=elspeth` and `source = ["elspeth"]`

### 4. Example Files

Updated `example/simple/test_config.py`:
```python
# Old
from dmp.config import load_settings

# New
from elspeth.config import load_settings
```

## Why src Layout?

The src layout is a Python packaging best practice that provides several benefits:

### 1. **Prevents Accidental Imports**
With a flat layout, Python might import the package from the source directory instead of the installed version, hiding import errors. The src layout ensures you're always testing the installed package.

### 2. **Clear Separation**
Clearly separates source code (`src/`) from tests, docs, examples, and configuration files.

### 3. **Better for Testing**
Ensures tests run against the installed package, not the source directory, catching packaging issues early.

### 4. **Industry Standard**
Widely adopted by the Python community and recommended by PyPA (Python Packaging Authority).

### 5. **Tool Compatibility**
Better supported by modern Python tools like pytest, mypy, and build systems.

## Migration Impact

### Files Modified
- **57 Python files**: All import statements updated
- **pyproject.toml**: Build, test, and coverage configuration
- **example/simple/test_config.py**: Import statements

### Files Moved
- All files from `dmp/` → `src/elspeth/`
- Directory structure preserved within the package

### No Breaking Changes for Users
The CLI command remains the same:
```bash
elspeth --settings example/simple/settings.yaml
```

Configuration files (YAML) remain unchanged - they don't import Python modules directly.

## Verification

### Package Import
```bash
python -c "import elspeth; print(elspeth.__version__)"
# Output: 2.0.0
```

### CLI Works
```bash
elspeth --help
# Shows help text
```

### Examples Work
```bash
python example/simple/test_config.py
# ✓ Configuration loaded successfully
```

### Pipeline Runs
```bash
elspeth --settings example/simple/settings.yaml
# Processes data successfully
```

## For Developers

### Editable Install
After pulling the changes, reinstall in editable mode:
```bash
uv pip install -e ".[dev]"
```

### IDE Configuration
Update your IDE's Python path to include `src/`:
- **VSCode**: `"python.analysis.extraPaths": ["src"]`
- **PyCharm**: Mark `src/` as "Sources Root"

### Running Tests
```bash
pytest
# pytest automatically uses src/ from pythonpath configuration
```

### Type Checking
```bash
mypy src/elspeth
# Type check the package
```

### Linting
```bash
ruff check src/elspeth
ruff format src/elspeth
```

## Rollback (If Needed)

If you need to rollback (unlikely):

1. Move files back: `mv src/elspeth/* dmp/`
2. Update pyproject.toml (reverse the changes)
3. Update imports: `find . -name "*.py" -exec sed -i 's/from elspeth\./from dmp./g' {} \;`
4. Reinstall: `uv pip install -e ".[dev]"`

## References

- [Python Packaging User Guide - src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [pytest - src layout](https://docs.pytest.org/en/latest/explanation/goodpractices.html#tests-outside-application-code)
- [Hatchling - Build configuration](https://hatch.pypa.io/latest/config/build/)

## Timeline

- **v2.0.0**: Used `dmp` package with flat layout
- **v2.0.0+**: Migrated to `elspeth` package with src layout
- Version number unchanged (no API changes, internal refactor only)
