"""Multi-step workflow engine."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.automation.workflow")


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    name: str
    command: str
    status: StepStatus = StepStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    depends_on: list[str] = field(default_factory=list)


@dataclass
class Workflow:
    """A multi-step workflow."""

    id: str
    name: str
    steps: list[WorkflowStep]
    status: StepStatus = StepStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class WorkflowEngine:
    """Execute multi-step workflows with dependency management."""

    def __init__(self) -> None:
        self.workflows: dict[str, Workflow] = {}
        self._command_handler: Optional[Callable[..., Any]] = None

    def set_command_handler(self, handler: Callable[..., Any]) -> None:
        """Set the function that executes individual commands."""
        self._command_handler = handler

    def create_workflow(self, name: str, steps: list[dict[str, Any]]) -> Workflow:
        """Create a new workflow from a list of step definitions."""
        workflow_id = str(uuid.uuid4())[:8]
        workflow_steps = [
            WorkflowStep(
                name=s.get("name", f"Step {i+1}"),
                command=s["command"],
                depends_on=s.get("depends_on", []),
            )
            for i, s in enumerate(steps)
        ]
        workflow = Workflow(id=workflow_id, name=name, steps=workflow_steps)
        self.workflows[workflow_id] = workflow
        logger.info(f"Created workflow '{name}' with {len(workflow_steps)} steps")
        return workflow

    async def execute(self, workflow_id: str) -> Workflow:
        """Execute a workflow, respecting step dependencies."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow.status = StepStatus.RUNNING
        completed_steps: set[str] = set()

        for step in workflow.steps:
            # Check dependencies
            unmet = [d for d in step.depends_on if d not in completed_steps]
            if unmet:
                step.status = StepStatus.SKIPPED
                step.error = f"Unmet dependencies: {unmet}"
                logger.warning(f"Skipped step '{step.name}': unmet deps {unmet}")
                continue

            step.status = StepStatus.RUNNING
            try:
                if self._command_handler:
                    result = await self._command_handler(step.command)
                    step.result = str(result)
                step.status = StepStatus.COMPLETED
                completed_steps.add(step.name)
                logger.info(f"Step '{step.name}' completed")
            except Exception as exc:
                step.status = StepStatus.FAILED
                step.error = str(exc)
                logger.error(f"Step '{step.name}' failed: {exc}")
                workflow.status = StepStatus.FAILED
                return workflow

        all_done = all(s.status == StepStatus.COMPLETED for s in workflow.steps)
        workflow.status = StepStatus.COMPLETED if all_done else StepStatus.FAILED
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID."""
        return self.workflows.get(workflow_id)

    def list_workflows(self) -> list[Workflow]:
        """List all workflows."""
        return list(self.workflows.values())
