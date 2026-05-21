"""Mission durum makinesi — şartname §3.1.1 madde 10'daki 8 durum + iç fazlar."""

from __future__ import annotations

from enum import Enum


class RobotStatus(str, Enum):
    IDLE = "IDLE"
    MISSION_RECEIVED = "MISSION_RECEIVED"
    MOVING_UNLOADED = "MOVING_UNLOADED"
    MOVING_LOADED = "MOVING_LOADED"
    WAITING_PLC = "WAITING_PLC"
    RETURNING_HOME = "RETURNING_HOME"
    ERROR = "ERROR"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class MissionPhase(str, Enum):
    RECEIVED = "RECEIVED"
    PLANNING = "PLANNING"
    MOVING_TO_PICKUP = "MOVING_TO_PICKUP"
    APPROACHING_LOAD = "APPROACHING_LOAD"
    PICKING = "PICKING"
    MOVING_TO_DOOR = "MOVING_TO_DOOR"
    AT_DOOR = "AT_DOOR"
    MOVING_TO_DROPOFF = "MOVING_TO_DROPOFF"
    APPROACHING_DROP = "APPROACHING_DROP"
    DROPPING = "DROPPING"
    RETURNING_TO_DOOR = "RETURNING_TO_DOOR"
    RETURNING_HOME = "RETURNING_HOME"
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"


_ALLOWED: dict[MissionPhase, set[MissionPhase]] = {
    MissionPhase.RECEIVED: {MissionPhase.PLANNING, MissionPhase.ABORTED},
    MissionPhase.PLANNING: {MissionPhase.MOVING_TO_PICKUP, MissionPhase.ABORTED},
    MissionPhase.MOVING_TO_PICKUP: {MissionPhase.APPROACHING_LOAD, MissionPhase.ABORTED},
    MissionPhase.APPROACHING_LOAD: {MissionPhase.PICKING, MissionPhase.ABORTED},
    MissionPhase.PICKING: {MissionPhase.MOVING_TO_DOOR, MissionPhase.ABORTED},
    MissionPhase.MOVING_TO_DOOR: {MissionPhase.AT_DOOR, MissionPhase.ABORTED},
    MissionPhase.AT_DOOR: {MissionPhase.MOVING_TO_DROPOFF, MissionPhase.ABORTED},
    MissionPhase.MOVING_TO_DROPOFF: {MissionPhase.APPROACHING_DROP, MissionPhase.ABORTED},
    MissionPhase.APPROACHING_DROP: {MissionPhase.DROPPING, MissionPhase.ABORTED},
    MissionPhase.DROPPING: {MissionPhase.RETURNING_TO_DOOR, MissionPhase.ABORTED},
    MissionPhase.RETURNING_TO_DOOR: {MissionPhase.RETURNING_HOME, MissionPhase.ABORTED},
    MissionPhase.RETURNING_HOME: {MissionPhase.COMPLETED, MissionPhase.ABORTED},
    MissionPhase.COMPLETED: set(),
    MissionPhase.ABORTED: set(),
}


def can_transition(from_phase: MissionPhase, to_phase: MissionPhase) -> bool:
    return to_phase in _ALLOWED[from_phase]


def phase_to_status(phase: MissionPhase) -> RobotStatus:
    """Faz'dan dış-dünyaya gösterilecek şartname durumuna eşleme."""
    match phase:
        case MissionPhase.RECEIVED | MissionPhase.PLANNING:
            return RobotStatus.MISSION_RECEIVED
        case (
            MissionPhase.MOVING_TO_PICKUP
            | MissionPhase.APPROACHING_LOAD
            | MissionPhase.RETURNING_HOME
        ):
            return RobotStatus.MOVING_UNLOADED
        case (
            MissionPhase.PICKING
            | MissionPhase.MOVING_TO_DOOR
            | MissionPhase.MOVING_TO_DROPOFF
            | MissionPhase.APPROACHING_DROP
            | MissionPhase.DROPPING
            | MissionPhase.RETURNING_TO_DOOR
        ):
            return RobotStatus.MOVING_LOADED
        case MissionPhase.AT_DOOR:
            return RobotStatus.WAITING_PLC
        case MissionPhase.COMPLETED:
            return RobotStatus.IDLE
        case MissionPhase.ABORTED:
            return RobotStatus.ERROR
