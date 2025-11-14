"""Single row processing for SDA execution."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd

    from elspeth.core.interfaces import LLMClientProtocol
    from elspeth.core.prompts import PromptEngine, PromptTemplate
    from elspeth.core.sda.llm_executor import LLMExecutor
    from elspeth.core.sda.plugins import TransformPlugin


class RowProcessor:
    """Processes single rows through LLM and transforms."""

    def __init__(
        self,
        llm_client: LLMClientProtocol,
        engine: PromptEngine,
        system_template: PromptTemplate,
        user_template: PromptTemplate,
        criteria_templates: dict[str, PromptTemplate],
        transform_plugins: list[TransformPlugin],
        criteria: list[dict[str, Any]] | None = None,
        llm_executor: LLMExecutor | None = None,
        security_level: str | None = None,
    ):
        """
        Initialize row processor.

        Args:
            llm_client: LLM client for generation
            engine: Prompt engine for rendering
            system_template: Compiled system prompt
            user_template: Compiled user prompt
            criteria_templates: Compiled criteria prompts
            transform_plugins: Transform plugins to apply
            criteria: Criteria definitions
            llm_executor: LLM executor for retry logic
            security_level: Security level for records
        """
        self.llm_client = llm_client
        self.engine = engine
        self.system_template = system_template
        self.user_template = user_template
        self.criteria_templates = criteria_templates
        self.transform_plugins = transform_plugins
        self.criteria = criteria or []
        self.llm_executor = llm_executor
        self.security_level = security_level

    def process_row(
        self,
        row: pd.Series,
        context: dict[str, Any],
        row_id: str | None,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
        """
        Process single row through LLM and transforms.

        Args:
            row: Pandas Series representing row
            context: Prompt context dictionary
            row_id: Unique row identifier

        Returns:
            Tuple of (record, failure). One will be None.
        """
        from elspeth.core.prompts import PromptRenderingError, PromptValidationError

        try:
            rendered_system = self.engine.render(self.system_template, context)

            if self.criteria:
                responses: dict[str, dict[str, Any]] = {}
                for crit in self.criteria:
                    crit_name = crit.get("name") or crit.get("template", "criteria")
                    prompt_template = self.criteria_templates[crit_name]
                    user_prompt = self.engine.render(prompt_template, context, extra={"criteria": crit_name})

                    # Use LLM executor if available, otherwise direct call
                    if self.llm_executor:
                        response = self.llm_executor.execute(
                            user_prompt,
                            {"row_id": row.get("APPID"), "criteria": crit_name},
                            system_prompt=rendered_system,
                        )
                    else:
                        response = self.llm_client.generate(
                            system=rendered_system,
                            user=user_prompt,
                            metadata={"row_id": row.get("APPID"), "criteria": crit_name},
                        )

                    responses[crit_name] = response

                first_response = next(iter(responses.values())) if responses else {}
                record: dict[str, Any] = {
                    "row": context,
                    "response": first_response,
                    "responses": responses,
                }

                # Merge metrics from all responses
                for resp in responses.values():
                    metrics = resp.get("metrics")
                    if metrics:
                        record.setdefault("metrics", {}).update(metrics)
            else:
                user_prompt = self.engine.render(self.user_template, context)

                # Use LLM executor if available
                if self.llm_executor:
                    response = self.llm_executor.execute(
                        user_prompt,
                        {"row_id": row.get("APPID")},
                        system_prompt=rendered_system,
                    )
                else:
                    response = self.llm_client.generate(
                        system=rendered_system,
                        user=user_prompt,
                        metadata={"row_id": row.get("APPID")},
                    )

                record = {"row": context, "response": response}
                metrics = response.get("metrics")
                if metrics:
                    record.setdefault("metrics", {}).update(metrics)

            # Add retry metadata if present
            retry_meta = response.get("retry")
            if retry_meta:
                record["retry"] = retry_meta

            # Apply transform plugins
            for plugin in self.transform_plugins:
                derived = plugin.transform(
                    record["row"],
                    record.get("responses") or {"default": record["response"]},
                )
                if derived:
                    record.setdefault("metrics", {}).update(derived)

            # Add security level
            if self.security_level:
                record["security_level"] = self.security_level

            return record, None

        except (PromptRenderingError, PromptValidationError) as exc:
            return None, {
                "row": context,
                "error": str(exc),
                "error_type": type(exc).__name__,
            }
        except Exception as exc:  # pylint: disable=broad-except
            import time

            failure = {
                "row": context,
                "error": str(exc),
                "timestamp": time.time(),
            }
            history = getattr(exc, "_dmp_retry_history", None)
            if history:
                failure["retry"] = {
                    "attempts": getattr(exc, "_dmp_retry_attempts", len(history)),
                    "max_attempts": getattr(exc, "_dmp_retry_max_attempts", len(history)),
                    "history": history,
                }
            return None, failure
