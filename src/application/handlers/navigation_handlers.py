"""Navigation context handler'ları.

Mission faz değişimine göre alt seviye sürüş komutu üretir; engelde durdurur,
kapı yaklaşımında PLC'ye haber ver.
"""

from __future__ import annotations

import logging
from typing import Awaitable, Callable

from domain._shared.events import DomainEvent
from domain.fleet_io.gateway import PlcGateway
from domain.mission.events import MissionPhaseChanged
from domain.mission.states import MissionPhase
from domain.navigation.events import NavigationResumed, NavigationStopped
from domain.perception.events import ObstacleCleared, ObstacleDetected
from eventbus import AsyncEventBus

log = logging.getLogger(__name__)


def on_phase_changed(bus: AsyncEventBus, plc: PlcGateway) -> Callable[[DomainEvent], Awaitable[None]]:
    """Mission faz değiştikçe planlayıcıya hedef verir, PLC'ye uygun yerlerde sinyalle."""
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, MissionPhaseChanged)
        # Burada gerçek implementasyonda Nav2 client'a NavigateThroughPoses gönderilir.
        # Şimdilik yön akışını sabitliyoruz.
        if event.to_phase == MissionPhase.AT_DOOR:
            await plc.request_door_open(node_id="q5")
    return handle


def on_obstacle_detected(bus: AsyncEventBus) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, ObstacleDetected)
        # Nav2 zaten durur; biz event'i akışa enjekte ediyoruz ki mission haberdar olsun
        await bus.publish(NavigationStopped(aggregate_id="navigation", reason="obstacle"))
    return handle


def on_obstacle_cleared(bus: AsyncEventBus) -> Callable[[DomainEvent], Awaitable[None]]:
    async def handle(event: DomainEvent) -> None:
        assert isinstance(event, ObstacleCleared)
        await bus.publish(NavigationResumed(aggregate_id="navigation"))
    return handle
