"""Mock yarışma senaryosu — gerçek mimariye dokunmadan adımları takip eder.

GUI hem headless modunda kullanılır.
"""

from __future__ import annotations

import asyncio
import logging

from domain._shared.value_objects import Pose
from domain.fleet_io.events import (
    DoorGrantReceived,
    PickAssignmentReceived,
    PlcMessageReceived,
    PlcMessageSent,
)
from domain.navigation.events import RobotPoseUpdated, WaypointReached
from domain.perception.events import QrCodeDetected
from domain.telemetry.projector import TelemetryProjector
from eventbus import AsyncEventBus

log = logging.getLogger(__name__)


async def run_demo_scenario(bus: AsyncEventBus, projector: TelemetryProjector) -> None:
    log.info("[demo] başlıyor")
    await asyncio.sleep(2.0)

    await bus.publish(PlcMessageReceived(aggregate_id="plc", payload="ASSIGN p1 -> d1"))
    await bus.publish(
        PickAssignmentReceived(aggregate_id="plc", pickup_node="p1", dropoff_node="d1")
    )

    await asyncio.sleep(2.5)
    for x in [0.3, 0.7, 1.2, 1.8, 2.4]:
        await bus.publish(RobotPoseUpdated(aggregate_id="nav", pose=Pose(x, 0.5, 0.0)))
        projector.set_battery(95.0 - x * 2)
        await asyncio.sleep(0.4)

    await bus.publish(WaypointReached(aggregate_id="nav", waypoint_id="p1-pre"))
    await asyncio.sleep(0.5)
    await bus.publish(
        QrCodeDetected(
            aggregate_id="camera",
            qr_id="p1",
            pose_camera=Pose(0.0, 0.0, 0.0),
            confidence=0.97,
        )
    )

    await asyncio.sleep(2.0)
    await bus.publish(PlcMessageSent(aggregate_id="plc", payload="door_request q5"))
    await asyncio.sleep(1.0)
    await bus.publish(PlcMessageReceived(aggregate_id="plc", payload="door_grant q5"))
    await bus.publish(DoorGrantReceived(aggregate_id="plc", node_id="q5"))

    log.info("[demo] senaryo tamam")
