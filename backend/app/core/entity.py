"""Entity extraction from user input."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtractedEntity:
    """A single extracted entity."""

    entity_type: str
    value: str
    start: int
    end: int
    confidence: float = 1.0


class EntityExtractor:
    """Extract named entities from text using pattern matching."""

    PATTERNS: dict[str, str] = {
        "time": r"\b(\d{1,2}:\d{2}\s*(?:am|pm)?|\d{1,2}\s*(?:am|pm))\b",
        "date": r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|today|tomorrow|yesterday|"
                r"monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        "duration": r"\b(\d+)\s*(second|minute|hour|day|week|month|year)s?\b",
        "email": r"\b([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b",
        "url": r"(https?://\S+|www\.\S+)",
        "file_path": r"([a-zA-Z]:\\[\w\\.-]+|/[\w/.-]+\.\w+|~/[\w/.-]+)",
        "number": r"\b(\d+(?:\.\d+)?)\b",
        "percentage": r"\b(\d+(?:\.\d+)?)\s*%",
        "app_name": r"\b(chrome|firefox|vscode|code|terminal|spotify|"
                    r"notepad|calculator|vlc|discord|slack|telegram|whatsapp|"
                    r"youtube|netflix|github|word|excel|powerpoint|explorer)\b",
    }

    def extract(self, text: str) -> list[ExtractedEntity]:
        """Extract all entities from text."""
        entities: list[ExtractedEntity] = []
        lower_text = text.lower()

        for entity_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, lower_text, re.IGNORECASE):
                entities.append(
                    ExtractedEntity(
                        entity_type=entity_type,
                        value=match.group(1) if match.lastindex else match.group(0),
                        start=match.start(),
                        end=match.end(),
                    )
                )

        return entities

    def extract_by_type(self, text: str, entity_type: str) -> list[str]:
        """Extract entities of a specific type."""
        return [
            e.value for e in self.extract(text) if e.entity_type == entity_type
        ]

    def extract_app_name(self, text: str) -> Optional[str]:
        """Extract an application name from text."""
        results = self.extract_by_type(text, "app_name")
        return results[0] if results else None

    def extract_time(self, text: str) -> Optional[str]:
        """Extract a time reference from text."""
        results = self.extract_by_type(text, "time")
        return results[0] if results else None
