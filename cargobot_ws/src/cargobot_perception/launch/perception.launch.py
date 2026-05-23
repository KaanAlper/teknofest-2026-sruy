"""QR/ArUco, cizgi takibi ve guvenlik durma dugumlerini baslatir."""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package="cargobot_perception", executable="qr_detector",
             name="qr_detector", output="screen"),
        Node(package="cargobot_perception", executable="line_follower",
             name="line_follower", output="screen"),
        Node(package="cargobot_perception", executable="safety_stop",
             name="safety_stop", output="screen"),
    ])
