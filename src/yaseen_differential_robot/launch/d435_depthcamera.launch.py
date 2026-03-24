from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_realsense_arg = DeclareLaunchArgument(
        "use_realsense",
        default_value="true",
        description="Enable/disable RealSense camera node"
    )

    camera_namespace_arg = DeclareLaunchArgument(
        "camera_namespace",
        default_value="",
        description="Camera namespace"
    )

    camera_name_arg = DeclareLaunchArgument(
        "camera_name",
        default_value="camera",
        description="Camera node name prefix"
    )

    depth_profile_arg = DeclareLaunchArgument(
        "depth_profile",
        default_value="640x480x15",
        description="Depth stream profile (WxHxFPS)"
    )

    color_profile_arg = DeclareLaunchArgument(
        "color_profile",
        default_value="640x480x15",
        description="Color stream profile (WxHxFPS)"
    )

    enable_infra1_arg = DeclareLaunchArgument(
        "enable_infra1",
        default_value="false",
        description="Enable infra1 stream"
    )

    enable_infra2_arg = DeclareLaunchArgument(
        "enable_infra2",
        default_value="false",
        description="Enable infra2 stream"
    )

    align_depth_arg = DeclareLaunchArgument(
        "align_depth",
        default_value="true",
        description="Align depth to color"
    )

    enable_pointcloud_arg = DeclareLaunchArgument(
        "enable_pointcloud",
        default_value="false",
        description="Enable pointcloud output"
    )

    realsense_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("realsense2_camera"), "launch", "rs_launch.py"]
            )
        ),
        launch_arguments={
            "camera_namespace": LaunchConfiguration("camera_namespace"),
            "camera_name": LaunchConfiguration("camera_name"),
            "depth_module.depth_profile": LaunchConfiguration("depth_profile"),
            "rgb_camera.color_profile": LaunchConfiguration("color_profile"),
            "enable_infra1": LaunchConfiguration("enable_infra1"),
            "enable_infra2": LaunchConfiguration("enable_infra2"),
            "align_depth.enable": LaunchConfiguration("align_depth"),
            "pointcloud.enable": LaunchConfiguration("enable_pointcloud"),
            "publish_tf": "false",
            "tf_publish_rate": "0.0",
        }.items(),
        condition=IfCondition(LaunchConfiguration("use_realsense")),
    )

    return LaunchDescription([
        use_realsense_arg,
        camera_namespace_arg,
        camera_name_arg,
        depth_profile_arg,
        color_profile_arg,
        enable_infra1_arg,
        enable_infra2_arg,
        align_depth_arg,
        enable_pointcloud_arg,
        realsense_launch,
    ])