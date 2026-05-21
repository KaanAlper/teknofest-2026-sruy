"""/amcl_pose ve /odom → RobotPoseUpdated event'leri.

AMCL pose tercih edilir (harita üstünde global pose). AMCL yoksa /odom
yeterlidir (göreceli pose). İkisini de dinler, ikisi de gelirse AMCL kazanır.
"""

from __future__ import annotations

import logging
import math
from typing import Optional

from domain._shared.value_objects import Pose
from domain.navigation.events import RobotPoseUpdated
from eventbus import AsyncEventBus
from infrastructure.ros2.node import Ros2Runtime, available

log = logging.getLogger(__name__)

if available():
    import rclpy
    from geometry_msgs.msg import PoseWithCovarianceStamped
    from nav_msgs.msg import Odometry
    from rclpy.node import Node


def _yaw_from_quaternion(x: float, y: float, z: float, w: float) -> float:
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


class Ros2PoseBridge:
    def __init__(self, runtime: Ros2Runtime, bus: AsyncEventBus) -> None:
        if not available():
            raise RuntimeError("rclpy yok")
        self._runtime = runtime
        self._bus = bus
        self._amcl_seen = False
        self._node: Optional[Node] = None

    def install(self) -> None:
        self._node = rclpy.create_node("cargobot_pose_bridge")
        self._node.create_subscription(
            PoseWithCovarianceStamped, "/amcl_pose", self._on_amcl, 10
        )
        self._node.create_subscription(Odometry, "/odom", self._on_odom, 10)
        self._runtime.add_node(self._node)
        log.info("pose bridge yüklendi: /amcl_pose + /odom")

    def _on_amcl(self, msg) -> None:
        self._amcl_seen = True
        p = msg.pose.pose
        self._publish_pose(p.position.x, p.position.y, p.orientation)

    def _on_odom(self, msg) -> None:
        if self._amcl_seen:
            return  # AMCL varken odom'u atla
        p = msg.pose.pose
        self._publish_pose(p.position.x, p.position.y, p.orientation)

    def _publish_pose(self, x: float, y: float, q) -> None:
        yaw = _yaw_from_quaternion(q.x, q.y, q.z, q.w)
        event = RobotPoseUpdated(aggregate_id="nav", pose=Pose(x=x, y=y, theta=yaw))
        self._runtime.post_to_asyncio(self._bus.publish(event))
