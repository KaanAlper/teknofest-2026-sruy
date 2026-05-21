"""Gazebo + slam_toolbox + Nav2 + cargobot URDF tek launch."""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    gazebo = ExecuteProcess(
        cmd=["gazebo", "--verbose", "-s", "libgazebo_ros_factory.so", "/workspace/sim/worlds/cargobot.world"],
        output="screen",
    )

    robot_state_pub = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": open("/workspace/urdf/cargobot.urdf").read()}],
        output="screen",
    )

    slam = Node(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    nav2_dir = get_package_share_directory("nav2_bringup")
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_dir, "launch", "navigation_launch.py")),
        launch_arguments={"use_sim_time": "True"}.items(),
    )

    return LaunchDescription([gazebo, robot_state_pub, slam, nav2])
