"""Calendar and event management."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class CalendarEvent:
    """A calendar event."""

    id: str
    title: str
    start_time: str
    end_time: str
    description: str = ""
    location: str = ""
    recurring: Optional[str] = None
    reminder_minutes: int = 15


class CalendarManager:
    """Manage calendar events."""

    def __init__(self) -> None:
        self.events: dict[str, CalendarEvent] = {}

    def add_event(
        self,
        title: str,
        start_time: datetime,
        duration_minutes: int = 60,
        description: str = "",
        location: str = "",
        recurring: Optional[str] = None,
    ) -> CalendarEvent:
        """Add a new calendar event."""
        event_id = str(uuid.uuid4())[:8]
        end_time = start_time + timedelta(minutes=duration_minutes)

        event = CalendarEvent(
            id=event_id,
            title=title,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            description=description,
            location=location,
            recurring=recurring,
        )
        self.events[event_id] = event
        return event

    def remove_event(self, event_id: str) -> bool:
        """Remove a calendar event."""
        if event_id in self.events:
            del self.events[event_id]
            return True
        return False

    def get_today_events(self) -> list[CalendarEvent]:
        """Get today's events."""
        today = datetime.now().date().isoformat()
        return [
            e
            for e in self.events.values()
            if e.start_time.startswith(today)
        ]

    def get_upcoming(self, days: int = 7) -> list[CalendarEvent]:
        """Get events within the next N days."""
        now = datetime.now()
        cutoff = (now + timedelta(days=days)).isoformat()
        now_str = now.isoformat()
        upcoming = [
            e
            for e in self.events.values()
            if now_str <= e.start_time <= cutoff
        ]
        return sorted(upcoming, key=lambda e: e.start_time)

    def list_all(self) -> list[CalendarEvent]:
        """List all calendar events."""
        return sorted(self.events.values(), key=lambda e: e.start_time)
