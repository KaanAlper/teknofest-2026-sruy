"""PLC -> Mission -> PLC tam akışını event bus üzerinden test et."""

from __future__ import annotations

import asyncio

import pytest

from application.bootstrap import App
from application.wiring import wire
from domain.fleet_io.events import PickAssignmentReceived
from domain.mission.events import MissionPhaseChanged, MissionStarted
from domain.mission.states import MissionPhase
from infrastructure.motor.mock_motor import MockMotor
from infrastructure.plc.mock_adapter import MockPlc


@pytest.mark.asyncio
async def test_pick_assignment_starts_mission_and_plans():
    app = App.build(plc=MockPlc(), motor=MockMotor())
    wire(app.bus, app.deps)

    seen: list[MissionPhaseChanged] = []

    async def capture(e):
        seen.append(e)

    app.bus.subscribe(MissionPhaseChanged, capture)

    started: list[MissionStarted] = []

    async def cap_start(e):
        started.append(e)

    app.bus.subscribe(MissionStarted, cap_start)

    # PLC bir atama yayar
    await app.bus.publish(
        PickAssignmentReceived(aggregate_id="plc", pickup_node="P1", dropoff_node="D1")
    )
    # MissionStarted handler bir sonraki fazları publish eder; akış asenkron
    await asyncio.sleep(0.05)

    assert len(started) == 1
    assert started[0].pickup_node == "P1"
    phases = [e.to_phase for e in seen]
    assert MissionPhase.PLANNING in phases
    assert MissionPhase.MOVING_TO_PICKUP in phases
