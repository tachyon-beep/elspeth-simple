"""Command-line entry point for local experimentation.

For now the CLI focuses on hydrating experiment input data from Azure Blob
Storage using the configuration profiles defined in ``config/blob_store.yaml``.
Future work will layer in the experiment runner once additional modules land.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import pandas as pd

from elspeth.config import load_settings
from elspeth.core.config_merger import ConfigSource, ConfigurationMerger
from elspeth.core.orchestrator import SDAOrchestrator
from elspeth.core.sda import SDASuite, SDASuiteRunner
from elspeth.core.validation import validate_settings, validate_suite
from elspeth.plugins.outputs.csv_file import CsvResultSink

logger = logging.getLogger(__name__)


def load_dotenv() -> None:
    """Load environment variables from .env file if it exists."""
    env_file = Path(".env")
    if not env_file.exists():
        return

    try:
        with env_file.open() as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Parse key=value pairs
                if "=" in line:
                    key, value = line.split("=", 1)
                    # Only set if not already in environment (env vars take precedence)
                    if key not in os.environ:
                        os.environ[key] = value
        logger.debug(f"Loaded environment variables from {env_file}")
    except Exception as e:
        logger.warning(f"Failed to load .env file: {e}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DMP data bootstrap CLI")
    parser.add_argument(
        "--settings",
        default="config/settings.yaml",
        help="Path to orchestrator settings YAML",
    )
    parser.add_argument(
        "--profile",
        default="default",
        help="Settings profile to load",
    )
    parser.add_argument(
        "--head",
        type=int,
        default=5,
        help="Number of rows to display as a quick preview (0 to skip)",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        help="Optional local path to persist the downloaded dataset",
    )
    parser.add_argument(
        "--suite-root",
        type=Path,
        help="Override suite root directory (if unset, uses settings)",
    )
    parser.add_argument(
        "--single-run",
        action="store_true",
        help="Force single experiment run even if suite settings exist",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Set logging verbosity",
    )
    parser.add_argument(
        "--disable-metrics",
        action="store_true",
        help="Disable metrics/statistical plugins from the loaded settings",
    )
    parser.add_argument(
        "--live-outputs",
        action="store_true",
        help="Allow sinks to perform live writes (disables repo dry-run modes)",
    )
    parser.add_argument(
        "--print-config",
        action="store_true",
        help="Print resolved configuration and exit (no execution)",
    )
    parser.add_argument(
        "--explain-config",
        type=str,
        metavar="KEY",
        help="Explain source of specific config key (e.g., 'rate_limiter' or 'llm.options.temperature')",
    )
    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))


def format_preview(df: pd.DataFrame, head: int) -> str:
    """Convert the dataframe preview into a printable string."""

    preview = df.head(head) if head > 0 else df.head(0)
    with pd.option_context("display.max_columns", None):
        return preview.to_string(index=False)


def _flatten_value(target: dict[str, Any], prefix: str, value: Any) -> None:
    if isinstance(value, Mapping):
        for key, inner in value.items():
            next_prefix = f"{prefix}_{key}" if prefix else key
            _flatten_value(target, next_prefix, inner)
    else:
        target[prefix] = value


def _result_to_row(record: dict[str, Any]) -> dict[str, Any]:
    row = dict(record.get("row") or {})

    def consume_response(prefix: str, response: Mapping[str, Any] | None) -> None:
        if not response:
            return
        content = response.get("content")
        if content is not None:
            row[prefix] = content
        metrics = response.get("metrics")
        if isinstance(metrics, Mapping):
            for key, value in metrics.items():
                _flatten_value(row, f"{prefix}_metric_{key}", value)

    consume_response("llm_content", record.get("response"))
    for name, response in (record.get("responses") or {}).items():
        consume_response(f"llm_{name}", response)

    for key, value in (record.get("metrics") or {}).items():
        _flatten_value(row, f"metric_{key}", value)

    retry_info = record.get("retry")
    if retry_info:
        row["retry_attempts"] = retry_info.get("attempts")
        row["retry_max_attempts"] = retry_info.get("max_attempts")
        history = retry_info.get("history")
        if history:
            row["retry_history"] = json.dumps(history)

    if "security_level" in record:
        row["security_level"] = record["security_level"]

    return row


def _print_configuration(args: argparse.Namespace, settings) -> None:
    """Print resolved configuration for debugging."""
    import yaml

    # Build configuration dictionary for display
    config_dict = {
        "datasource": {
            "plugin": type(settings.datasource).__name__,
        },
        "llm": {
            "plugin": type(settings.llm).__name__,
        },
        "prompts": settings.orchestrator_config.llm_prompt,
        "row_plugins": settings.orchestrator_config.transform_plugin_defs,
        "aggregator_plugins": settings.orchestrator_config.aggregation_transform_defs,
        "baseline_plugins": settings.orchestrator_config.baseline_plugin_defs,
        "sinks": [{"plugin": type(sink).__name__} for sink in settings.sinks],
    }

    # Add optional fields
    if settings.orchestrator_config.prompt_fields:
        config_dict["prompt_fields"] = settings.orchestrator_config.prompt_fields
    if settings.orchestrator_config.prompt_aliases:
        config_dict["prompt_aliases"] = settings.orchestrator_config.prompt_aliases
    if settings.orchestrator_config.criteria:
        config_dict["criteria"] = settings.orchestrator_config.criteria
    if settings.orchestrator_config.concurrency_config:
        config_dict["concurrency"] = settings.orchestrator_config.concurrency_config
    if settings.orchestrator_config.retry_config:
        config_dict["retry"] = settings.orchestrator_config.retry_config
    if settings.orchestrator_config.checkpoint_config:
        config_dict["checkpoint"] = settings.orchestrator_config.checkpoint_config
    if settings.orchestrator_config.halt_condition_config:
        config_dict["early_stop"] = settings.orchestrator_config.halt_condition_config
    if settings.orchestrator_config.halt_condition_plugin_defs:
        config_dict["early_stop_plugins"] = settings.orchestrator_config.halt_condition_plugin_defs
    if settings.orchestrator_config.llm_middleware_defs:
        config_dict["llm_middlewares"] = settings.orchestrator_config.llm_middleware_defs
    if settings.orchestrator_config.prompt_defaults:
        config_dict["prompt_defaults"] = settings.orchestrator_config.prompt_defaults
    if settings.rate_limiter:
        config_dict["rate_limiter"] = type(settings.rate_limiter).__name__
    if settings.cost_tracker:
        config_dict["cost_tracker"] = type(settings.cost_tracker).__name__
    if settings.suite_root:
        config_dict["suite_root"] = str(settings.suite_root)
    if settings.suite_defaults:
        config_dict["suite_defaults"] = settings.suite_defaults
    if settings.prompt_pack:
        config_dict["prompt_pack"] = settings.prompt_pack

    print("# Resolved Configuration")
    print(f"# Loaded from: {args.settings} (profile: {args.profile})")
    print()

    if args.explain_config:
        # Explain specific key
        print(f"Configuration key: {args.explain_config}")
        print()
        print("Note: Full explain() support requires preserving ConfigurationMerger instance.")
        print("Currently showing resolved value only:")
        print()

        # Navigate to the key value
        keys = args.explain_config.split(".")
        value = config_dict
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                print(f"{args.explain_config} = <not found>")
                return

        print(f"{args.explain_config} = {value}")
    else:
        # Print full config
        print(yaml.dump(config_dict, default_flow_style=False, sort_keys=False))


def run(args: argparse.Namespace) -> None:
    configure_logging(args.log_level)
    settings_report = validate_settings(args.settings, profile=args.profile)
    for warning in settings_report.warnings:
        logger.warning(warning.format())
    settings_report.raise_if_errors()
    settings = load_settings(args.settings, profile=args.profile)

    # Handle --print-config and --explain-config
    if args.print_config or args.explain_config:
        _print_configuration(args, settings)
        return
    if args.disable_metrics:
        _strip_metrics_plugins(settings)
    _configure_sink_dry_run(settings, enable_live=args.live_outputs)
    suite_root = args.suite_root or settings.suite_root

    if suite_root and not args.single_run:
        suite_validation = validate_suite(suite_root)
        for warning in suite_validation.report.warnings:
            logger.warning(warning.format())
        suite_validation.report.raise_if_errors()
        _run_suite(args, settings, suite_root, preflight=suite_validation.preflight)
    else:
        _run_single(args, settings)


def _run_single(args: argparse.Namespace, settings) -> None:
    logger.info("Running single experiment")
    orchestrator = SDAOrchestrator(
        datasource=settings.datasource,
        llm_client=settings.llm,
        sinks=settings.sinks,
        config=settings.orchestrator_config,
        rate_limiter=settings.rate_limiter,
        cost_tracker=settings.cost_tracker,
    )
    payload = orchestrator.run()

    for failure in payload.get("failures", []):
        retry = failure.get("retry") or {}
        attempts = retry.get("attempts")
        logger.error(
            "Row processing failed after %s attempts: %s",
            attempts if attempts is not None else 1,
            failure.get("error"),
        )

    rows = [_result_to_row(result) for result in payload["results"]]
    df = pd.DataFrame(rows)

    if args.output_csv:
        output_path: Path = args.output_csv
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info("Saved dataset to %s", output_path)

    if args.head and args.head > 0 and not df.empty:
        print(format_preview(df, args.head))


def _clone_suite_sinks(base_sinks: list, experiment_name: str) -> list:
    cloned = []
    for sink in base_sinks:
        if isinstance(sink, CsvResultSink):
            base_path = Path(sink.path)
            new_path = base_path.with_name(f"{experiment_name}_{base_path.name}")
            cloned.append(CsvResultSink(path=new_path, overwrite=True))
        else:
            cloned.append(sink)
    return cloned


def _run_suite(args: argparse.Namespace, settings, suite_root: Path, *, preflight: dict | None = None) -> None:
    """Run experiment suite with merged configuration."""
    logger.info("Running suite at %s", suite_root)
    suite = SDASuite.load(suite_root)
    df = settings.datasource.load()
    suite_runner = SDASuiteRunner(
        suite=suite,
        llm_client=settings.llm,
        sinks=settings.sinks,
    )

    # Use ConfigurationMerger for defaults
    merger = ConfigurationMerger()

    # Source 1: orchestrator config
    orch_config_data = {
        "prompt_system": settings.orchestrator_config.llm_prompt.get("system", ""),
        "prompt_template": settings.orchestrator_config.llm_prompt.get("user", ""),
        "prompt_fields": settings.orchestrator_config.prompt_fields,
        "criteria": settings.orchestrator_config.criteria,
        "prompt_packs": settings.prompt_packs,
    }

    # Add optional fields if present
    if settings.orchestrator_config.prompt_pack:
        orch_config_data["prompt_pack"] = settings.orchestrator_config.prompt_pack
    if settings.orchestrator_config.row_plugin_defs:
        orch_config_data["row_plugin_defs"] = settings.orchestrator_config.row_plugin_defs
    if settings.orchestrator_config.aggregator_plugin_defs:
        orch_config_data["aggregator_plugin_defs"] = settings.orchestrator_config.aggregator_plugin_defs
    if settings.orchestrator_config.baseline_plugin_defs:
        orch_config_data["baseline_plugin_defs"] = settings.orchestrator_config.baseline_plugin_defs
    if settings.orchestrator_config.sink_defs:
        orch_config_data["sink_defs"] = settings.orchestrator_config.sink_defs
    if settings.orchestrator_config.llm_middleware_defs:
        orch_config_data["llm_middleware_defs"] = settings.orchestrator_config.llm_middleware_defs
    if settings.orchestrator_config.prompt_defaults:
        orch_config_data["prompt_defaults"] = settings.orchestrator_config.prompt_defaults
    if settings.orchestrator_config.concurrency_config:
        orch_config_data["concurrency_config"] = settings.orchestrator_config.concurrency_config
    if settings.orchestrator_config.early_stop_plugin_defs:
        orch_config_data["early_stop_plugin_defs"] = settings.orchestrator_config.early_stop_plugin_defs
    if settings.orchestrator_config.early_stop_config:
        orch_config_data["early_stop_config"] = settings.orchestrator_config.early_stop_config

    # Source 2: suite_defaults (with key normalization)
    suite_defaults = settings.suite_defaults or {}
    suite_defaults_normalized = dict(suite_defaults)

    # Normalize plugin key names for consistency
    if "row_plugins" in suite_defaults_normalized:
        suite_defaults_normalized["row_plugin_defs"] = suite_defaults_normalized.pop("row_plugins")
    if "aggregator_plugins" in suite_defaults_normalized:
        suite_defaults_normalized["aggregator_plugin_defs"] = suite_defaults_normalized.pop("aggregator_plugins")
    if "baseline_plugins" in suite_defaults_normalized:
        suite_defaults_normalized["baseline_plugin_defs"] = suite_defaults_normalized.pop("baseline_plugins")
    if "llm_middlewares" in suite_defaults_normalized:
        suite_defaults_normalized["llm_middleware_defs"] = suite_defaults_normalized.pop("llm_middlewares")
    if "concurrency" in suite_defaults_normalized:
        suite_defaults_normalized["concurrency_config"] = suite_defaults_normalized.pop("concurrency")
    if "early_stop_plugins" in suite_defaults_normalized:
        suite_defaults_normalized["early_stop_plugin_defs"] = suite_defaults_normalized.pop("early_stop_plugins")
    if "early_stop" in suite_defaults_normalized:
        suite_defaults_normalized["early_stop_config"] = suite_defaults_normalized.pop("early_stop")
    if "sinks" in suite_defaults_normalized:
        suite_defaults_normalized["sink_defs"] = suite_defaults_normalized.pop("sinks")

    sources = [
        ConfigSource(name="orchestrator", data=orch_config_data, precedence=1),
        ConfigSource(name="suite_defaults", data=suite_defaults_normalized, precedence=2),
    ]

    defaults = merger.merge(*sources)

    # Add runtime instances (not part of merge)
    if settings.rate_limiter:
        defaults["rate_limiter"] = settings.rate_limiter
    if settings.cost_tracker:
        defaults["cost_tracker"] = settings.cost_tracker

    results = suite_runner.run(
        df,
        defaults=defaults,
        sink_factory=lambda exp: _clone_suite_sinks(settings.sinks, exp.name),
        preflight_info=preflight,
    )

    for name, entry in results.items():
        logger.info("Experiment %s completed with %s rows", name, len(entry["payload"]["results"]))


def _strip_metrics_plugins(settings) -> None:
    """Remove metrics plugins from settings and prompt packs when disabled."""

    row_names = {"score_extractor"}
    agg_names = {"score_stats", "score_recommendation"}
    baseline_names = {"score_delta"}

    def _filter(defs, names):
        if not defs:
            return defs
        return [entry for entry in defs if entry.get("name") not in names]

    cfg = settings.orchestrator_config
    cfg.row_plugin_defs = _filter(cfg.row_plugin_defs, row_names)
    cfg.aggregator_plugin_defs = _filter(cfg.aggregator_plugin_defs, agg_names)
    cfg.baseline_plugin_defs = _filter(cfg.baseline_plugin_defs, baseline_names)

    defaults = settings.suite_defaults or {}
    if "row_plugins" in defaults:
        defaults["row_plugins"] = _filter(defaults.get("row_plugins"), row_names)
    if "aggregator_plugins" in defaults:
        defaults["aggregator_plugins"] = _filter(defaults.get("aggregator_plugins"), agg_names)
    if "baseline_plugins" in defaults:
        defaults["baseline_plugins"] = _filter(defaults.get("baseline_plugins"), baseline_names)

    for pack in settings.prompt_packs.values():
        if isinstance(pack, dict):
            if "row_plugins" in pack:
                pack["row_plugins"] = _filter(pack.get("row_plugins"), row_names)
            if "aggregator_plugins" in pack:
                pack["aggregator_plugins"] = _filter(pack.get("aggregator_plugins"), agg_names)
            if "baseline_plugins" in pack:
                pack["baseline_plugins"] = _filter(pack.get("baseline_plugins"), baseline_names)


def _configure_sink_dry_run(settings, enable_live: bool) -> None:
    """Toggle dry-run behaviour for sinks supporting remote writes."""

    dry_run = not enable_live

    for sink in settings.sinks:
        if hasattr(sink, "dry_run"):
            sink.dry_run = dry_run

    def _update_defs(defs):
        if not defs:
            return defs
        updated = []
        for entry in defs:
            options = dict(entry.get("options", {}))
            if entry.get("plugin") in {"github_repo", "azure_devops_repo"} or "dry_run" in options:
                options["dry_run"] = dry_run
            updated.append({"plugin": entry.get("plugin"), "options": options})
        return updated

    config = settings.orchestrator_config
    config.sink_defs = _update_defs(config.sink_defs)

    suite_defaults = settings.suite_defaults or {}
    if "sinks" in suite_defaults:
        suite_defaults["sinks"] = _update_defs(suite_defaults.get("sinks"))

    for pack in settings.prompt_packs.values():
        if isinstance(pack, dict) and pack.get("sinks"):
            pack["sinks"] = _update_defs(pack.get("sinks"))


def main(argv: Iterable[str] | None = None) -> None:
    # Load .env file if it exists
    load_dotenv()

    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    run(args)


if __name__ == "__main__":  # pragma: no cover
    main()
