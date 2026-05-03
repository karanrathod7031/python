"""Mouse and keyboard control using pyautogui."""

from __future__ import annotations

from typing import Optional, Tuple

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.advanced.input")


class InputController:
    """Control mouse and keyboard programmatically."""

    def __init__(self) -> None:
        self._gui = None
        self._init_gui()

    def _init_gui(self) -> None:
        """Initialize pyautogui."""
        try:
            import pyautogui

            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            self._gui = pyautogui
        except ImportError:
            logger.warning("pyautogui not installed")

    def click(self, x: int, y: int, button: str = "left") -> dict[str, str]:
        """Click at coordinates."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.click(x, y, button=button)
            return {"status": "success", "message": f"Clicked at ({x}, {y})"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def double_click(self, x: int, y: int) -> dict[str, str]:
        """Double-click at coordinates."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.doubleClick(x, y)
            return {"status": "success", "message": f"Double-clicked at ({x}, {y})"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def type_text(self, text: str, interval: float = 0.05) -> dict[str, str]:
        """Type text with optional interval between keystrokes."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.typewrite(text, interval=interval)
            return {"status": "success", "message": f"Typed: {text[:50]}"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def hotkey(self, *keys: str) -> dict[str, str]:
        """Press a hotkey combination (e.g., 'ctrl', 'c')."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.hotkey(*keys)
            return {"status": "success", "message": f"Hotkey: {'+'.join(keys)}"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def press_key(self, key: str) -> dict[str, str]:
        """Press a single key."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.press(key)
            return {"status": "success", "message": f"Pressed: {key}"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> dict[str, str]:
        """Move the mouse to coordinates."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.moveTo(x, y, duration=duration)
            return {"status": "success", "message": f"Moved to ({x}, {y})"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> dict[str, str]:
        """Scroll the mouse wheel."""
        if not self._gui:
            return {"status": "error", "message": "pyautogui not available"}
        try:
            self._gui.scroll(clicks, x, y)
            return {"status": "success", "message": f"Scrolled {clicks} clicks"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        if not self._gui:
            return (0, 0)
        pos = self._gui.position()
        return (pos.x, pos.y)

    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen resolution."""
        if not self._gui:
            return (1920, 1080)
        size = self._gui.size()
        return (size.width, size.height)
