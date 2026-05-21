"""Tüm pub/sub bağlantılarının tek listelendiği yer.

C++'taki connection manager'ın Python karşılığı. Sınıf yapmaya gerek yok —
modül içi açık fonksiyonlar yeterli ve okurken "neyin neye bağlı" tek bakışta
görünür.

Yeni bir handler ekleyince burayı güncelle, başka yerde subscribe çağrısı yapma.
"""

from __future__ import annotations

import logging

from cargobot.application.handlers import mission_handlers, navigation_handlers
from cargobot.application.handlers import fleet_handlers, safety_handlers
from cargobot.domain.fleet_io.events import (
    DoorGrantReceived,
    PickAssignmentReceived,
    PlcConnected,
    PlcDisconnected,
)
from cargobot.domain.mission.events import (
    LoadDropped,
    LoadPicked,
    MissionAborted,
    MissionCompleted,
    MissionPhaseChanged,
    MissionStarted,
)
from cargobot.domain.navigation.events import (
    NavigationFailed,
    NavigationStopped,
    WaypointReached,
)
from cargobot.domain.perception.events import (
    ObstacleCleared,
    ObstacleDetected,
    QrCodeDetected,
)
from cargobot.domain.safety.events import EmergencyStopActivated, EmergencyStopReleased
from cargobot.infrastructure.bus import AsyncEventBus

log = logging.getLogger(__name__)


def wire(bus: AsyncEventBus, deps) -> None:
    """Domain handler'larını event bus'a bağlar.

    `deps` ihtiyaç duyulan port'ları taşır (PLC gateway, motor driver vs.).
    Burada **kim neye dinler** açık görünür.
    """

    # PLC'den gelen atama mission saga'yı tetikler
    bus.subscribe(PickAssignmentReceived, mission_handlers.on_pick_assignment(bus))

    # Mission faz geçişleri navigation'u sürer
    bus.subscribe(MissionStarted, mission_handlers.on_mission_started(bus))
    bus.subscribe(MissionPhaseChanged, navigation_handlers.on_phase_changed(bus, deps.plc))
    bus.subscribe(WaypointReached, mission_handlers.on_waypoint_reached(bus))

    # QR kod algılanınca mission ID kontrol eder
    bus.subscribe(QrCodeDetected, mission_handlers.on_qr_detected(bus))

    # Engel: navigation durdur / devam et
    bus.subscribe(ObstacleDetected, navigation_handlers.on_obstacle_detected(bus))
    bus.subscribe(ObstacleCleared, navigation_handlers.on_obstacle_cleared(bus))

    # Kapı izni geldi -> mission devam
    bus.subscribe(DoorGrantReceived, mission_handlers.on_door_grant(bus))

    # Mission tamamlandı / iptal -> PLC'ye bildir
    bus.subscribe(LoadPicked, fleet_handlers.on_load_picked(deps.plc))
    bus.subscribe(LoadDropped, fleet_handlers.on_load_dropped(deps.plc))
    bus.subscribe(MissionCompleted, fleet_handlers.on_mission_completed(deps.plc))
    bus.subscribe(MissionAborted, fleet_handlers.on_mission_aborted(deps.plc))

    # PLC bağlantı durumu telemetriye akar
    bus.subscribe(PlcConnected, fleet_handlers.on_plc_connected())
    bus.subscribe(PlcDisconnected, fleet_handlers.on_plc_disconnected())

    # E-stop tüm hareket akışını dondurur
    bus.subscribe(EmergencyStopActivated, safety_handlers.on_estop_engaged(bus, deps.motor))
    bus.subscribe(EmergencyStopReleased, safety_handlers.on_estop_released(bus))

    # Navigation kendi başarısızlığını mission'a haber verir
    bus.subscribe(NavigationFailed, mission_handlers.on_navigation_failed(bus))
    bus.subscribe(NavigationStopped, mission_handlers.on_navigation_stopped(bus))

    log.info("event bus wiring tamam, %d sınıf dinleniyor", len(bus._subs))
