"""Tam simulasyon: Gazebo + SLAM + Nav2 + algi + gorev + arayuz.

Kullanim:
  # Once haritalama icin (Gorev-1):
  ros2 launch cargobot_bringup simulation.launch.py slam:=true
  # Harita kaydedildikten sonra navigasyon + tam senaryo:
  ros2 launch cargobot_bringup simulation.launch.py slam:=false
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            GroupAction, TimerAction)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_gz = get_package_share_directory("cargobot_gazebo")
    pkg_nav = get_package_share_directory("cargobot_navigation")
    pkg_perc = get_package_share_directory("cargobot_perception")
    pkg_mission = get_package_share_directory("cargobot_mission")

    slam = LaunchConfiguration("slam")

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gz, "launch", "gazebo.launch.py")))

    slam_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav, "launch", "slam.launch.py")),
        condition=IfCondition(slam))

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav, "launch", "navigation.launch.py")),
        condition=UnlessCondition(slam))

    perception = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_perc, "launch", "perception.launch.py")))

    mission = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_mission, "launch", "mission.launch.py")))

    return LaunchDescription([
        DeclareLaunchArgument("slam", default_value="true",
                              description="true: haritalama, false: Nav2 + senaryo"),
        gazebo,
        # Gazebo ayaga kalksin diye kucuk gecikmelerle baslat
        TimerAction(period=5.0, actions=[GroupAction([slam_node, nav2])]),
        TimerAction(period=7.0, actions=[perception]),
        TimerAction(period=9.0, actions=[mission]),
    ])
