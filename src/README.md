This repository will be for my autonomous robot project where I will be using a Jetson Orin Nano Super, Odrive S1 FOC controllers, Odrive Bothweel motors, Intel Realsense D435 camera, and RPLidar.

------------------------------------------------------------------
**Sourcing**
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source ~/ws_odrive_robot/install/setup.bash
```

**CAN Bringup**
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source ~/ws_odrive_robot/install/setup.bash

sudo modprobe can
sudo modprobe can_raw
sudo modprobe gs_usb

sudo ip link set can0 down 2>/dev/null
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 up

ip -details link show can0
```

**SSH into my Jetson**
```bash
ssh yaseenjetson@192.168.0.133
```  



------------------------------------------------------------------
## **Controlling Odrive and Motors**  
(https://docs.odriverobotics.com/v/latest/guides/ros-package.html)

**_APPROACH A -> odrive_node_ (just test things are working)**
1. Initialize CAN node
```bash
ros2 launch odrive_can example_launch.yaml
``` 
2. Request ODrive State (one for each motor, node id 0, node id 1)
```bash
ros2 service call /odrive_axis0/request_axis_state odrive_can/srv/AxisState "{axis_requested_state: 8}"
ros2 service call /odrive_axis1/request_axis_state odrive_can/srv/AxisState "{axis_requested_state: 8}"
```  
3. Run simple velocity check (one for each motor, node id 0, node id 1)
```bash
ros2 topic pub /odrive_axis0/control_message odrive_can/msg/ControlMessage "{control_mode: 2, input_mode: 1, input_pos: 0.0, input_vel: 1.0, input_torque: 0.0}"
ros2 topic pub /odrive_axis1/control_message odrive_can/msg/ControlMessage "{control_mode: 2, input_mode: 1, input_pos: 0.0, input_vel: 1.0, input_torque: 0.0}"
```

------------------------------------------------------------------
**_APPROACH B -> odrive_ros2_control_ (my implementation)**

**1. Real Robot Bringup (ros2_control + ODrive + LiDAR)**  
_Controller bringup (on Jetson)_ 
```bash
ros2 launch yaseen_differential_robot control.launch.py use_mock_hardware:=false use_lidar:=true use_rviz:=false
```

_RVIZ2 (on PC)_
```bash
rviz2 -d ~/ws_odrive_robot/src/yaseen_differential_robot/rviz/view_robot_odom.rviz
```

_Teleoperation (on PC)_
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel_unstamped
```

_Joystick (unstamped, on PC)_
```bash
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/yaseen_diffbot_controller/cmd_vel_unstamped use_stamped:=false
```

**2. Simulated Robot Bringup** 

_Gazebo Sim Bringup (also bringsup RVIZ2)_
```bash
ros2 launch yaseen_differential_robot gz_sim.launch.py world:=hospital.sdf
```

_Teleop (Gazebo Sim)_
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel
```

_Joystick (Gazebo Sim)_
```bash
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/yaseen_diffbot_controller/cmd_vel use_stamped:=true
```

