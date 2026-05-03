"""Text-to-speech using edge-tts and pyttsx3 fallback."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.voice.tts")

VOICE_MAP = {
    "en-male": "en-US-GuyNeural",
    "en-female": "en-US-JennyNeural",
    "hi-male": "hi-IN-MadhurNeural",
    "hi-female": "hi-IN-SwaraNeural",
}


class TextToSpeech:
    """Convert text to speech using edge-tts with pyttsx3 fallback."""

    def __init__(self, voice: Optional[str] = None):
        settings = get_settings()
        self.voice = voice or settings.tts_voice
        self.output_dir = Path(tempfile.gettempdir()) / "jarvis_tts"
        self.output_dir.mkdir(exist_ok=True)

    async def synthesize(self, text: str, output_path: Optional[str] = None) -> str:
        """Synthesize text to an audio file and return the file path."""
        if not output_path:
            output_path = str(self.output_dir / "output.mp3")

        try:
            import edge_tts

            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_path)
            logger.info(f"TTS audio saved to: {output_path}")
            return output_path
        except ImportError:
            logger.warning("edge-tts not available, trying pyttsx3 fallback")
            return self._pyttsx3_fallback(text, output_path)
        except Exception as exc:
            logger.error(f"edge-tts failed: {exc}, trying pyttsx3")
            return self._pyttsx3_fallback(text, output_path)

    async def synthesize_bytes(self, text: str) -> bytes:
        """Synthesize text and return raw audio bytes."""
        path = await self.synthesize(text)
        if path and Path(path).exists():
            return Path(path).read_bytes()
        return b""

    def _pyttsx3_fallback(self, text: str, output_path: str) -> str:
        """Fallback TTS using pyttsx3 (offline)."""
        try:
            import pyttsx3

            engine = pyttsx3.init()
            wav_path = output_path.replace(".mp3", ".wav")
            engine.save_to_file(text, wav_path)
            engine.runAndWait()
            logger.info(f"pyttsx3 audio saved to: {wav_path}")
            return wav_path
        except Exception as exc:
            logger.error(f"pyttsx3 fallback also failed: {exc}")
            return ""

    def set_voice(self, voice_key: str) -> None:
        """Set TTS voice by key (e.g., 'en-male', 'hi-female')."""
        self.voice = VOICE_MAP.get(voice_key, voice_key)
        logger.info(f"TTS voice set to: {self.voice}")

    @staticmethod
    def list_voices() -> dict[str, str]:
        """Return available voice presets."""
        return dict(VOICE_MAP)
