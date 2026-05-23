import os
from glob import glob
from setuptools import setup

package_name = "cargobot_perception"

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
    description="QR/ArUco, cizgi takibi, guvenlik durma dugumleri",
    license="MIT",
    entry_points={
        "console_scripts": [
            "qr_detector = cargobot_perception.qr_detector:main",
            "line_follower = cargobot_perception.line_follower:main",
            "safety_stop = cargobot_perception.safety_stop:main",
        ],
    },
)
