"""Algı portları (abstract). Gerçek implementasyonlar infrastructure katmanında."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from cargobot.domain.perception.events import (
    LineDetected,
    LineLost,
    ObstacleDetected,
    QrCodeDetected,
)


@runtime_checkable
class QrDetector(Protocol):
    async def scan(self, frame_bytes: bytes) -> list[QrCodeDetected]: ...


@runtime_checkable
class LineDetector(Protocol):
    async def detect(self, frame_bytes: bytes) -> LineDetected | LineLost: ...


@runtime_checkable
class ObstacleDetector(Protocol):
    async def evaluate(self, scan_ranges: list[float], angles: list[float]) -> ObstacleDetected | None: ...
