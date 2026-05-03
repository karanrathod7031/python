"""To-do list manager."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class TodoItem:
    """A to-do list item."""

    id: str
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    completed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    due_date: Optional[str] = None
    tags: list[str] = field(default_factory=list)


class TodoManager:
    """Manage to-do items."""

    def __init__(self) -> None:
        self.items: dict[str, TodoItem] = {}

    def add(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> TodoItem:
        """Add a new to-do item."""
        item_id = str(uuid.uuid4())[:8]
        item = TodoItem(
            id=item_id,
            title=title,
            description=description,
            priority=Priority(priority),
            due_date=due_date,
            tags=tags or [],
        )
        self.items[item_id] = item
        return item

    def remove(self, item_id: str) -> bool:
        """Remove a to-do item."""
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False

    def complete(self, item_id: str) -> bool:
        """Mark a to-do item as complete."""
        if item_id in self.items:
            self.items[item_id].completed = True
            return True
        return False

    def update(self, item_id: str, **kwargs: object) -> Optional[TodoItem]:
        """Update fields on a to-do item."""
        item = self.items.get(item_id)
        if not item:
            return None
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return item

    def list_all(self, include_completed: bool = False) -> list[TodoItem]:
        """List to-do items, optionally including completed ones."""
        items = list(self.items.values())
        if not include_completed:
            items = [i for i in items if not i.completed]
        return sorted(items, key=lambda x: (x.completed, x.priority.value))

    def list_by_priority(self, priority: str) -> list[TodoItem]:
        """List items by priority level."""
        return [
            i
            for i in self.items.values()
            if i.priority.value == priority and not i.completed
        ]

    def search(self, query: str) -> list[TodoItem]:
        """Search to-do items by title or description."""
        query_lower = query.lower()
        return [
            i
            for i in self.items.values()
            if query_lower in i.title.lower() or query_lower in i.description.lower()
        ]
