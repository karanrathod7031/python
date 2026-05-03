"""Volume and brightness control across platforms."""

from __future__ import annotations

import platform
import subprocess

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.system.volume_brightness")


class VolumeController:
    """Control system volume."""

    def __init__(self) -> None:
        self.os_type = platform.system().lower()

    def set_volume(self, level: int) -> dict[str, object]:
        """Set volume to a specific level (0-100)."""
        level = max(0, min(100, level))
        logger.info(f"Setting volume to {level}%")

        try:
            if self.os_type == "linux":
                subprocess.run(
                    ["amixer", "set", "Master", f"{level}%"],
                    capture_output=True,
                    check=True,
                )
            elif self.os_type == "windows":
                # Uses nircmd for Windows volume control
                subprocess.run(
                    ["nircmd", "setsysvolume", str(int(level * 655.35))],
                    capture_output=True,
                )
            elif self.os_type == "darwin":
                subprocess.run(
                    ["osascript", "-e", f"set volume output volume {level}"],
                    capture_output=True,
                    check=True,
                )
            return {"status": "success", "volume": level}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def increase_volume(self, step: int = 10) -> dict[str, object]:
        """Increase volume by step percent."""
        current = self.get_volume()
        new_level = min(100, current + step)
        return self.set_volume(new_level)

    def decrease_volume(self, step: int = 10) -> dict[str, object]:
        """Decrease volume by step percent."""
        current = self.get_volume()
        new_level = max(0, current - step)
        return self.set_volume(new_level)

    def mute(self) -> dict[str, str]:
        """Mute system audio."""
        try:
            if self.os_type == "linux":
                subprocess.run(
                    ["amixer", "set", "Master", "mute"], capture_output=True
                )
            elif self.os_type == "windows":
                subprocess.run(["nircmd", "mutesysvolume", "1"], capture_output=True)
            elif self.os_type == "darwin":
                subprocess.run(
                    ["osascript", "-e", "set volume with output muted"],
                    capture_output=True,
                )
            return {"status": "success", "message": "Audio muted"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def unmute(self) -> dict[str, str]:
        """Unmute system audio."""
        try:
            if self.os_type == "linux":
                subprocess.run(
                    ["amixer", "set", "Master", "unmute"], capture_output=True
                )
            elif self.os_type == "windows":
                subprocess.run(["nircmd", "mutesysvolume", "0"], capture_output=True)
            elif self.os_type == "darwin":
                subprocess.run(
                    ["osascript", "-e", "set volume without output muted"],
                    capture_output=True,
                )
            return {"status": "success", "message": "Audio unmuted"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def get_volume(self) -> int:
        """Get current volume level."""
        try:
            if self.os_type == "linux":
                result = subprocess.run(
                    ["amixer", "get", "Master"],
                    capture_output=True,
                    text=True,
                )
                import re

                match = re.search(r"\[(\d+)%\]", result.stdout)
                return int(match.group(1)) if match else 50
            elif self.os_type == "darwin":
                result = subprocess.run(
                    ["osascript", "-e", "output volume of (get volume settings)"],
                    capture_output=True,
                    text=True,
                )
                return int(result.stdout.strip()) if result.stdout.strip() else 50
        except Exception:
            pass
        return 50


class BrightnessController:
    """Control display brightness."""

    def __init__(self) -> None:
        self.os_type = platform.system().lower()

    def set_brightness(self, level: int) -> dict[str, object]:
        """Set brightness to a specific level (0-100)."""
        level = max(0, min(100, level))
        logger.info(f"Setting brightness to {level}%")

        try:
            if self.os_type == "linux":
                subprocess.run(
                    ["xrandr", "--output", self._get_display(), "--brightness",
                     str(level / 100.0)],
                    capture_output=True,
                    check=True,
                )
            elif self.os_type == "windows":
                subprocess.run(
                    ["powershell", "-Command",
                     f"(Get-WmiObject -Namespace root/WMI "
                     f"-Class WmiMonitorBrightnessMethods)"
                     f".WmiSetBrightness(1,{level})"],
                    capture_output=True,
                )
            elif self.os_type == "darwin":
                subprocess.run(
                    ["osascript", "-e",
                     f'tell application "System Preferences" to set brightness to {level / 100.0}'],
                    capture_output=True,
                )
            return {"status": "success", "brightness": level}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def increase_brightness(self, step: int = 10) -> dict[str, object]:
        """Increase brightness."""
        return self.set_brightness(min(100, self._get_current() + step))

    def decrease_brightness(self, step: int = 10) -> dict[str, object]:
        """Decrease brightness."""
        return self.set_brightness(max(0, self._get_current() - step))

    def _get_current(self) -> int:
        """Get current brightness level (best effort)."""
        try:
            if self.os_type == "linux":
                import glob
                from pathlib import Path

                paths = glob.glob("/sys/class/backlight/*/brightness")
                if paths:
                    current = int(Path(paths[0]).read_text().strip())
                    max_path = Path(paths[0]).parent / "max_brightness"
                    max_val = int(max_path.read_text().strip())
                    return int((current / max_val) * 100)
        except Exception:
            pass
        return 50

    def _get_display(self) -> str:
        """Get the primary display name on Linux."""
        try:
            result = subprocess.run(
                ["xrandr", "--query"],
                capture_output=True,
                text=True,
            )
            for line in result.stdout.splitlines():
                if " connected" in line:
                    return line.split()[0]
        except Exception:
            pass
        return "eDP-1"
