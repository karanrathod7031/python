"""Conversation memory for long-term storage and retrieval."""

from __future__ import annotations

import uuid
from typing import Any, Optional

from app.memory.database import Database
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.memory.conversation")


class ConversationMemory:
    """Persist and retrieve conversation history."""

    def __init__(self, db: Database) -> None:
        self.db = db
        self.session_id = str(uuid.uuid4())[:8]

    def new_session(self) -> str:
        """Start a new conversation session."""
        self.session_id = str(uuid.uuid4())[:8]
        logger.info(f"New conversation session: {self.session_id}")
        return self.session_id

    async def save(
        self,
        role: str,
        content: str,
        intent: Optional[str] = None,
    ) -> None:
        """Save a conversation turn to persistent storage."""
        await self.db.save_conversation(
            session_id=self.session_id,
            role=role,
            content=content,
            intent=intent,
        )

    async def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get conversation history for the current session."""
        return await self.db.get_conversations(self.session_id, limit)

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search across all conversation history."""
        # Simple text search across all sessions
        if self.db._db is None:
            return []
        cursor = await self.db._db.execute(
            "SELECT session_id, role, content, timestamp FROM conversations "
            "WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{query}%", limit),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
