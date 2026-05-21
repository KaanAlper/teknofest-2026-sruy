"""Çalışma profili — mock / sim / real arasında adapter set'leri.

mock:  geliştirme makinesinde, donanım/ROS2/PLC yok. Sahte adapter'ler ve demo.
sim:   Docker compose Gazebo + Modbus simulator. ROS2 köprüleri aktif.
real:  Jetson + gerçek donanım + saha PLC'si.

Profil environment değişkeniyle seçilir:
    CARGOBOT_PROFILE=mock|sim|real    (default: mock)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


class Profile(str, Enum):
    MOCK = "mock"
    SIM = "sim"
    REAL = "real"


@dataclass
class ProfileConfig:
    profile: Profile
    plc_host: str
    plc_port: int
    use_ros2: bool
    run_demo: bool


def current() -> ProfileConfig:
    name = os.environ.get("CARGOBOT_PROFILE", "mock").lower()
    try:
        prof = Profile(name)
    except ValueError:
        prof = Profile.MOCK

    if prof == Profile.MOCK:
        return ProfileConfig(profile=prof, plc_host="", plc_port=0, use_ros2=False, run_demo=True)
    if prof == Profile.SIM:
        return ProfileConfig(
            profile=prof,
            plc_host=os.environ.get("PLC_HOST", "localhost"),
            plc_port=int(os.environ.get("PLC_PORT", "5020")),
            use_ros2=True,
            run_demo=False,
        )
    # REAL
    return ProfileConfig(
        profile=prof,
        plc_host=os.environ.get("PLC_HOST", "192.168.1.10"),
        plc_port=int(os.environ.get("PLC_PORT", "502")),
        use_ros2=True,
        run_demo=False,
    )
