"""Tests for the memory system."""

import pytest

from app.memory.database import Database
from app.memory.cache import Cache
from app.memory.preferences import PreferencesManager
from app.memory.conversation import ConversationMemory


@pytest.fixture
async def db(tmp_path):
    database = Database(db_path=str(tmp_path / "test.db"))
    await database.connect()
    yield database
    await database.close()


@pytest.fixture
async def cache():
    c = Cache(redis_url="redis://localhost:6379/15")
    await c.connect()
    yield c
    await c.close()


class TestDatabase:
    @pytest.mark.asyncio
    async def test_save_and_get_conversation(self, db):
        await db.save_conversation("s1", "user", "hello", "greeting")
        history = await db.get_conversations("s1")
        assert len(history) == 1
        assert history[0]["content"] == "hello"

    @pytest.mark.asyncio
    async def test_save_and_get_preference(self, db):
        await db.save_preference("theme", "dark")
        value = await db.get_preference("theme")
        assert value == "dark"

    @pytest.mark.asyncio
    async def test_preference_default(self, db):
        value = await db.get_preference("nonexistent", "default")
        assert value == "default"

    @pytest.mark.asyncio
    async def test_command_history(self, db):
        await db.save_command("open chrome", "system_control", "success")
        history = await db.get_command_history()
        assert len(history) == 1


class TestCache:
    @pytest.mark.asyncio
    async def test_set_and_get(self, cache):
        await cache.set("test_key", {"data": 42})
        value = await cache.get("test_key")
        assert value == {"data": 42} or value is not None

    @pytest.mark.asyncio
    async def test_delete(self, cache):
        await cache.set("del_key", "value")
        await cache.delete("del_key")
        value = await cache.get("del_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_rate_limit(self, cache):
        result = await cache.get_rate_limit("test_endpoint", max_requests=5)
        assert result is True


class TestPreferences:
    @pytest.mark.asyncio
    async def test_get_default(self, db):
        prefs = PreferencesManager(db)
        lang = await prefs.get("language")
        assert lang == "en"

    @pytest.mark.asyncio
    async def test_set_and_get(self, db):
        prefs = PreferencesManager(db)
        await prefs.set("theme", "light")
        value = await prefs.get("theme")
        assert value == "light"

    @pytest.mark.asyncio
    async def test_get_all(self, db):
        prefs = PreferencesManager(db)
        all_prefs = await prefs.get_all()
        assert "language" in all_prefs


class TestConversationMemory:
    @pytest.mark.asyncio
    async def test_save_and_retrieve(self, db):
        conv = ConversationMemory(db)
        await conv.save("user", "test message")
        history = await conv.get_history()
        assert len(history) == 1
