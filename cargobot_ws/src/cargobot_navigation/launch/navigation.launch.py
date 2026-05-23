"""Nav2 stack'i baslatir. Onceden olusturulmus harita ile lokalizasyon + navigasyon.
   map argumani verilmezse SLAM modunda (haritasiz) calistirilabilir."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_nav = get_package_share_directory("cargobot_navigation")
    pkg_nav2_bringup = get_package_share_directory("nav2_bringup")

    params = os.path.join(pkg_nav, "config", "nav2_params.yaml")
    default_map = os.path.join(pkg_nav, "maps", "factory_map.yaml")

    map_yaml = LaunchConfiguration("map")
    use_sim_time = LaunchConfiguration("use_sim_time")

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, "launch", "bringup_launch.py")),
        launch_arguments={
            "map": map_yaml,
            "use_sim_time": use_sim_time,
            "params_file": params,
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument("map", default_value=default_map),
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        nav2,
    ])
