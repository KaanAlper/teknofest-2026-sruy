"""Perception domain event'leri."""

from __future__ import annotations

from dataclasses import dataclass

from cargobot.domain._shared.events import DomainEvent
from cargobot.domain._shared.value_objects import Pose


@dataclass(frozen=True, kw_only=True)
class QrCodeDetected(DomainEvent):
    qr_id: str
    pose_camera: Pose
    confidence: float


@dataclass(frozen=True, kw_only=True)
class ArucoMarkerDetected(DomainEvent):
    marker_id: int
    pose_6dof: Pose


@dataclass(frozen=True, kw_only=True)
class LineDetected(DomainEvent):
    centerline_offset_px: float
    slope_deg: float


@dataclass(frozen=True, kw_only=True)
class LineLost(DomainEvent):
    last_offset: float


@dataclass(frozen=True, kw_only=True)
class ObstacleDetected(DomainEvent):
    distance_m: float
    angle_rad: float


@dataclass(frozen=True, kw_only=True)
class ObstacleCleared(DomainEvent):
    pass
