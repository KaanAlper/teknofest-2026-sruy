"""GUI ile aynı süreçte çalışan asyncio backend + mock demo senaryosu.

QThread içinde tek bir asyncio loop koşuyor. TelemetryProjector bus event'lerini
yakalayıp snapshot üretiyor; snapshot Qt Signal ile main thread'e iletiliyor,
oradan QML'e push ediliyor.

Demo coroutine: yarışma senaryosunu mock akışla geçer — PLC bağlantı, atama,
waypoint, QR, kapı, drop, return.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict
from typing import Optional

from PySide6.QtCore import QThread, Signal

from application.bootstrap import App
from application.demo import run_demo_scenario
from application.wiring import wire
from domain.fleet_io.events import (
    PlcConnected,
    PlcMessageReceived,
    PlcMessageSent,
)
from domain.telemetry.projector import TelemetryProjector
from domain.telemetry.snapshot import RobotSnapshot
from infrastructure.motor.mock_motor import MockMotor
from infrastructure.plc.mock_adapter import MockPlc

log = logging.getLogger(__name__)


class LocalRunner(QThread):
    snapshotReceived = Signal(dict)
    plcMessageReceived = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self._stop_event: Optional[asyncio.Event] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def run(self) -> None:
        asyncio.run(self._main())

    def stop(self) -> None:
        if self._loop and self._stop_event:
            self._loop.call_soon_threadsafe(self._stop_event.set)

    async def _main(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._stop_event = asyncio.Event()

        plc = MockPlc()
        motor = MockMotor()
        app = App.build(plc=plc, motor=motor)
        wire(app.bus, app.deps)

        projector = TelemetryProjector(app.bus, sink=self._push_snapshot)
        projector.install()
        # PLC mesajlarını da ayrı olarak GUI'ye akıt
        app.bus.subscribe(PlcMessageSent, self._push_plc("TX"))
        app.bus.subscribe(PlcMessageReceived, self._push_plc("RX"))

        await plc.connect()
        await app.bus.publish(
            PlcConnected(aggregate_id="plc", host="mock", port=0, protocol="mock")
        )

        # Demo senaryosu
        asyncio.create_task(run_demo_scenario(app.bus, projector))

        log.info("LocalRunner çalışıyor")
        await self._stop_event.wait()
        await plc.disconnect()

    async def _push_snapshot(self, snap: RobotSnapshot) -> None:
        # asdict immutable kopya verir; Qt signal'a dict olarak geçer
        d = asdict(snap)
        # Enum'ları string'e çevir (QML'de doğrudan okunabilsin)
        d["status"] = snap.status.value
        d["mode"] = snap.mode.value
        if snap.mission:
            d["mission"]["phase"] = snap.mission.phase.value
        self.snapshotReceived.emit(d)

    def _push_plc(self, direction: str):
        async def handle(event):
            self.plcMessageReceived.emit({
                "direction": direction,
                "payload": event.payload,
                "timestamp": event.occurred_at.isoformat(),
            })
        return handle


