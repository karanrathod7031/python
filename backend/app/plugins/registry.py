"""Plugin registry for managing loaded plugins."""

from __future__ import annotations

from typing import Any, Optional

from app.plugins.base import BasePlugin, PluginInfo
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.plugins.registry")


class PluginRegistry:
    """Central registry for all loaded plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin) -> bool:
        """Register a plugin."""
        info = plugin.get_info()
        if info.name in self._plugins:
            logger.warning(f"Plugin '{info.name}' already registered, skipping")
            return False

        self._plugins[info.name] = plugin
        plugin.on_load()
        logger.info(f"Plugin registered: {info.name} v{info.version}")
        return True

    def unregister(self, name: str) -> bool:
        """Unregister a plugin."""
        plugin = self._plugins.pop(name, None)
        if plugin:
            plugin.on_unload()
            logger.info(f"Plugin unregistered: {name}")
            return True
        return False

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def find_handler(self, command: str) -> Optional[BasePlugin]:
        """Find a plugin that handles the given command."""
        for plugin in self._plugins.values():
            if plugin.can_handle(command):
                return plugin
        return None

    async def execute(self, command: str, args: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Find and execute a command via the appropriate plugin."""
        handler = self.find_handler(command)
        if handler:
            return await handler.execute(command, args)
        return None

    def list_plugins(self) -> list[PluginInfo]:
        """List all registered plugins."""
        return [p.get_info() for p in self._plugins.values()]

    def list_all_commands(self) -> list[dict[str, str]]:
        """List all commands across all plugins."""
        commands: list[dict[str, str]] = []
        for plugin in self._plugins.values():
            info = plugin.get_info()
            for cmd in plugin.get_commands():
                commands.append({"command": cmd, "plugin": info.name})
        return commands
