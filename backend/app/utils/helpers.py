"""Utility helper functions."""

from __future__ import annotations

import asyncio
import functools
import time
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def timed(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure execution time of a function."""

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        from app.utils.logger import logger

        logger.debug(f"{func.__name__} took {elapsed:.3f}s")
        return result

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        from app.utils.logger import logger

        logger.debug(f"{func.__name__} took {elapsed:.3f}s")
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper  # type: ignore[return-value]
    return sync_wrapper


def sanitize_path(path: str) -> str:
    """Remove dangerous path traversal sequences."""
    import os

    normalized = os.path.normpath(path)
    if ".." in normalized.split(os.sep):
        raise ValueError(f"Path traversal detected in: {path}")
    return normalized


def truncate(text: str, max_length: int = 500) -> str:
    """Truncate text to max_length, appending ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
