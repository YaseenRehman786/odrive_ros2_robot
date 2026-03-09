from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler, SetEnvironmentVariable
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    world_sdf = PathJoinSubstitution(
        [FindPackageShare("yaseen_differential_robot"), "worlds", "empty.sdf"]
    )

    # Process the URDF file with xacro to generate the robot description, which is necessary for both Gazebo and ROS2 to understand the robot's structure and properties. This allows the robot to be correctly spawned in the simulation and to interact with other ROS2 nodes that depend on the robot description.
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

    # Create a dictionary for the robot description parameter, which is required to pass the robot description to ROS2 nodes that need it, such as the robot state publisher and the controller manager. This allows those nodes to access the robot's structure and properties for visualization and control purposes.
    robot_description = {"robot_description": robot_description_content}

    set_gz_resource_path = SetEnvironmentVariable(
        name="GZ_SIM_RESOURCE_PATH",
        value="/home/ysn786/ws_odrive_robot/install/yaseen_differential_robot/share"
    )

    set_ign_resource_path = SetEnvironmentVariable(
        name="IGN_GAZEBO_RESOURCE_PATH",
        value="/home/ysn786/ws_odrive_robot/install/yaseen_differential_robot/share"
    )

    set_gz_plugin_path = SetEnvironmentVariable(
        name="GZ_SIM_SYSTEM_PLUGIN_PATH",
        value="/opt/ros/humble/lib"
    )

    set_ign_plugin_path = SetEnvironmentVariable(
        name="IGN_GAZEBO_SYSTEM_PLUGIN_PATH",
        value="/opt/ros/humble/lib"
    )


    # Start Gazebo with the specified world file, which is necessary to create the simulation environment where the robot will operate. This allows users to test the robot in different scenarios and environments by simply changing the world file.
    gz_sim = ExecuteProcess(
    cmd=["ign", "gazebo", "-r", world_sdf],
    output="screen",
    )

    # Create the robot state publisher node to publish the robot's state to TF, which is necessary to visualize the robot in RViz and to allow the robot controller to function properly, as the robot controller depends on the robot state publisher to provide the robot's state information.
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description, {"use_sim_time": True}],
        output="both",
    )

    # Spawn robot from /robot_description into Gazebo, which is necessary to create the robot entity in the simulation based on the robot description. This allows the robot to be visualized and interacted with in Gazebo, and also allows it to be controlled by ROS2 nodes that depend on the robot being present in the simulation.
    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name", "yaseen_bot",
            "-topic", "robot_description",
            "-allow_renaming", "true",
            "-z", "1.5",
        ],
        output="screen",
    )

    # Joint state broadcaster and robot controller spawners, which are necessary to ensure that the joint state broadcaster is spawned before the robot controller, as the robot controller depends on the joint state broadcaster to function properly. This allows the robot to be controlled in the simulation using ROS2 control, and ensures that the necessary components are started in the correct order for proper functionality.
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "120", 
        ],
        output="screen",
    )

    # diff_drive_controller spawner, which is necessary to spawn the robot controller after the joint state broadcaster is spawned, as the robot controller depends on the joint state broadcaster to function properly. This allows the robot to be controlled in the simulation using ROS2 control, and ensures that the necessary components are started in the correct order for proper functionality.
    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[ 
            "yaseen_diffbot_controller",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "120",
        ],
        output="screen",
    )

    # Register event handlers to ensure the correct order of node execution, which is necessary to ensure that the joint state broadcaster is spawned before the robot controller, as the robot controller depends on the joint state broadcaster to function properly. This allows the robot to be controlled in the simulation using ROS2 control, and ensures that the necessary components are started in the correct order for proper functionality.
    delay_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    # Register event handler to delay the spawning of the diff drive controller until after the joint state broadcaster is spawned, which is necessary to ensure that the robot controller is spawned after the joint state broadcaster, as the robot controller depends on the joint state broadcaster to function properly. This allows the robot to be controlled in the simulation using ROS2 control, and ensures that the necessary components are started in the correct order for proper functionality.
    delay_diff_drive_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_drive_controller_spawner],
        )
    )

    return LaunchDescription(
        [
            set_gz_resource_path,
            set_ign_resource_path,
            set_gz_plugin_path,
            set_ign_plugin_path,
            gz_sim,
            robot_state_publisher,
            spawn_entity,
            delay_joint_state_broadcaster,
            delay_diff_drive_controller,
        ]
    )
