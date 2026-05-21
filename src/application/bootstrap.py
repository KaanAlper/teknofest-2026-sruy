"""Composition root: profil seçer, port'ları ona göre wire eder."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional

from application.handlers.safety_handlers import MotorPort
from application.profile import Profile, ProfileConfig, current
from domain.fleet_io.gateway import PlcGateway
from domain.safety.aggregate import SafetyState
from eventbus import AsyncEventBus

log = logging.getLogger(__name__)


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
    config: Optional[ProfileConfig] = None
    ros2_runtime: object | None = None

    @classmethod
    async def build_from_profile(
        cls, asyncio_loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> "App":
        cfg = current()
        log.info("Profil: %s", cfg.profile.value)

        plc, motor, runtime = await _wire_adapters(cfg, asyncio_loop)
        return cls(
            bus=AsyncEventBus(),
            deps=Deps(plc=plc, motor=motor, safety=SafetyState()),
            config=cfg,
            ros2_runtime=runtime,
        )

    @classmethod
    def build(cls, plc: PlcGateway, motor: MotorPort) -> "App":
        """Test ve mock için doğrudan kurulum — profil okumaz."""
        cfg = ProfileConfig(
            profile=Profile.MOCK,
            plc_host="",
            plc_port=0,
            use_ros2=False,
            run_demo=True,
        )
        return cls(
            bus=AsyncEventBus(),
            deps=Deps(plc=plc, motor=motor, safety=SafetyState()),
            config=cfg,
        )


async def _wire_adapters(cfg: ProfileConfig, loop):
    """Profil için uygun adapter'leri kur. ROS2/PLC yoksa graceful fallback."""
    runtime = None

    if cfg.profile == Profile.MOCK:
        from infrastructure.motor.mock_motor import MockMotor
        from infrastructure.plc.mock_adapter import MockPlc
        return MockPlc(), MockMotor(), None

    # SIM / REAL — gerçek Modbus + ROS2
    from infrastructure.plc.modbus_adapter import ModbusPlc

    plc = ModbusPlc(host=cfg.plc_host, port=cfg.plc_port)
    try:
        await plc.connect()
    except Exception:
        log.exception("PLC bağlantısı başarısız, mock'a düşülüyor")
        from infrastructure.plc.mock_adapter import MockPlc
        plc = MockPlc()
        await plc.connect()

    motor = None
    if cfg.use_ros2:
        from infrastructure.ros2.node import available, init_runtime
        if available() and loop is not None:
            runtime = init_runtime(loop)
            from infrastructure.motor.ros2_cmd_vel import Ros2CmdVelPublisher
            motor = Ros2CmdVelPublisher(runtime)
            motor.install()

            # LIDAR + kamera + pose köprülerini de aç
            from infrastructure.lidar.ros2_scan_subscriber import Ros2ScanBridge
            from infrastructure.camera.ros2_image_subscriber import Ros2ImageBridge
            from infrastructure.ros2.pose_bridge import Ros2PoseBridge
            # Bus parametresi App kurulduktan sonra geçecek — şimdilik handle dışında bırak
            # (LocalRunner / main.py içinde install çağrılır)
        else:
            log.warning("ROS2 yok — motor MockMotor'a düşürüldü")

    if motor is None:
        from infrastructure.motor.mock_motor import MockMotor
        motor = MockMotor()

    return plc, motor, runtime


def install_ros2_input_bridges(app: "App") -> None:
    """ROS2 köprülerinin bus'a publish'ini App kurulduktan sonra bağla."""
    if app.ros2_runtime is None:
        return
    from infrastructure.camera.ros2_image_subscriber import Ros2ImageBridge
    from infrastructure.lidar.ros2_scan_subscriber import Ros2ScanBridge
    from infrastructure.ros2.pose_bridge import Ros2PoseBridge

    Ros2ScanBridge(app.ros2_runtime, app.bus).install()
    Ros2PoseBridge(app.ros2_runtime, app.bus).install()
    Ros2ImageBridge(app.ros2_runtime, app.bus).install()
