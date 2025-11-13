"""Config loader for orchestrator settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from elspeth.core.orchestrator import SDAConfig
from elspeth.core.registry import registry
from elspeth.core.controls import create_rate_limiter, create_cost_tracker
from elspeth.core.sda.plugin_registry import normalize_halt_condition_definitions
from elspeth.core.config_merger import ConfigurationMerger, ConfigSource


@dataclass
class Settings:
    datasource: Any
    llm: Any
    sinks: Any
    orchestrator_config: SDAConfig
    suite_root: Path | None = None
    suite_defaults: Dict[str, Any] = field(default_factory=dict)
    rate_limiter: Any | None = None
    cost_tracker: Any | None = None
    prompt_packs: Dict[str, Any] = field(default_factory=dict)
    prompt_pack: Optional[str] = None


def load_settings(path: str | Path, profile: str = "default") -> Settings:
    """Load settings from YAML configuration file.

    Uses ConfigurationMerger for consistent precedence:
    1. System defaults (if any)
    2. Prompt pack
    3. Profile
    4. Suite defaults
    5. Experiment config (handled by suite_runner)
    """
    config_path = Path(path)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    profile_data = dict(data.get(profile, {}))

    prompt_packs = profile_data.pop("prompt_packs", {})
    prompt_pack_name = profile_data.get("prompt_pack")
    pack = prompt_packs.get(prompt_pack_name) if prompt_pack_name else None

    # Use ConfigurationMerger for prompt pack merging
    merger = ConfigurationMerger()

    # Merge pack config into profile config
    if pack:
        pack_source = ConfigSource(name="prompt_pack", data=pack, precedence=2)
        profile_source = ConfigSource(name="profile", data=profile_data, precedence=3)
        merged_config = merger.merge(pack_source, profile_source)
    else:
        merged_config = profile_data

    # Extract merged values
    datasource_cfg = merged_config["datasource"]
    datasource = registry.create_datasource(
        datasource_cfg["plugin"], datasource_cfg.get("options", {})
    )

    llm_cfg = merged_config["llm"]
    llm = registry.create_llm(llm_cfg["plugin"], llm_cfg.get("options", {}))

    # Plugins are now properly appended by merger
    transform_plugin_defs = merged_config.get("row_plugins", [])
    aggregation_transform_defs = merged_config.get("aggregator_plugins", [])
    baseline_plugin_defs = merged_config.get("baseline_plugins", [])
    sink_defs = merged_config.get("sinks", [])
    llm_middleware_defs = merged_config.get("llm_middlewares", [])

    # Other config extraction
    rate_limiter_def = merged_config.get("rate_limiter")
    cost_tracker_def = merged_config.get("cost_tracker")
    prompt_defaults = merged_config.get("prompt_defaults")
    concurrency_config = merged_config.get("concurrency")
    halt_condition_config = merged_config.get("early_stop")
    halt_condition_plugin_defs = normalize_halt_condition_definitions(
        merged_config.get("early_stop_plugins")
    ) or []

    if not halt_condition_plugin_defs and halt_condition_config:
        halt_condition_plugin_defs = normalize_halt_condition_definitions(halt_condition_config)

    prompts = merged_config.get("prompts", {})
    prompt_fields = merged_config.get("prompt_fields")
    prompt_aliases = merged_config.get("prompt_aliases")
    criteria = merged_config.get("criteria")

    # Create sinks and controls
    sinks = [registry.create_sink(item["plugin"], item.get("options", {})) for item in sink_defs]
    rate_limiter = create_rate_limiter(rate_limiter_def)
    cost_tracker = create_cost_tracker(cost_tracker_def)

    # Handle suite_defaults merging with prompt packs
    suite_defaults = dict(merged_config.get("suite_defaults", {}))
    suite_pack_name = suite_defaults.get("prompt_pack")
    if suite_pack_name and suite_pack_name in prompt_packs:
        suite_pack = prompt_packs[suite_pack_name]
        suite_pack_source = ConfigSource(name="suite_prompt_pack", data=suite_pack, precedence=2)
        suite_source = ConfigSource(name="suite_defaults", data=suite_defaults, precedence=3)
        suite_defaults = merger.merge(suite_pack_source, suite_source)

    orchestrator_config = SDAConfig(
        llm_prompt=prompts,
        prompt_fields=prompt_fields,
        prompt_aliases=prompt_aliases,
        criteria=criteria,
        transform_plugin_defs=transform_plugin_defs,
        aggregation_transform_defs=aggregation_transform_defs,
        baseline_plugin_defs=baseline_plugin_defs,
        sink_defs=sink_defs,
        prompt_pack=prompt_pack_name,
        retry_config=merged_config.get("retry"),
        checkpoint_config=merged_config.get("checkpoint"),
        llm_middleware_defs=llm_middleware_defs,
        prompt_defaults=prompt_defaults,
        concurrency_config=concurrency_config,
        halt_condition_config=halt_condition_config,
        halt_condition_plugin_defs=halt_condition_plugin_defs or None,
    )

    suite_root = merged_config.get("suite_root")

    return Settings(
        datasource=datasource,
        llm=llm,
        sinks=sinks,
        orchestrator_config=orchestrator_config,
        suite_root=Path(suite_root) if suite_root else None,
        suite_defaults=suite_defaults,
        rate_limiter=rate_limiter,
        cost_tracker=cost_tracker,
        prompt_packs=prompt_packs,
        prompt_pack=prompt_pack_name,
    )
