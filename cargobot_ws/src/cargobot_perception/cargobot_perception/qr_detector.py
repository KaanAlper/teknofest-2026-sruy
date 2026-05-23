"""Gorev-5: QR / ArUco kod okuma ve kameraya gore konum hesaplama.

- /camera/image_raw uzerinden goruntu alir.
- QR kod (cv2.QRCodeDetector) ve ArUco (cv2.aruco) tespiti yapar.
- Kameraya gore 3B pozisyonu (solvePnP / estimatePoseSingleMarkers) hesaplar.
- Sonucu /perception/qr (std_msgs/String JSON) ve /perception/qr_pose (PoseStamped) yayinlar.
"""
import json
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2


class QrDetector(Node):
    def __init__(self):
        super().__init__("qr_detector")
        self.declare_parameter("marker_size", 0.15)  # ArUco kenar (m)
        self.marker_size = self.get_parameter("marker_size").value

        self.bridge = CvBridge()
        self.qr = cv2.QRCodeDetector()
        # ArUco sozluk (yarismada kullanilacak sozluk bildirilecek)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters()

        # Kamera matrisi (CameraInfo gelene kadar makul varsayilan)
        self.K = None
        self.D = np.zeros(5)

        self.create_subscription(CameraInfo, "/camera/camera_info", self.on_info, 10)
        self.create_subscription(Image, "/camera/image_raw", self.on_image, 10)
        self.pub_str = self.create_publisher(String, "/perception/qr", 10)
        self.pub_pose = self.create_publisher(PoseStamped, "/perception/qr_pose", 10)
        self.get_logger().info("qr_detector hazir (QR + ArUco)")

    def on_info(self, msg: CameraInfo):
        self.K = np.array(msg.k, dtype=np.float64).reshape(3, 3)
        self.D = np.array(msg.d, dtype=np.float64)

    def on_image(self, msg: Image):
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ---- QR kod ----
        data, pts, _ = self.qr.detectAndDecode(gray)
        if data:
            self._publish(msg.header, "QR", data, pts)

        # ---- ArUco ----
        corners, ids, _ = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.aruco_params)
        if ids is not None and self.K is not None:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, self.marker_size, self.K, self.D)
            for i, mid in enumerate(ids.flatten()):
                self._publish_pose(msg.header, tvecs[i][0])
                self._publish(msg.header, "ARUCO", str(int(mid)), corners[i])

    def _publish(self, header, kind, value, pts):
        out = {"type": kind, "value": value}
        if pts is not None:
            out["corners"] = np.array(pts).reshape(-1, 2).tolist()
        self.pub_str.publish(String(data=json.dumps(out)))
        self.get_logger().info(f"{kind} okundu: {value}")

    def _publish_pose(self, header, tvec):
        ps = PoseStamped()
        ps.header = header
        ps.pose.position.x = float(tvec[0])
        ps.pose.position.y = float(tvec[1])
        ps.pose.position.z = float(tvec[2])
        ps.pose.orientation.w = 1.0
        self.pub_pose.publish(ps)


def main():
    rclpy.init()
    node = QrDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
