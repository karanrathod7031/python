"""Reminder system with persistent storage."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.assistant.reminders")


@dataclass
class Reminder:
    """A reminder entry."""

    id: str
    text: str
    remind_at: str  # ISO format datetime
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed: bool = False
    notified: bool = False
    recurring: Optional[str] = None  # "daily", "weekly", etc.


class ReminderManager:
    """Manage reminders with scheduling support."""

    def __init__(self) -> None:
        self.reminders: dict[str, Reminder] = {}

    def add(
        self,
        text: str,
        remind_at: datetime,
        recurring: Optional[str] = None,
    ) -> Reminder:
        """Create a new reminder."""
        reminder_id = str(uuid.uuid4())[:8]
        reminder = Reminder(
            id=reminder_id,
            text=text,
            remind_at=remind_at.isoformat(),
            recurring=recurring,
        )
        self.reminders[reminder_id] = reminder
        logger.info(f"Reminder added: '{text}' at {remind_at}")
        return reminder

    def remove(self, reminder_id: str) -> bool:
        """Remove a reminder."""
        if reminder_id in self.reminders:
            del self.reminders[reminder_id]
            return True
        return False

    def complete(self, reminder_id: str) -> bool:
        """Mark a reminder as completed."""
        if reminder_id in self.reminders:
            self.reminders[reminder_id].completed = True
            return True
        return False

    def get_due(self) -> list[Reminder]:
        """Get all due reminders."""
        now = datetime.now().isoformat()
        return [
            r
            for r in self.reminders.values()
            if not r.completed and not r.notified and r.remind_at <= now
        ]

    def get_upcoming(self, limit: int = 10) -> list[Reminder]:
        """Get upcoming reminders."""
        active = [r for r in self.reminders.values() if not r.completed]
        return sorted(active, key=lambda r: r.remind_at)[:limit]

    def list_all(self) -> list[Reminder]:
        """List all reminders."""
        return list(self.reminders.values())

    def mark_notified(self, reminder_id: str) -> None:
        """Mark a reminder as notified."""
        if reminder_id in self.reminders:
            self.reminders[reminder_id].notified = True
