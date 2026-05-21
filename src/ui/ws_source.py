"""Uzak mod — robot ayrı bir cihazda çalışırken WebSocket üzerinden snapshot dinler.

Geliştirmede kullanılmaz; yarışma günü Jetson + operatör laptop senaryosu için.
"""

from __future__ import annotations

import asyncio
import json
import logging

import websockets
from PySide6.QtCore import QThread, Signal

log = logging.getLogger(__name__)


class WebSocketSource(QThread):
    snapshotReceived = Signal(dict)
    plcMessageReceived = Signal(dict)
    connectionState = Signal(bool)

    def __init__(self, url: str) -> None:
        super().__init__()
        self._url = url
        self._stop = False

    def stop(self) -> None:
        self._stop = True

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
                log.warning("WS bağlantı koptu, yeniden deneniyor", exc_info=True)
                self.connectionState.emit(False)
                await asyncio.sleep(2)
