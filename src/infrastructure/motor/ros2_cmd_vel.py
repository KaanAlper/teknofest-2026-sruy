"""/cmd_vel publisher — MotorPort uygulaması.

application/handlers/safety_handlers.py'da MotorPort protocol var:
    async def stop()
    async def enable()

Bu adapter Twist mesajı yayar; stop = sıfır hız, enable = no-op (Nav2 zaten
publish edecektir). Manuel sürüş için ek `drive(linear, angular)` metodu var.
"""

from __future__ import annotations

import logging
from typing import Optional

from domain._shared.value_objects import Velocity
from infrastructure.ros2.node import Ros2Runtime, available

log = logging.getLogger(__name__)

if available():
    import rclpy
    from geometry_msgs.msg import Twist
    from rclpy.node import Node


class Ros2CmdVelPublisher:
    def __init__(self, runtime: Ros2Runtime, topic: str = "/cmd_vel") -> None:
        if not available():
            raise RuntimeError("rclpy yok")
        self._runtime = runtime
        self._topic = topic
        self._node: Optional[Node] = None
        self._pub = None

    def install(self) -> None:
        self._node = rclpy.create_node("cargobot_cmd_vel")
        self._pub = self._node.create_publisher(Twist, self._topic, 10)
        self._runtime.add_node(self._node)
        log.info("cmd_vel publisher yüklendi: %s", self._topic)

    async def stop(self) -> None:
        self._send(0.0, 0.0)

    async def enable(self) -> None:
        # Nav2 cmd_vel yayınlayacak; manuel modda drive() çağrılır
        pass

    async def drive(self, vel: Velocity) -> None:
        self._send(vel.linear, vel.angular)

    def _send(self, linear: float, angular: float) -> None:
        if self._pub is None:
            log.warning("cmd_vel publisher henüz install edilmedi")
            return
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self._pub.publish(msg)
