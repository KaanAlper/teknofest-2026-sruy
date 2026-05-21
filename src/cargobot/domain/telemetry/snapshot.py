"""RobotSnapshot — GUI'ye push edilen tek doğru read-model.

Şartname §3.1.1 madde 10 zorunlu alanların hepsini barındırır.
Eksik alan = −4 puan.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional

from cargobot.domain._shared.value_objects import Mode, Pose
from cargobot.domain.mission.states import MissionPhase, RobotStatus


@dataclass(frozen=True, slots=True)
class MissionView:
    mission_id: str
    pickup_node: str
    dropoff_node: str
    phase: MissionPhase


@dataclass(frozen=True, slots=True)
class QrView:
    qr_id: str
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class PlcView:
    connected: bool
    protocol: str
    last_tx: Optional[str] = None
    last_rx: Optional[str] = None


@dataclass(frozen=True, slots=True)
class RobotSnapshot:
    status: RobotStatus = RobotStatus.IDLE
    mission: Optional[MissionView] = None
    last_qr: Optional[QrView] = None
    plc: PlcView = field(default_factory=lambda: PlcView(connected=False, protocol="none"))
    pose: Pose = field(default_factory=lambda: Pose(0.0, 0.0, 0.0))
    battery_pct: float = 100.0
    mode: Mode = Mode.AUTO
    emergency: bool = False
    map_name: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def asdict(self) -> dict:
        return asdict(self)
