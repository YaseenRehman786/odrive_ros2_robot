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
    # Get the package directory
    #pkg_name = 'yaseen_differential_robot' # package name
    #pkg_share = get_package_share_directory(pkg_name) # get the package share directory

    # Declare launch argument for hardware type
    use_mock_hardware_arg = DeclareLaunchArgument(
        'use_mock_hardware',
        default_value='true',
        description='Use mock hardware (true) or real ODrive hardware (false)'
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Whether to launch RViz2 for visualization'
    )

    use_lidar_arg = DeclareLaunchArgument(
        "use_lidar",
        default_value="true",
        description="Whether to launch the LiDAR node for the RPLIDAR A2M8 LiDAR sensor"
    )
    
    lidar_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("yaseen_differential_robot"), "launch", "rp_lidar_a2m8.launch.py"]
            )
        ),
        condition=IfCondition(LaunchConfiguration("use_lidar"))
    )   


    # Process the URDF file with xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("yaseen_differential_robot"), "urdf", "robot.urdf.xacro"]
            ),
            " ",
            "use_mock_hardware:=", LaunchConfiguration('use_mock_hardware'),
        ]
    )
    # Create a dictionary for the robot description parameter
    robot_description = {"robot_description": robot_description_content}

    # Path to the controllers.yaml file
    robot_controllers = PathJoinSubstitution(
        [FindPackageShare("yaseen_differential_robot"), "config", "controllers.yaml"]
    )

    # Create the control node to load the robot description and controllers
    # this is necessary to load the robot description and controllers into the ROS2 control framework, which is required for the robot controller to function properly, as the robot controller depends on the ROS2 control framework to provide the necessary interfaces and functionality for controlling the robot
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, robot_controllers],
        output="both",
    )

    # Create the robot state publisher node to publish the robot's state to TF
    # this is necessary to visualize the robot in RViz and to allow the robot controller to function properly, as the robot controller depends on the robot state publisher to provide the robot's state information
    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description],
        output="both",
    )

    # Create the spawner node to spawn the joint state broadcaster and robot controller
    # this is necessary to ensure that the joint state broadcaster is spawned before the robot controller, as the robot controller depends on the joint state broadcaster to function properly
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    # Create the spawner node to spawn the robot controller after the joint state broadcaster is spawned
    # this is necessary to ensure that the robot controller is spawned after the joint state broadcaster, as the robot controller depends on the joint state broadcaster to function properly
    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["yaseen_diffbot_controller", "--controller-manager", "/controller_manager"],
    )

    # Create an event handler to delay the spawning of the robot controller until after the joint state broadcaster is spawned
    # this is necessary to ensure that the robot controller is spawned after the joint state broadcaster, as the robot controller depends on the joint state broadcaster to function properly
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
            control_node,
            robot_state_pub_node,
            joint_state_broadcaster_spawner,
            delay_robot_controller,
            rviz_node,
            lidar_node,
        ]
    )