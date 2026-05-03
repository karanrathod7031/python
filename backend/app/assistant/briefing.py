"""Daily briefing generator."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.assistant.briefing")


class DailyBriefing:
    """Generate daily briefing summaries."""

    def generate(
        self,
        reminders: list[dict[str, Any]],
        todos: list[dict[str, Any]],
        events: list[dict[str, Any]],
        system_info: dict[str, Any],
    ) -> str:
        """Generate a daily briefing summary."""
        now = datetime.now()
        greeting = self._get_greeting(now.hour)
        date_str = now.strftime("%A, %B %d, %Y")

        sections: list[str] = [
            f"{greeting} Here's your briefing for {date_str}.",
            "",
        ]

        # Calendar events
        if events:
            sections.append(f"📅 You have {len(events)} event(s) today:")
            for event in events[:5]:
                sections.append(f"  - {event.get('title', 'Event')} at {event.get('start_time', 'TBD')}")
            sections.append("")

        # Reminders
        if reminders:
            sections.append(f"🔔 {len(reminders)} reminder(s):")
            for reminder in reminders[:5]:
                sections.append(f"  - {reminder.get('text', '')}")
            sections.append("")

        # To-dos
        if todos:
            sections.append(f"✅ {len(todos)} pending to-do(s):")
            for todo in todos[:5]:
                sections.append(f"  - {todo.get('title', '')}")
            sections.append("")

        # System status
        if system_info:
            cpu = system_info.get("cpu_percent", "N/A")
            ram = system_info.get("memory_percent", "N/A")
            battery = system_info.get("battery_percent")
            sections.append(f"💻 System: CPU {cpu}% | RAM {ram}%")
            if battery is not None:
                sections.append(f"🔋 Battery: {battery}%")

        if len(sections) <= 3:
            sections.append("You have no pending items. Enjoy your day!")

        return "\n".join(sections)

    def _get_greeting(self, hour: int) -> str:
        """Get time-appropriate greeting."""
        if hour < 12:
            return "Good morning!"
        elif hour < 17:
            return "Good afternoon!"
        elif hour < 21:
            return "Good evening!"
        return "Hello!"
