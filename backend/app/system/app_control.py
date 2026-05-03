"""Application control — open, close, switch, minimize, maximize."""

from __future__ import annotations

import platform
import subprocess

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.system.app_control")

# Common application name mappings per platform
APP_MAP_LINUX = {
    "chrome": "google-chrome",
    "browser": "google-chrome",
    "firefox": "firefox",
    "terminal": "gnome-terminal",
    "code": "code",
    "vscode": "code",
    "files": "nautilus",
    "explorer": "nautilus",
    "calculator": "gnome-calculator",
    "settings": "gnome-control-center",
    "spotify": "spotify",
    "vlc": "vlc",
    "discord": "discord",
    "slack": "slack",
    "gimp": "gimp",
    "libreoffice": "libreoffice",
}

APP_MAP_WINDOWS = {
    "chrome": "chrome",
    "browser": "chrome",
    "firefox": "firefox",
    "terminal": "cmd",
    "powershell": "powershell",
    "code": "code",
    "vscode": "code",
    "explorer": "explorer",
    "files": "explorer",
    "calculator": "calc",
    "notepad": "notepad",
    "paint": "mspaint",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "spotify": "spotify",
    "vlc": "vlc",
    "discord": "discord",
    "slack": "slack",
    "task manager": "taskmgr",
}

APP_MAP_MAC = {
    "chrome": "Google Chrome",
    "browser": "Google Chrome",
    "safari": "Safari",
    "firefox": "Firefox",
    "terminal": "Terminal",
    "code": "Visual Studio Code",
    "vscode": "Visual Studio Code",
    "finder": "Finder",
    "explorer": "Finder",
    "files": "Finder",
    "calculator": "Calculator",
    "spotify": "Spotify",
    "discord": "Discord",
    "slack": "Slack",
    "notes": "Notes",
    "music": "Music",
}


class AppController:
    """Control applications — open, close, switch windows."""

    def __init__(self) -> None:
        self.os_type = platform.system().lower()
        self.app_map = self._get_app_map()

    def _get_app_map(self) -> dict[str, str]:
        if self.os_type == "linux":
            return APP_MAP_LINUX
        elif self.os_type == "windows":
            return APP_MAP_WINDOWS
        elif self.os_type == "darwin":
            return APP_MAP_MAC
        return {}

    def open_app(self, app_name: str) -> dict[str, str]:
        """Open an application by name."""
        resolved = self.app_map.get(app_name.lower(), app_name)
        logger.info(f"Opening application: {resolved}")

        try:
            if self.os_type == "linux":
                subprocess.Popen(
                    [resolved],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            elif self.os_type == "windows":
                subprocess.Popen(
                    ["start", resolved],
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            elif self.os_type == "darwin":
                subprocess.Popen(
                    ["open", "-a", resolved],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                return {"status": "error", "message": f"Unsupported OS: {self.os_type}"}

            return {"status": "success", "message": f"Opened {app_name}"}
        except FileNotFoundError:
            return {"status": "error", "message": f"Application not found: {app_name}"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def close_app(self, app_name: str) -> dict[str, str]:
        """Close an application by name."""
        resolved = self.app_map.get(app_name.lower(), app_name)
        logger.info(f"Closing application: {resolved}")

        try:
            if self.os_type == "linux":
                subprocess.run(["pkill", "-f", resolved], capture_output=True)
            elif self.os_type == "windows":
                subprocess.run(
                    ["taskkill", "/IM", f"{resolved}.exe", "/F"],
                    capture_output=True,
                )
            elif self.os_type == "darwin":
                subprocess.run(
                    ["osascript", "-e", f'quit app "{resolved}"'],
                    capture_output=True,
                )
            return {"status": "success", "message": f"Closed {app_name}"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def list_running(self) -> list[str]:
        """List currently running applications."""
        try:
            import psutil

            return list({
                p.name()
                for p in psutil.process_iter(["name"])
                if p.info["name"]
            })
        except ImportError:
            return []

    def is_running(self, app_name: str) -> bool:
        """Check if an application is currently running."""
        resolved = self.app_map.get(app_name.lower(), app_name)
        try:
            import psutil

            for proc in psutil.process_iter(["name"]):
                if resolved.lower() in (proc.info["name"] or "").lower():
                    return True
        except ImportError:
            pass
        return False
