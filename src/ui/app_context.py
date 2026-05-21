"""AppContext — QML'in eriştiği singleton köprü.

WebSocket istemcisi çalıştırır, gelen snapshot'ları Signal ile QML'e iletir.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import websockets
from PySide6.QtCore import Property, QObject, QThread, Signal, Slot


class _WSWorker(QThread):
    snapshotReceived = Signal(dict)
    plcMessageReceived = Signal(dict)
    connectionState = Signal(bool)

    def __init__(self, url: str) -> None:
        super().__init__()
        self._url = url
        self._stop = False

    def run(self) -> None:
        asyncio.run(self._loop())

    async def _loop(self) -> None:
        while not self._stop:
            try:
                async with websockets.connect(self._url) as ws:
                    self.connectionState.emit(True)
                    async for raw in ws:
                        msg = json.loads(raw)
                        if msg.get("type") == "snapshot":
                            self.snapshotReceived.emit(msg["payload"])
                        elif msg.get("type") == "plc_message":
                            self.plcMessageReceived.emit(msg["payload"])
            except Exception:
                self.connectionState.emit(False)
                await asyncio.sleep(2)

    def stop(self) -> None:
        self._stop = True


class AppContext(QObject):
    snapshotChanged = Signal()
    plcMessageReceived = Signal("QVariant")
    connectionStateChanged = Signal()

    def __init__(self, ws_url: str) -> None:
        super().__init__()
        self._snapshot: dict[str, Any] = {}
        self._connected = False
        self._worker = _WSWorker(ws_url)
        self._worker.snapshotReceived.connect(self._on_snapshot)
        self._worker.plcMessageReceived.connect(self._on_plc_message)
        self._worker.connectionState.connect(self._on_connection)

    def start(self) -> None:
        self._worker.start()

    def stop(self) -> None:
        self._worker.stop()
        self._worker.wait(2000)

    @Slot(dict)
    def _on_snapshot(self, payload: dict) -> None:
        self._snapshot = payload
        self.snapshotChanged.emit()

    @Slot(dict)
    def _on_plc_message(self, payload: dict) -> None:
        self.plcMessageReceived.emit(payload)

    @Slot(bool)
    def _on_connection(self, connected: bool) -> None:
        self._connected = connected
        self.connectionStateChanged.emit()

    @Property("QVariant", notify=snapshotChanged)
    def snapshot(self) -> dict:
        return self._snapshot

    @Property(bool, notify=connectionStateChanged)
    def connected(self) -> bool:
        return self._connected

    @Slot(str)
    def sendCommand(self, command_json: str) -> None:
        # TODO: WS üzerinden komut gönderme (commands.py modeline göre)
        pass
