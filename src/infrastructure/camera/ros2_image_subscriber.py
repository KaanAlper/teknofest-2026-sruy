"""/camera/color/image_raw → QrCodeDetected + ArucoMarkerDetected.

sensor_msgs/Image alır, cv_bridge ile np.ndarray'a çevirir, pyzbar ile QR
okur, opsiyonel olarak ArUco ile pose tahmini yapar.

QR ID'den şartname noktası eşlemesi için config (`field.yaml`) gerek — burada
sadece kameranın gördüğü qr_id event'i yayınlanır. Mission handler eşlemeyi
yapar.
"""

from __future__ import annotations

import logging
from typing import Optional

from domain._shared.value_objects import Pose
from domain.perception.events import ArucoMarkerDetected, QrCodeDetected
from eventbus import AsyncEventBus
from infrastructure.ros2.node import Ros2Runtime, available

log = logging.getLogger(__name__)

if available():
    import cv2
    import numpy as np
    import rclpy
    from cv_bridge import CvBridge
    from pyzbar.pyzbar import decode as zbar_decode
    from rclpy.node import Node
    from sensor_msgs.msg import Image


class Ros2ImageBridge:
    def __init__(
        self,
        runtime: Ros2Runtime,
        bus: AsyncEventBus,
        topic: str = "/camera/color/image_raw",
        enable_aruco: bool = True,
        aruco_dict: int = 0,  # cv2.aruco.DICT_4X4_50
        marker_length_m: float = 0.05,
    ) -> None:
        if not available():
            raise RuntimeError("rclpy yok")
        self._runtime = runtime
        self._bus = bus
        self._topic = topic
        self._enable_aruco = enable_aruco
        self._marker_length = marker_length_m
        self._bridge: Optional[CvBridge] = None
        self._node: Optional[Node] = None
        self._aruco_detector = None
        self._camera_matrix = None
        self._dist_coeffs = None

    def install(self, camera_matrix=None, dist_coeffs=None) -> None:
        self._bridge = CvBridge()
        self._node = rclpy.create_node("cargobot_image_bridge")
        self._node.create_subscription(Image, self._topic, self._on_image, qos_profile=5)
        self._runtime.add_node(self._node)
        if self._enable_aruco:
            self._aruco_detector = cv2.aruco.ArucoDetector(
                cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50),
                cv2.aruco.DetectorParameters(),
            )
            self._camera_matrix = camera_matrix
            self._dist_coeffs = dist_coeffs
        log.info("image bridge yüklendi: %s", self._topic)

    def _on_image(self, msg) -> None:
        try:
            frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception:
            log.exception("cv_bridge dönüşüm hatası")
            return

        for code in zbar_decode(frame):
            qr_id = code.data.decode(errors="ignore")
            event = QrCodeDetected(
                aggregate_id="camera",
                qr_id=qr_id,
                pose_camera=Pose(0.0, 0.0, 0.0),
                confidence=1.0,
            )
            self._runtime.post_to_asyncio(self._bus.publish(event))

        if self._enable_aruco and self._aruco_detector is not None:
            self._detect_aruco(frame)

    def _detect_aruco(self, frame) -> None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self._aruco_detector.detectMarkers(gray)
        if ids is None or self._camera_matrix is None:
            return
        for marker_id, marker_corners in zip(ids.flatten(), corners):
            obj_pts = np.array(
                [
                    [-self._marker_length / 2, self._marker_length / 2, 0],
                    [self._marker_length / 2, self._marker_length / 2, 0],
                    [self._marker_length / 2, -self._marker_length / 2, 0],
                    [-self._marker_length / 2, -self._marker_length / 2, 0],
                ],
                dtype=np.float32,
            )
            ok, rvec, tvec = cv2.solvePnP(
                obj_pts,
                marker_corners.astype(np.float32),
                self._camera_matrix,
                self._dist_coeffs,
            )
            if not ok:
                continue
            # Yaw (z ekseni etrafında dönüş) — basit Rodrigues
            R, _ = cv2.Rodrigues(rvec)
            yaw = float(np.arctan2(R[1, 0], R[0, 0]))
            pose = Pose(x=float(tvec[0]), y=float(tvec[1]), theta=yaw)
            event = ArucoMarkerDetected(
                aggregate_id="camera",
                marker_id=int(marker_id),
                pose_6dof=pose,
            )
            self._runtime.post_to_asyncio(self._bus.publish(event))
