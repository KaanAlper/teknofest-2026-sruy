"""Navigation domain event'leri."""

from __future__ import annotations

from dataclasses import dataclass

from cargobot.domain._shared.events import DomainEvent
from cargobot.domain._shared.value_objects import Pose


@dataclass(frozen=True, kw_only=True)
class MapBuilt(DomainEvent):
    map_name: str
    width: int
    height: int


@dataclass(frozen=True, kw_only=True)
class RouteDefined(DomainEvent):
    node_count: int
    edge_count: int


@dataclass(frozen=True, kw_only=True)
class PathReady(DomainEvent):
    waypoint_ids: list[str]


@dataclass(frozen=True, kw_only=True)
class WaypointReached(DomainEvent):
    waypoint_id: str


@dataclass(frozen=True, kw_only=True)
class PathDeviationDetected(DomainEvent):
    meters_off: float


@dataclass(frozen=True, kw_only=True)
class RobotPoseUpdated(DomainEvent):
    pose: Pose


@dataclass(frozen=True, kw_only=True)
class NavigationFailed(DomainEvent):
    reason: str


@dataclass(frozen=True, kw_only=True)
class NavigationStopped(DomainEvent):
    reason: str  # "obstacle" | "estop" | "command"


@dataclass(frozen=True, kw_only=True)
class NavigationResumed(DomainEvent):
    pass
