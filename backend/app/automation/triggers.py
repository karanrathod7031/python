"""Event-based triggers for automated actions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from app.utils.logger import setup_logger

logger = setup_logger("jarvis.automation.triggers")


class TriggerType(str, Enum):
    TIME = "time"
    BATTERY_LOW = "battery_low"
    HIGH_CPU = "high_cpu"
    HIGH_MEMORY = "high_memory"
    FILE_CHANGE = "file_change"
    CUSTOM = "custom"


@dataclass
class Trigger:
    """An event-based trigger."""

    id: str
    name: str
    trigger_type: TriggerType
    condition: dict[str, Any]
    action: str
    enabled: bool = True
    last_fired: Optional[str] = None
    fire_count: int = 0


class TriggerEngine:
    """Monitor events and fire triggers when conditions are met."""

    def __init__(self) -> None:
        self.triggers: dict[str, Trigger] = {}
        self._action_handler: Optional[Callable[..., Any]] = None
        self._monitoring = False

    def set_action_handler(self, handler: Callable[..., Any]) -> None:
        """Set the callback for trigger actions."""
        self._action_handler = handler

    def add_trigger(
        self,
        trigger_id: str,
        name: str,
        trigger_type: TriggerType,
        condition: dict[str, Any],
        action: str,
    ) -> Trigger:
        """Register a new trigger."""
        trigger = Trigger(
            id=trigger_id,
            name=name,
            trigger_type=trigger_type,
            condition=condition,
            action=action,
        )
        self.triggers[trigger_id] = trigger
        logger.info(f"Added trigger: {name} ({trigger_type.value})")
        return trigger

    def remove_trigger(self, trigger_id: str) -> bool:
        """Remove a trigger."""
        if trigger_id in self.triggers:
            del self.triggers[trigger_id]
            return True
        return False

    async def check_triggers(self) -> list[str]:
        """Check all triggers and fire those whose conditions are met."""
        fired: list[str] = []

        for trigger in self.triggers.values():
            if not trigger.enabled:
                continue

            if await self._evaluate_condition(trigger):
                trigger.last_fired = datetime.now().isoformat()
                trigger.fire_count += 1
                fired.append(trigger.id)

                if self._action_handler:
                    try:
                        await self._action_handler(trigger.action)
                        logger.info(f"Trigger fired: {trigger.name}")
                    except Exception as exc:
                        logger.error(f"Trigger action failed: {exc}")

        return fired

    async def _evaluate_condition(self, trigger: Trigger) -> bool:
        """Evaluate whether a trigger's condition is met."""
        try:
            if trigger.trigger_type == TriggerType.BATTERY_LOW:
                import psutil

                battery = psutil.sensors_battery()
                if battery:
                    threshold = trigger.condition.get("threshold", 20)
                    return battery.percent <= threshold

            elif trigger.trigger_type == TriggerType.HIGH_CPU:
                import psutil

                threshold = trigger.condition.get("threshold", 90)
                return psutil.cpu_percent(interval=1) >= threshold

            elif trigger.trigger_type == TriggerType.HIGH_MEMORY:
                import psutil

                threshold = trigger.condition.get("threshold", 90)
                return psutil.virtual_memory().percent >= threshold

        except ImportError:
            pass
        except Exception as exc:
            logger.error(f"Condition evaluation error: {exc}")

        return False

    def list_triggers(self) -> list[Trigger]:
        """List all triggers."""
        return list(self.triggers.values())
