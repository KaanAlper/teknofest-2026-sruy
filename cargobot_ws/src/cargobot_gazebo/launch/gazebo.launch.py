"""Gazebo Classic + fabrika dunyasi + CargoBot spawn + robot_state_publisher."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_desc = get_package_share_directory("cargobot_description")
    pkg_gz = get_package_share_directory("cargobot_gazebo")
    pkg_gazebo_ros = get_package_share_directory("gazebo_ros")

    xacro_file = os.path.join(pkg_desc, "urdf", "cargobot.urdf.xacro")
    world = os.path.join(pkg_gz, "worlds", "factory.world")

    x = LaunchConfiguration("x")
    y = LaunchConfiguration("y")
    yaw = LaunchConfiguration("yaw")

    robot_desc = ParameterValue(Command(["xacro ", xacro_file]), value_type=str)

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gzserver.launch.py")),
        launch_arguments={"world": world, "verbose": "true"}.items(),
    )
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gzclient.launch.py")),
    )

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_desc, "use_sim_time": True}],
    )

    spawn = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-topic", "robot_description", "-entity", "cargobot",
                   "-x", x, "-y", y, "-z", "0.1", "-Y", yaw],
        output="screen",
    )

    return LaunchDescription([
        # baslangic alani: sahanin sol-alt kosesi
        DeclareLaunchArgument("x", default_value="-5.0"),
        DeclareLaunchArgument("y", default_value="-2.5"),
        DeclareLaunchArgument("yaw", default_value="0.0"),
        gzserver, gzclient, rsp, spawn,
    ])
