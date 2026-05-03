"""Redis cache for short-term memory and fast lookups."""

from __future__ import annotations

import json
from typing import Any, Optional

from app.config import get_settings
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.memory.cache")


class Cache:
    """Redis-based cache for short-term data and rate limiting."""

    def __init__(self, redis_url: Optional[str] = None) -> None:
        settings = get_settings()
        self.redis_url = redis_url or settings.redis_url
        self._client = None

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            import redis.asyncio as aioredis

            self._client = aioredis.from_url(
                self.redis_url, decode_responses=True
            )
            await self._client.ping()
            logger.info("Redis connected")
        except ImportError:
            logger.warning("redis package not installed, using in-memory fallback")
            self._client = None
            self._memory: dict[str, Any] = {}
        except Exception as exc:
            logger.warning(f"Redis connection failed: {exc}, using in-memory fallback")
            self._client = None
            self._memory = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if self._client:
            value = await self._client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        return self._memory.get(key) if hasattr(self, "_memory") else None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set a value in cache with TTL in seconds."""
        serialized = json.dumps(value) if not isinstance(value, str) else value
        if self._client:
            await self._client.set(key, serialized, ex=ttl)
        elif hasattr(self, "_memory"):
            self._memory[key] = value

    async def delete(self, key: str) -> None:
        """Delete a key from cache."""
        if self._client:
            await self._client.delete(key)
        elif hasattr(self, "_memory"):
            self._memory.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if self._client:
            return bool(await self._client.exists(key))
        return key in self._memory if hasattr(self, "_memory") else False

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in cache (for rate limiting)."""
        if self._client:
            return await self._client.incrby(key, amount)
        if hasattr(self, "_memory"):
            current = self._memory.get(key, 0)
            self._memory[key] = current + amount
            return self._memory[key]
        return 0

    async def get_rate_limit(self, key: str, max_requests: int, window: int = 60) -> bool:
        """Check rate limit: returns True if request is allowed."""
        count_key = f"rate:{key}"
        count = await self.increment(count_key)
        if count == 1 and self._client:
            await self._client.expire(count_key, window)
        return count <= max_requests

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._client:
            await self._client.close()
