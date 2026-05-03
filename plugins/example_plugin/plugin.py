"""Example plugin demonstrating the plugin system."""

from __future__ import annotations

from typing import Any

from app.plugins.base import BasePlugin, PluginInfo


class ExamplePlugin(BasePlugin):
    """A simple example plugin showing how to extend Jarvis."""

    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="example",
            version="1.0.0",
            description="An example plugin showing how to extend Jarvis",
            author="Jarvis Team",
            commands=["greet", "joke", "echo"],
        )

    def get_commands(self) -> list[str]:
        return ["greet", "joke", "echo"]

    async def execute(self, command: str, args: dict[str, Any]) -> dict[str, Any]:
        if command == "greet":
            name = args.get("name", "User")
            return {
                "status": "success",
                "response": f"Hello, {name}! I'm the example plugin.",
            }
        elif command == "joke":
            return {
                "status": "success",
                "response": "Why do programmers prefer dark mode? Because light attracts bugs!",
            }
        elif command == "echo":
            text = args.get("text", "")
            return {"status": "success", "response": f"Echo: {text}"}
        return {"status": "error", "message": f"Unknown command: {command}"}
