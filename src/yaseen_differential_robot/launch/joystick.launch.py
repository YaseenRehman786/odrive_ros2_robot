from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument


import os 
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    
    #----------------PARAMETERS----------------
    joy_params = os.path.join(get_package_share_directory('yaseen_differential_robot'), 'config', 'joystick.yaml')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic', default='/yaseen_diffbot_controller/cmd_vel_unstamped')
    use_stamped = LaunchConfiguration('use_stamped', default='false')
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')


    #----------------LAUNCH ARGUMENTS----------------
    cmd_vel_topic_arg = DeclareLaunchArgument(
        'cmd_vel_topic',
        default_value='/yaseen_diffbot_controller/cmd_vel_unstamped',
        description='Output cmd_vel topic for teleop_twist_joy'
    )

    use_stamped_arg = DeclareLaunchArgument(
        'use_stamped',
        default_value='false',
        description='Publish geometry_msgs/msg/TwistStamped if true'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )

    #----------------NODES----------------
    joy_node = Node(
        package='joy',
        executable='joy_node',
        parameters=[joy_params, {'use_sim_time': use_sim_time}],
    )

    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name = 'teleop_node',
        parameters=[joy_params, {'publish_stamped_twist': use_stamped}],
        remappings=[('/cmd_vel', cmd_vel_topic)]
    )

    # twist_stamper = Node(
    #     package='teleop_twist_joy',
    #     executable='teleop_node',
    #     name = 'twist_stamper',
    #     parameters=[joy_params, {'publish_stamped_twist': use_stamped}, {'use_sim_time': use_sim_time}],
    #     remappings=[
    #         ('/cmd_vel_in', '/yaseen_diffbot_controller/cmd_vel_unstamped'),
    #         ('/cmd_vel_unstamped', '/yaseen_diffbot_controller/cmd_vel'),
    #         ]
    # )

    #----------------SIMULATION NODES----------------
    return LaunchDescription([
        cmd_vel_topic_arg,
        use_stamped_arg,
        use_sim_time_arg,
        joy_node,
        teleop_node,
        # twist_stamper
    ])