"""Tests for PromptCompiler."""

from elspeth.core.prompts import PromptEngine
from elspeth.core.sda.prompt_compiler import PromptCompiler


def test_prompt_compiler_compiles_system_and_user():
    """PromptCompiler compiles system and user prompt templates."""
    compiler = PromptCompiler(
        engine=PromptEngine(),
        system_prompt="You are {role}",
        user_prompt="Process: {text}",
        cycle_name="test-cycle",
        defaults={"role": "assistant"},
    )

    templates = compiler.compile()

    assert templates.system is not None
    assert templates.user is not None
    assert "system" in templates.system.name
    assert "user" in templates.user.name


def test_prompt_compiler_compiles_criteria():
    """PromptCompiler compiles criteria-based prompts."""
    compiler = PromptCompiler(
        engine=PromptEngine(),
        system_prompt="System",
        user_prompt="Default",
        cycle_name="test",
        criteria=[
            {"name": "accuracy", "template": "Rate accuracy: {text}"},
            {"name": "clarity", "template": "Rate clarity: {text}"},
        ],
    )

    templates = compiler.compile()

    assert len(templates.criteria) == 2
    assert "accuracy" in templates.criteria
    assert "clarity" in templates.criteria
