"""System monitoring API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.monitoring.system_monitor import SystemMonitor

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

monitor = SystemMonitor()


@router.get("/status")
async def system_status() -> dict[str, Any]:
    """Get full system status report."""
    return monitor.get_full_report()


@router.get("/cpu")
async def cpu_info() -> dict[str, Any]:
    return monitor.get_cpu_info()


@router.get("/memory")
async def memory_info() -> dict[str, Any]:
    return monitor.get_memory_info()


@router.get("/disk")
async def disk_info() -> list[dict[str, Any]]:
    return monitor.get_disk_info()


@router.get("/network")
async def network_info() -> dict[str, Any]:
    return monitor.get_network_info()


@router.get("/battery")
async def battery_info() -> dict[str, Any]:
    return monitor.get_battery_info()


@router.get("/processes")
async def process_list(limit: int = 20) -> dict[str, Any]:
    procs = monitor.get_process_list(limit)
    return {"processes": procs, "count": len(procs)}
