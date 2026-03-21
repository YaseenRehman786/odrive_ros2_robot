This repository will be for my autonomous robot project where I will be using a Jetson Orin Nano Super, Odrive S1 FOC controllers, Odrive Botwheel motors, Intel Realsense D435 camera, and RPLidar.

------------------------------------------------------------------
**1) Install project dependencies used in this repo**
```bash
sudo apt update
sudo apt install -y \
	ros-humble-ros2-control \
	ros-humble-ros2-controllers \
	ros-humble-controller-manager \
	ros-humble-diff-drive-controller \
	ros-humble-joint-state-broadcaster \
	ros-humble-xacro \
	ros-humble-robot-state-publisher \
	ros-humble-joint-state-publisher \
	ros-humble-rviz2 \
	ros-humble-slam-toolbox \
	ros-humble-navigation2 \
	ros-humble-nav2-bringup \
	ros-humble-nav2-map-server \
	ros-humble-twist-mux \
	ros-humble-joy \
	ros-humble-teleop-twist-joy \
	ros-humble-teleop-twist-keyboard \
	ros-humble-ros-gz \
	ros-humble-ros-gz-sim \
	ros-humble-ros-gz-bridge
```

**2) Resolve and build workspace**
```bash
cd ~/ws_odrive_robot
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
```

**Building**
```bash
colcon build --symlink-install
```

**Sourcing**
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source ~/ws_odrive_robot/install/setup.bash
```

**CAN Bringup**
```bash
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
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/yaseen_diffbot_controller/cmd_vel_unstamped use_stamped:=false use_sim_time:=false
```

**2. Simulated Robot Bringup** 

_Gazebo Sim Bringup (also bringsup RVIZ2)_
```bash
pkill -9 ruby
pkill -9 ign
pkill -9 gz

ros2 launch yaseen_differential_robot gz_sim.launch.py world:=hospital.sdf
```

_Teleop (Gazebo Sim)_
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel
```

_Joystick (Gazebo Sim)_
```bash
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/yaseen_diffbot_controller/cmd_vel use_stamped:=true use_sim_time:=true
```

**3. SLAM Mapping**  

_SLAM Mapping_
```bash
ros2 launch slam_toolbox online_async_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_mapping.yaml use_sim_time:=true
```

_Save Occupancy Map (Nav2: `.yaml` + `.pgm`)_
```bash
ros2 run nav2_map_server map_saver_cli -f ~/ws_odrive_robot/maps/my_map_$(date +%Y%m%d_%H%M)
```

_Save Posegraph (SLAM Toolbox: `.data` / `.posegraph`)_
```bash
stamp=$(date +%Y%m%d_%H%M)
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '$HOME/ws_odrive_robot/maps/my_posegraph_${stamp}'}"
```

_SLAM Localization (Real Robot)_
```bash
ros2 launch slam_toolbox localization_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml use_sim_time:=false
```

_SLAM Localization (Gazebo Sim)_
```bash
ros2 launch slam_toolbox localization_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml use_sim_time:=true
```

_Note:_ `slam_localization.yaml` uses a slam_toolbox posegraph `.data` file, while Nav2 uses a map `.yaml` file.

_Map + 2D Pose Estimate + Goal (Simulation)_
```bash
ros2 launch nav2_bringup bringup_launch.py map:=$HOME/ws_odrive_robot/maps/my_map_xxxxxxxx_xxxx.yaml use_sim_time:=true autostart:=true
ros2 launch nav2_bringup rviz_launch.py use_sim_time:=true
```

_Map + 2D Pose Estimate + Goal (Real Robot)_
```bash
ros2 launch nav2_bringup bringup_launch.py map:=$HOME/ws_odrive_robot/maps/my_map_xxxxxxxx_xxxx.yaml use_sim_time:=false autostart:=true
ros2 launch nav2_bringup rviz_launch.py use_sim_time:=false
```