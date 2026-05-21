"""PLC ile değişilen mesajların protokol-bağımsız domain modeli."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class MessageDirection(str, Enum):
    TX = "TX"
    RX = "RX"


@dataclass(frozen=True, slots=True)
class PlcMessage:
    direction: MessageDirection
    payload: str
    timestamp: datetime

    @classmethod
    def tx(cls, payload: str) -> "PlcMessage":
        return cls(MessageDirection.TX, payload, datetime.now(timezone.utc))

    @classmethod
    def rx(cls, payload: str) -> "PlcMessage":
        return cls(MessageDirection.RX, payload, datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class PickAssignment:
    pickup_node: str
    dropoff_node: str


@dataclass(frozen=True, slots=True)
class DoorRequest:
    node_id: str


@dataclass(frozen=True, slots=True)
class DoorGrant:
    node_id: str
