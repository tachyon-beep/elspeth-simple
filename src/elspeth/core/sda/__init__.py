"""SDA orchestration primitives."""

from .config import SDACycleConfig, SDASuite
from .runner import SDARunner

# DEPRECATED: SDASuiteRunner moved to orchestrators package
# Use StandardOrchestrator or ExperimentalOrchestrator instead
# Kept for backward compatibility - will be removed in future version
from .suite_runner import SDASuiteRunner

__all__ = [
    "SDACycleConfig",
    "SDASuite",
    "SDARunner",
    "SDASuiteRunner",  # Deprecated
]
