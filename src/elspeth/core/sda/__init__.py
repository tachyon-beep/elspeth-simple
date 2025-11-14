"""SDA orchestration primitives."""

from .checkpoint import CheckpointManager
from .config import SDACycleConfig, SDASuite
from .early_stop import EarlyStopCoordinator
from .llm_executor import LLMExecutor
from .prompt_compiler import CompiledPrompts, PromptCompiler
from .result_aggregator import ResultAggregator
from .row_processor import RowProcessor
from .runner import SDARunner

# DEPRECATED: SDASuiteRunner moved to orchestrators package
# Use StandardOrchestrator or ExperimentalOrchestrator instead
# Kept for backward compatibility - will be removed in future version
from .suite_runner import SDASuiteRunner

__all__ = [
    "CheckpointManager",
    "CompiledPrompts",
    "EarlyStopCoordinator",
    "LLMExecutor",
    "PromptCompiler",
    "ResultAggregator",
    "RowProcessor",
    "SDACycleConfig",
    "SDARunner",
    "SDASuite",
    "SDASuiteRunner",  # Deprecated
]
