import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler, SetEnvironmentVariable, DeclareLaunchArgument
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource



def generate_launch_description():
    pkg_share = get_package_share_directory("yaseen_differential_robot")
    temp_urdf = "/tmp/yaseen_full.urdf"
    temp_sdf = "/tmp/yaseen_full.sdf"

    # # added joystick launch file to the Gazebo simulation launch file, and set the use_sim_time argument to true to ensure that the joystick node uses the simulation time provided by Gazebo, which is necessary for the joystick to function properly in the Gazebo simulation environment, as the joystick node relies on the simulation time to synchronize its operations with the rest of the simulation and to ensure that the joystick inputs are processed correctly in relation to the simulated time in Gazebo
    # joystick = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(get_package_share_directory("yaseen_differential_robot"), "launch", "joystick.launch.py")
    #     ),
    #     launch_arguments=[('use_sim_time', 'true'), ('use_stamped', 'true')]
    # )

    # add twist mux
    twist_mux_params = os.path.join(pkg_share, 'config', 'twist_mux.yaml')
    twist_mux = Node(
        package='twist_mux',
        executable='twist_mux',
        parameters=[twist_mux_params, {'use_sim_time': True}],
        remappings=[('/cmd_vel_out', '/yaseen_diffbot_controller/cmd_vel_unstamped')]
    )
    

    world_arg = DeclareLaunchArgument(
        "world",
        default_value="empty.sdf",
        description="Name of the world file to load (located in yaseen_differential_robot/worlds)",
    )

    use_simulated_realsense_arg = DeclareLaunchArgument(
        "use_simulated_realsense",
        default_value="true",
        description="Enable bridges for simulated RealSense camera topics",
    )


    # Set environment variables for Gazebo resource and plugin paths, which is necessary for Gazebo to locate the robot's URDF and SDF files, as well as any custom plugins that are required for the robot to function properly in the Gazebo simulation environment
    world_sdf = PathJoinSubstitution(
        [FindPackageShare("yaseen_differential_robot"), "worlds", LaunchConfiguration("world")]
    )

    # Create the robot description parameter by processing the xacro file with the use_gazebo argument set to true, which is necessary to include the Gazebo-specific tags and properties in the generated URDF file, allowing the robot to function properly in Gazebo, as the Gazebo-specific tags and properties are required for the robot to interact correctly with the Gazebo simulation environment and to ensure that the robot's behavior and performance in Gazebo matches its intended design and functionality
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("yaseen_differential_robot"), "urdf", "robot.urdf.xacro"]
            ),
            " ",
            "use_gazebo:=true",
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    set_gz_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value="/home/ysn786/ws_odrive_robot/install/yaseen_differential_robot/share",
    )
    set_ign_resource_path = SetEnvironmentVariable(
        name="IGN_GAZEBO_RESOURCE_PATH",
        value="/home/ysn786/ws_odrive_robot/install/yaseen_differential_robot/share",
    )
    set_gz_plugin_path = SetEnvironmentVariable(
        name="GZ_SIM_SYSTEM_PLUGIN_PATH",
        value="/opt/ros/humble/lib",
    )
    set_ign_plugin_path = SetEnvironmentVariable(
        name="IGN_GAZEBO_SYSTEM_PLUGIN_PATH",
        value="/opt/ros/humble/lib",
    )

    # Launch Gazebo with the specified world file, and set the physics engine to ODE (Open Dynamics Engine), which is necessary for the robot to function properly in Gazebo, as the robot's URDF file is designed to work with the ODE physics engine, and using a different physics engine can cause issues with the robot's behavior and performance in Gazebo
    gz_sim = ExecuteProcess(
        cmd=["ign", "gazebo", "-r", world_sdf],
        output="screen",
    )

    # the robot state publisher is necessary to visualize the robot in RViz and to allow the robot controller to function properly, as the robot controller depends on the robot state publisher to provide the robot's state information
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description, {"use_sim_time": True}],
        output="both",
    )

    # Generate the SDF file from the XACRO file, and then spawn the robot in Gazebo after the SDF file is generated, and set the robot's initial position to (0, 0, 0.5) to avoid spawning it underground, which can cause issues with the physics engine and prevent the robot from functioning properly
    generate_sdf = ExecuteProcess(
        cmd=[
            "bash",
            "-lc",
            "xacro "
            + os.path.join(pkg_share, "urdf", "robot.urdf.xacro")
            + " use_gazebo:=true > "
            + temp_urdf
            + " && ign sdf -p "
            + temp_urdf
            + " > "
            + temp_sdf,
        ],
        output="screen",
    )

    # Spawn the robot in Gazebo using the generated SDF file, and set the robot's initial position to (0, 0, 0.5) to avoid spawning it underground, which can cause issues with the physics engine and prevent the robot from functioning properly
    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name",
            "yaseen_bot",
            "-file",
            temp_sdf,
            "-allow_renaming",
            "false",
            "-z",
            "0.5",
        ],
        output="screen",
    )

    # generate the sdf file from the xacro file and then spawn the robot in Gazebo after the sdf file is generated
    delay_spawn_entity = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=generate_sdf,
            on_exit=[spawn_entity],
        )
    )

    # Create the robot description parameter by processing the xacro file with the use_mock_hardware argument set to the value of the use_mock_hardware launch configuration
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
            "--controller-manager-timeout",
            "120",
        ],
        output="screen",
    )

    # Create the robot controller node to control the robot in Gazebo
    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "yaseen_diffbot_controller",
            "--controller-manager",
            "/controller_manager",
            "--controller-manager-timeout",
            "120",
        ],
        output="screen",
    )

    # Create the robot controller node to control the robot in Gazebo
    delay_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    # Create the robot controller node to control the robot in Gazebo
    delay_diff_drive_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_drive_controller_spawner],
        )
    )

    # Create ROS <-> Gazebo bridges for scan and simulation clock
    scan_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
        ],
        output="screen",
    )

    simulated_realsense_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/camera/camera/color/image_raw@sensor_msgs/msg/Image[gz.msgs.Image",
            "/camera/camera/color/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
            "/camera/camera/depth/image_rect_raw@sensor_msgs/msg/Image[gz.msgs.Image",
            "/camera/camera/depth/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
        ],
        output="screen",
        condition=IfCondition(LaunchConfiguration("use_simulated_realsense")),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_share, 'rviz', 'view_robot_gz.rviz')]
    )

    return LaunchDescription(
        [
            # joystick,
            twist_mux,
            world_arg,
            use_simulated_realsense_arg,
            set_gz_resource_path,
            set_ign_resource_path,
            set_gz_plugin_path,
            set_ign_plugin_path,
            gz_sim,
            robot_state_publisher,
            generate_sdf,
            delay_spawn_entity,
            delay_joint_state_broadcaster,
            delay_diff_drive_controller,
            scan_bridge,
            simulated_realsense_bridge,
            rviz_node,
        ]
    )
