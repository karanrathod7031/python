"""Authentication and authorization."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from app.config import get_settings
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.security.auth")


class AuthManager:
    """Manage authentication for the Jarvis API."""

    def __init__(self) -> None:
        settings = get_settings()
        self._secret_key = settings.secret_key
        self._admin_password_hash = self._hash(settings.admin_password)
        self._tokens: dict[str, datetime] = {}

    def authenticate(self, password: str) -> Optional[str]:
        """Authenticate with password and return a session token."""
        if self._hash(password) == self._admin_password_hash:
            token = secrets.token_urlsafe(32)
            self._tokens[token] = datetime.now() + timedelta(hours=24)
            logger.info("Authentication successful")
            return token
        logger.warning("Authentication failed")
        return None

    def validate_token(self, token: str) -> bool:
        """Validate a session token."""
        expiry = self._tokens.get(token)
        if expiry and datetime.now() < expiry:
            return True
        if expiry:
            del self._tokens[token]
        return False

    def revoke_token(self, token: str) -> None:
        """Revoke a session token."""
        self._tokens.pop(token, None)

    def change_password(self, old_password: str, new_password: str) -> bool:
        """Change the admin password."""
        if self._hash(old_password) == self._admin_password_hash:
            self._admin_password_hash = self._hash(new_password)
            self._tokens.clear()
            logger.info("Password changed successfully")
            return True
        return False

    def _hash(self, value: str) -> str:
        """Hash a string using SHA-256 with salt."""
        salted = f"{self._secret_key}:{value}"
        return hashlib.sha256(salted.encode()).hexdigest()


class VoiceAuth:
    """Basic voice-based authentication (voice print matching)."""

    def __init__(self) -> None:
        settings = get_settings()
        self.enabled = settings.voice_auth_enabled
        self._enrolled_prints: list[list[float]] = []

    def enroll(self, audio_features: list[float]) -> bool:
        """Enroll a voice print."""
        self._enrolled_prints.append(audio_features)
        logger.info("Voice print enrolled")
        return True

    def verify(self, audio_features: list[float], threshold: float = 0.8) -> bool:
        """Verify a voice against enrolled prints."""
        if not self.enabled or not self._enrolled_prints:
            return True  # pass-through when disabled

        for enrolled in self._enrolled_prints:
            similarity = self._cosine_similarity(audio_features, enrolled)
            if similarity >= threshold:
                return True

        logger.warning("Voice authentication failed")
        return False

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two feature vectors."""
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = sum(x**2 for x in a) ** 0.5
        mag_b = sum(x**2 for x in b) ** 0.5
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)
