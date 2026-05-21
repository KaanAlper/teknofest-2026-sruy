"""Application komutları — emir kipindeki isimler."""

from __future__ import annotations

from dataclasses import dataclass

from domain._shared.value_objects import Mode, Velocity


@dataclass(frozen=True)
class StartMissionCommand:
    pickup_node: str
    dropoff_node: str


@dataclass(frozen=True)
class AbortMissionCommand:
    reason: str


@dataclass(frozen=True)
class BuildMapCommand:
    pass


@dataclass(frozen=True)
class SaveMapCommand:
    name: str


@dataclass(frozen=True)
class LoadMapCommand:
    name: str


@dataclass(frozen=True)
class DefineRouteCommand:
    route_yaml: str


@dataclass(frozen=True)
class ManualDriveCommand:
    velocity: Velocity


@dataclass(frozen=True)
class EngageEStopCommand:
    pass


@dataclass(frozen=True)
class ReleaseEStopCommand:
    pass


@dataclass(frozen=True)
class SwitchModeCommand:
    mode: Mode


@dataclass(frozen=True)
class ConnectPlcCommand:
    pass


@dataclass(frozen=True)
class StartChargingCommand:
    pass
