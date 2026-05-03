"""Speech-to-text using faster-whisper for local transcription."""

from __future__ import annotations

import tempfile

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.voice.stt")


class SpeechToText:
    """Transcribe audio to text using faster-whisper."""

    def __init__(self, model_size: str = "base", language: str = "en"):
        self.model_size = model_size
        self.language = language
        self._model = None

    def _load_model(self) -> None:
        """Lazy-load the whisper model."""
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
            )
            logger.info(f"Loaded whisper model: {self.model_size}")
        except ImportError:
            logger.warning(
                "faster-whisper not installed. Install with: "
                "pip install faster-whisper"
            )

    def transcribe_file(self, audio_path: str) -> str:
        """Transcribe an audio file to text."""
        self._load_model()
        if self._model is None:
            return ""

        try:
            segments, info = self._model.transcribe(
                audio_path,
                language=self.language if self.language != "auto" else None,
                beam_size=5,
                vad_filter=True,
            )
            text = " ".join(segment.text for segment in segments).strip()
            logger.info(f"Transcribed ({info.language}, {info.duration:.1f}s): {text[:80]}")
            return text
        except Exception as exc:
            logger.error(f"Transcription failed: {exc}")
            return ""

    def transcribe_bytes(self, audio_data: bytes, format: str = "wav") -> str:
        """Transcribe raw audio bytes."""
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=True) as tmp:
            tmp.write(audio_data)
            tmp.flush()
            return self.transcribe_file(tmp.name)

    def set_language(self, language: str) -> None:
        """Set the transcription language (e.g., 'en', 'hi', 'auto')."""
        self.language = language
        logger.info(f"STT language set to: {language}")
