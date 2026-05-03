"""Presentation control — next/previous slide, start/stop presentation."""

from __future__ import annotations

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.advanced.presentation")


class PresentationController:
    """Control presentation software (e.g., LibreOffice Impress, PowerPoint)."""

    def __init__(self) -> None:
        self._gui = None
        try:
            import pyautogui

            self._gui = pyautogui
        except ImportError:
            logger.warning("pyautogui not installed for presentation control")

    def start_presentation(self) -> dict[str, str]:
        """Start a slideshow (F5 key)."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.press("f5")
            return {"status": "success", "message": "Presentation started"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def stop_presentation(self) -> dict[str, str]:
        """Stop the slideshow (Escape key)."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.press("escape")
            return {"status": "success", "message": "Presentation stopped"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def next_slide(self) -> dict[str, str]:
        """Go to the next slide."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.press("right")
            return {"status": "success", "message": "Next slide"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def previous_slide(self) -> dict[str, str]:
        """Go to the previous slide."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.press("left")
            return {"status": "success", "message": "Previous slide"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def go_to_slide(self, slide_number: int) -> dict[str, str]:
        """Jump to a specific slide number."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.typewrite(str(slide_number))
            self._gui.press("enter")
            return {"status": "success", "message": f"Jumped to slide {slide_number}"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def blank_screen(self) -> dict[str, str]:
        """Toggle black/blank screen during presentation."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.press("b")
            return {"status": "success", "message": "Screen blanked/unblanked"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}
