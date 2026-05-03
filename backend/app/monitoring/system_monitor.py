"""System resource monitoring — CPU, RAM, disk, network, processes."""

from __future__ import annotations

from typing import Any

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.monitoring")


class SystemMonitor:
    """Monitor system resources."""

    def get_cpu_info(self) -> dict[str, Any]:
        """Get CPU usage information."""
        try:
            import psutil

            return {
                "percent": psutil.cpu_percent(interval=1),
                "count_physical": psutil.cpu_count(logical=False),
                "count_logical": psutil.cpu_count(logical=True),
                "frequency_mhz": (
                    psutil.cpu_freq().current if psutil.cpu_freq() else None
                ),
            }
        except ImportError:
            return {"error": "psutil not installed"}

    def get_memory_info(self) -> dict[str, Any]:
        """Get memory usage information."""
        try:
            import psutil

            mem = psutil.virtual_memory()
            return {
                "total_gb": round(mem.total / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "percent": mem.percent,
            }
        except ImportError:
            return {"error": "psutil not installed"}

    def get_disk_info(self) -> list[dict[str, Any]]:
        """Get disk usage information."""
        try:
            import psutil

            disks: list[dict[str, Any]] = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent": usage.percent,
                    })
                except PermissionError:
                    continue
            return disks
        except ImportError:
            return [{"error": "psutil not installed"}]

    def get_network_info(self) -> dict[str, Any]:
        """Get network information."""
        try:
            import psutil

            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "recv_mb": round(net_io.bytes_recv / (1024**2), 2),
            }
        except ImportError:
            return {"error": "psutil not installed"}

    def get_battery_info(self) -> dict[str, Any]:
        """Get battery information."""
        try:
            import psutil

            battery = psutil.sensors_battery()
            if battery is None:
                return {"has_battery": False}
            return {
                "has_battery": True,
                "percent": battery.percent,
                "plugged_in": battery.power_plugged,
                "seconds_left": battery.secsleft if battery.secsleft > 0 else None,
            }
        except ImportError:
            return {"error": "psutil not installed"}

    def get_process_list(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get top processes by CPU usage."""
        try:
            import psutil

            processes: list[dict[str, Any]] = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    info = proc.info
                    processes.append({
                        "pid": info["pid"],
                        "name": info["name"],
                        "cpu_percent": info["cpu_percent"],
                        "memory_percent": round(info["memory_percent"] or 0, 2),
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            processes.sort(key=lambda p: p["cpu_percent"] or 0, reverse=True)
            return processes[:limit]
        except ImportError:
            return [{"error": "psutil not installed"}]

    def get_full_report(self) -> dict[str, Any]:
        """Get a complete system status report."""
        return {
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
            "battery": self.get_battery_info(),
        }
