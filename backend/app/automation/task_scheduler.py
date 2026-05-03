"""Task scheduler for recurring and one-time tasks."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.automation.scheduler")


@dataclass
class ScheduledTask:
    """A scheduled task entry."""

    id: str
    name: str
    task_type: str  # "once", "interval", "cron"
    command: str
    schedule: str
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_run: Optional[str] = None
    run_count: int = 0


class TaskScheduler:
    """Schedule and manage recurring tasks."""

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.tasks: dict[str, ScheduledTask] = {}
        self._callbacks: dict[str, Callable[..., Any]] = {}

    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Task scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Task scheduler stopped")

    def add_interval_task(
        self,
        name: str,
        command: str,
        callback: Callable[..., Any],
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ) -> ScheduledTask:
        """Schedule a task to run at regular intervals."""
        task_id = str(uuid.uuid4())[:8]
        schedule_str = f"every {hours}h {minutes}m {seconds}s"

        self.scheduler.add_job(
            callback,
            IntervalTrigger(hours=hours, minutes=minutes, seconds=seconds),
            id=task_id,
            args=[command],
        )

        task = ScheduledTask(
            id=task_id,
            name=name,
            task_type="interval",
            command=command,
            schedule=schedule_str,
        )
        self.tasks[task_id] = task
        logger.info(f"Scheduled interval task: {name} ({schedule_str})")
        return task

    def add_cron_task(
        self,
        name: str,
        command: str,
        callback: Callable[..., Any],
        cron_expression: str,
    ) -> ScheduledTask:
        """Schedule a task using a cron expression."""
        task_id = str(uuid.uuid4())[:8]

        parts = cron_expression.split()
        trigger = CronTrigger(
            minute=parts[0] if len(parts) > 0 else "*",
            hour=parts[1] if len(parts) > 1 else "*",
            day=parts[2] if len(parts) > 2 else "*",
            month=parts[3] if len(parts) > 3 else "*",
            day_of_week=parts[4] if len(parts) > 4 else "*",
        )

        self.scheduler.add_job(callback, trigger, id=task_id, args=[command])

        task = ScheduledTask(
            id=task_id,
            name=name,
            task_type="cron",
            command=command,
            schedule=cron_expression,
        )
        self.tasks[task_id] = task
        logger.info(f"Scheduled cron task: {name} ({cron_expression})")
        return task

    def add_one_time_task(
        self,
        name: str,
        command: str,
        callback: Callable[..., Any],
        run_at: datetime,
    ) -> ScheduledTask:
        """Schedule a one-time task."""
        task_id = str(uuid.uuid4())[:8]

        self.scheduler.add_job(
            callback,
            DateTrigger(run_date=run_at),
            id=task_id,
            args=[command],
        )

        task = ScheduledTask(
            id=task_id,
            name=name,
            task_type="once",
            command=command,
            schedule=run_at.isoformat(),
        )
        self.tasks[task_id] = task
        logger.info(f"Scheduled one-time task: {name} at {run_at}")
        return task

    def remove_task(self, task_id: str) -> bool:
        """Remove a scheduled task."""
        if task_id in self.tasks:
            try:
                self.scheduler.remove_job(task_id)
            except Exception:
                pass
            del self.tasks[task_id]
            logger.info(f"Removed task: {task_id}")
            return True
        return False

    def list_tasks(self) -> list[ScheduledTask]:
        """List all scheduled tasks."""
        return list(self.tasks.values())

    def pause_task(self, task_id: str) -> bool:
        """Pause a scheduled task."""
        if task_id in self.tasks:
            self.scheduler.pause_job(task_id)
            self.tasks[task_id].enabled = False
            return True
        return False

    def resume_task(self, task_id: str) -> bool:
        """Resume a paused task."""
        if task_id in self.tasks:
            self.scheduler.resume_job(task_id)
            self.tasks[task_id].enabled = True
            return True
        return False
