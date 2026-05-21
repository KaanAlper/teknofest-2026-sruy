"""Fleet I/O context handler'ları — domain event'lerini PLC'ye yansıt."""

from __future__ import annotations

import logging
from typing import Awaitable, Callable

from cargobot.domain._shared.events import DomainEvent
from cargobot.domain.fleet_io.events import PlcConnected, PlcDisconnected
from cargobot.domain.fleet_io.gateway import PlcGateway
from cargobot.domain.mission.events import (
    LoadDropped,
    LoadPicked,
    MissionAborted,
    MissionCompleted,
)

log = logging.getLogger(__name__)


def on_load_picked(plc: PlcGateway) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, LoadPicked)
        await plc.notify_load_picked(event.node)
    return handle


def on_load_dropped(plc: PlcGateway) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, LoadDropped)
        await plc.notify_load_dropped(event.node)
    return handle


def on_mission_completed(plc: PlcGateway) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, MissionCompleted)
        await plc.notify_at_home()
    return handle


def on_mission_aborted(plc: PlcGateway) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, MissionAborted)
        log.warning("mission iptal: %s", event.reason)
    return handle


def on_plc_connected() -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, PlcConnected)
        log.info("PLC bağlı %s:%d (%s)", event.host, event.port, event.protocol)
    return handle


def on_plc_disconnected() -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, PlcDisconnected)
        log.warning("PLC koptu: %s", event.reason)
    return handle
