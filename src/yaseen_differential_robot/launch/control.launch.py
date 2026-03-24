import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, IncludeLaunchDescription
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    twist_mux_params = os.path.join(
        get_package_share_directory("yaseen_differential_robot"),
        "config",
        "twist_mux.yaml",
    )
    twist_mux = Node(
        package="twist_mux",
        executable="twist_mux",
        parameters=[twist_mux_params],
        remappings=[("/cmd_vel_out", "/yaseen_diffbot_controller/cmd_vel_unstamped")],
    )

    use_mock_hardware_arg = DeclareLaunchArgument(
        "use_mock_hardware",
        default_value="true",
        description="Use mock hardware (true) or real ODrive hardware (false)",
    )

    use_rviz_arg = DeclareLaunchArgument(
        "use_rviz",
        default_value="true",
        description="Whether to launch RViz2 for visualization",
    )

    use_lidar_arg = DeclareLaunchArgument(
        "use_lidar",
        default_value="true",
        description="Whether to launch RPLIDAR node",
    )

    use_realsense_arg = DeclareLaunchArgument(
        "use_realsense",
        default_value="true",
        description="Whether to launch RealSense D435",
    )

    depth_profile_arg = DeclareLaunchArgument(
        "depth_profile",
        default_value="640x480x15",
        description="RealSense depth profile",
    )

    color_profile_arg = DeclareLaunchArgument(
        "color_profile",
        default_value="640x480x15",
        description="RealSense color profile",
    )

    align_depth_arg = DeclareLaunchArgument(
        "align_depth",
        default_value="true",
        description="Align depth to color",
    )

    enable_pointcloud_arg = DeclareLaunchArgument(
        "enable_pointcloud",
        default_value="false",
        description="Enable RealSense pointcloud",
    )

    lidar_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("yaseen_differential_robot"), "launch", "rp_lidar_a2m8.launch.py"]
            )
        ),
        condition=IfCondition(LaunchConfiguration("use_lidar")),
    )

    realsense_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("yaseen_differential_robot"), "launch", "d435_depthcamera.launch.py"]
            )
        ),
        launch_arguments={
            "use_realsense": LaunchConfiguration("use_realsense"),
            "depth_profile": LaunchConfiguration("depth_profile"),
            "color_profile": LaunchConfiguration("color_profile"),
            "align_depth": LaunchConfiguration("align_depth"),
            "enable_pointcloud": LaunchConfiguration("enable_pointcloud"),
            "enable_infra1": "false",
            "enable_infra2": "false",
            "camera_namespace": "",
            "camera_name": "camera",
        }.items(),
    )

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("yaseen_differential_robot"), "urdf", "robot.urdf.xacro"]
            ),
            " ",
            "use_mock_hardware:=",
            LaunchConfiguration("use_mock_hardware"),
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    robot_controllers = PathJoinSubstitution(
        [FindPackageShare("yaseen_differential_robot"), "config", "controllers.yaml"]
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, robot_controllers],
        output="both",
    )

    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description],
        output="both",
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["yaseen_diffbot_controller", "--controller-manager", "/controller_manager"],
    )

    delay_robot_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[robot_controller_spawner],
        )
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=[
            "-d",
            PathJoinSubstitution(
                [FindPackageShare("yaseen_differential_robot"), "rviz", "view_robot_odom.rviz"]
            ),
        ],
        condition=IfCondition(LaunchConfiguration("use_rviz")),
    )

    return LaunchDescription(
        [
            use_mock_hardware_arg,
            use_rviz_arg,
            use_lidar_arg,
            use_realsense_arg,
            depth_profile_arg,
            color_profile_arg,
            align_depth_arg,
            enable_pointcloud_arg,
            twist_mux,
            control_node,
            robot_state_pub_node,
            joint_state_broadcaster_spawner,
            delay_robot_controller,
            rviz_node,
            lidar_node,
            realsense_node,
        ]
    )