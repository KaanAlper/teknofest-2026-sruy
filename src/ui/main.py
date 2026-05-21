"""PySide6 + QML operatör arayüzü entry-point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from ui.app_context import AppContext


def main() -> None:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("CargoBot Operatör Panel")
    app.setOrganizationName("CargoBot")

    engine = QQmlApplicationEngine()

    context = AppContext(ws_url="ws://localhost:8765/telemetry")
    engine.rootContext().setContextProperty("AppContext", context)

    qml_file = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        sys.exit(-1)

    context.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
