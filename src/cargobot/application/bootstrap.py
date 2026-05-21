"""Uygulama composition root: portları, bus'ı, deps'ı tek yerden kur."""

from __future__ import annotations

from dataclasses import dataclass

from cargobot.application.handlers.safety_handlers import MotorPort
from cargobot.domain.fleet_io.gateway import PlcGateway
from cargobot.domain.safety.aggregate import SafetyState
from cargobot.infrastructure.bus import AsyncEventBus


@dataclass
class Deps:
    """Handler'lara enjekte edilen dış port koleksiyonu."""
    plc: PlcGateway
    motor: MotorPort
    safety: SafetyState


@dataclass
class App:
    bus: AsyncEventBus
    deps: Deps

    @classmethod
    def build(cls, plc: PlcGateway, motor: MotorPort) -> "App":
        return cls(
            bus=AsyncEventBus(),
            deps=Deps(plc=plc, motor=motor, safety=SafetyState()),
        )
