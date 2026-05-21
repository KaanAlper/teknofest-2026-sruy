"""Safety agregası — e-stop ve mode invariant'larını korur."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from cargobot.domain._shared.events import DomainEvent
from cargobot.domain._shared.exceptions import SafetyViolation
from cargobot.domain._shared.value_objects import Mode
from cargobot.domain.safety.events import (
    EmergencyStopActivated,
    EmergencyStopReleased,
    ModeSwitched,
)


@dataclass
class SafetyState:
    mode: Mode = Mode.AUTO
    estop_active: bool = False
    _pending: List[DomainEvent] = field(default_factory=list)

    def engage_estop(self, source: str = "software") -> None:
        if self.estop_active:
            return
        self.estop_active = True
        self._pending.append(EmergencyStopActivated(aggregate_id="safety", source=source))

    def release_estop(self) -> None:
        if not self.estop_active:
            return
        self.estop_active = False
        self._pending.append(EmergencyStopReleased(aggregate_id="safety"))

    def switch_mode(self, mode: Mode) -> None:
        if self.mode == mode:
            return
        self.mode = mode
        self._pending.append(ModeSwitched(aggregate_id="safety", mode=mode))

    def allow_autonomous_command(self) -> None:
        if self.estop_active:
            raise SafetyViolation("E-stop aktif — otonom komut reddedildi")
        if self.mode != Mode.AUTO:
            raise SafetyViolation("Mod AUTO değil — otonom komut reddedildi")

    def allow_manual_command(self) -> None:
        if self.estop_active:
            raise SafetyViolation("E-stop aktif — manuel komut reddedildi")
        if self.mode != Mode.MANUAL:
            raise SafetyViolation("Mod MANUAL değil — manuel komut reddedildi")

    def collect_events(self) -> list[DomainEvent]:
        events, self._pending = self._pending, []
        return events
