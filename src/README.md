This repository will be for my autonomous robot project where I will be using a Jetson Orin Nano Super, Odrive S1 FOC controllers, Odrive Botwheel motors, Intel Realsense D435 camera, and RPLidar.

------------------------------------------------------------------
# General Setup
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

**Build + Source**
```bash
colcon build --symlink-install
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
# **Controlling Odrive and Motors**  
(https://docs.odriverobotics.com/v/latest/guides/ros-package.html)

## **_APPROACH A -> odrive_node_ (just test things are working)**
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
## **_APPROACH B -> odrive_ros2_control_ (my implementation)**

### 1) Real Robot Bringup (ros2_control + ODrive + LiDAR)
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

### 2) Simulated Robot Bringup

_Gazebo Sim Bringup (also bringsup RVIZ2)_
```bash
# Optional cleanup if a previous Gazebo session is stuck:
pkill -9 ruby
pkill -9 ign
pkill -9 gz

ros2 launch yaseen_differential_robot gz_sim.launch.py world:=hospital.sdf use_sim_time:=true
```

_Teleop (Gazebo Sim)_
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=false -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel_unstamped
```

_Joystick (Gazebo Sim)_
```bash
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/cmd_vel_joy use_stamped:=false use_sim_time:=true
```

_Twist Mux (Gazebo Sim, required for Nav2 + joystick safety override)_
```bash
ros2 run twist_mux twist_mux --ros-args --params-file $HOME/ws_odrive_robot/src/yaseen_differential_robot/config/twist_mux.yaml -r cmd_vel_out:=/yaseen_diffbot_controller/cmd_vel_unstamped
```

### 3) SLAM + Nav2 Workflows

#### **3A. Gazebo Sim — Full Workflow (Create Map → Save → Localize → Nav2)**

**3A-0) Cleanup (if needed)**
```bash
pkill -f "nav2_bringup|slam_toolbox|twist_mux|gz_sim.launch.py|ign gazebo" || true
```

**3A-1) Create a map in Gazebo**  
_Terminal 1: Gazebo Sim_
```bash
ros2 launch yaseen_differential_robot gz_sim.launch.py world:=hospital.sdf use_sim_time:=true
```

_Terminal 2: twist_mux (optional but recommended for joystick safety override)_
```bash
ros2 run twist_mux twist_mux --ros-args --params-file $HOME/ws_odrive_robot/src/yaseen_differential_robot/config/twist_mux.yaml -r cmd_vel_out:=/yaseen_diffbot_controller/cmd_vel_unstamped
```

_Terminal 3: Joystick teleop through mux_
```bash
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/cmd_vel_joy use_stamped:=false use_sim_time:=true
```

_Terminal 4: SLAM mapping (NOT localization)_
```bash
ros2 launch slam_toolbox online_async_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_mapping.yaml use_sim_time:=true
```

Drive the robot around the environment until the map is complete.

**3A-2) Save map + posegraph**
```bash
stamp=$(date +%Y%m%d_%H%M)
session_dir="/home/ysn786/ws_odrive_robot/maps/${stamp}"
mkdir -p "$session_dir"
ros2 run nav2_map_server map_saver_cli -f "$session_dir/map"
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '$session_dir/posegraph'}"
```

This creates:
- Occupancy map for Nav2: `.../<stamp>/map.yaml` + `map.pgm`
- Posegraph for SLAM localization: `.../<stamp>/posegraph.posegraph` (+ `.data`)

**3A-3) Update `slam_localization.yaml` to use the new posegraph**  
`map_file_name` must point to the posegraph base path (no extension).

```bash
posegraph_base=$(find /home/ysn786/ws_odrive_robot/maps -type f -name "posegraph.posegraph" -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2- | sed 's/\.posegraph$//')
sed -i "s|^\s*map_file_name:.*|    map_file_name: ${posegraph_base}|" /home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml
grep "map_file_name:" /home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml
```

**3A-4) Run localization + Nav2 using saved files**  
_Cleanup mapping processes first if still running:_
```bash
pkill -f "slam_toolbox.*online_async_launch" || true
```

_Terminal 2 (or new): SLAM localization_
```bash
ros2 launch slam_toolbox localization_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml use_sim_time:=true
```

_Terminal 5: Nav2 with latest saved occupancy map_
```bash
MAP=$(find /home/ysn786/ws_odrive_robot/maps -type f -name "map.yaml" -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
ros2 launch nav2_bringup bringup_launch.py map:="$MAP" use_sim_time:=true autostart:=true
```

_Important:_ In RViz, set initial pose once using **2D Pose Estimate** before sending Nav2 goals.

_Important:_ During navigation, use one localization source only (do not run AMCL and SLAM localization simultaneously).

#### **3B. Real Robot — Full Workflow (Create Map → Save → Localize → Nav2)**

**3B-0) Cleanup (if needed)**  
```bash
pkill -f "nav2_bringup|slam_toolbox|twist_mux|joystick.launch.py|control.launch.py" || true
```

**3B-1) Create a map on the real robot**  
_Terminal 1 (Jetson): robot + lidar + ros2_control_
```bash
ros2 launch yaseen_differential_robot control.launch.py use_mock_hardware:=false use_lidar:=true use_rviz:=false
```

_Terminal 2 (PC): twist_mux_
```bash
ros2 run twist_mux twist_mux --ros-args --params-file $HOME/ws_odrive_robot/src/yaseen_differential_robot/config/twist_mux.yaml -r cmd_vel_out:=/yaseen_diffbot_controller/cmd_vel_unstamped
```

_Terminal 3 (PC): joystick teleop through mux_
```bash
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/cmd_vel_joy use_stamped:=false use_sim_time:=false
```

_Terminal 4 (PC): SLAM mapping (NOT localization)_
```bash
ros2 launch slam_toolbox online_async_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_mapping.yaml use_sim_time:=false
```

Drive robot around the room until the map is complete.

**3B-2) Save map + posegraph**
```bash
stamp=$(date +%Y%m%d_%H%M)
session_dir="/home/ysn786/ws_odrive_robot/maps/${stamp}"
mkdir -p "$session_dir"
ros2 run nav2_map_server map_saver_cli -f "$session_dir/map"
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '$session_dir/posegraph'}"
```

This creates:
- Occupancy map for Nav2: `.../<stamp>/map.yaml` + `map.pgm`
- Posegraph for SLAM localization: `.../<stamp>/posegraph.posegraph` (+ `.data`)

**3B-3) Update `slam_localization.yaml` to use the new posegraph**  
`map_file_name` must point to the posegraph base path (no extension).

```bash
posegraph_base=$(find /home/ysn786/ws_odrive_robot/maps -type f -name "posegraph.posegraph" -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2- | sed 's/\.posegraph$//')
sed -i "s|^\s*map_file_name:.*|    map_file_name: ${posegraph_base}|" /home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml
grep "map_file_name:" /home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml
```

**3B-4) Run localization + Nav2 using saved files**  
_Cleanup mapping process first if still running:_
```bash
pkill -f "slam_toolbox.*online_async_launch" || true
```

_Terminal 4 (PC): SLAM localization_
```bash
ros2 launch slam_toolbox localization_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml use_sim_time:=false
```

_Terminal 5 (PC): Nav2 with latest saved occupancy map_
```bash
MAP=$(find /home/ysn786/ws_odrive_robot/maps -type f -name "map.yaml" -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
ros2 launch nav2_bringup bringup_launch.py map:="$MAP" use_sim_time:=false autostart:=true
```

_Important:_ In RViz, set initial pose once using **2D Pose Estimate** before sending Nav2 goals.

_Important notes_
- Use only one localization source at a time during navigation.
- Keep command pipeline unstamped to controller: `/yaseen_diffbot_controller/cmd_vel_unstamped`.
- For safety override with joystick + Nav2, publish joystick to `/cmd_vel_joy` and let `twist_mux` arbitrate.
