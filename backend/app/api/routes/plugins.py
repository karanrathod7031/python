"""Plugin management API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/plugins", tags=["plugins"])


class PluginCommandRequest(BaseModel):
    command: str
    args: dict[str, Any] = {}


@router.get("/list")
async def list_plugins() -> dict[str, Any]:
    """List all loaded plugins."""
    from app.main import get_plugin_registry

    registry = get_plugin_registry()
    plugins = registry.list_plugins()
    return {
        "plugins": [
            {
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "commands": p.commands,
                "enabled": p.enabled,
            }
            for p in plugins
        ]
    }


@router.get("/commands")
async def list_commands() -> dict[str, Any]:
    """List all available plugin commands."""
    from app.main import get_plugin_registry

    registry = get_plugin_registry()
    return {"commands": registry.list_all_commands()}


@router.post("/execute")
async def execute_command(request: PluginCommandRequest) -> dict[str, Any]:
    """Execute a plugin command."""
    from app.main import get_plugin_registry

    registry = get_plugin_registry()
    result = await registry.execute(request.command, request.args)
    if result is None:
        return {"status": "error", "message": f"No plugin handles: {request.command}"}
    return result


@router.post("/reload/{plugin_name}")
async def reload_plugin(plugin_name: str) -> dict[str, str]:
    """Reload a specific plugin."""
    from app.main import get_plugin_manager

    manager = get_plugin_manager()
    if manager.reload_plugin(plugin_name):
        return {"status": "success", "message": f"Plugin '{plugin_name}' reloaded"}
    return {"status": "error", "message": f"Failed to reload '{plugin_name}'"}
