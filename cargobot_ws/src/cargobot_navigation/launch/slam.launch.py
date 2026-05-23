"""slam_toolbox ile online haritalama (Gorev-1: Haritalama)."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("cargobot_navigation")
    slam_cfg = os.path.join(pkg, "config", "slam_toolbox.yaml")
    return LaunchDescription([
        Node(
            package="slam_toolbox",
            executable="async_slam_toolbox_node",
            name="slam_toolbox",
            output="screen",
            parameters=[slam_cfg],
        ),
    ])
