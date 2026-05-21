"""Tam sim akışı: Gazebo + robot spawn + slam_toolbox + Nav2.

xacro Command substitution ile runtime'da URDF üretilir — ayrıca dosya yazımı yok.

Kullanım (cargobot/ros2-sim image içinde):
    ros2 launch /workspace/sim/launch/sim.launch.py
"""

from launch import LaunchDescription
from launch.actions import (
    ExecuteProcess,
    IncludeLaunchDescription,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    world_path = "/workspace/sim/worlds/teknofest_saha.world"
    xacro_path = "/workspace/hardware/urdf/cargobot.urdf.xacro"

    # 1) Gazebo
    gazebo = ExecuteProcess(
        cmd=[
            "gazebo", "--verbose",
            "-s", "libgazebo_ros_init.so",
            "-s", "libgazebo_ros_factory.so",
            world_path,
        ],
        output="screen",
    )

    # 2) URDF — xacro runtime'da çalışır
    robot_description = ParameterValue(
        Command([FindExecutable(name="xacro"), " ", xacro_path]),
        value_type=str,
    )
    robot_state_pub = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"use_sim_time": True, "robot_description": robot_description}],
        output="screen",
    )

    # 3) Robot spawn (Gazebo açıldıktan sonra)
    spawn = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "cargobot",
            "-topic", "robot_description",
            "-x", "-5", "-y", "-3", "-z", "0.1",
        ],
        output="screen",
    )
    spawn_after_gazebo = RegisterEventHandler(
        OnProcessStart(target_action=gazebo, on_start=[spawn])
    )

    # 4) slam_toolbox (online async)
    slam = Node(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        parameters=[{
            "use_sim_time": True,
            "odom_frame": "odom",
            "base_frame": "base_link",
            "map_frame": "map",
            "scan_topic": "/scan",
            "mode": "mapping",
            "resolution": 0.05,
            "minimum_travel_distance": 0.5,
        }],
        output="screen",
    )

    # 5) Nav2
    nav2_bringup = get_package_share_directory("nav2_bringup")
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup, "launch", "navigation_launch.py")
        ),
        launch_arguments={"use_sim_time": "true", "autostart": "true"}.items(),
    )

    return LaunchDescription([
        gazebo,
        robot_state_pub,
        spawn_after_gazebo,
        slam,
        nav2,
    ])
