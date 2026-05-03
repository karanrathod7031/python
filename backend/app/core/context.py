"""Conversation context management for multi-turn interactions."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)
    intent: Optional[str] = None
    entities: dict[str, str] = field(default_factory=dict)


class ContextManager:
    """Manage short-term conversation context and multi-turn state."""

    def __init__(self, max_turns: int = 20, context_timeout: float = 300.0):
        self.max_turns = max_turns
        self.context_timeout = context_timeout
        self.history: deque[ConversationTurn] = deque(maxlen=max_turns)
        self._active_topic: Optional[str] = None
        self._pending_confirmation: Optional[dict[str, str]] = None

    def add_turn(
        self,
        role: str,
        content: str,
        intent: Optional[str] = None,
        entities: Optional[dict[str, str]] = None,
    ) -> None:
        """Add a conversation turn to history."""
        self.history.append(
            ConversationTurn(
                role=role,
                content=content,
                intent=intent,
                entities=entities or {},
            )
        )

    def get_history(self, max_turns: Optional[int] = None) -> list[dict[str, str]]:
        """Return conversation history as a list of role/content dicts."""
        self._prune_stale()
        limit = max_turns or self.max_turns
        recent = list(self.history)[-limit:]
        return [{"role": t.role, "content": t.content} for t in recent]

    def get_last_user_message(self) -> Optional[str]:
        """Return the most recent user message."""
        for turn in reversed(self.history):
            if turn.role == "user":
                return turn.content
        return None

    def get_last_intent(self) -> Optional[str]:
        """Return the most recent detected intent."""
        for turn in reversed(self.history):
            if turn.intent:
                return turn.intent
        return None

    def set_pending_confirmation(self, action: str, details: str) -> None:
        """Store a pending confirmation for risky actions."""
        self._pending_confirmation = {"action": action, "details": details}

    def get_pending_confirmation(self) -> Optional[dict[str, str]]:
        """Retrieve and clear the pending confirmation."""
        pending = self._pending_confirmation
        self._pending_confirmation = None
        return pending

    def set_topic(self, topic: str) -> None:
        """Set the current conversation topic."""
        self._active_topic = topic

    @property
    def topic(self) -> Optional[str]:
        return self._active_topic

    def clear(self) -> None:
        """Reset all context."""
        self.history.clear()
        self._active_topic = None
        self._pending_confirmation = None

    def _prune_stale(self) -> None:
        """Remove turns older than the context timeout."""
        now = time.time()
        while self.history and (now - self.history[0].timestamp) > self.context_timeout:
            self.history.popleft()

    def to_llm_messages(self, system_prompt: str = "") -> list[dict[str, str]]:
        """Format context as LLM-compatible messages."""
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.get_history())
        return messages
