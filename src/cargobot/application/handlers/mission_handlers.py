"""Mission context'inin event tepkileri.

Her fonksiyon bir handler factory: dış bağımlılıkları (bus, repo, port) closure'a
alıp asıl handler'ı döner. wiring.py bunları toplar ve bus'a register eder.

Burada mission agregasını yönetir, kendi event'lerini bus'a iletir.
"""

from __future__ import annotations

import logging
from typing import Callable, Awaitable

from cargobot.domain._shared.events import DomainEvent
from cargobot.domain.fleet_io.events import DoorGrantReceived, PickAssignmentReceived
from cargobot.domain.mission.aggregate import Mission
from cargobot.domain.mission.events import MissionStarted
from cargobot.domain.mission.states import MissionPhase
from cargobot.domain.navigation.events import (
    NavigationFailed,
    NavigationStopped,
    WaypointReached,
)
from cargobot.domain.perception.events import QrCodeDetected
from cargobot.infrastructure.bus import AsyncEventBus

log = logging.getLogger(__name__)

# Tek-mission saha senaryosu — repo soyutlamasını sade tutuyoruz
_active: Mission | None = None


def _set(m: Mission | None) -> None:
    global _active
    _active = m


def _get() -> Mission | None:
    return _active


async def _flush(bus: AsyncEventBus, m: Mission) -> None:
    await bus.publish_many(m.collect_events())


def on_pick_assignment(bus: AsyncEventBus) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, PickAssignmentReceived)
        if _get() is not None:
            log.warning("önceki mission bitmemişken yeni atama geldi, görmezden gelindi")
            return
        m = Mission.new(event.pickup_node, event.dropoff_node)
        _set(m)
        await _flush(bus, m)
    return handle


def on_mission_started(bus: AsyncEventBus) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, MissionStarted)
        m = _get()
        if m is None:
            return
        m.transition(MissionPhase.PLANNING)
        m.transition(MissionPhase.MOVING_TO_PICKUP)
        await _flush(bus, m)
    return handle


def on_waypoint_reached(bus: AsyncEventBus) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, WaypointReached)
        m = _get()
        if m is None:
            return
        next_phase = _next_phase_for(m.phase, event.waypoint_id)
        if next_phase is None:
            return
        m.transition(next_phase)
        await _flush(bus, m)
    return handle


def on_qr_detected(bus: AsyncEventBus) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, QrCodeDetected)
        m = _get()
        if m is None:
            return
        if m.phase == MissionPhase.APPROACHING_LOAD and event.qr_id == m.pickup_node:
            m.transition(MissionPhase.PICKING)
            m.mark_picked(event.qr_id)
            await _flush(bus, m)
    return handle


def on_door_grant(bus: AsyncEventBus) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, DoorGrantReceived)
        m = _get()
        if m is None or m.phase != MissionPhase.AT_DOOR:
            return
        m.transition(MissionPhase.MOVING_TO_DROPOFF)
        await _flush(bus, m)
    return handle


def on_navigation_failed(bus: AsyncEventBus) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, NavigationFailed)
        m = _get()
        if m is None:
            return
        m.abort(f"navigation: {event.reason}")
        await _flush(bus, m)
        _set(None)
    return handle


def on_navigation_stopped(bus: AsyncEventBus) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        # şimdilik sadece logla — engelde durma normal akış
        log.info("navigation duraladı: %s", event.reason)
    return handle


def _next_phase_for(current: MissionPhase, waypoint_id: str) -> MissionPhase | None:
    # küçük geçiş tablosu, dış kullanım için aggregate üstünde değil burada
    if current == MissionPhase.MOVING_TO_PICKUP:
        return MissionPhase.APPROACHING_LOAD
    if current == MissionPhase.MOVING_TO_DOOR:
        return MissionPhase.AT_DOOR
    if current == MissionPhase.MOVING_TO_DROPOFF:
        return MissionPhase.APPROACHING_DROP
    if current == MissionPhase.RETURNING_HOME and waypoint_id == "home":
        return MissionPhase.COMPLETED
    return None
