"""QML'in eriştiği singleton köprü.

Veri kaynağı (lokal event bus köprüsü ya da uzak WebSocket istemcisi) dışarıdan
verilir; AppContext kaynak tipini bilmez, yalnız snapshot/PLC mesajlarını
QML'e yansıtır.

Kaynak Qt Signal'ları kullanır:
    - snapshotReceived(dict)
    - plcMessageReceived(dict)
"""

from __future__ import annotations

from typing import Any, Protocol

from PySide6.QtCore import Property, QObject, Signal, Slot


class TelemetrySource(Protocol):
    snapshotReceived: Signal
    plcMessageReceived: Signal

    def start(self) -> None: ...
    def stop(self) -> None: ...


class AppContext(QObject):
    snapshotChanged = Signal()
    plcMessageReceived = Signal("QVariant")

    def __init__(self, source: TelemetrySource) -> None:
        super().__init__()
        self._snapshot: dict[str, Any] = {}
        self._source = source
        self._source.snapshotReceived.connect(self._on_snapshot)
        self._source.plcMessageReceived.connect(self._on_plc_message)

    def start(self) -> None:
        self._source.start()

    def stop(self) -> None:
        self._source.stop()

    @Slot(dict)
    def _on_snapshot(self, payload: dict) -> None:
        self._snapshot = payload
        self.snapshotChanged.emit()

    @Slot(dict)
    def _on_plc_message(self, payload: dict) -> None:
        self.plcMessageReceived.emit(payload)

    @Property("QVariant", notify=snapshotChanged)
    def snapshot(self) -> dict:
        return self._snapshot
