"""PLC mock — yarışma protokolü gelene kadar geliştirme ve test için."""

from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator

from cargobot.domain.fleet_io.messages import DoorGrant, PickAssignment

log = logging.getLogger(__name__)


class MockPlc:
    def __init__(self) -> None:
        self._connected = False
        self._door_q: asyncio.Queue[DoorGrant] = asyncio.Queue()
        self._assign_q: asyncio.Queue[PickAssignment] = asyncio.Queue()

    async def connect(self) -> None:
        self._connected = True
        log.info("[mock-plc] bağlandı")

    async def disconnect(self) -> None:
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def assignments(self) -> AsyncIterator[PickAssignment]:
        while self._connected:
            yield await self._assign_q.get()

    async def request_door_open(self, node_id: str) -> None:
        log.info("[mock-plc] door request %s -> grant veriliyor (1 sn)", node_id)
        await asyncio.sleep(1.0)
        await self._door_q.put(DoorGrant(node_id=node_id))

    async def door_grants(self) -> AsyncIterator[DoorGrant]:
        while self._connected:
            yield await self._door_q.get()

    async def notify_arrived(self, node_id: str) -> None:
        log.info("[mock-plc] arrived %s", node_id)

    async def notify_load_picked(self, node_id: str) -> None:
        log.info("[mock-plc] load picked %s", node_id)

    async def notify_load_dropped(self, node_id: str) -> None:
        log.info("[mock-plc] load dropped %s", node_id)

    async def notify_at_home(self) -> None:
        log.info("[mock-plc] at home")

    # Test yardımcısı
    async def push_assignment(self, pickup: str, dropoff: str) -> None:
        await self._assign_q.put(PickAssignment(pickup_node=pickup, dropoff_node=dropoff))
