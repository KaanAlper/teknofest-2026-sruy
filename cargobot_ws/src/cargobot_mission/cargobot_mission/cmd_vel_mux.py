"""cmd_vel coklayici (mux) + guvenlik kapisi.

Kaynaklar (oncelik sirasi yuksekten dusuge):
  1. EMERGENCY_STOP  -> her zaman 0 (sartname: tum motorlar durur)
  2. /safety/stop    -> engel varsa 0 (Gorev-6: guvenli durma)
  3. /cmd_vel_teleop -> manuel mod (anahtar 'manuel' iken)
  4. /cmd_vel_line   -> cizgi takibi aktifken
  5. /cmd_vel        -> Nav2 ciktisi (otonom navigasyon, Nav2 varsayilani)

Cikis: /cmd_vel_out  (diff_drive eklentisinin dinledigi topic)

Boylece Nav2 hicbir remap gerektirmeden /cmd_vel'e yayinlar; mux guvenlik
kapisi olarak araya girip tekerlere giden /cmd_vel_out'u uretir.
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool


class CmdVelMux(Node):
    def __init__(self):
        super().__init__("cmd_vel_mux")
        self.estop = False
        self.safety = False
        self.manual = False           # /manual_mode (anahtar)
        self.line_active = False

        self.last = {"nav": Twist(), "line": Twist(), "teleop": Twist()}

        self.create_subscription(Twist, "/cmd_vel", self.cb("nav"), 10)
        self.create_subscription(Twist, "/cmd_vel_line", self.cb("line"), 10)
        self.create_subscription(Twist, "/cmd_vel_teleop", self.cb("teleop"), 10)
        self.create_subscription(Bool, "/emergency_stop", self.on_estop, 10)
        self.create_subscription(Bool, "/safety/stop", self.on_safety, 10)
        self.create_subscription(Bool, "/manual_mode", self.on_manual, 10)
        self.create_subscription(Bool, "/line_following/active", self.on_line, 10)

        self.pub = self.create_publisher(Twist, "/cmd_vel_out", 10)
        self.create_timer(0.05, self.tick)   # 20 Hz
        self.get_logger().info("cmd_vel_mux hazir")

    def cb(self, key):
        def _f(msg):
            self.last[key] = msg
        return _f

    def on_estop(self, m):  self.estop = m.data
    def on_safety(self, m): self.safety = m.data
    def on_manual(self, m): self.manual = m.data
    def on_line(self, m):   self.line_active = m.data

    def tick(self):
        if self.estop or self.safety:
            self.pub.publish(Twist())          # dur
            return
        if self.manual:
            self.pub.publish(self.last["teleop"])
            return
        if self.line_active:
            self.pub.publish(self.last["line"])
            return
        self.pub.publish(self.last["nav"])


def main():
    rclpy.init()
    node = CmdVelMux()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
