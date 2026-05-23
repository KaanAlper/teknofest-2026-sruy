"""Gorev yoneticisi - sartname senaryosunu yoneten durum makinesi (FSM).

Durumlar (sartname madde-10'daki UI durumlariyla birebir):
  IDLE                  - goreve hazir bekleme
  PROCESSING            - gorev alindi, isleniyor
  MOVING_UNLOADED       - gorev alindi, yuksuz hareket (alma noktasina)
  MOVING_LOADED         - gorev alindi, yuklu hareket (birakma noktasina)
  WAITING_PLC           - fabrika otomasyon sistemi komutu bekleniyor (kapi)
  RETURNING             - gorev tamamlandi, baslangic/bekleme noktasina
  ERROR                 - hata durumu
  EMERGENCY_STOP        - acil stop

Akis: PLC'ye baglan -> gorev al -> alma noktasina git (QR + cizgi takibi ile
hassas konumlan) -> yuku al (fork kaldir) -> kapi noktasinda PLC ile el sikis ->
birakma noktasina git -> yuku birak -> donerken tekrar kapi -> bekleme noktasi.

Navigasyon icin Nav2 (nav2_simple_commander.BasicNavigator) kullanilir.
"""
import json
import math
import time
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import PoseStamped, Twist
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

try:
    from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
    HAVE_NAV2 = True
except Exception:
    HAVE_NAV2 = False

HOME = {"x": -5.0, "y": -2.5, "yaw": 0.0}
DOOR_Q5 = {"x": -1.5, "y": 0.0, "yaw": 0.0}


def yaw_to_quat(yaw):
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))


class MissionManager(Node):
    def __init__(self):
        super().__init__("mission_manager")
        self.state = "IDLE"
        self.task = None
        self.plc_connected = False
        self.door_open = False
        self.estop = False
        self.safety_stop = False

        # Pub/Sub
        self.pub_state = self.create_publisher(String, "/robot_state", 10)
        self.pub_plc_connect = self.create_publisher(Bool, "/plc/connect", 10)
        self.pub_plc_status = self.create_publisher(String, "/plc/status", 10)
        self.pub_door_req = self.create_publisher(String, "/plc/door_request", 10)
        self.pub_line_active = self.create_publisher(Bool, "/line_following/active", 10)
        self.pub_fork = self.create_publisher(
            JointTrajectory, "/set_joint_trajectory", 10)

        self.create_subscription(Bool, "/plc/connected", self.on_plc_conn, 10)
        self.create_subscription(String, "/plc/task", self.on_task, 10)
        self.create_subscription(String, "/plc/door_status", self.on_door, 10)
        self.create_subscription(Bool, "/safety/stop", self.on_safety, 10)
        self.create_subscription(Bool, "/emergency_stop", self.on_estop, 10)

        if HAVE_NAV2:
            self.nav = BasicNavigator()
        else:
            self.nav = None
            self.get_logger().warn("nav2_simple_commander yok - sadece FSM/iskelet calisir")

        self.create_timer(0.5, self.publish_state)
        # Senaryoyu ayri bir thread'de calistir; ana thread rclpy.spin ile
        # callback'leri (PLC/QR/safety bayraklari) gunceller.
        self._thread = threading.Thread(target=self.run_scenario, daemon=True)
        self._thread.start()
        self.get_logger().info("mission_manager hazir")

    # ---------------- Callbacks ----------------
    def on_plc_conn(self, m):    self.plc_connected = m.data
    def on_task(self, m):        self.task = json.loads(m.data)
    def on_door(self, m):        self.door_open = (m.data == "OPEN")
    def on_safety(self, m):      self.safety_stop = m.data
    def on_estop(self, m):
        self.estop = m.data
        if m.data:
            self.set_state("EMERGENCY_STOP")
            if self.nav:
                self.nav.cancelTask()

    def publish_state(self):
        self.pub_state.publish(String(data=self.state))

    def set_state(self, s):
        self.state = s
        self.get_logger().info(f"DURUM -> {s}")
        self.pub_plc_status.publish(String(data=s))

    # ---------------- Hareket yardimcilari ----------------
    def goto(self, p, label=""):
        """Nav2 ile hedefe git; engel/estop'ta guvenli bekle."""
        if not self.nav:
            self.get_logger().info(f"[SIM-YOK] {label} -> {p}")
            time.sleep(1.0)
            return True
        goal = PoseStamped()
        goal.header.frame_id = "map"
        goal.header.stamp = self.nav.get_clock().now().to_msg()
        goal.pose.position.x = float(p["x"])
        goal.pose.position.y = float(p["y"])
        qx, qy, qz, qw = yaw_to_quat(float(p["yaw"]))
        goal.pose.orientation.z, goal.pose.orientation.w = qz, qw
        self.nav.goToPose(goal)
        while not self.nav.isTaskComplete():   # BasicNavigator kendi node'unu spin eder
            if self.estop:
                self.nav.cancelTask()
                return False
            # Engel: sartname geregi dur, kacma. Engel kalkinca Nav2 devam eder.
            time.sleep(0.1)
        return self.nav.getResult() == TaskResult.SUCCEEDED

    def set_fork(self, height):
        jt = JointTrajectory()
        jt.joint_names = ["fork_joint"]
        pt = JointTrajectoryPoint()
        pt.positions = [float(height)]
        pt.time_from_start = Duration(sec=2)
        jt.points = [pt]
        self.pub_fork.publish(jt)
        time.sleep(2.5)

    def precise_line_approach(self, seconds=4.0):
        """QR'dan sonra cizgi takibi ile hassas konumlanma."""
        self.pub_line_active.publish(Bool(data=True))
        t0 = time.time()
        while time.time() - t0 < seconds and not self.estop:
            time.sleep(0.1)
        self.pub_line_active.publish(Bool(data=False))

    def door_handshake(self):
        """Kapi noktasinda PLC ile el sikis: bildir, izin bekle, gec."""
        self.set_state("WAITING_PLC")
        self.door_open = False
        self.pub_door_req.publish(String(data="AT_DOOR_Q5"))
        t0 = time.time()
        while not self.door_open and time.time() - t0 < 15.0 and not self.estop:
            time.sleep(0.1)
        return self.door_open

    # ---------------- Ana senaryo ----------------
    def run_scenario(self):
        time.sleep(3.0)   # diger dugumler ayaga kalksin
        if self.nav:
            self.get_logger().info("Nav2 aktif olmasi bekleniyor...")
            self.nav.waitUntilNav2Active()

        # 1-2) Baglan, PLC teyidi ve gorev bekle
        self.set_state("PROCESSING")
        self.pub_plc_connect.publish(Bool(data=True))
        t0 = time.time()
        while (not self.plc_connected or self.task is None) and time.time() - t0 < 20:
            time.sleep(0.1)
        if self.task is None:
            self.set_state("ERROR")
            return

        pu = self.task["pickup_pose"]
        do = self.task["dropoff_pose"]

        # 5) Alma noktasina git (yuksuz), QR + cizgi ile hassas konumlan
        self.set_state("MOVING_UNLOADED")
        self.goto(pu, "alma noktasi")
        self.precise_line_approach()

        # Yuku al (fork kaldir)
        self.set_fork(0.20)

        # 6-8) Yuklu git, q5 kapi noktasinda dur + PLC el sikis
        self.set_state("MOVING_LOADED")
        self.goto(DOOR_Q5, "kapi q5")
        if not self.door_handshake():
            self.set_state("ERROR"); return

        # 9) Birakma noktasina git ve yuku birak
        self.set_state("MOVING_LOADED")
        self.goto(do, "birakma noktasi")
        self.precise_line_approach()
        self.set_fork(0.0)
        self.pub_plc_status.publish(String(data="LOAD_DROPPED"))

        # 10-11) Donus: tekrar kapi el sikisi, sonra bekleme noktasi
        self.set_state("RETURNING")
        self.goto(DOOR_Q5, "kapi q5 (donus)")
        self.door_handshake()
        self.goto(HOME, "bekleme noktasi")
        self.pub_plc_status.publish(String(data="AT_HOME"))
        self.set_state("IDLE")
        self.get_logger().info("Gorev tamamlandi.")


def main():
    rclpy.init()
    node = MissionManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
