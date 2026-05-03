"""Settings and configuration API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/settings", tags=["settings"])


class LoginRequest(BaseModel):
    password: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class VoiceSettingsRequest(BaseModel):
    voice: str = ""
    language: str = ""
    wake_word: str = ""


@router.post("/login")
async def login(request: LoginRequest) -> dict[str, Any]:
    """Authenticate and get a session token."""
    from app.main import get_auth

    auth = get_auth()
    token = auth.authenticate(request.password)
    if token:
        return {"status": "success", "token": token}
    return {"status": "error", "message": "Invalid password"}


@router.post("/change-password")
async def change_password(request: PasswordChangeRequest) -> dict[str, str]:
    """Change the admin password."""
    from app.main import get_auth

    auth = get_auth()
    if auth.change_password(request.old_password, request.new_password):
        return {"status": "success", "message": "Password changed"}
    return {"status": "error", "message": "Invalid current password"}


@router.post("/voice")
async def update_voice_settings(request: VoiceSettingsRequest) -> dict[str, str]:
    """Update voice settings."""
    from app.main import get_stt, get_tts

    if request.voice:
        tts = get_tts()
        tts.set_voice(request.voice)
    if request.language:
        stt = get_stt()
        stt.set_language(request.language)
    return {"status": "success", "message": "Voice settings updated"}


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "jarvis-ai-assistant"}
