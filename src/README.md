This repository contains the ROS 2 Humble workspace for a custom UGV built around:

- Jetson Orin Nano Super for on-robot compute
- ODrive S1 FOC controllers and ODrive Botwheel motors
- Intel RealSense D435
- RPLidar

The README is organized as a reference manual. Detailed session history and experiments live in [SESSION_LOG.md](SESSION_LOG.md).

---

## Quick jump

- [General Setup](#general-setup)
- [ODrive and Motors](#odrive-and-motors)
- [SLAM & Nav2](#slam--nav2)
- [Intel RealSense](#intel-realsense)
- [Useful references](#useful-references)

---

## 🔧 General Setup

### Install dependencies

```bash
# update apt index
sudo apt update

# install ROS 2 dependencies
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

# Resolve dependencies and build
# go to workspace
cd ~/ws_odrive_robot
# source ROS 2 environment
source /opt/ros/humble/setup.bash
# install package dependencies from source tree
rosdep install --from-paths src --ignore-src -r -y
# build workspace
colcon build --symlink-install
# source local workspace overlay
source ~/ws_odrive_robot/install/setup.bash
```

### Source and Build

```bash
# go to workspace
cd ~/ws_odrive_robot
# build workspace
colcon build --symlink-install
# source base ROS distro
source /opt/ros/$ROS_DISTRO/setup.bash
# source local workspace overlay
source ~/ws_odrive_robot/install/setup.bash
```

### CAN bringup

```bash
# load CAN kernel modules
sudo modprobe can
sudo modprobe can_raw
sudo modprobe gs_usb

# reset interface
sudo ip link set can0 down 2>/dev/null
# set bitrate
sudo ip link set can0 type can bitrate 1000000
# bring interface up
sudo ip link set can0 up

# inspect interface status and counters
ip -details link show can0
```

### Connecting to the Jetson

```bash
# SSH into the Jetson 
ssh yaseenjetson@192.168.0.133

# NoMachine into the Jetson

# Stop Linux display manager
sudo systemctl stop display-manager
# Restart NoMachine to create virtual display
sudo /etc/NX/nxserver --restart
```

---

## ⚡ ODrive and Motors

Reference: https://docs.odriverobotics.com/v/latest/guides/ros-package.html

### A. Direct ODrive CAN test

Use this only to verify the CAN node and axis commands are working.

```bash
# launch ODrive CAN node
ros2 launch odrive_can example_launch.yaml

# request closed loop control for axis 0
ros2 service call /odrive_axis0/request_axis_state odrive_can/srv/AxisState "{axis_requested_state: 8}"

# request closed loop control for axis 1
ros2 service call /odrive_axis1/request_axis_state odrive_can/srv/AxisState "{axis_requested_state: 8}"

# publish velocity command to axis 0
ros2 topic pub /odrive_axis0/control_message odrive_can/msg/ControlMessage "{control_mode: 2, input_mode: 1, input_pos: 0.0, input_vel: 1.0, input_torque: 0.0}"

# publish velocity command to axis 1
ros2 topic pub /odrive_axis1/control_message odrive_can/msg/ControlMessage "{control_mode: 2, input_mode: 1, input_pos: 0.0, input_vel: 1.0, input_torque: 0.0}"
```

### B. ros2_control implementation

#### Real robot

Jetson bringup:

```bash
ros2 launch yaseen_differential_robot control.launch.py use_mock_hardware:=false use_lidar:=true use_rviz:=false
```

PC tools:

```bash
# launch RViz with odom profile
rviz2 -d ~/ws_odrive_robot/src/yaseen_differential_robot/rviz/view_robot_odom.rviz

# start twist_mux and remap output to controller cmd_vel
ros2 run twist_mux twist_mux --ros-args --params-file $HOME/ws_odrive_robot/src/yaseen_differential_robot/config/twist_mux.yaml -r cmd_vel_out:=/yaseen_diffbot_controller/cmd_vel_unstamped

# keyboard teleop direct to controller cmd_vel
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel_unstamped

# joystick launch (unstamped)
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/yaseen_diffbot_controller/cmd_vel_unstamped use_stamped:=false use_sim_time:=false
```

#### Simulated robot

```bash
# Optional cleanup if Gazebo gets stuck
# kill ruby process
pkill -9 ruby
# kill legacy ign processes
pkill -9 ign
# kill gz processes
pkill -9 gz

# launch Gazebo simulation
ros2 launch yaseen_differential_robot gz_sim.launch.py world:=hospital.sdf use_sim_time:=true

# keyboard teleop for sim controller
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=false -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel_unstamped

# joystick to /cmd_vel_joy for mux arbitration
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/cmd_vel_joy use_stamped:=false use_sim_time:=true

# start twist_mux and route to controller cmd_vel
ros2 run twist_mux twist_mux --ros-args --params-file $HOME/ws_odrive_robot/src/yaseen_differential_robot/config/twist_mux.yaml -r cmd_vel_out:=/yaseen_diffbot_controller/cmd_vel_unstamped
```

---

## 🗺️ SLAM & Nav2

### What each tool does

- SLAM mapping: build a map while driving the robot
- SLAM localization: localize against a saved SLAM posegraph
- AMCL: localize against a saved occupancy map
- Nav2: path planning and navigation using whichever localization source is active

### Preflight checklist

Before sending navigation goals:

- [ ] Exactly one localization source is running: SLAM localization or AMCL
- [ ] `twist_mux` is running and output is `/yaseen_diffbot_controller/cmd_vel_unstamped`
- [ ] Robot control stack is running
- [ ] RViz fixed frame is `map`
- [ ] `2D Pose Estimate` has been set once
- [ ] `cmd_vel` output is visible when navigating

Useful checks:

```bash
# verify required nodes are alive
ros2 node list | grep -E "slam_toolbox|amcl|bt_navigator|controller_server|planner_server|twist_mux"

# verify simulation clock is publishing
ros2 topic hz /clock

# check nav cmd_vel output
ros2 topic echo /cmd_vel --once
```

### Simulated robot

#### 1. Map creation

```bash
# launch Gazebo sim
ros2 launch yaseen_differential_robot gz_sim.launch.py world:=hospital.sdf use_sim_time:=true

# start twist_mux
ros2 run twist_mux twist_mux --ros-args --params-file $HOME/ws_odrive_robot/src/yaseen_differential_robot/config/twist_mux.yaml -r cmd_vel_out:=/yaseen_diffbot_controller/cmd_vel_unstamped

# launch joystick
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/cmd_vel_joy use_stamped:=false use_sim_time:=true

# start SLAM mapping
ros2 launch yaseen_differential_robot online_async_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_mapping.yaml use_sim_time:=true
```

Save the map and posegraph:

```bash
# create timestamp for this mapping session
stamp=$(date +%Y%m%d_%H%M)

# create output directory
session_dir="/home/ysn786/ws_odrive_robot/maps/${stamp}"
mkdir -p "$session_dir"

# save occupancy map (yaml + pgm)
ros2 run nav2_map_server map_saver_cli -f "$session_dir/map"

# save SLAM posegraph
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '$session_dir/posegraph'}"
```

#### 2. SLAM localization + Nav2

Update `slam_localization.yaml` so `map_file_name` points to the latest posegraph base path, then launch:

```bash
# launch SLAM localization using saved posegraph
ros2 launch slam_toolbox localization_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml use_sim_time:=true

# launch Nav2 stack
ros2 launch yaseen_differential_robot navigation_launch.py use_sim_time:=true
```

#### 3. AMCL + Nav2

```bash
# launch Gazebo sim
ros2 launch yaseen_differential_robot gz_sim.launch.py world:=hospital.sdf use_sim_time:=true

# start twist_mux
ros2 run twist_mux twist_mux --ros-args --params-file $HOME/ws_odrive_robot/src/yaseen_differential_robot/config/twist_mux.yaml -r cmd_vel_out:=/yaseen_diffbot_controller/cmd_vel_unstamped

# launch joystick
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/cmd_vel_joy use_stamped:=false use_sim_time:=false

# launch AMCL localization
ros2 launch yaseen_differential_robot localization_launch.py map:=$HOME/ws_odrive_robot/maps/hopital/my_map_hospital20260321_0015.yaml use_sim_time:=true

# launch Nav2 with transient local map subscribe
ros2 launch yaseen_differential_robot navigation_launch.py use_sim_time:=true map_subscribe_transient_local:=true
```

### Real robot

#### 1. Map creation

```bash
# launch robot control stack on hardware
ros2 launch yaseen_differential_robot control.launch.py use_mock_hardware:=false use_lidar:=true use_rviz:=false

# start twist_mux
ros2 run twist_mux twist_mux --ros-args --params-file $HOME/ws_odrive_robot/src/yaseen_differential_robot/config/twist_mux.yaml -r cmd_vel_out:=/yaseen_diffbot_controller/cmd_vel_unstamped

# launch joystick
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/cmd_vel_joy use_stamped:=false use_sim_time:=false

# start SLAM mapping on real robot
ros2 launch yaseen_differential_robot online_async_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_mapping.yaml use_sim_time:=false
```

Save the map and posegraph with the same commands as simulation.

#### 2. SLAM localization + Nav2

```bash
# launch SLAM localization using saved posegraph
ros2 launch slam_toolbox localization_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml use_sim_time:=false

# launch Nav2 stack
ros2 launch yaseen_differential_robot navigation_launch.py use_sim_time:=false
```

#### 3. AMCL + Nav2

```bash
# find latest saved map.yaml
MAP=$(find /home/ysn786/ws_odrive_robot/maps -type f -name "map.yaml" -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)

# launch AMCL with latest map
ros2 launch yaseen_differential_robot localization_launch.py map:="$MAP" use_sim_time:=false

# launch Nav2 with transient local map subscribe
ros2 launch yaseen_differential_robot navigation_launch.py use_sim_time:=false map_subscribe_transient_local:=true
```

---

## 📷 Intel RealSense

### PC visualization workflow

```bash
# restart ROS daemon
ros2 daemon stop && ros2 daemon start

# select CycloneDDS RMW
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# point DDS to local config
export CYCLONEDDS_URI=file:///home/$USER/cyclonedds.xml

# start RViz
rviz2
```

### Official launch

Use the official `realsense2_camera` launch for the real camera:

```bash
ros2 launch realsense2_camera rs_launch.py \
	align_depth.enable:=true \
	rgb_camera.color_profile:=424x240x5 \
	depth_module.depth_profile:=424x240x5 \
	enable_sync:=true
```

### Enable Point Cloud
```bash
#after launching in new terminal set point cloud to true
ros2 param set /camera/camera pointcloud__neon_.enable true
```

### RViz DepthCloud configuration

In RViz, add a DepthCloud display and set the following:

| Field | Value |
|---|---|
| Fixed Frame | `camera_link` |
| Depth Map Topic | `/camera/camera/aligned_depth_to_color/image_raw` |
| Color Image Topic | `/camera/camera/color/image_raw` |
| Color Transport Hint | `compressed` |
| Reliability Policy | `Best Effort` |
| Queue Size | `2` |


## 📚 Useful references

- ODrive ROS package docs: https://docs.odriverobotics.com/v/latest/guides/ros-package.html
- Jetson RealSense install notes: https://github.com/meisner91/JetsonNanoOrinScripts/blob/main/03_Install_Intel_RealSense_on_JetPack_6.md
- Session history and troubleshooting: [SESSION_LOG.md](SESSION_LOG.md)
