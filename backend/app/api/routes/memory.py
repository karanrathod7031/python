"""Memory and preferences API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/memory", tags=["memory"])


class PreferenceRequest(BaseModel):
    key: str
    value: Any


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


@router.get("/preferences")
async def get_all_preferences() -> dict[str, Any]:
    """Get all user preferences."""
    from app.main import get_preferences

    prefs = get_preferences()
    return {"preferences": await prefs.get_all()}


@router.post("/preferences")
async def set_preference(request: PreferenceRequest) -> dict[str, str]:
    """Set a user preference."""
    from app.main import get_preferences

    prefs = get_preferences()
    await prefs.set(request.key, request.value)
    return {"status": "success", "message": f"Preference '{request.key}' updated"}


@router.get("/preferences/{key}")
async def get_preference(key: str) -> dict[str, Any]:
    """Get a specific preference."""
    from app.main import get_preferences

    prefs = get_preferences()
    value = await prefs.get(key)
    return {"key": key, "value": value}


@router.get("/history")
async def get_command_history(limit: int = 50) -> dict[str, Any]:
    """Get command history."""
    from app.main import get_database

    db = get_database()
    history = await db.get_command_history(limit)
    return {"history": history}


@router.post("/conversations/search")
async def search_conversations(request: SearchRequest) -> dict[str, Any]:
    """Search conversation history."""
    from app.main import get_conversation_memory

    conv = get_conversation_memory()
    results = await conv.search(request.query, request.limit)
    return {"results": results, "count": len(results)}
