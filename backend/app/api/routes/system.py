"""System control API routes."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.system.app_control import AppController
from app.system.file_manager import FileManager
from app.system.os_control import OSController
from app.system.volume_brightness import BrightnessController, VolumeController
from app.utils.errors import ConfirmationRequired

router = APIRouter(prefix="/api/system", tags=["system"])

app_ctrl = AppController()
os_ctrl = OSController()
file_mgr = FileManager()
vol_ctrl = VolumeController()
bright_ctrl = BrightnessController()


class AppRequest(BaseModel):
    name: str


class FileRequest(BaseModel):
    path: str
    content: str = ""
    destination: str = ""
    confirmed: bool = False


class VolumeRequest(BaseModel):
    level: Optional[int] = None
    action: str = "set"  # set, up, down, mute, unmute


class BrightnessRequest(BaseModel):
    level: Optional[int] = None
    action: str = "set"


@router.post("/app/open")
async def open_app(request: AppRequest) -> dict[str, str]:
    return app_ctrl.open_app(request.name)


@router.post("/app/close")
async def close_app(request: AppRequest) -> dict[str, str]:
    return app_ctrl.close_app(request.name)


@router.get("/app/running")
async def list_running() -> dict[str, list[str]]:
    return {"apps": app_ctrl.list_running()}


@router.post("/os/shutdown")
async def shutdown(confirmed: bool = False) -> dict[str, str]:
    try:
        return os_ctrl.shutdown(confirmed=confirmed)
    except ConfirmationRequired as exc:
        return {"status": "confirmation_required", "message": str(exc)}


@router.post("/os/restart")
async def restart(confirmed: bool = False) -> dict[str, str]:
    try:
        return os_ctrl.restart(confirmed=confirmed)
    except ConfirmationRequired as exc:
        return {"status": "confirmation_required", "message": str(exc)}


@router.post("/os/lock")
async def lock_screen() -> dict[str, str]:
    return os_ctrl.lock_screen()


@router.get("/os/battery")
async def battery_info() -> dict[str, object]:
    return os_ctrl.get_battery_info()


@router.post("/file/create")
async def create_file(request: FileRequest) -> dict[str, str]:
    return file_mgr.create_file(request.path, request.content)


@router.post("/file/delete")
async def delete_file(request: FileRequest) -> dict[str, str]:
    try:
        return file_mgr.delete(request.path, confirmed=request.confirmed)
    except ConfirmationRequired as exc:
        return {"status": "confirmation_required", "message": str(exc)}


@router.post("/file/move")
async def move_file(request: FileRequest) -> dict[str, str]:
    return file_mgr.move(request.path, request.destination)


@router.post("/file/copy")
async def copy_file(request: FileRequest) -> dict[str, str]:
    return file_mgr.copy(request.path, request.destination)


@router.get("/file/search")
async def search_files(pattern: str, directory: str = "") -> dict[str, Any]:
    results = file_mgr.search(pattern, directory or None)
    return {"results": results, "count": len(results)}


@router.get("/file/list")
async def list_directory(path: str = "") -> dict[str, Any]:
    items = file_mgr.list_directory(path or None)
    return {"items": items, "count": len(items)}


@router.post("/volume")
async def control_volume(request: VolumeRequest) -> dict[str, object]:
    if request.action == "up":
        return vol_ctrl.increase_volume()
    elif request.action == "down":
        return vol_ctrl.decrease_volume()
    elif request.action == "mute":
        return vol_ctrl.mute()
    elif request.action == "unmute":
        return vol_ctrl.unmute()
    elif request.level is not None:
        return vol_ctrl.set_volume(request.level)
    return {"status": "error", "message": "Invalid volume action"}


@router.post("/brightness")
async def control_brightness(request: BrightnessRequest) -> dict[str, object]:
    if request.action == "up":
        return bright_ctrl.increase_brightness()
    elif request.action == "down":
        return bright_ctrl.decrease_brightness()
    elif request.level is not None:
        return bright_ctrl.set_brightness(request.level)
    return {"status": "error", "message": "Invalid brightness action"}
