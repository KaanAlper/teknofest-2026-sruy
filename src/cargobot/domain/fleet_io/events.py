"""Fleet I/O domain event'leri."""

from __future__ import annotations

from dataclasses import dataclass

from cargobot.domain._shared.events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class PlcConnected(DomainEvent):
    host: str
    port: int
    protocol: str


@dataclass(frozen=True, kw_only=True)
class PlcDisconnected(DomainEvent):
    reason: str


@dataclass(frozen=True, kw_only=True)
class PickAssignmentReceived(DomainEvent):
    pickup_node: str
    dropoff_node: str


@dataclass(frozen=True, kw_only=True)
class DoorGrantReceived(DomainEvent):
    node_id: str


@dataclass(frozen=True, kw_only=True)
class PlcMessageSent(DomainEvent):
    payload: str


@dataclass(frozen=True, kw_only=True)
class PlcMessageReceived(DomainEvent):
    payload: str


@dataclass(frozen=True, kw_only=True)
class PlcTimeout(DomainEvent):
    last_request: str
