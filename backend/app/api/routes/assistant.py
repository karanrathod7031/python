"""Main assistant API routes — process commands, chat, voice."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


class CommandRequest(BaseModel):
    text: str
    session_id: str | None = None


class CommandResponse(BaseModel):
    type: str
    intent: str
    action: str
    response: str | None = None
    confidence: float = 0.0
    entities: dict[str, str] = {}
    requires_confirmation: bool = False


@router.post("/command", response_model=CommandResponse)
async def process_command(request: CommandRequest) -> dict[str, Any]:
    """Process a text command through the brain."""
    from app.main import get_brain

    brain = get_brain()
    result = await brain.process(request.text)
    return result


@router.post("/voice")
async def process_voice(audio: UploadFile = File(...)) -> dict[str, Any]:
    """Process voice input — transcribe and execute."""
    from app.main import get_brain, get_stt, get_tts

    stt = get_stt()
    audio_bytes = await audio.read()
    transcribed = stt.transcribe_bytes(audio_bytes)

    if not transcribed:
        return {"error": "Could not transcribe audio"}

    brain = get_brain()
    result = await brain.process(transcribed)

    # Generate TTS response
    tts = get_tts()
    response_text = result.get("response", "")
    if response_text:
        audio_path = await tts.synthesize(response_text)
        result["audio_path"] = audio_path

    result["transcribed_text"] = transcribed
    return result


@router.get("/history")
async def get_history(limit: int = 50) -> dict[str, Any]:
    """Get conversation history."""
    from app.main import get_brain

    brain = get_brain()
    history = brain.context.get_history(limit)
    return {"history": history}


@router.post("/clear-context")
async def clear_context() -> dict[str, str]:
    """Clear the current conversation context."""
    from app.main import get_brain

    brain = get_brain()
    brain.context.clear()
    return {"status": "success", "message": "Context cleared"}
