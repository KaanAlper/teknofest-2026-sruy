"""Robot tarafı entry-point."""

from __future__ import annotations

import asyncio
import logging
import signal

from application.bootstrap import App
from application.wiring import wire
from infrastructure.plc.mock_adapter import MockPlc
from infrastructure.motor.mock_motor import MockMotor

log = logging.getLogger(__name__)


async def run() -> None:
    plc = MockPlc()
    motor = MockMotor()

    app = App.build(plc=plc, motor=motor)
    wire(app.bus, app.deps)

    await plc.connect()

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    log.info("CargoBot çalışıyor — Ctrl+C ile dur")
    await stop.wait()
    await plc.disconnect()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    asyncio.run(run())


if __name__ == "__main__":
    main()
