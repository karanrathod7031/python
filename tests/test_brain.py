"""Tests for the core brain module."""

import pytest

from app.core.brain import Brain


@pytest.fixture
def brain():
    return Brain()


class TestBrain:
    @pytest.mark.asyncio
    async def test_process_greeting(self, brain):
        result = await brain.process("hello")
        assert result["intent"] in ("conversation", "question")
        assert "type" in result

    @pytest.mark.asyncio
    async def test_process_system_command(self, brain):
        result = await brain.process("open chrome")
        assert result["intent"] == "system_control"
        assert result["action"] == "open_app"

    @pytest.mark.asyncio
    async def test_process_question(self, brain):
        result = await brain.process("what is python?")
        assert result["intent"] in ("question", "conversation")

    @pytest.mark.asyncio
    async def test_confirmation_flow(self, brain):
        result = await brain.process("shutdown")
        assert result["type"] == "confirmation_required"

        result2 = await brain.process("yes")
        assert result2.get("confirmed") is True or result2["type"] == "command"

    @pytest.mark.asyncio
    async def test_context_maintained(self, brain):
        await brain.process("hello")
        await brain.process("how are you?")
        history = brain.context.get_history()
        assert len(history) >= 4  # 2 user + 2 assistant turns

    @pytest.mark.asyncio
    async def test_close(self, brain):
        await brain.close()
