"""Fabrika otomasyon sistemi (PLC) SIMULATORU - yarisma sahasindaki endustriyel
PLC'yi temsil eder. Gercek yarismada bu, WiFi uzerinden Modbus/OPC-UA ile
haberlesen fiziksel bir PLC olacaktir; burada ROS topic'leriyle taklit edilir.

Gorevleri:
- Robot baglandiginda (/plc/connect) iletisimi teyit eder.
- Rastgele 1 alma + 1 birakma noktasi uretir, /plc/task (String JSON) ile yollar.
- /plc/door_request gelince uygun zamanda kapiyi acar:
    * Gazebo kapisini /factory_door/set_joint_trajectory ile kaydirir.
    * /plc/door_status = "OPEN" yayinlar.
- Robotun durum bildirimlerini (/plc/status) loglar.
"""
import json
import random
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

# Sartname: 3 alma + 3 birakma noktasindan rastgele birer tane secilir.
PICKUP_POINTS = {
    "P1": {"x": -4.2, "y": 2.5, "yaw": 3.14},
    "P2": {"x": -4.2, "y": 0.5, "yaw": 3.14},
    "P3": {"x": -4.2, "y": -1.5, "yaw": 3.14},
}
DROPOFF_POINTS = {
    "D1": {"x": 4.2, "y": 2.5, "yaw": 0.0},
    "D2": {"x": 4.2, "y": 0.5, "yaw": 0.0},
    "D3": {"x": 4.2, "y": -1.5, "yaw": 0.0},
}


class PlcSimulator(Node):
    def __init__(self):
        super().__init__("plc_simulator")
        self.connected = False
        self.task_sent = False

        self.create_subscription(Bool, "/plc/connect", self.on_connect, 10)
        self.create_subscription(String, "/plc/door_request", self.on_door_request, 10)
        self.create_subscription(String, "/plc/status", self.on_status, 10)

        self.pub_task = self.create_publisher(String, "/plc/task", 10)
        self.pub_conn = self.create_publisher(Bool, "/plc/connected", 10)
        self.pub_door = self.create_publisher(String, "/plc/door_status", 10)
        self.pub_door_cmd = self.create_publisher(
            JointTrajectory, "/factory_door/set_joint_trajectory", 10)

        self.get_logger().info("PLC simulator hazir - robot baglantisi bekleniyor")

    def on_connect(self, msg: Bool):
        if msg.data and not self.connected:
            self.connected = True
            self.pub_conn.publish(Bool(data=True))
            self.get_logger().info("Robot WiFi/PLC kanali kuruldu - teyit edildi")
            self.send_task()

    def send_task(self):
        if self.task_sent:
            return
        pu = random.choice(list(PICKUP_POINTS))
        do = random.choice(list(DROPOFF_POINTS))
        task = {"pickup": pu, "pickup_pose": PICKUP_POINTS[pu],
                "dropoff": do, "dropoff_pose": DROPOFF_POINTS[do]}
        self.pub_task.publish(String(data=json.dumps(task)))
        self.task_sent = True
        self.get_logger().info(f"Gorev gonderildi: alma={pu} birakma={do}")

    def on_door_request(self, msg: String):
        self.get_logger().info(f"Kapi gecis talebi alindi: {msg.data}")
        self.move_door(open_=True)
        self.pub_door.publish(String(data="OPEN"))
        self.get_logger().info("Kapi acildi - gecis izni verildi")

    def move_door(self, open_: bool):
        jt = JointTrajectory()
        jt.joint_names = ["door_slide"]
        pt = JointTrajectoryPoint()
        pt.positions = [2.0 if open_ else 0.0]
        pt.time_from_start = Duration(sec=2)
        jt.points = [pt]
        self.pub_door_cmd.publish(jt)

    def on_status(self, msg: String):
        self.get_logger().info(f"[Robot durumu] {msg.data}")


def main():
    rclpy.init()
    node = PlcSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
