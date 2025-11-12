"""SDA (Sense/Decide/Act) orchestrator coordinating data input, decision-making, and action execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd

from dmp.core.interfaces import DataSource, LLMClientProtocol, ResultSink
from dmp.core.sda.runner import SDARunner
from dmp.core.controls import RateLimiter, CostTracker
from dmp.core.llm.registry import create_middlewares
from dmp.core.sda.plugin_registry import create_transform_plugin, create_aggregation_transform, create_halt_condition_plugin


@dataclass
class SDAConfig:
    llm_prompt: Dict[str, str]
    prompt_fields: List[str] | None = None
    prompt_aliases: Dict[str, str] | None = None
    criteria: List[Dict[str, str]] | None = None
    transform_plugin_defs: List[Dict[str, Any]] | None = None
    aggregation_transform_defs: List[Dict[str, Any]] | None = None
    sink_defs: List[Dict[str, Any]] | None = None
    prompt_pack: str | None = None
    baseline_plugin_defs: List[Dict[str, Any]] | None = None
    retry_config: Dict[str, Any] | None = None
    checkpoint_config: Dict[str, Any] | None = None
    llm_middleware_defs: List[Dict[str, Any]] | None = None
    prompt_defaults: Dict[str, Any] | None = None
    concurrency_config: Dict[str, Any] | None = None
    halt_condition_config: Dict[str, Any] | None = None
    halt_condition_plugin_defs: List[Dict[str, Any]] | None = None


class SDAOrchestrator:
    def __init__(
        self,
        *,
        datasource: DataSource,
        llm_client: LLMClientProtocol,
        sinks: List[ResultSink],
        config: SDAConfig,
        sda_runner: SDARunner | None = None,
        rate_limiter: RateLimiter | None = None,
        cost_tracker: CostTracker | None = None,
        name: str = "default",
    ):
        self.datasource = datasource
        self.llm_client = llm_client
        self.sinks = sinks
        self.config = config
        self.rate_limiter = rate_limiter
        self.cost_tracker = cost_tracker
        self.name = name
        transform_plugins = None
        if config.transform_plugin_defs:
            transform_plugins = [create_transform_plugin(defn) for defn in config.transform_plugin_defs]
        aggregation_transforms = None
        if config.aggregation_transform_defs:
            aggregation_transforms = [create_aggregation_transform(defn) for defn in config.aggregation_transform_defs]
        halt_condition_plugins = None
        if config.halt_condition_plugin_defs:
            halt_condition_plugins = [create_halt_condition_plugin(defn) for defn in config.halt_condition_plugin_defs]
        self.halt_condition_plugins = halt_condition_plugins

        self.sda_runner = sda_runner or SDARunner(
            llm_client=llm_client,
            sinks=sinks,
            prompt_system=config.llm_prompt["system"],
            prompt_template=config.llm_prompt["user"],
            prompt_fields=config.prompt_fields,
            criteria=config.criteria,
            transform_plugins=transform_plugins,
            aggregation_transforms=aggregation_transforms,
            rate_limiter=rate_limiter,
            cost_tracker=cost_tracker,
            cycle_name=name,
            retry_config=config.retry_config,
            checkpoint_config=config.checkpoint_config,
            llm_middlewares=create_middlewares(config.llm_middleware_defs),
            prompt_defaults=config.prompt_defaults,
            concurrency_config=config.concurrency_config,
            halt_condition_plugins=halt_condition_plugins,
            halt_condition_config=config.halt_condition_config,
        )

    def run(self) -> Dict[str, Any]:
        df = self.datasource.load()
        system_prompt = self.config.llm_prompt["system"]
        user_prompt_format = self.config.llm_prompt["user"]

        results = []
        runner = self.sda_runner
        runner.prompt_system = system_prompt
        runner.prompt_template = user_prompt_format
        runner.prompt_fields = self.config.prompt_fields
        runner.criteria = self.config.criteria
        runner.rate_limiter = self.rate_limiter
        runner.cost_tracker = self.cost_tracker
        runner.cycle_name = self.name
        runner.concurrency_config = self.config.concurrency_config
        runner.halt_condition_plugins = self.halt_condition_plugins
        payload = runner.run(df)
        return payload
