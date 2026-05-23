import os
from glob import glob
from setuptools import setup

package_name = "cargobot_mission"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="cargobot team",
    maintainer_email="muammer@clonifylabs.com",
    description="Gorev FSM, PLC simulatoru, cmd_vel mux, kontrol paneli",
    license="MIT",
    entry_points={
        "console_scripts": [
            "mission_manager = cargobot_mission.mission_manager:main",
            "plc_simulator = cargobot_mission.plc_simulator:main",
            "cmd_vel_mux = cargobot_mission.cmd_vel_mux:main",
            "dashboard = cargobot_mission.dashboard:main",
        ],
    },
)
