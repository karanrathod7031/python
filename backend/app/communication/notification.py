"""System notification handling."""

from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass, field
from datetime import datetime

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.communication.notification")


@dataclass
class Notification:
    """A notification entry."""

    id: str
    title: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    read: bool = False
    source: str = "jarvis"


class NotificationManager:
    """Manage and display system notifications."""

    def __init__(self) -> None:
        self.notifications: list[Notification] = []
        self.os_type = platform.system().lower()

    def send(self, title: str, message: str, source: str = "jarvis") -> Notification:
        """Send a system notification."""
        import uuid

        notif = Notification(
            id=str(uuid.uuid4())[:8],
            title=title,
            message=message,
            source=source,
        )
        self.notifications.append(notif)

        self._show_system_notification(title, message)
        logger.info(f"Notification: {title}")
        return notif

    def _show_system_notification(self, title: str, message: str) -> None:
        """Display an OS-level notification."""
        try:
            if self.os_type == "linux":
                subprocess.run(
                    ["notify-send", f"Jarvis: {title}", message],
                    capture_output=True,
                )
            elif self.os_type == "darwin":
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        f'display notification "{message}" with title "Jarvis: {title}"',
                    ],
                    capture_output=True,
                )
            elif self.os_type == "windows":
                # PowerShell toast notification
                ps_script = (
                    f"[Windows.UI.Notifications.ToastNotificationManager, "
                    f"Windows.UI.Notifications, ContentType = WindowsRuntime] > $null; "
                    f'$template = "<toast><visual><binding template=\\"ToastText02\\">'
                    f"<text id=\\\"1\\\">Jarvis: {title}</text>"
                    f"<text id=\\\"2\\\">{message}</text>"
                    f'</binding></visual></toast>"'
                )
                subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True,
                )
        except Exception as exc:
            logger.debug(f"System notification failed: {exc}")

    def get_unread(self) -> list[Notification]:
        """Get unread notifications."""
        return [n for n in self.notifications if not n.read]

    def mark_read(self, notif_id: str) -> bool:
        """Mark a notification as read."""
        for notif in self.notifications:
            if notif.id == notif_id:
                notif.read = True
                return True
        return False

    def mark_all_read(self) -> int:
        """Mark all notifications as read."""
        count = 0
        for notif in self.notifications:
            if not notif.read:
                notif.read = True
                count += 1
        return count

    def clear(self) -> None:
        """Clear all notifications."""
        self.notifications.clear()
