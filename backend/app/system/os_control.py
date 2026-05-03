"""OS-level control — shutdown, restart, lock screen."""

from __future__ import annotations

import platform
import subprocess

from app.utils.errors import ConfirmationRequired
from app.utils.logger import setup_logger

logger = setup_logger("jarvis.system.os_control")


class OSController:
    """Control OS-level operations with safety confirmations."""

    def __init__(self) -> None:
        self.os_type = platform.system().lower()

    def shutdown(self, confirmed: bool = False) -> dict[str, str]:
        """Shutdown the system (requires confirmation)."""
        if not confirmed:
            raise ConfirmationRequired(
                "shutdown",
                "This will shut down the computer. All unsaved work will be lost.",
            )

        logger.warning("Executing system shutdown")
        try:
            if self.os_type == "linux":
                subprocess.run(["systemctl", "poweroff"], check=True)
            elif self.os_type == "windows":
                subprocess.run(["shutdown", "/s", "/t", "5"], check=True)
            elif self.os_type == "darwin":
                subprocess.run(
                    ["osascript", "-e", 'tell app "System Events" to shut down'],
                    check=True,
                )
            return {"status": "success", "message": "System shutting down..."}
        except subprocess.CalledProcessError as exc:
            return {"status": "error", "message": f"Shutdown failed: {exc}"}

    def restart(self, confirmed: bool = False) -> dict[str, str]:
        """Restart the system (requires confirmation)."""
        if not confirmed:
            raise ConfirmationRequired(
                "restart", "This will restart the computer."
            )

        logger.warning("Executing system restart")
        try:
            if self.os_type == "linux":
                subprocess.run(["systemctl", "reboot"], check=True)
            elif self.os_type == "windows":
                subprocess.run(["shutdown", "/r", "/t", "5"], check=True)
            elif self.os_type == "darwin":
                subprocess.run(
                    ["osascript", "-e", 'tell app "System Events" to restart'],
                    check=True,
                )
            return {"status": "success", "message": "System restarting..."}
        except subprocess.CalledProcessError as exc:
            return {"status": "error", "message": f"Restart failed: {exc}"}

    def lock_screen(self) -> dict[str, str]:
        """Lock the screen."""
        logger.info("Locking screen")
        try:
            if self.os_type == "linux":
                subprocess.run(["loginctl", "lock-session"], check=True)
            elif self.os_type == "windows":
                subprocess.run(
                    ["rundll32.exe", "user32.dll,LockWorkStation"], check=True
                )
            elif self.os_type == "darwin":
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to keystroke "q" '
                        "using {control down, command down}",
                    ],
                    check=True,
                )
            return {"status": "success", "message": "Screen locked"}
        except subprocess.CalledProcessError as exc:
            return {"status": "error", "message": f"Lock failed: {exc}"}

    def sleep(self) -> dict[str, str]:
        """Put the system to sleep."""
        logger.info("Putting system to sleep")
        try:
            if self.os_type == "linux":
                subprocess.run(["systemctl", "suspend"], check=True)
            elif self.os_type == "windows":
                subprocess.run(
                    ["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"],
                    check=True,
                )
            elif self.os_type == "darwin":
                subprocess.run(["pmset", "sleepnow"], check=True)
            return {"status": "success", "message": "System going to sleep..."}
        except subprocess.CalledProcessError as exc:
            return {"status": "error", "message": f"Sleep failed: {exc}"}

    def get_battery_info(self) -> dict[str, object]:
        """Get battery status."""
        try:
            import psutil

            battery = psutil.sensors_battery()
            if battery is None:
                return {"status": "info", "has_battery": False}
            return {
                "status": "success",
                "has_battery": True,
                "percent": battery.percent,
                "plugged_in": battery.power_plugged,
                "seconds_left": battery.secsleft if battery.secsleft > 0 else None,
            }
        except ImportError:
            return {"status": "error", "message": "psutil not available"}
