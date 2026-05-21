"""Mission agregası — bir alma-bırakma görevinin yaşam döngüsü."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from cargobot.domain._shared.events import DomainEvent
from cargobot.domain._shared.exceptions import InvalidPhaseTransition
from cargobot.domain.mission.events import (
    LoadDropped,
    LoadPicked,
    MissionAborted,
    MissionCompleted,
    MissionPhaseChanged,
    MissionStarted,
)
from cargobot.domain.mission.states import MissionPhase, can_transition


@dataclass
class Mission:
    mission_id: UUID
    pickup_node: str
    dropoff_node: str
    phase: MissionPhase = MissionPhase.RECEIVED
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _pending: List[DomainEvent] = field(default_factory=list)

    @classmethod
    def new(cls, pickup: str, dropoff: str) -> "Mission":
        m = cls(mission_id=uuid4(), pickup_node=pickup, dropoff_node=dropoff)
        m._pending.append(
            MissionStarted(
                aggregate_id=str(m.mission_id),
                pickup_node=pickup,
                dropoff_node=dropoff,
            )
        )
        return m

    def transition(self, to_phase: MissionPhase) -> None:
        if not can_transition(self.phase, to_phase):
            raise InvalidPhaseTransition(
                f"{self.phase.value} -> {to_phase.value} izinli değil"
            )
        prev = self.phase
        self.phase = to_phase
        self._pending.append(
            MissionPhaseChanged(
                aggregate_id=str(self.mission_id),
                from_phase=prev,
                to_phase=to_phase,
            )
        )
        if to_phase == MissionPhase.COMPLETED:
            elapsed = (datetime.now(timezone.utc) - self.started_at).total_seconds()
            self._pending.append(
                MissionCompleted(aggregate_id=str(self.mission_id), duration_seconds=elapsed)
            )

    def mark_picked(self, qr_id: str) -> None:
        self._pending.append(
            LoadPicked(
                aggregate_id=str(self.mission_id),
                node=self.pickup_node,
                qr_id=qr_id,
            )
        )

    def mark_dropped(self) -> None:
        self._pending.append(
            LoadDropped(aggregate_id=str(self.mission_id), node=self.dropoff_node)
        )

    def abort(self, reason: str) -> None:
        self.transition(MissionPhase.ABORTED)
        self._pending.append(
            MissionAborted(aggregate_id=str(self.mission_id), reason=reason)
        )

    def collect_events(self) -> list[DomainEvent]:
        events, self._pending = self._pending, []
        return events
