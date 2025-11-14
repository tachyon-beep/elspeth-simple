"""Tests for PromptCompiler."""

from elspeth.core.sda.prompt_compiler import PromptCompiler
from elspeth.core.prompts import PromptEngine


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
