"""Navigation context'i için değer nesneleri."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from cargobot.domain._shared.value_objects import Pose


class NodeType(str, Enum):
    HOME = "home"
    IDLE = "idle"
    PICKUP = "pickup"
    DROPOFF = "dropoff"
    DOOR_REQUEST = "door_request"
    DOCK = "dock"
    WAYPOINT = "waypoint"


@dataclass(frozen=True, slots=True)
class Waypoint:
    node_id: str
    type: NodeType
    pose: Pose


@dataclass(frozen=True, slots=True)
class Edge:
    from_id: str
    to_id: str
    cost: float


@dataclass(frozen=True, slots=True)
class Path:
    mission_id: str
    waypoints: List[Waypoint]


@dataclass(frozen=True, slots=True)
class MapMetadata:
    name: str
    resolution: float  # meters per pixel
    width: int
    height: int
    origin: Pose
