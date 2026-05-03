"""Application configuration using pydantic-settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Ollama LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Database
    database_url: str = "sqlite:///./data/jarvis.db"

    # Voice
    wake_word: str = "jarvis"
    tts_voice: str = "en-US-GuyNeural"
    stt_model: str = "base"
    language: str = "en"

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_address: Optional[str] = None
    email_password: Optional[str] = None

    # Security
    secret_key: str = "change-me-to-a-random-string"
    admin_password: str = "admin123"
    voice_auth_enabled: bool = False

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/jarvis.log"

    # Paths
    base_dir: str = str(Path(__file__).resolve().parent.parent)
    data_dir: str = str(Path(__file__).resolve().parent.parent / "data")
    plugins_dir: str = str(Path(__file__).resolve().parent.parent.parent / "plugins")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


def ensure_directories() -> None:
    """Create required directories if they don't exist."""
    settings = get_settings()
    for dir_path in [settings.data_dir, os.path.dirname(settings.log_file)]:
        os.makedirs(dir_path, exist_ok=True)
