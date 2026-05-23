"""Gorev-6: Rota uzerinde engelle karsilasinca guvenli mesafede durma.

- /scan'i dinler; on sektorde (varsayilan +/-30 derece) en yakin engel
  guvenlik mesafesinin altina inerse /safety/stop = True yayinlar.
- Mission manager bu sinyali gorunce hareketi durdurur; engel kalkinca devam eder.
  (Sartname: engelden kacinmak gerekmiyor, durup beklemek yeterli.)
"""
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool, Float32


class SafetyStop(Node):
    def __init__(self):
        super().__init__("safety_stop")
        self.declare_parameter("stop_distance", 0.45)   # guvenli durma mesafesi (m)
        self.declare_parameter("front_angle", 0.52)     # +/- ~30 derece (rad)
        self.create_subscription(LaserScan, "/scan", self.on_scan, 10)
        self.pub_stop = self.create_publisher(Bool, "/safety/stop", 10)
        self.pub_dist = self.create_publisher(Float32, "/safety/min_front_dist", 10)
        self.get_logger().info("safety_stop hazir")

    def on_scan(self, scan: LaserScan):
        stop_d = self.get_parameter("stop_distance").value
        fa = self.get_parameter("front_angle").value
        min_d = float("inf")
        a = scan.angle_min
        for r in scan.ranges:
            if -fa <= a <= fa and scan.range_min < r < scan.range_max:
                min_d = min(min_d, r)
            a += scan.angle_increment
        if math.isinf(min_d):
            min_d = scan.range_max
        self.pub_dist.publish(Float32(data=min_d))
        self.pub_stop.publish(Bool(data=bool(min_d < stop_d)))


def main():
    rclpy.init()
    node = SafetyStop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
