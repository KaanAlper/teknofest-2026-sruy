"""PySide6 + QML operatör arayüzü entry-point.

Varsayılan: lokal mod — robot çekirdeği ve UI aynı süreçte, event bus
üzerinden snapshot push edilir. Yarışma günü için `--remote ws://host:port`
ile WebSocket istemcisine geçilebilir.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from ui.app_context import AppContext
from ui.local_runner import LocalRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="CargoBot operatör paneli")
    parser.add_argument(
        "--remote",
        metavar="URL",
        help="Uzak modda çalış: WebSocket URL'si (ör. ws://192.168.1.42:8765/telemetry)",
    )
    parser.add_argument("--log", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=args.log.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    app = QGuiApplication(sys.argv)
    app.setApplicationName("CargoBot Operatör Panel")
    app.setOrganizationName("CargoBot")

    if args.remote:
        from ui.ws_source import WebSocketSource
        source = WebSocketSource(args.remote)
    else:
        source = LocalRunner()

    context = AppContext(source)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("AppContext", context)

    qml_file = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        sys.exit(-1)

    context.start()
    exit_code = app.exec()
    context.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
