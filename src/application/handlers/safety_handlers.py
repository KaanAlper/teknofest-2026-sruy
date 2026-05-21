"""Safety event handler'ları — e-stop tetiği motora ulaşır, mode değişimi log'a."""

from __future__ import annotations

import logging
from typing import Awaitable, Callable, Protocol

from domain._shared.events import DomainEvent
from domain.safety.events import EmergencyStopActivated, EmergencyStopReleased
from eventbus import AsyncEventBus

log = logging.getLogger(__name__)


class MotorPort(Protocol):
    async def stop(self) -> None: ...
    async def enable(self) -> None: ...


def on_estop_engaged(bus: AsyncEventBus, motor: MotorPort) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, EmergencyStopActivated)
        await motor.stop()
        log.critical("E-STOP aktif (%s) — tüm motorlar durduruldu", event.source)
    return handle


def on_estop_released(bus: AsyncEventBus) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, EmergencyStopReleased)
        log.info("E-STOP serbest, sistem operatör onayı bekliyor")
    return handle
