"""Prompt template compilation for SDA execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from elspeth.core.prompts import PromptEngine, PromptTemplate


@dataclass
class CompiledPrompts:
    """Compiled prompt templates."""

    system: PromptTemplate
    user: PromptTemplate
    criteria: Dict[str, PromptTemplate]


class PromptCompiler:
    """Compiles Jinja2 prompt templates for SDA execution."""

    def __init__(
        self,
        engine: PromptEngine,
        system_prompt: str,
        user_prompt: str,
        cycle_name: str,
        defaults: Dict[str, Any] | None = None,
        criteria: list[Dict[str, Any]] | None = None,
    ):
        """
        Initialize prompt compiler.

        Args:
            engine: PromptEngine instance
            system_prompt: System prompt template
            user_prompt: User prompt template
            cycle_name: Name of SDA cycle (for template naming)
            defaults: Default values for template variables
            criteria: Criteria-based prompt definitions
        """
        self.engine = engine
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.cycle_name = cycle_name
        self.defaults = defaults or {}
        self.criteria = criteria or []

    def compile(self) -> CompiledPrompts:
        """Compile all prompt templates."""
        system_template = self.engine.compile(
            self.system_prompt,
            name=f"{self.cycle_name}:system",
            defaults=self.defaults,
        )

        user_template = self.engine.compile(
            self.user_prompt,
            name=f"{self.cycle_name}:user",
            defaults=self.defaults,
        )

        criteria_templates: Dict[str, PromptTemplate] = {}
        for crit in self.criteria:
            template_text = crit.get("template", self.user_prompt)
            crit_name = crit.get("name") or template_text
            crit_defaults = dict(self.defaults)
            crit_defaults.update(crit.get("defaults", {}))

            criteria_templates[crit_name] = self.engine.compile(
                template_text,
                name=f"{self.cycle_name}:criteria:{crit_name}",
                defaults=crit_defaults,
            )

        return CompiledPrompts(
            system=system_template,
            user=user_template,
            criteria=criteria_templates,
        )
