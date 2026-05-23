"""Gorev-4: Goruntu isleme ile cizgi takibi (hibrit navigasyonun gorsel ayagi).

- Kameradan goruntu alir, renkli seridi (varsayilan sari) HSV ile maskeler.
- Goruntunun alt bandindaki seridin merkezini bulur, sapmadan orantili
  bir aci hizi (P kontrol) uretir.
- /line_following/active true iken /cmd_vel_line topigine komut yayinlar.
  Mission manager hassas konumlanma fazinda bu topigi cmd_vel'e baglar.
- /perception/line_detected (Bool) ile serit gorulup gorulmedigini bildirir.
"""
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
from cv_bridge import CvBridge
import cv2


class LineFollower(Node):
    def __init__(self):
        super().__init__("line_follower")
        self.declare_parameter("active", False)
        self.declare_parameter("linear_speed", 0.12)
        self.declare_parameter("kp", 0.004)
        # Sari serit HSV araligi
        self.declare_parameter("hsv_low", [20, 100, 100])
        self.declare_parameter("hsv_high", [35, 255, 255])

        self.bridge = CvBridge()
        self.create_subscription(Image, "/camera/image_raw", self.on_image, 10)
        self.create_subscription(Bool, "/line_following/active", self.on_active, 10)
        self.pub_cmd = self.create_publisher(Twist, "/cmd_vel_line", 10)
        self.pub_det = self.create_publisher(Bool, "/perception/line_detected", 10)
        self.active = self.get_parameter("active").value
        self.get_logger().info("line_follower hazir")

    def on_active(self, msg: Bool):
        self.active = msg.data

    def on_image(self, msg: Image):
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        h, w = frame.shape[:2]
        roi = frame[int(h * 0.6):, :]  # alt %40

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        low = np.array(self.get_parameter("hsv_low").value)
        high = np.array(self.get_parameter("hsv_high").value)
        mask = cv2.inRange(hsv, low, high)

        M = cv2.moments(mask)
        detected = M["m00"] > 1000
        self.pub_det.publish(Bool(data=bool(detected)))

        if not self.active:
            return

        cmd = Twist()
        if detected:
            cx = M["m10"] / M["m00"]
            err = cx - (w / 2.0)              # +sag, -sol
            kp = self.get_parameter("kp").value
            cmd.linear.x = self.get_parameter("linear_speed").value
            cmd.angular.z = -kp * err
        else:
            # serit kaybolduysa yavasca dur
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
        self.pub_cmd.publish(cmd)


def main():
    rclpy.init()
    node = LineFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
