"""Ortak değer nesneleri (Value Objects) — context'ler arası paylaşılır."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class Pose:
    x: float
    y: float
    theta: float

    def distance_to(self, other: "Pose") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)


@dataclass(frozen=True, slots=True)
class Velocity:
    linear: float
    angular: float


@dataclass(frozen=True, slots=True)
class NodeId:
    value: str

    def __str__(self) -> str:
        return self.value


class Mode(str, Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"
