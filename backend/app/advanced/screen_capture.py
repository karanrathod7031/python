"""Screenshot and screen recording capabilities."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.advanced.screen")


class ScreenCapture:
    """Capture screenshots and record screen."""

    def __init__(self, output_dir: str = "screenshots") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def take_screenshot(
        self, filename: Optional[str] = None, region: Optional[tuple[int, int, int, int]] = None
    ) -> dict[str, str]:
        """Take a screenshot of the entire screen or a region."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        filepath = self.output_dir / filename

        try:
            import pyautogui

            screenshot = pyautogui.screenshot(region=region)
            screenshot.save(str(filepath))
            logger.info(f"Screenshot saved: {filepath}")
            return {"status": "success", "path": str(filepath)}
        except ImportError:
            # Fallback: use scrot on Linux
            try:
                import subprocess

                subprocess.run(["scrot", str(filepath)], check=True, capture_output=True)
                return {"status": "success", "path": str(filepath)}
            except Exception:
                return {"status": "error", "message": "No screenshot tool available"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def take_window_screenshot(self, window_title: str) -> dict[str, str]:
        """Take a screenshot of a specific window."""
        try:
            import pyautogui

            windows = pyautogui.getWindowsWithTitle(window_title)
            if not windows:
                return {"status": "error", "message": f"Window not found: {window_title}"}

            window = windows[0]
            region = (window.left, window.top, window.width, window.height)
            return self.take_screenshot(region=region)
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def start_recording(self, output_file: Optional[str] = None) -> dict[str, str]:
        """Start screen recording (Linux: ffmpeg)."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(self.output_dir / f"recording_{timestamp}.mp4")

        try:
            import subprocess

            self._recording_process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-f", "x11grab",
                    "-framerate", "30",
                    "-i", os.environ.get("DISPLAY", ":0"),
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    output_file,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info(f"Screen recording started: {output_file}")
            return {"status": "success", "path": output_file, "message": "Recording started"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def stop_recording(self) -> dict[str, str]:
        """Stop the current screen recording."""
        if hasattr(self, "_recording_process") and self._recording_process:
            self._recording_process.terminate()
            self._recording_process.wait()
            self._recording_process = None
            return {"status": "success", "message": "Recording stopped"}
        return {"status": "error", "message": "No active recording"}
