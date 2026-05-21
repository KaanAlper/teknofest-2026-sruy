"""Motor port mock'u."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


class MockMotor:
    def __init__(self) -> None:
        self._enabled = False

    async def stop(self) -> None:
        log.info("[mock-motor] stop")
        self._enabled = False

    async def enable(self) -> None:
        log.info("[mock-motor] enable")
        self._enabled = True
