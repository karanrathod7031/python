"""Tests for personal assistant modules."""

from datetime import datetime, timedelta

from app.assistant.reminders import ReminderManager
from app.assistant.todo import TodoManager, Priority
from app.assistant.calendar_mgr import CalendarManager
from app.assistant.alarm import AlarmManager
from app.assistant.briefing import DailyBriefing


class TestReminderManager:
    def test_add_reminder(self):
        mgr = ReminderManager()
        reminder = mgr.add("Study DSA", datetime.now() + timedelta(hours=1))
        assert reminder.text == "Study DSA"
        assert reminder.completed is False

    def test_complete_reminder(self):
        mgr = ReminderManager()
        reminder = mgr.add("Test", datetime.now())
        assert mgr.complete(reminder.id) is True
        assert mgr.reminders[reminder.id].completed is True

    def test_remove_reminder(self):
        mgr = ReminderManager()
        reminder = mgr.add("Remove me", datetime.now())
        assert mgr.remove(reminder.id) is True
        assert len(mgr.reminders) == 0

    def test_get_due(self):
        mgr = ReminderManager()
        mgr.add("Past", datetime.now() - timedelta(hours=1))
        mgr.add("Future", datetime.now() + timedelta(hours=1))
        due = mgr.get_due()
        assert len(due) == 1

    def test_get_upcoming(self):
        mgr = ReminderManager()
        mgr.add("A", datetime.now() + timedelta(hours=1))
        mgr.add("B", datetime.now() + timedelta(hours=2))
        upcoming = mgr.get_upcoming()
        assert len(upcoming) == 2


class TestTodoManager:
    def test_add_todo(self):
        mgr = TodoManager()
        item = mgr.add("Buy groceries", priority="high")
        assert item.title == "Buy groceries"
        assert item.priority == Priority.HIGH

    def test_complete_todo(self):
        mgr = TodoManager()
        item = mgr.add("Task")
        assert mgr.complete(item.id) is True

    def test_list_excludes_completed(self):
        mgr = TodoManager()
        item = mgr.add("Done")
        mgr.complete(item.id)
        mgr.add("Active")
        active = mgr.list_all(include_completed=False)
        assert len(active) == 1

    def test_search(self):
        mgr = TodoManager()
        mgr.add("Buy milk")
        mgr.add("Read book")
        results = mgr.search("milk")
        assert len(results) == 1


class TestCalendarManager:
    def test_add_event(self):
        mgr = CalendarManager()
        event = mgr.add_event("Meeting", datetime.now() + timedelta(hours=1))
        assert event.title == "Meeting"

    def test_remove_event(self):
        mgr = CalendarManager()
        event = mgr.add_event("Delete me", datetime.now())
        assert mgr.remove_event(event.id) is True

    def test_get_upcoming(self):
        mgr = CalendarManager()
        mgr.add_event("Soon", datetime.now() + timedelta(hours=1))
        mgr.add_event("Later", datetime.now() + timedelta(days=10))
        upcoming = mgr.get_upcoming(days=7)
        assert len(upcoming) == 1


class TestAlarmManager:
    def test_set_alarm(self):
        mgr = AlarmManager()
        alarm = mgr.set_alarm("07:00", label="Wake up")
        assert alarm.time == "07:00"

    def test_toggle_alarm(self):
        mgr = AlarmManager()
        alarm = mgr.set_alarm("08:00")
        result = mgr.toggle_alarm(alarm.id)
        assert result is not None
        assert result.enabled is False

    def test_list_alarms(self):
        mgr = AlarmManager()
        mgr.set_alarm("06:00")
        mgr.set_alarm("07:00")
        mgr.set_alarm("08:00")
        alarms = mgr.list_all()
        assert len(alarms) == 3
        assert alarms[0].time == "06:00"


class TestDailyBriefing:
    def test_generate_empty(self):
        briefing = DailyBriefing()
        result = briefing.generate([], [], [], {})
        assert "no pending items" in result.lower() or "briefing" in result.lower()

    def test_generate_with_data(self):
        briefing = DailyBriefing()
        result = briefing.generate(
            reminders=[{"text": "Call mom"}],
            todos=[{"title": "Buy groceries"}],
            events=[{"title": "Meeting", "start_time": "10:00"}],
            system_info={"cpu_percent": 45, "memory_percent": 62},
        )
        assert "Call mom" in result
        assert "Buy groceries" in result
        assert "Meeting" in result
