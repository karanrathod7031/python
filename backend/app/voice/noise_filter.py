"""Audio noise filtering and preprocessing."""

from __future__ import annotations

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.voice.noise_filter")


class NoiseFilter:
    """Filter noise from audio input using VAD and basic processing."""

    def __init__(self, aggressiveness: int = 2, sample_rate: int = 16000):
        self.aggressiveness = aggressiveness
        self.sample_rate = sample_rate
        self._vad = None

    def _init_vad(self) -> None:
        """Initialize WebRTC VAD."""
        if self._vad is not None:
            return
        try:
            import webrtcvad

            self._vad = webrtcvad.Vad(self.aggressiveness)
            logger.info(f"VAD initialized (aggressiveness={self.aggressiveness})")
        except ImportError:
            logger.warning("webrtcvad not installed, noise filtering limited")

    def is_speech(self, audio_frame: bytes, sample_rate: int = 16000) -> bool:
        """Detect if an audio frame contains speech."""
        self._init_vad()
        if self._vad is None:
            return True  # assume speech if VAD unavailable
        try:
            return self._vad.is_speech(audio_frame, sample_rate)
        except Exception:
            return True

    def filter_silence(
        self,
        audio_data: bytes,
        frame_duration_ms: int = 30,
    ) -> bytes:
        """Remove silent frames from audio data.

        Audio must be 16-bit PCM at the configured sample rate.
        """
        self._init_vad()
        if self._vad is None:
            return audio_data

        frame_size = int(self.sample_rate * frame_duration_ms / 1000) * 2  # 16-bit
        voiced_frames = bytearray()

        for i in range(0, len(audio_data) - frame_size, frame_size):
            frame = audio_data[i : i + frame_size]
            if self.is_speech(frame, self.sample_rate):
                voiced_frames.extend(frame)

        ratio = len(voiced_frames) / max(len(audio_data), 1)
        logger.debug(f"Noise filter: kept {ratio:.1%} of audio as speech")
        return bytes(voiced_frames)

    def normalize_audio(self, audio_data: bytes) -> bytes:
        """Basic audio normalization (peak normalization)."""
        try:
            import numpy as np

            samples = np.frombuffer(audio_data, dtype=np.int16).copy()
            if samples.size == 0:
                return audio_data
            peak = np.max(np.abs(samples))
            if peak == 0:
                return audio_data
            scale = 32767.0 / peak
            normalized = (samples * scale).astype(np.int16)
            return normalized.tobytes()
        except ImportError:
            return audio_data
