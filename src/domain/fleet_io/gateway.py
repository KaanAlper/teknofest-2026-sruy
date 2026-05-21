"""PlcGateway port — protokol-bağımsız PLC arayüzü.

Concrete adapter'lar `infrastructure.plc` altında yaşar.
"""

from __future__ import annotations

from typing import AsyncIterator, Protocol, runtime_checkable

from domain.fleet_io.messages import DoorGrant, PickAssignment


@runtime_checkable
class PlcGateway(Protocol):
    async def connect(self) -> None: ...

    async def disconnect(self) -> None: ...

    @property
    def is_connected(self) -> bool: ...

    async def assignments(self) -> AsyncIterator[PickAssignment]:
        """Yarışma süresince gelen rastgele atamaları stream'ler."""
        ...

    async def request_door_open(self, node_id: str) -> None: ...

    async def door_grants(self) -> AsyncIterator[DoorGrant]: ...

    async def notify_arrived(self, node_id: str) -> None: ...

    async def notify_load_picked(self, node_id: str) -> None: ...

    async def notify_load_dropped(self, node_id: str) -> None: ...

    async def notify_at_home(self) -> None: ...
