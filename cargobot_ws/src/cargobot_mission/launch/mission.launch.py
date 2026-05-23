"""Gorev yoneticisi, PLC simulatoru, cmd_vel mux ve kontrol panelini baslatir."""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package="cargobot_mission", executable="cmd_vel_mux",
             name="cmd_vel_mux", output="screen"),
        Node(package="cargobot_mission", executable="plc_simulator",
             name="plc_simulator", output="screen"),
        Node(package="cargobot_mission", executable="mission_manager",
             name="mission_manager", output="screen"),
        # Pano ayri terminalde calistirilmasi onerilir (ekrani temizler):
        # ros2 run cargobot_mission dashboard
    ])
