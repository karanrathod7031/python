"""SQLite database operations for persistent storage."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Optional

import aiosqlite

from app.config import get_settings
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.memory.database")


class Database:
    """Async SQLite database for Jarvis persistent storage."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            settings = get_settings()
            db_path = settings.database_url.replace("sqlite:///", "")
        self.db_path = db_path
        self._db: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """Open the database connection and create tables."""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self._db = await aiosqlite.connect(self.db_path)
        self._db.row_factory = aiosqlite.Row
        await self._create_tables()
        logger.info(f"Database connected: {self.db_path}")

    async def close(self) -> None:
        """Close the database connection."""
        if self._db:
            await self._db.close()
            self._db = None

    async def _create_tables(self) -> None:
        """Create required tables if they don't exist."""
        assert self._db is not None
        await self._db.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                intent TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                recurring TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS todos (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT DEFAULT 'medium',
                completed INTEGER DEFAULT 0,
                due_date TEXT,
                tags TEXT DEFAULT '[]',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                description TEXT DEFAULT '',
                location TEXT DEFAULT '',
                recurring TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                intent TEXT,
                result TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_conversations_session
                ON conversations(session_id);
            CREATE INDEX IF NOT EXISTS idx_reminders_remind_at
                ON reminders(remind_at);
            CREATE INDEX IF NOT EXISTS idx_command_history_timestamp
                ON command_history(timestamp);
        """)
        await self._db.commit()

    async def save_conversation(
        self,
        session_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
    ) -> None:
        """Save a conversation turn."""
        assert self._db is not None
        await self._db.execute(
            "INSERT INTO conversations (session_id, role, content, intent) VALUES (?, ?, ?, ?)",
            (session_id, role, content, intent),
        )
        await self._db.commit()

    async def get_conversations(
        self, session_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Retrieve conversation history for a session."""
        assert self._db is not None
        cursor = await self._db.execute(
            "SELECT role, content, intent, timestamp FROM conversations "
            "WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in reversed(rows)]

    async def save_preference(self, key: str, value: Any) -> None:
        """Save a user preference."""
        assert self._db is not None
        serialized = json.dumps(value) if not isinstance(value, str) else value
        await self._db.execute(
            "INSERT OR REPLACE INTO preferences (key, value, updated_at) VALUES (?, ?, ?)",
            (key, serialized, datetime.now().isoformat()),
        )
        await self._db.commit()

    async def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        assert self._db is not None
        cursor = await self._db.execute(
            "SELECT value FROM preferences WHERE key = ?", (key,)
        )
        row = await cursor.fetchone()
        if row:
            try:
                return json.loads(row["value"])
            except (json.JSONDecodeError, TypeError):
                return row["value"]
        return default

    async def save_command(
        self, command: str, intent: Optional[str] = None, result: Optional[str] = None
    ) -> None:
        """Log a command execution."""
        assert self._db is not None
        await self._db.execute(
            "INSERT INTO command_history (command, intent, result) VALUES (?, ?, ?)",
            (command, intent, result),
        )
        await self._db.commit()

    async def get_command_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get recent command history."""
        assert self._db is not None
        cursor = await self._db.execute(
            "SELECT command, intent, result, timestamp FROM command_history "
            "ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in reversed(rows)]
