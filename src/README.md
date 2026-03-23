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
cd ~/ws_odrive_robot
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

#### **3-Quick) Fast Preflight Checklists (Do This Before Sending Goals)**

Use this as a rapid verification list so you do not miss a required node.

**A) Nav2 + SLAM Localization Checklist**
- [ ] Exactly one localization source is running: **SLAM localization** (`slam_toolbox localization_launch.py`).
- [ ] AMCL is **not** running.
- [ ] Robot/control stack is up:
	- Gazebo: `gz_sim.launch.py` is running.
	- Real robot: `control.launch.py use_mock_hardware:=false use_lidar:=true` is running.
- [ ] `twist_mux` is running and output remap is `/yaseen_diffbot_controller/cmd_vel_unstamped`.
- [ ] Nav2 is running from your launch: `ros2 launch yaseen_differential_robot navigation_launch.py use_sim_time:=<true|false>`.
- [ ] RViz fixed frame is `map`, then set **2D Pose Estimate** once.
- [ ] Quick checks pass:
```bash
ros2 node list | grep -E "slam_toolbox|amcl|bt_navigator|controller_server|planner_server|twist_mux"
ros2 topic hz /clock            # required in sim (should publish)
ros2 topic echo /cmd_vel --once # Nav2 command output present when navigating
```

**B) Nav2 + AMCL Localization Checklist**
- [ ] Exactly one localization source is running: **AMCL** (`localization_launch.py` from your package).
- [ ] SLAM localization is **not** running.
- [ ] AMCL map path is valid (`map:=.../map.yaml`).
- [ ] Robot/control stack is up:
	- Gazebo: `gz_sim.launch.py` is running.
	- Real robot: `control.launch.py use_mock_hardware:=false use_lidar:=true` is running.
- [ ] `twist_mux` is running and output remap is `/yaseen_diffbot_controller/cmd_vel_unstamped`.
- [ ] Nav2 is running with transient local map subscribe:
	- `ros2 launch yaseen_differential_robot navigation_launch.py use_sim_time:=<true|false> map_subscribe_transient_local:=true`
- [ ] RViz setup is complete: Fixed Frame=`map`, click **2D Pose Estimate**, map/costmap durability set to **Transient Local**.
- [ ] Quick checks pass:
```bash
ros2 node list | grep -E "amcl|slam_toolbox|bt_navigator|controller_server|planner_server|twist_mux"
ros2 topic hz /clock            # required in sim (should publish)
ros2 topic echo /amcl_pose --once
```

**If a goal is accepted but robot does not move, check immediately**
- [ ] `ros2 topic echo /yaseen_diffbot_controller/cmd_vel_unstamped --once`
- [ ] `ros2 topic echo /yaseen_diffbot_controller/odom --once`
- [ ] No duplicate `twist_mux` processes are running.

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
ros2 launch yaseen_differential_robot online_async_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_mapping.yaml use_sim_time:=true
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

_Terminal 5: Nav2 (without AMCL interference)_
```bash
ros2 launch yaseen_differential_robot navigation_launch.py use_sim_time:=true
```

_Important:_ In RViz, set initial pose once using **2D Pose Estimate** before sending Nav2 goals.

_Important:_ During navigation, use one localization source only (do not run AMCL and SLAM localization simultaneously).

#### **3B. Gazebo Sim — AMCL + Nav2 Workflow (Map-Based Localization)**

Use this flow when you want Nav2 with AMCL localization (instead of SLAM localization).

**3B-1) Bring up simulation + control pipeline**  
_Terminal 1: Gazebo sim_
```bash
ros2 launch yaseen_differential_robot gz_sim.launch.py world:=hospital.sdf use_sim_time:=true
```

_Terminal 2: twist_mux_
```bash
ros2 run twist_mux twist_mux --ros-args --params-file $HOME/ws_odrive_robot/src/yaseen_differential_robot/config/twist_mux.yaml -r cmd_vel_out:=/yaseen_diffbot_controller/cmd_vel_unstamped
```

_Terminal 3: joystick teleop through mux_
```bash
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/cmd_vel_joy use_stamped:=false use_sim_time:=false
```

**3B-2) Launch AMCL localization + Nav2**  
_Terminal 4: AMCL localization_
```bash
ros2 launch yaseen_differential_robot localization_launch.py map:=$HOME/ws_odrive_robot/maps/hopital/my_map_hospital20260321_0015.yaml use_sim_time:=true
```

_Terminal 5: Nav2_
```bash
ros2 launch yaseen_differential_robot navigation_launch.py use_sim_time:=true map_subscribe_transient_local:=true
```

**3B-3) RViz setup required for AMCL/costmaps**  
- Set RViz **Fixed Frame** to `map` manually.
- Click **2D Pose Estimate** once to initialize AMCL; this allows costmaps to load.
- Set the AMCL/costmap map display durability to **Transient Local** so the map is visible.

_Important:_ For navigation, run only one localization source at a time (AMCL **or** SLAM localization, not both).

#### **3C. Real Robot — Full Workflow (Create Map → Save → Localize → Nav2)**

**3C-0) Cleanup (if needed)**  
```bash
pkill -f "nav2_bringup|slam_toolbox|twist_mux|joystick.launch.py|control.launch.py" || true
```

**3C-1) Create a map on the real robot**  
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
ros2 launch yaseen_differential_robot online_async_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_mapping.yaml use_sim_time:=false
```

Drive robot around the room until the map is complete.

**3C-2) Save map + posegraph**  
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

**3C-3) Update `slam_localization.yaml` to use the new posegraph**  
`map_file_name` must point to the posegraph base path (no extension).

```bash
posegraph_base=$(find /home/ysn786/ws_odrive_robot/maps -type f -name "posegraph.posegraph" -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2- | sed 's/\.posegraph$//')
sed -i "s|^\s*map_file_name:.*|    map_file_name: ${posegraph_base}|" /home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml
grep "map_file_name:" /home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml
```

**3C-4) Run localization + Nav2 using saved files**  
_Cleanup mapping process first if still running:_
```bash
pkill -f "slam_toolbox.*online_async_launch" || true
```

_Terminal 4 (PC): SLAM localization_
```bash
ros2 launch slam_toolbox localization_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml use_sim_time:=false
```

_Terminal 5 (PC): Nav2 (without AMCL interference)_
```bash
ros2 launch yaseen_differential_robot navigation_launch.py use_sim_time:=false
```

_Important:_ In RViz, set initial pose once using **2D Pose Estimate** before sending Nav2 goals.

_Important notes_
- Use only one localization source at a time during navigation.
- Keep command pipeline unstamped to controller: `/yaseen_diffbot_controller/cmd_vel_unstamped`.
- For safety override with joystick + Nav2, publish joystick to `/cmd_vel_joy` and let `twist_mux` arbitrate.

#### **3D. Real Robot — AMCL + Nav2 Workflow (Map-Based Localization)**  

Use this flow when you want Nav2 with AMCL localization on hardware (instead of SLAM localization).

**3D-0) Cleanup (if needed)**  
```bash
pkill -f "nav2_bringup|slam_toolbox|twist_mux|joystick.launch.py|control.launch.py" || true
```

**3D-1) Bring up robot + control pipeline**  
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

**3D-2) Launch AMCL localization + Nav2**  
_Terminal 4 (PC): AMCL localization_
```bash
MAP=$(find /home/ysn786/ws_odrive_robot/maps -type f -name "map.yaml" -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
ros2 launch yaseen_differential_robot localization_launch.py map:="$MAP" use_sim_time:=false
```

_Terminal 5 (PC): Nav2_
```bash
ros2 launch yaseen_differential_robot navigation_launch.py use_sim_time:=false map_subscribe_transient_local:=true
```

**3D-3) RViz setup required for AMCL/costmaps**  
- Set RViz **Fixed Frame** to `map` manually.
- Click **2D Pose Estimate** once to initialize AMCL; this allows costmaps to load.
- Set the AMCL/costmap map display durability to **Transient Local** so the map is visible.

_Important:_ For navigation, run only one localization source at a time (AMCL **or** SLAM localization, not both).
