"""CargoBot ana entry-point.

Varsayılan davranış: operatör arayüzünü mock backend ile aç (lokal mod,
event bus → Qt signal → QML). Yarışma günü için `--remote ws://host:port`
ile robot süreciyle WebSocket üzerinden konuşulur.

Sadece konsoldan robot çekirdeğini koşturmak istersen `--headless` ile
GUI olmadan mock akışı log'a yansıt.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal


def main() -> None:
    parser = argparse.ArgumentParser(description="CargoBot")
    parser.add_argument(
        "--remote",
        metavar="URL",
        help="GUI'i uzak modda aç: WebSocket URL'si",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="GUI'siz, sadece robot çekirdeği + log",
    )
    parser.add_argument("--log", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=args.log.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.headless:
        asyncio.run(_run_headless())
        return

    # GUI modu — ui.main argparse'ı kendi çalıştırır
    import sys
    sys.argv = [sys.argv[0]] + (["--remote", args.remote] if args.remote else [])
    from ui.main import main as ui_main
    ui_main()


async def _run_headless() -> None:
    from application.bootstrap import App
    from application.profile import Profile
    from application.wiring import wire
    from domain.fleet_io.events import PlcConnected
    from domain.telemetry.projector import TelemetryProjector
    from application.demo import run_demo_scenario

    log = logging.getLogger("cargobot")

    loop = asyncio.get_running_loop()
    app = await App.build_from_profile(asyncio_loop=loop)
    wire(app.bus, app.deps)

    async def log_snapshot(snap):
        log.info(
            "snapshot status=%s mission=%s qr=%s plc=%s",
            snap.status.value,
            snap.mission and snap.mission.phase.value,
            snap.last_qr and snap.last_qr.qr_id,
            snap.plc.connected,
        )

    projector = TelemetryProjector(app.bus, sink=log_snapshot)
    projector.install()

    # PlcConnected event'i — protokol bilgisi profile'dan gelir
    await app.bus.publish(PlcConnected(
        aggregate_id="plc",
        host=app.config.plc_host or "mock",
        port=app.config.plc_port,
        protocol="modbus" if app.config.profile != Profile.MOCK else "mock",
    ))

    if app.config.run_demo:
        asyncio.create_task(run_demo_scenario(app.bus, projector))
    else:
        log.info("Demo akış kapalı (profile=%s) — gerçek PLC akışı bekleniyor", app.config.profile.value)

    stop = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    log.info("Headless mod — Ctrl+C ile dur")
    await stop.wait()
    await app.deps.plc.disconnect()


if __name__ == "__main__":
    main()
