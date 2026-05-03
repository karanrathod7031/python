"""Tests for automation modules."""

import pytest

from app.automation.workflow import WorkflowEngine, StepStatus


class TestWorkflowEngine:
    def test_create_workflow(self):
        engine = WorkflowEngine()
        wf = engine.create_workflow("test", [
            {"name": "step1", "command": "echo hello"},
            {"name": "step2", "command": "echo world"},
        ])
        assert wf.name == "test"
        assert len(wf.steps) == 2

    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        engine = WorkflowEngine()

        async def mock_handler(cmd):
            return f"Executed: {cmd}"

        engine.set_command_handler(mock_handler)

        wf = engine.create_workflow("test", [
            {"name": "step1", "command": "cmd1"},
            {"name": "step2", "command": "cmd2"},
        ])
        result = await engine.execute(wf.id)
        assert result.status == StepStatus.COMPLETED
        assert all(s.status == StepStatus.COMPLETED for s in result.steps)

    @pytest.mark.asyncio
    async def test_workflow_not_found(self):
        engine = WorkflowEngine()
        with pytest.raises(ValueError):
            await engine.execute("nonexistent")

    def test_list_workflows(self):
        engine = WorkflowEngine()
        engine.create_workflow("wf1", [{"command": "a"}])
        engine.create_workflow("wf2", [{"command": "b"}])
        assert len(engine.list_workflows()) == 2
