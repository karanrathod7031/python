"""Base plugin class that all plugins must extend."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PluginInfo:
    """Metadata about a plugin."""

    name: str
    version: str
    description: str
    author: str = ""
    commands: list[str] = field(default_factory=list)
    enabled: bool = True


class BasePlugin(ABC):
    """Abstract base class for all Jarvis plugins."""

    @abstractmethod
    def get_info(self) -> PluginInfo:
        """Return plugin metadata."""

    @abstractmethod
    def get_commands(self) -> list[str]:
        """Return list of commands this plugin handles."""

    @abstractmethod
    async def execute(self, command: str, args: dict[str, Any]) -> dict[str, Any]:
        """Execute a plugin command."""

    def on_load(self) -> None:
        """Called when the plugin is loaded. Override for initialization."""

    def on_unload(self) -> None:
        """Called when the plugin is unloaded. Override for cleanup."""

    def can_handle(self, command: str) -> bool:
        """Check if this plugin handles the given command."""
        return command in self.get_commands()
