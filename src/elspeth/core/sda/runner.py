"""SDA (Sense/Decide/Act) runner executing one complete orchestration cycle."""

from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from elspeth.core.artifact_pipeline import ArtifactPipeline, SinkBinding
from elspeth.core.processing import prepare_prompt_context
from elspeth.core.prompts import PromptEngine, PromptTemplate
from elspeth.core.sda.checkpoint import CheckpointManager
from elspeth.core.sda.early_stop import EarlyStopCoordinator
from elspeth.core.sda.llm_executor import LLMExecutor
from elspeth.core.sda.plugin_registry import create_halt_condition_plugin
from elspeth.core.sda.prompt_compiler import PromptCompiler
from elspeth.core.sda.result_aggregator import ResultAggregator
from elspeth.core.sda.row_processor import RowProcessor
from elspeth.core.security import normalize_security_level

if TYPE_CHECKING:
    import pandas as pd

    from elspeth.core.controls import CostTracker, RateLimiter
    from elspeth.core.interfaces import LLMClientProtocol, ResultSink
    from elspeth.core.llm.middleware import LLMMiddleware
    from elspeth.core.sda.plugins import AggregationTransform, HaltConditionPlugin, TransformPlugin

logger = logging.getLogger(__name__)


@dataclass
class SDARunner:
    llm_client: LLMClientProtocol
    sinks: list[ResultSink]
    prompt_system: str
    prompt_template: str
    prompt_fields: list[str] | None = None
    criteria: list[dict[str, str]] | None = None
    transform_plugins: list[TransformPlugin] | None = None
    aggregation_transforms: list[AggregationTransform] | None = None
    rate_limiter: RateLimiter | None = None
    cost_tracker: CostTracker | None = None
    cycle_name: str | None = None
    retry_config: dict[str, Any] | None = None
    checkpoint_config: dict[str, Any] | None = None
    _checkpoint_ids: set[str] | None = None
    prompt_defaults: dict[str, Any] | None = None
    prompt_engine: PromptEngine | None = None
    _compiled_system_prompt: PromptTemplate | None = None
    _compiled_user_prompt: PromptTemplate | None = None
    _compiled_criteria_prompts: dict[str, PromptTemplate] | None = None
    llm_middlewares: list[LLMMiddleware] | None = None
    concurrency_config: dict[str, Any] | None = None
    security_level: str | None = None
    _active_security_level: str | None = None
    halt_condition_plugins: list[HaltConditionPlugin] | None = None
    halt_condition_config: dict[str, Any] | None = None

    def run(self, df: pd.DataFrame) -> dict[str, Any]:
        # Initialize early stop coordinator
        plugins = []
        if self.halt_condition_plugins:
            plugins = list(self.halt_condition_plugins)
        elif self.halt_condition_config:
            definition = {"name": "threshold", "options": dict(self.halt_condition_config)}
            plugin = create_halt_condition_plugin(definition)
            plugins = [plugin]
        self._early_stop_coordinator = EarlyStopCoordinator(plugins=plugins)

        checkpoint_manager: CheckpointManager | None = None
        checkpoint_field: str | None = None
        if self.checkpoint_config:
            checkpoint_path = Path(self.checkpoint_config.get("path", "checkpoint.jsonl"))
            checkpoint_field = self.checkpoint_config.get("field", "APPID")
            checkpoint_manager = CheckpointManager(checkpoint_path, checkpoint_field)

        transform_plugins = self.transform_plugins or []
        engine = self.prompt_engine or PromptEngine()
        compiler = PromptCompiler(
            engine=engine,
            system_prompt=self.prompt_system or "",
            user_prompt=self.prompt_template or "",
            cycle_name=self.cycle_name or "experiment",
            defaults=self.prompt_defaults or {},
            criteria=self.criteria,
        )
        compiled_prompts = compiler.compile()

        system_template = compiled_prompts.system
        user_template = compiled_prompts.user
        criteria_templates = compiled_prompts.criteria

        self._compiled_system_prompt = system_template
        self._compiled_user_prompt = user_template
        self._compiled_criteria_prompts = criteria_templates

        # Create LLM executor
        llm_executor = LLMExecutor(
            llm_client=self.llm_client,
            middlewares=self.llm_middlewares or [],
            retry_config=self.retry_config,
            rate_limiter=self.rate_limiter,
            cost_tracker=self.cost_tracker,
            cycle_name=self.cycle_name,
        )

        # Create row processor
        row_processor = RowProcessor(
            llm_client=self.llm_client,
            engine=engine,
            system_template=system_template,
            user_template=user_template,
            criteria_templates=criteria_templates,
            transform_plugins=transform_plugins,
            criteria=self.criteria,
            llm_executor=llm_executor,
            security_level=self._active_security_level,
        )

        # Create result aggregator
        aggregator = ResultAggregator(
            aggregation_plugins=self.aggregation_transforms or [],
            cost_tracker=self.cost_tracker,
        )

        rows_to_process: list[tuple[int, pd.Series, dict[str, Any], str | None]] = []
        for idx, (_, row) in enumerate(df.iterrows()):
            context = prepare_prompt_context(row, include_fields=self.prompt_fields)
            row_id = context.get(checkpoint_field) if checkpoint_field else None
            if checkpoint_manager and row_id and checkpoint_manager.is_processed(str(row_id)):
                continue
            if self._early_stop_coordinator.is_stopped():
                break
            rows_to_process.append((idx, row, context, row_id))

        def handle_success(idx: int, record: dict[str, Any], row_id: str | None) -> None:
            aggregator.add_result(record, row_index=idx)
            if checkpoint_manager and row_id:
                checkpoint_manager.mark_processed(str(row_id))
            self._early_stop_coordinator.check_record(record, row_index=idx)

        def handle_failure(failure: dict[str, Any]) -> None:
            aggregator.add_failure(failure)

        concurrency_cfg = self.concurrency_config or {}
        if rows_to_process and self._should_run_parallel(concurrency_cfg, len(rows_to_process)):
            self._run_parallel(
                rows_to_process,
                row_processor,
                handle_success,
                handle_failure,
                concurrency_cfg,
            )
        else:
            for idx, row, context, row_id in rows_to_process:
                if self._early_stop_coordinator.is_stopped():
                    break
                record, failure = row_processor.process_row(row, context, row_id)
                if record:
                    handle_success(idx, record, row_id)
                if failure:
                    handle_failure(failure)

        # Build payload with aggregator
        payload = aggregator.build_payload(
            security_level=self._active_security_level,
            early_stop_reason=self._early_stop_coordinator.get_reason(),
        )

        pipeline = ArtifactPipeline(self._build_sink_bindings())
        pipeline.execute(payload, payload["metadata"])
        self._active_security_level = None
        return payload

    def _should_run_parallel(self, config: dict[str, Any], backlog_size: int) -> bool:
        if not config or not config.get("enabled"):
            return False
        max_workers = max(int(config.get("max_workers", 1)), 1)
        if max_workers <= 1:
            return False
        threshold = int(config.get("backlog_threshold", 50))
        return backlog_size >= threshold

    def _run_parallel(
        self,
        rows_to_process: list[tuple[int, pd.Series, dict[str, Any], str | None]],
        row_processor: RowProcessor,
        handle_success,
        handle_failure,
        config: dict[str, Any],
    ) -> None:
        max_workers = max(int(config.get("max_workers", 4)), 1)
        pause_threshold = float(config.get("utilization_pause", 0.8))
        pause_interval = float(config.get("pause_interval", 0.5))

        lock = threading.Lock()

        def worker(data: tuple[int, pd.Series, dict[str, Any], str | None]) -> None:
            if self._early_stop_coordinator.is_stopped():
                return
            idx, row, context, row_id = data
            record, failure = row_processor.process_row(row, context, row_id)
            with lock:
                if record:
                    handle_success(idx, record, row_id)
                if failure:
                    handle_failure(failure)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for data in rows_to_process:
                if self.rate_limiter and pause_threshold > 0:
                    while True:
                        utilization = self.rate_limiter.utilization()
                        if utilization < pause_threshold:
                            break
                        time.sleep(pause_interval)
                if self._early_stop_coordinator.is_stopped():
                    break
                executor.submit(worker, data)

    def _build_sink_bindings(self) -> list[SinkBinding]:
        bindings: list[SinkBinding] = []
        for index, sink in enumerate(self.sinks):
            artifact_config = getattr(sink, "_dmp_artifact_config", {}) or {}
            plugin = getattr(sink, "_dmp_plugin_name", sink.__class__.__name__)
            base_id = getattr(sink, "_dmp_sink_name", plugin)
            sink_id = f"{base_id}:{index}"
            security_level = getattr(sink, "_dmp_security_level", None)
            if security_level is not None:
                security_level = normalize_security_level(security_level)
            bindings.append(
                SinkBinding(
                    id=sink_id,
                    plugin=plugin,
                    sink=sink,
                    artifact_config=artifact_config,
                    original_index=index,
                    security_level=security_level,
                )
            )
        return bindings


