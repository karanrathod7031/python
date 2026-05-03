"""Action confirmation system for risky operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

RISKY_ACTIONS = {
    "shutdown",
    "restart",
    "delete",
    "format",
    "remove",
    "kill",
    "wipe",
    "uninstall",
}


@dataclass
class PendingAction:
    """A pending action awaiting confirmation."""

    id: str
    action: str
    details: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    confirmed: bool = False
    expires_in_seconds: int = 60


class ConfirmationManager:
    """Manage confirmations for risky actions."""

    def __init__(self) -> None:
        self._pending: dict[str, PendingAction] = {}

    def requires_confirmation(self, action: str) -> bool:
        """Check if an action requires confirmation."""
        return action.lower() in RISKY_ACTIONS

    def request_confirmation(
        self, action_id: str, action: str, details: str
    ) -> PendingAction:
        """Request confirmation for an action."""
        pending = PendingAction(id=action_id, action=action, details=details)
        self._pending[action_id] = pending
        return pending

    def confirm(self, action_id: str) -> Optional[PendingAction]:
        """Confirm a pending action."""
        action = self._pending.pop(action_id, None)
        if action:
            action.confirmed = True
        return action

    def deny(self, action_id: str) -> Optional[PendingAction]:
        """Deny a pending action."""
        return self._pending.pop(action_id, None)

    def get_pending(self) -> list[PendingAction]:
        """List all pending confirmations."""
        return list(self._pending.values())
