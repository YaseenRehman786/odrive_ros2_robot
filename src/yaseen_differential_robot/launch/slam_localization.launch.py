import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("yaseen_differential_robot")

    use_sim_time = LaunchConfiguration("use_sim_time")
    slam_params_file = LaunchConfiguration("slam_params_file")
    posegraph_file = LaunchConfiguration("posegraph_file")

    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation clock if true",
    )

    declare_slam_params_file = DeclareLaunchArgument(
        "slam_params_file",
        default_value=os.path.join(pkg_share, "config", "slam_localization.yaml"),
        description="Path to slam_toolbox localization parameters YAML",
    )

    declare_posegraph_file = DeclareLaunchArgument(
        "posegraph_file",
        default_value="",
        description="Absolute path to serialized posegraph (without extension), e.g. /home/user/ws_odrive_robot/maps/20260323_1358/posegraph",
    )

    slam_localization_node = Node(
        package="slam_toolbox",
        executable="localization_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[
            slam_params_file,
            {
                "use_sim_time": use_sim_time,
                "map_file_name": posegraph_file,
            },
        ],
    )

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_slam_params_file)
    ld.add_action(declare_posegraph_file)
    ld.add_action(slam_localization_node)

    return ld
