"""Gorev-10: Kullanici arayuzu (terminal panosu).

Sartname geregi gosterilenler:
  - Robot durum bilgisi (/robot_state)
  - Gorev durum bilgisi (/plc/task)
  - Okunan QR kod bilgisi (/perception/qr)
  - Fabrika otomasyon sistemi haberlesme durumu (/plc/connected, /plc/door_status)
  - Alinip verilen mesajlar (/plc/status)
  - Guvenlik / engel mesafesi (/safety/*), acil stop (/emergency_stop)

NOT: Yarisma teslimi icin PySide6+QML grafik arayuz onerilir (repodaki ui/ ile
ayni veriler). Bu pano hizli dogrulama ve video icin yeterlidir.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool, Float32


class Dashboard(Node):
    def __init__(self):
        super().__init__("dashboard")
        self.d = {
            "Robot durumu": "-", "Gorev": "-", "QR": "-",
            "PLC bagli": "-", "Kapi": "-", "Son mesaj": "-",
            "Engel mesafe": "-", "Acil stop": "HAYIR", "Manuel mod": "HAYIR",
        }
        self.create_subscription(String, "/robot_state", self.s("Robot durumu"), 10)
        self.create_subscription(String, "/plc/task", self.s("Gorev"), 10)
        self.create_subscription(String, "/perception/qr", self.s("QR"), 10)
        self.create_subscription(String, "/plc/door_status", self.s("Kapi"), 10)
        self.create_subscription(String, "/plc/status", self.s("Son mesaj"), 10)
        self.create_subscription(Bool, "/plc/connected",
                                 self.b("PLC bagli"), 10)
        self.create_subscription(Bool, "/emergency_stop",
                                 self.b("Acil stop", "EVET", "HAYIR"), 10)
        self.create_subscription(Bool, "/manual_mode",
                                 self.b("Manuel mod", "EVET", "HAYIR"), 10)
        self.create_subscription(Float32, "/safety/min_front_dist",
                                 self.f("Engel mesafe"), 10)
        self.create_timer(0.5, self.render)

    def s(self, k):
        def _f(m): self.d[k] = m.data[:60]
        return _f

    def b(self, k, t="EVET", f="HAYIR"):
        def _f(m): self.d[k] = t if m.data else f
        return _f

    def f(self, k):
        def _f(m): self.d[k] = f"{m.data:.2f} m"
        return _f

    def render(self):
        print("\033[2J\033[H", end="")  # ekrani temizle
        print("=" * 52)
        print("   CARGOBOT - KONTROL PANELI (TEKNOFEST 2026 SRUY)")
        print("=" * 52)
        for k, v in self.d.items():
            print(f"  {k:<16}: {v}")
        print("=" * 52)
        print("  Acil stop:  ros2 topic pub --once /emergency_stop "
              "std_msgs/Bool '{data: true}'")


def main():
    rclpy.init()
    node = Dashboard()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
