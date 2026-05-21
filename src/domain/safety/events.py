"""Safety bounded context event'leri."""

from __future__ import annotations

from dataclasses import dataclass

from domain._shared.events import DomainEvent
from domain._shared.value_objects import Mode


@dataclass(frozen=True, kw_only=True)
class EmergencyStopActivated(DomainEvent):
    source: str  # "button" | "software" | "lidar_safety"


@dataclass(frozen=True, kw_only=True)
class EmergencyStopReleased(DomainEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class ModeSwitched(DomainEvent):
    mode: Mode


@dataclass(frozen=True, kw_only=True)
class SafetyViolationDetected(DomainEvent):
    kind: str
    value: float
    limit: float
