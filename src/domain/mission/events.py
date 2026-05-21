"""Mission bounded context'in yayınladığı domain event'leri."""

from __future__ import annotations

from dataclasses import dataclass

from domain._shared.events import DomainEvent
from domain.mission.states import MissionPhase


@dataclass(frozen=True, kw_only=True)
class MissionAssigned(DomainEvent):
    pickup_node: str
    dropoff_node: str


@dataclass(frozen=True, kw_only=True)
class MissionStarted(DomainEvent):
    pickup_node: str
    dropoff_node: str


@dataclass(frozen=True, kw_only=True)
class MissionPhaseChanged(DomainEvent):
    from_phase: MissionPhase
    to_phase: MissionPhase


@dataclass(frozen=True, kw_only=True)
class LoadPicked(DomainEvent):
    node: str
    qr_id: str


@dataclass(frozen=True, kw_only=True)
class LoadDropped(DomainEvent):
    node: str


@dataclass(frozen=True, kw_only=True)
class MissionCompleted(DomainEvent):
    duration_seconds: float


@dataclass(frozen=True, kw_only=True)
class MissionAborted(DomainEvent):
    reason: str


@dataclass(frozen=True, kw_only=True)
class MissionGenericError(DomainEvent):
    code: str
    detail: str
