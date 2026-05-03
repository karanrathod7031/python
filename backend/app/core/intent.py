"""Intent detection and classification for user commands."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class IntentCategory(str, Enum):
    """Top-level intent categories."""

    SYSTEM_CONTROL = "system_control"
    FILE_OPERATION = "file_operation"
    WEB_AUTOMATION = "web_automation"
    QUESTION = "question"
    REMINDER = "reminder"
    TODO = "todo"
    ALARM = "alarm"
    EMAIL = "email"
    MONITORING = "monitoring"
    AUTOMATION = "automation"
    CONVERSATION = "conversation"
    CALENDAR = "calendar"
    TRANSLATION = "translation"
    CODE = "code"
    SEARCH = "search"
    VOLUME_BRIGHTNESS = "volume_brightness"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Detected intent from user input."""

    category: IntentCategory
    action: str
    confidence: float
    entities: dict[str, str] = field(default_factory=dict)
    raw_input: str = ""
    requires_confirmation: bool = False


# Rule-based pattern matchers
INTENT_PATTERNS: list[tuple[str, IntentCategory, str, bool]] = [
    # System control
    (r"\b(open|launch|start|run)\s+(.+)", IntentCategory.SYSTEM_CONTROL, "open_app", False),
    (r"\b(close|quit|exit|kill)\s+(.+)", IntentCategory.SYSTEM_CONTROL, "close_app", False),
    (r"\b(shutdown|shut\s*down)\b", IntentCategory.SYSTEM_CONTROL, "shutdown", True),
    (r"\b(restart|reboot)\b", IntentCategory.SYSTEM_CONTROL, "restart", True),
    (r"\block\s*(screen)?\b", IntentCategory.SYSTEM_CONTROL, "lock_screen", False),
    (r"\b(minimize|maximise|maximize)\b", IntentCategory.SYSTEM_CONTROL, "window_control", False),
    # Volume & brightness
    (r"\b(volume|sound)\s*(up|down|mute|set|increase|decrease)\b", IntentCategory.VOLUME_BRIGHTNESS, "volume", False),
    (r"\b(brightness)\s*(up|down|set|increase|decrease)\b", IntentCategory.VOLUME_BRIGHTNESS, "brightness", False),
    (r"\b(mute|unmute)\b", IntentCategory.VOLUME_BRIGHTNESS, "mute_toggle", False),
    # File operations
    (r"\b(create|make|new)\s+(file|folder|directory)\b", IntentCategory.FILE_OPERATION, "create", False),
    (r"\b(delete|remove|rm)\s+(file|folder|directory)?\s*(.+)", IntentCategory.FILE_OPERATION, "delete", True),
    (r"\b(move|mv)\s+(.+)\s+to\s+(.+)", IntentCategory.FILE_OPERATION, "move", False),
    (r"\b(copy|cp)\s+(.+)\s+to\s+(.+)", IntentCategory.FILE_OPERATION, "copy", False),
    (r"\b(find|search|locate)\s+(file|folder)?\s*(.+)", IntentCategory.FILE_OPERATION, "search", False),
    # Web
    (r"\b(google|search)\s+(for\s+)?(.+)", IntentCategory.WEB_AUTOMATION, "search", False),
    (r"\b(open|go\s+to|visit|browse)\s+(https?://\S+|www\.\S+|\S+\.(com|org|net|io)\S*)", IntentCategory.WEB_AUTOMATION, "open_url", False),
    (r"\b(open|go\s+to)\s+(youtube|google|github|stackoverflow)", IntentCategory.WEB_AUTOMATION, "open_site", False),
    # Reminders
    (r"\bremind\s+me\s+(.+)", IntentCategory.REMINDER, "set_reminder", False),
    # Todo
    (r"\b(add|create)\s+(a\s+)?to\s*do\b", IntentCategory.TODO, "add_todo", False),
    (r"\b(show|list|view)\s+(my\s+)?to\s*do", IntentCategory.TODO, "list_todos", False),
    # Alarm
    (r"\b(set|create)\s+(an?\s+)?alarm\b", IntentCategory.ALARM, "set_alarm", False),
    # Email
    (r"\b(send|write|compose)\s+(an?\s+)?email\b", IntentCategory.EMAIL, "send_email", False),
    (r"\b(read|check|show)\s+(my\s+)?email", IntentCategory.EMAIL, "read_email", False),
    # Monitoring
    (r"\b(cpu|ram|memory|disk|battery|network)\s*(usage|status|info)?\b", IntentCategory.MONITORING, "system_info", False),
    (r"\b(system|performance)\s+(status|info|monitor)", IntentCategory.MONITORING, "system_info", False),
    # Automation / scheduling
    (r"\bevery\s+(day|hour|minute|week)\b", IntentCategory.AUTOMATION, "schedule_task", False),
    (r"\bschedule\b", IntentCategory.AUTOMATION, "schedule_task", False),
    # Translation
    (r"\btranslate\s+(.+)", IntentCategory.TRANSLATION, "translate", False),
    # Code
    (r"\b(debug|explain|write|generate)\s+(code|function|script)\b", IntentCategory.CODE, "code_assist", False),
    # Search
    (r"\bsearch\s+(.+)", IntentCategory.SEARCH, "search", False),
    # Calendar
    (r"\b(calendar|event|meeting|schedule)\b", IntentCategory.CALENDAR, "calendar", False),
]


class IntentDetector:
    """Detect user intent using rule-based patterns with optional LLM fallback."""

    def detect(self, text: str) -> Intent:
        """Classify text into an intent using pattern matching."""
        normalized = text.strip().lower()

        for pattern, category, action, needs_confirm in INTENT_PATTERNS:
            match = re.search(pattern, normalized, re.IGNORECASE)
            if match:
                entities = self._extract_entities(match, category, normalized)
                return Intent(
                    category=category,
                    action=action,
                    confidence=0.85,
                    entities=entities,
                    raw_input=text,
                    requires_confirmation=needs_confirm,
                )

        if normalized.endswith("?") or normalized.startswith(("what", "who", "how", "why", "when", "where", "is", "can", "do", "does")):
            return Intent(
                category=IntentCategory.QUESTION,
                action="answer",
                confidence=0.7,
                raw_input=text,
            )

        return Intent(
            category=IntentCategory.CONVERSATION,
            action="chat",
            confidence=0.5,
            raw_input=text,
        )

    def _extract_entities(
        self, match: re.Match, category: IntentCategory, text: str  # type: ignore[type-arg]
    ) -> dict[str, str]:
        """Extract entities from a regex match."""
        entities: dict[str, str] = {}
        groups = match.groups()

        if category == IntentCategory.SYSTEM_CONTROL and len(groups) >= 2:
            entities["target"] = groups[1].strip()
        elif category == IntentCategory.FILE_OPERATION and len(groups) >= 2:
            entities["target"] = groups[-1].strip()
        elif category == IntentCategory.WEB_AUTOMATION and len(groups) >= 2:
            entities["query"] = groups[-1].strip()
        elif category == IntentCategory.REMINDER and groups:
            entities["reminder_text"] = groups[0].strip()

        time_match = re.search(
            r"(?:at|by)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", text
        )
        if time_match:
            entities["time"] = time_match.group(1).strip()

        return entities
