"""Modbus TCP PLC adapter — pymodbus async istemcisi ile.

Yarışmadan önce kullanılacak protokol netleşecek (Modbus TCP veya OPC UA).
Bu adapter Modbus TCP için. Register eşlemesi configurable, default şema:

    holding[100] = pickup_node      (PLC → robot)
    holding[101] = dropoff_node     (PLC → robot)
    holding[200] = door_request     (robot → PLC, 1 yaz → talep)
    holding[201] = door_grant       (PLC → robot, 1 olunca geçiş izni)
    holding[300] = load_picked_ack  (robot → PLC, 1 yaz)
    holding[301] = load_dropped_ack (robot → PLC, 1 yaz)

PlcGateway port'unu uygular. Bağlantı koparsa 2 sn'de tekrar dener.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from pymodbus.client import AsyncModbusTcpClient

from domain.fleet_io.messages import DoorGrant, PickAssignment

log = logging.getLogger(__name__)


@dataclass
class ModbusRegisters:
    pickup: int = 100
    dropoff: int = 101
    door_request: int = 200
    door_grant: int = 201
    load_picked: int = 300
    load_dropped: int = 301
    at_home: int = 302


class ModbusPlc:
    def __init__(
        self,
        host: str,
        port: int = 502,
        regs: ModbusRegisters | None = None,
        poll_period_s: float = 0.2,
    ) -> None:
        self._host = host
        self._port = port
        self._regs = regs or ModbusRegisters()
        self._poll = poll_period_s
        self._client: Optional[AsyncModbusTcpClient] = None
        self._connected = False
        self._assignments_q: asyncio.Queue[PickAssignment] = asyncio.Queue()
        self._door_q: asyncio.Queue[DoorGrant] = asyncio.Queue()
        self._poll_task: Optional[asyncio.Task] = None
        self._last_pickup = 0
        self._last_grant = 0

    async def connect(self) -> None:
        self._client = AsyncModbusTcpClient(host=self._host, port=self._port)
        await self._client.connect()
        self._connected = self._client.connected
        if not self._connected:
            raise ConnectionError(f"PLC bağlantısı kurulamadı {self._host}:{self._port}")
        log.info("Modbus PLC bağlı %s:%d", self._host, self._port)
        self._poll_task = asyncio.create_task(self._poll_loop())

    async def disconnect(self) -> None:
        if self._poll_task:
            self._poll_task.cancel()
        if self._client:
            self._client.close()
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def assignments(self) -> AsyncIterator[PickAssignment]:
        while self._connected:
            yield await self._assignments_q.get()

    async def door_grants(self) -> AsyncIterator[DoorGrant]:
        while self._connected:
            yield await self._door_q.get()

    async def request_door_open(self, node_id: str) -> None:
        await self._write(self._regs.door_request, 1)
        log.info("door_request -> %s", node_id)

    async def notify_arrived(self, node_id: str) -> None:
        # Konvansiyon: register 303'e node hash veya sıralı ID
        pass

    async def notify_load_picked(self, node_id: str) -> None:
        await self._write(self._regs.load_picked, 1)

    async def notify_load_dropped(self, node_id: str) -> None:
        await self._write(self._regs.load_dropped, 1)

    async def notify_at_home(self) -> None:
        await self._write(self._regs.at_home, 1)

    # --- iç ---
    async def _poll_loop(self) -> None:
        while self._connected and self._client and self._client.connected:
            try:
                rr = await self._client.read_holding_registers(
                    self._regs.pickup, count=2
                )
                if not rr.isError():
                    pickup, dropoff = rr.registers
                    if pickup != 0 and pickup != self._last_pickup:
                        self._last_pickup = pickup
                        await self._assignments_q.put(
                            PickAssignment(
                                pickup_node=f"p{pickup}", dropoff_node=f"d{dropoff}"
                            )
                        )

                gr = await self._client.read_holding_registers(self._regs.door_grant, count=1)
                if not gr.isError():
                    grant = gr.registers[0]
                    if grant == 1 and self._last_grant == 0:
                        self._last_grant = 1
                        await self._door_q.put(DoorGrant(node_id="q5"))
                    elif grant == 0:
                        self._last_grant = 0

            except Exception:
                log.exception("Modbus poll hatası, yeniden deneme")
                await asyncio.sleep(2.0)
                continue

            await asyncio.sleep(self._poll)

    async def _write(self, address: int, value: int) -> None:
        if not (self._client and self._client.connected):
            log.warning("PLC bağlı değil, write atlandı %d=%d", address, value)
            return
        await self._client.write_register(address, value)
