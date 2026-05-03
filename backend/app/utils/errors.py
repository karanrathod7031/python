"""Custom exception classes for Jarvis."""

from __future__ import annotations


class JarvisError(Exception):
    """Base exception for all Jarvis errors."""


class LLMError(JarvisError):
    """Raised when the LLM service is unavailable or returns an error."""


class VoiceError(JarvisError):
    """Raised for speech-to-text or text-to-speech failures."""


class SystemControlError(JarvisError):
    """Raised when a system control operation fails."""


class AutomationError(JarvisError):
    """Raised when an automation task fails."""


class MemoryError(JarvisError):
    """Raised when a memory operation fails."""


class SecurityError(JarvisError):
    """Raised for authentication or authorization failures."""


class PluginError(JarvisError):
    """Raised when a plugin fails to load or execute."""


class ConfirmationRequired(JarvisError):
    """Raised when a risky action requires user confirmation."""

    def __init__(self, action: str, details: str = ""):
        self.action = action
        self.details = details
        super().__init__(f"Confirmation required for: {action}. {details}")
