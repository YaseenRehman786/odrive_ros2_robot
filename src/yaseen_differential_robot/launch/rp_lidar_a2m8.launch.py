#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    channel_type =  LaunchConfiguration('channel_type', default='serial')
    serial_port = LaunchConfiguration('serial_port', default='/dev/ttyUSB0')
    serial_baudrate = LaunchConfiguration('serial_baudrate', default='115200')
    frame_id = LaunchConfiguration('frame_id', default='laser')
    inverted = LaunchConfiguration('inverted', default='false')
    angle_compensate = LaunchConfiguration('angle_compensate', default='true')
    
    scan_mode = LaunchConfiguration('scan_mode', default='Express')
    # main scan modes:
    #   Standard, Express, Boost, 
    # additional scan modes:
    #   Sensitivity, Stability, SingleChannel, ForceSample, ForceScan, ForceSingleScan
	
    return LaunchDescription([
        Node(
            package='rplidar_ros', # package name, using the ROS2 package rplidar_ros which provides the necessary drivers and interfaces to communicate with the RPLIDAR A2M8 LiDAR sensor, allowing the robot to receive and process data from the LiDAR sensor, which is essential for tasks such as mapping, localization, and obstacle avoidance
            executable='rplidar_node',
            name='rplidar_node',
            output='screen',
            parameters=[{
                'channel_type': channel_type,
                'serial_port': serial_port,
                'serial_baudrate': serial_baudrate,
                'frame_id': frame_id,
                'scan_mode': scan_mode,
                'angle_compensate': angle_compensate,
                'inverted': inverted
            }]
        )
    ])