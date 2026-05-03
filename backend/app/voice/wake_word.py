"""Wake word detection for hands-free activation."""

from __future__ import annotations

import re
from typing import Callable, Optional

from app.config import get_settings
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.voice.wake_word")


class WakeWordDetector:
    """Detect wake word in transcribed text or audio stream."""

    def __init__(self, wake_word: Optional[str] = None):
        settings = get_settings()
        self.wake_word = (wake_word or settings.wake_word).lower()
        self._callbacks: list[Callable[[str], None]] = []
        self._is_listening = False

    def check_text(self, text: str) -> tuple[bool, str]:
        """Check if the wake word appears in text.

        Returns (detected, remaining_text_after_wake_word).
        """
        lower = text.lower().strip()
        pattern = re.compile(rf"\b{re.escape(self.wake_word)}\b", re.IGNORECASE)
        match = pattern.search(lower)
        if match:
            remaining = text[match.end():].strip().lstrip(",").strip()
            logger.info(f"Wake word detected! Command: {remaining[:80]}")
            return True, remaining
        return False, text

    def on_wake(self, callback: Callable[[str], None]) -> None:
        """Register a callback for when the wake word is detected."""
        self._callbacks.append(callback)

    def _notify(self, command: str) -> None:
        """Notify all registered callbacks."""
        for cb in self._callbacks:
            try:
                cb(command)
            except Exception as exc:
                logger.error(f"Wake word callback error: {exc}")

    @property
    def is_listening(self) -> bool:
        return self._is_listening

    def start(self) -> None:
        """Start wake word listening."""
        self._is_listening = True
        logger.info(f"Wake word detection started (word: '{self.wake_word}')")

    def stop(self) -> None:
        """Stop wake word listening."""
        self._is_listening = False
        logger.info("Wake word detection stopped")
