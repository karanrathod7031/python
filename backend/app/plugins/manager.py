"""Plugin manager for loading plugins from the filesystem."""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path

from app.config import get_settings
from app.plugins.base import BasePlugin
from app.plugins.registry import PluginRegistry
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.plugins.manager")


class PluginManager:
    """Load and manage plugins from the plugins directory."""

    def __init__(self, registry: PluginRegistry) -> None:
        self.registry = registry
        settings = get_settings()
        self.plugins_dir = Path(settings.plugins_dir)

    def discover_plugins(self) -> list[str]:
        """Discover available plugins in the plugins directory."""
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return []

        plugins: list[str] = []
        for entry in self.plugins_dir.iterdir():
            if entry.is_dir() and (entry / "plugin.py").exists():
                plugins.append(entry.name)
            elif entry.is_dir() and (entry / "__init__.py").exists():
                plugins.append(entry.name)

        logger.info(f"Discovered {len(plugins)} plugins: {plugins}")
        return plugins

    def load_plugin(self, plugin_name: str) -> bool:
        """Load a single plugin by name."""
        plugin_path = self.plugins_dir / plugin_name / "plugin.py"
        if not plugin_path.exists():
            logger.error(f"Plugin not found: {plugin_path}")
            return False

        try:
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}", plugin_path
            )
            if spec is None or spec.loader is None:
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for a class that extends BasePlugin
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr is not BasePlugin
                ):
                    plugin_instance = attr()
                    return self.registry.register(plugin_instance)

            logger.warning(f"No BasePlugin subclass found in {plugin_name}")
            return False
        except Exception as exc:
            logger.error(f"Failed to load plugin '{plugin_name}': {exc}")
            return False

    def load_all(self) -> int:
        """Load all discovered plugins."""
        plugins = self.discover_plugins()
        loaded = 0
        for name in plugins:
            if self.load_plugin(name):
                loaded += 1
        logger.info(f"Loaded {loaded}/{len(plugins)} plugins")
        return loaded

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        return self.registry.unregister(plugin_name)

    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin."""
        self.unload_plugin(plugin_name)
        return self.load_plugin(plugin_name)
