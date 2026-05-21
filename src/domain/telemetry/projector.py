"""Event'lerden RobotSnapshot üreten read-model projeksiyonu.

Bus'a abone olur, mutable internal state tutar, her güncelleme sonrası
immutable bir snapshot oluşturup callback'e iletir.
"""

from __future__ import annotations

from typing import Awaitable, Callable, Optional

from domain._shared.events import DomainEvent
from domain._shared.value_objects import Mode, Pose
from domain.fleet_io.events import (
    PickAssignmentReceived,
    PlcConnected,
    PlcDisconnected,
    PlcMessageReceived,
    PlcMessageSent,
)
from domain.mission.events import (
    LoadDropped,
    LoadPicked,
    MissionAborted,
    MissionCompleted,
    MissionPhaseChanged,
    MissionStarted,
)
from domain.mission.states import RobotStatus, phase_to_status
from domain.navigation.events import RobotPoseUpdated
from domain.perception.events import QrCodeDetected
from domain.safety.events import EmergencyStopActivated, EmergencyStopReleased, ModeSwitched
from domain.telemetry.snapshot import MissionView, PlcView, QrView, RobotSnapshot
from eventbus import AsyncEventBus

SnapshotSink = Callable[[RobotSnapshot], Awaitable[None]]


class TelemetryProjector:
    def __init__(self, bus: AsyncEventBus, sink: SnapshotSink) -> None:
        self._bus = bus
        self._sink = sink
        self._status = RobotStatus.IDLE
        self._mission: Optional[MissionView] = None
        self._last_qr: Optional[QrView] = None
        self._plc = PlcView(connected=False, protocol="none")
        self._pose = Pose(0.0, 0.0, 0.0)
        self._battery = 100.0
        self._mode = Mode.AUTO
        self._emergency = False
        self._map_name: Optional[str] = None
        self._mission_id: Optional[str] = None
        self._pickup: Optional[str] = None
        self._dropoff: Optional[str] = None

    def install(self) -> None:
        b = self._bus
        b.subscribe(MissionStarted, self._on_mission_started)
        b.subscribe(MissionPhaseChanged, self._on_phase_changed)
        b.subscribe(MissionCompleted, self._on_mission_completed)
        b.subscribe(MissionAborted, self._on_mission_aborted)
        b.subscribe(LoadPicked, self._on_load_picked)
        b.subscribe(LoadDropped, self._on_load_dropped)
        b.subscribe(QrCodeDetected, self._on_qr_detected)
        b.subscribe(RobotPoseUpdated, self._on_pose_updated)
        b.subscribe(PlcConnected, self._on_plc_connected)
        b.subscribe(PlcDisconnected, self._on_plc_disconnected)
        b.subscribe(PlcMessageSent, self._on_plc_sent)
        b.subscribe(PlcMessageReceived, self._on_plc_received)
        b.subscribe(PickAssignmentReceived, self._on_assignment)
        b.subscribe(EmergencyStopActivated, self._on_estop_engaged)
        b.subscribe(EmergencyStopReleased, self._on_estop_released)
        b.subscribe(ModeSwitched, self._on_mode_switched)

    # --- event handler'ları
    async def _on_mission_started(self, e: DomainEvent) -> None:
        assert isinstance(e, MissionStarted)
        self._mission_id = e.aggregate_id
        self._pickup = e.pickup_node
        self._dropoff = e.dropoff_node
        await self._emit()

    async def _on_phase_changed(self, e: DomainEvent) -> None:
        assert isinstance(e, MissionPhaseChanged)
        self._status = phase_to_status(e.to_phase)
        if self._mission_id and self._pickup and self._dropoff:
            self._mission = MissionView(
                mission_id=self._mission_id,
                pickup_node=self._pickup,
                dropoff_node=self._dropoff,
                phase=e.to_phase,
            )
        await self._emit()

    async def _on_mission_completed(self, _e: DomainEvent) -> None:
        self._status = RobotStatus.IDLE
        self._mission = None
        await self._emit()

    async def _on_mission_aborted(self, _e: DomainEvent) -> None:
        self._status = RobotStatus.ERROR
        await self._emit()

    async def _on_load_picked(self, _e: DomainEvent) -> None:
        await self._emit()

    async def _on_load_dropped(self, _e: DomainEvent) -> None:
        await self._emit()

    async def _on_qr_detected(self, e: DomainEvent) -> None:
        assert isinstance(e, QrCodeDetected)
        self._last_qr = QrView(qr_id=e.qr_id, timestamp=e.occurred_at)
        await self._emit()

    async def _on_pose_updated(self, e: DomainEvent) -> None:
        assert isinstance(e, RobotPoseUpdated)
        self._pose = e.pose
        await self._emit()

    async def _on_plc_connected(self, e: DomainEvent) -> None:
        assert isinstance(e, PlcConnected)
        self._plc = PlcView(connected=True, protocol=e.protocol, last_tx=None, last_rx=None)
        await self._emit()

    async def _on_plc_disconnected(self, _e: DomainEvent) -> None:
        self._plc = PlcView(connected=False, protocol=self._plc.protocol)
        await self._emit()

    async def _on_plc_sent(self, e: DomainEvent) -> None:
        assert isinstance(e, PlcMessageSent)
        self._plc = PlcView(
            connected=self._plc.connected,
            protocol=self._plc.protocol,
            last_tx=e.payload,
            last_rx=self._plc.last_rx,
        )
        await self._emit()

    async def _on_plc_received(self, e: DomainEvent) -> None:
        assert isinstance(e, PlcMessageReceived)
        self._plc = PlcView(
            connected=self._plc.connected,
            protocol=self._plc.protocol,
            last_tx=self._plc.last_tx,
            last_rx=e.payload,
        )
        await self._emit()

    async def _on_assignment(self, e: DomainEvent) -> None:
        assert isinstance(e, PickAssignmentReceived)
        self._status = RobotStatus.MISSION_RECEIVED
        self._pickup = e.pickup_node
        self._dropoff = e.dropoff_node
        await self._emit()

    async def _on_estop_engaged(self, _e: DomainEvent) -> None:
        self._emergency = True
        self._status = RobotStatus.EMERGENCY_STOP
        await self._emit()

    async def _on_estop_released(self, _e: DomainEvent) -> None:
        self._emergency = False
        await self._emit()

    async def _on_mode_switched(self, e: DomainEvent) -> None:
        assert isinstance(e, ModeSwitched)
        self._mode = e.mode
        await self._emit()

    async def _emit(self) -> None:
        snap = RobotSnapshot(
            status=self._status,
            mission=self._mission,
            last_qr=self._last_qr,
            plc=self._plc,
            pose=self._pose,
            battery_pct=self._battery,
            mode=self._mode,
            emergency=self._emergency,
            map_name=self._map_name,
        )
        await self._sink(snap)

    # Demo / dış güncelleme
    def set_battery(self, pct: float) -> None:
        self._battery = max(0.0, min(100.0, pct))
