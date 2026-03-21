from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration


import os 
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    
    joy_params = os.path.join(get_package_share_directory('yaseen_differential_robot'), 'config', 'joystick.yaml')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic', default='/yaseen_diffbot_controller/cmd_vel_unstamped')
    use_stamped = LaunchConfiguration('use_stamped', default='false')

    joy_node = Node(
        package='joy',
        executable='joy_node',
        parameters=[joy_params],
    )

    teleop_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name = 'teleop_node',
        parameters=[joy_params, {'publish_stamped_twist': use_stamped}],
        remappings=[('/cmd_vel', cmd_vel_topic)]
    )

    return LaunchDescription([
        joy_node,
        teleop_node
    ])