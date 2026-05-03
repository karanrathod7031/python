"""Main FastAPI application — entry point for Jarvis AI Assistant."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import assistant, automation, memory, monitoring, plugins, settings, system
from app.api.websocket import websocket_endpoint
from app.config import ensure_directories, get_settings
from app.core.brain import Brain
from app.memory.cache import Cache
from app.memory.conversation import ConversationMemory
from app.memory.database import Database
from app.memory.preferences import PreferencesManager
from app.plugins.manager import PluginManager
from app.plugins.registry import PluginRegistry
from app.security.auth import AuthManager
from app.utils.logger import setup_logger
from app.voice.stt import SpeechToText
from app.voice.tts import TextToSpeech

logger = setup_logger("jarvis.main")

# Global service instances
_brain: Optional[Brain] = None
_database: Optional[Database] = None
_cache: Optional[Cache] = None
_conv_memory: Optional[ConversationMemory] = None
_preferences: Optional[PreferencesManager] = None
_plugin_registry: Optional[PluginRegistry] = None
_plugin_manager: Optional[PluginManager] = None
_auth: Optional[AuthManager] = None
_stt: Optional[SpeechToText] = None
_tts: Optional[TextToSpeech] = None


def get_brain() -> Brain:
    assert _brain is not None
    return _brain


def get_database() -> Database:
    assert _database is not None
    return _database


def get_cache() -> Cache:
    assert _cache is not None
    return _cache


def get_conversation_memory() -> ConversationMemory:
    assert _conv_memory is not None
    return _conv_memory


def get_preferences() -> PreferencesManager:
    assert _preferences is not None
    return _preferences


def get_plugin_registry() -> PluginRegistry:
    assert _plugin_registry is not None
    return _plugin_registry


def get_plugin_manager() -> PluginManager:
    assert _plugin_manager is not None
    return _plugin_manager


def get_auth() -> AuthManager:
    assert _auth is not None
    return _auth


def get_stt() -> SpeechToText:
    assert _stt is not None
    return _stt


def get_tts() -> TextToSpeech:
    assert _tts is not None
    return _tts


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle — startup and shutdown."""
    global _brain, _database, _cache, _conv_memory, _preferences
    global _plugin_registry, _plugin_manager, _auth, _stt, _tts

    logger.info("Starting Jarvis AI Assistant...")

    settings = get_settings()
    ensure_directories()

    # Initialize services
    _brain = Brain()
    _auth = AuthManager()

    # Database
    _database = Database()
    await _database.connect()

    # Cache (Redis)
    _cache = Cache()
    await _cache.connect()

    # Memory
    _conv_memory = ConversationMemory(_database)
    _preferences = PreferencesManager(_database)

    # Voice
    _stt = SpeechToText(model_size=settings.stt_model, language=settings.language)
    _tts = TextToSpeech(voice=settings.tts_voice)

    # Plugins
    _plugin_registry = PluginRegistry()
    _plugin_manager = PluginManager(_plugin_registry)
    _plugin_manager.load_all()

    logger.info("Jarvis is ready!")

    yield

    # Shutdown
    logger.info("Shutting down Jarvis...")
    await _brain.close()
    await _database.close()
    await _cache.close()
    logger.info("Jarvis shut down complete.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Jarvis AI Assistant",
        description="A production-level local AI assistant with voice, system control, automation, and more.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(assistant.router)
    app.include_router(system.router)
    app.include_router(automation.router)
    app.include_router(memory.router)
    app.include_router(monitoring.router)
    app.include_router(plugins.router)
    app.include_router(settings.router)

    # WebSocket
    app.add_api_route("/ws", websocket_endpoint, methods=["GET"])
    app.add_websocket_route("/ws", websocket_endpoint)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {
            "name": "Jarvis AI Assistant",
            "version": "1.0.0",
            "status": "running",
        }

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    _settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=_settings.host,
        port=_settings.port,
        reload=_settings.debug,
    )
