"""Alarm system."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Alarm:
    """An alarm entry."""

    id: str
    time: str  # HH:MM format
    label: str = ""
    enabled: bool = True
    days: list[str] = field(default_factory=list)  # e.g., ["mon", "tue", "wed"]
    sound: str = "default"
    snoozed: bool = False


class AlarmManager:
    """Manage alarms."""

    def __init__(self) -> None:
        self.alarms: dict[str, Alarm] = {}

    def set_alarm(
        self,
        time: str,
        label: str = "",
        days: Optional[list[str]] = None,
    ) -> Alarm:
        """Set a new alarm."""
        alarm_id = str(uuid.uuid4())[:8]
        alarm = Alarm(
            id=alarm_id,
            time=time,
            label=label,
            days=days or [],
        )
        self.alarms[alarm_id] = alarm
        return alarm

    def remove_alarm(self, alarm_id: str) -> bool:
        """Remove an alarm."""
        if alarm_id in self.alarms:
            del self.alarms[alarm_id]
            return True
        return False

    def toggle_alarm(self, alarm_id: str) -> Optional[Alarm]:
        """Toggle an alarm on/off."""
        alarm = self.alarms.get(alarm_id)
        if alarm:
            alarm.enabled = not alarm.enabled
        return alarm

    def snooze(self, alarm_id: str, minutes: int = 5) -> Optional[Alarm]:
        """Snooze an alarm."""
        alarm = self.alarms.get(alarm_id)
        if alarm:
            alarm.snoozed = True
            # Calculate snoozed time
            h, m = map(int, alarm.time.split(":"))
            m += minutes
            h += m // 60
            m %= 60
            h %= 24
            alarm.time = f"{h:02d}:{m:02d}"
        return alarm

    def check_due(self) -> list[Alarm]:
        """Check which alarms are due now."""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%a").lower()

        due: list[Alarm] = []
        for alarm in self.alarms.values():
            if not alarm.enabled:
                continue
            if alarm.time == current_time:
                if not alarm.days or current_day in alarm.days:
                    due.append(alarm)
        return due

    def list_all(self) -> list[Alarm]:
        """List all alarms."""
        return sorted(self.alarms.values(), key=lambda a: a.time)
