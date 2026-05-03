"""User preferences manager — learn and store user habits."""

from __future__ import annotations

from typing import Any, Optional

from app.memory.database import Database
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.memory.preferences")


class PreferencesManager:
    """Manage user preferences and learned habits."""

    DEFAULT_PREFS: dict[str, Any] = {
        "language": "en",
        "tts_voice": "en-US-GuyNeural",
        "wake_word": "jarvis",
        "theme": "dark",
        "greeting_name": "User",
        "confirmation_required": True,
        "auto_brightness": False,
        "notification_sound": True,
    }

    def __init__(self, db: Database) -> None:
        self.db = db

    async def get(self, key: str, default: Any = None) -> Any:
        """Get a preference value."""
        result = await self.db.get_preference(key)
        if result is not None:
            return result
        return default or self.DEFAULT_PREFS.get(key)

    async def set(self, key: str, value: Any) -> None:
        """Set a preference value."""
        await self.db.save_preference(key, value)
        logger.info(f"Preference updated: {key} = {value}")

    async def get_all(self) -> dict[str, Any]:
        """Get all preferences with defaults."""
        prefs = dict(self.DEFAULT_PREFS)
        for key in self.DEFAULT_PREFS:
            stored = await self.db.get_preference(key)
            if stored is not None:
                prefs[key] = stored
        return prefs

    async def reset(self, key: Optional[str] = None) -> None:
        """Reset preferences to defaults."""
        if key:
            default = self.DEFAULT_PREFS.get(key)
            if default is not None:
                await self.db.save_preference(key, default)
        else:
            for k, v in self.DEFAULT_PREFS.items():
                await self.db.save_preference(k, v)

    async def learn_habit(self, action: str, context: str) -> None:
        """Record a user habit for personalization."""
        habits_key = f"habit:{action}"
        existing = await self.db.get_preference(habits_key)
        if existing and isinstance(existing, list):
            existing.append(context)
            existing = existing[-20:]  # keep last 20
        else:
            existing = [context]
        await self.db.save_preference(habits_key, existing)
