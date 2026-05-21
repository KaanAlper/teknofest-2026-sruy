"""/scan → ObstacleDetected / ObstacleCleared adapter.

LaserScan mesajlarını polar bir kuşakta filtreler. Robotun önünde, belirli
açıyla, belirli mesafeden yakın bir engel bulursa event yayınlar. Engel
sınırın dışına çıkınca cleared event'i.

ROS2 yoksa modül hiçbir şey yapmaz (import zincirini kırmaz).
"""

from __future__ import annotations

import logging
import math
from typing import Optional

from domain.perception.events import ObstacleCleared, ObstacleDetected
from eventbus import AsyncEventBus
from infrastructure.ros2.node import Ros2Runtime, available

log = logging.getLogger(__name__)

if available():
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import LaserScan


SAFETY_DISTANCE_M = 0.5     # bu mesafe altı engel kabul
FRONT_HALF_ANGLE_RAD = math.radians(30)  # ön kuşak ±30°
CLEAR_HYSTERESIS_M = 0.1    # bir engel temizlenmiş sayılması için ek mesafe


class Ros2ScanBridge:
    def __init__(self, runtime: Ros2Runtime, bus: AsyncEventBus, topic: str = "/scan") -> None:
        if not available():
            raise RuntimeError("rclpy yok")
        self._runtime = runtime
        self._bus = bus
        self._topic = topic
        self._obstacle_active: bool = False
        self._node: Optional[Node] = None

    def install(self) -> None:
        self._node = rclpy.create_node("cargobot_scan_bridge")
        self._node.create_subscription(LaserScan, self._topic, self._on_scan, qos_profile=10)
        self._runtime.add_node(self._node)
        log.info("scan bridge yüklendi: %s", self._topic)

    def _on_scan(self, msg) -> None:
        # Önündeki kuşağı tara, en yakın engeli bul
        closest = self._closest_in_front(msg)
        if closest is None:
            return
        distance, angle = closest

        if distance < SAFETY_DISTANCE_M and not self._obstacle_active:
            self._obstacle_active = True
            self._publish(ObstacleDetected(aggregate_id="lidar", distance_m=distance, angle_rad=angle))
        elif distance > SAFETY_DISTANCE_M + CLEAR_HYSTERESIS_M and self._obstacle_active:
            self._obstacle_active = False
            self._publish(ObstacleCleared(aggregate_id="lidar"))

    def _closest_in_front(self, msg) -> Optional[tuple[float, float]]:
        best_dist = float("inf")
        best_angle = 0.0
        angle = msg.angle_min
        for r in msg.ranges:
            if msg.range_min < r < msg.range_max and abs(angle) <= FRONT_HALF_ANGLE_RAD and r < best_dist:
                best_dist = r
                best_angle = angle
            angle += msg.angle_increment
        if best_dist == float("inf"):
            return None
        return best_dist, best_angle

    def _publish(self, event) -> None:
        self._runtime.post_to_asyncio(self._bus.publish(event))
