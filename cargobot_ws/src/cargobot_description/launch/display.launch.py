"""robot_state_publisher + RViz ile URDF gorsellestirme (Gazebo'suz)."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory("cargobot_description")
    xacro_file = os.path.join(pkg, "urdf", "cargobot.urdf.xacro")
    rviz_cfg = os.path.join(pkg, "rviz", "display.rviz")

    use_sim_time = LaunchConfiguration("use_sim_time")
    robot_desc = ParameterValue(Command(["xacro ", xacro_file]), value_type=str)

    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{"robot_description": robot_desc,
                         "use_sim_time": use_sim_time}],
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_cfg],
        ),
    ])
