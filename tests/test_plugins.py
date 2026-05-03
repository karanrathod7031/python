"""Tests for the plugin system."""

import pytest

from app.plugins.base import BasePlugin, PluginInfo
from app.plugins.registry import PluginRegistry


class MockPlugin(BasePlugin):
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="mock",
            version="1.0.0",
            description="A mock plugin for testing",
            commands=["mock_cmd"],
        )

    def get_commands(self) -> list[str]:
        return ["mock_cmd"]

    async def execute(self, command, args):
        return {"status": "success", "command": command, "args": args}


class TestPluginRegistry:
    def test_register_plugin(self):
        registry = PluginRegistry()
        plugin = MockPlugin()
        assert registry.register(plugin) is True

    def test_duplicate_register_fails(self):
        registry = PluginRegistry()
        plugin = MockPlugin()
        registry.register(plugin)
        assert registry.register(plugin) is False

    def test_unregister_plugin(self):
        registry = PluginRegistry()
        plugin = MockPlugin()
        registry.register(plugin)
        assert registry.unregister("mock") is True
        assert registry.unregister("mock") is False

    def test_find_handler(self):
        registry = PluginRegistry()
        plugin = MockPlugin()
        registry.register(plugin)
        handler = registry.find_handler("mock_cmd")
        assert handler is not None

    def test_find_handler_returns_none(self):
        registry = PluginRegistry()
        handler = registry.find_handler("nonexistent")
        assert handler is None

    @pytest.mark.asyncio
    async def test_execute_command(self):
        registry = PluginRegistry()
        plugin = MockPlugin()
        registry.register(plugin)
        result = await registry.execute("mock_cmd", {"key": "value"})
        assert result is not None
        assert result["status"] == "success"

    def test_list_plugins(self):
        registry = PluginRegistry()
        plugin = MockPlugin()
        registry.register(plugin)
        plugins = registry.list_plugins()
        assert len(plugins) == 1
        assert plugins[0].name == "mock"

    def test_list_all_commands(self):
        registry = PluginRegistry()
        plugin = MockPlugin()
        registry.register(plugin)
        commands = registry.list_all_commands()
        assert len(commands) == 1
        assert commands[0]["command"] == "mock_cmd"
