# ROS2 Differential Drive Robot Development Session Log
**Date**: March 8-9, 2026  
**Project**: yaseen_differential_robot - ODrive S1 Differential Drive Robot  
**ROS2 Version**: Humble  
**Status**: ✅ Phase 1, 2 & 3 Complete - Gazebo Simulation Working

## Quick Navigation

**Last updated**: March 22, 2026

- [Project Overview](#project-overview)
- [Package Structure Created](#package-structure-created)
- [Phase 1: Foundation & Visualization ✅](#phase-1-foundation--visualization-)
- [Phase 2: ros2_control Integration ✅](#phase-2-ros2_control-integration-)
- [Phase 3: ODrive CAN Hardware Integration ✅](#phase-3-odrive-can-hardware-integration-)
- [Contact Info for Continuity](#contact-info-for-continuity)
- [March 15, 2026 — Gazebo Fortress ↔ Harmonic Switching Playbook](#march-15-2026--gazebo-fortress--harmonic-switching-playbook)
- [March 19-20, 2026 — Real Robot LiDAR + SLAM + Joystick Integration](#march-19-20-2026--real-robot-lidar--slam--joystick-integration)
- [March 21–22, 2026 — Continuation Addendum (Merged)](#march-2122-2026--continuation-addendum-merged)

---

## Project Overview

Building a differential drive robot from scratch with:
- **Hardware**: 2x ODrive S1 motor controllers, 2x ODrive botwheels, Jetson Orin Nano Super, RPLidar, Intel RealSense depth camera
- **Communication**: CAN bus between all components
- **Approach**: Simulate-first pipeline (mock hardware → real hardware)
- **Goal**: Full autonomous navigation pipeline starting from ground-up robotics learning

---

## Package Structure Created

```
src/yaseen_differential_robot/
├── CMakeLists.txt
├── package.xml
├── urdf/
│   ├── robot.urdf.xacro              (main xacro - includes all)
│   ├── robot_description.xacro       (robot geometry as macro)
│   └── robot_ros2_control.xacro      (ros2_control hardware interface)
├── config/
│   └── controllers.yaml              (diff_drive_controller config)
├── launch/
│   ├── view_robot.launch.py          (visualization only)
│   └── control.launch.py             (ros2_control with mock/real switching)
├── meshes/
│   ├── base_link.STL
│   ├── wheel_left_link.STL
│   ├── wheel_right_link.STL
│   ├── caster_left_wheel_link.STL
│   ├── caster_wheel_right_link.STL
│   └── lidar_link.STL
└── rviz/
    └── view_robot.rviz               (saved RViz config)
```

---

## Phase 1: Foundation & Visualization ✅

### What We Did:

1. **Created clean ROS2 package** using `ros2 pkg create`
2. **Converted SolidWorks URDF to proper xacro structure**:
   - Fixed duplicate robot tags
   - Changed package paths from `view_robot_pkg` to `yaseen_differential_robot`
   - Created macro-based structure for modularity
   - Added `base_footprint` to fix TF tree

3. **Key URDF Structure**:
   - `robot.urdf.xacro` - main file that includes everything
   - `robot_description.xacro` - wrapped in `<xacro:macro name="yaseen_description">`
   - Proper joint hierarchy: `base_footprint` → `base_link` → wheels/casters/lidar

4. **Files Modified**:

**package.xml additions**:
```xml
<depend>urdf</depend>
<depend>xacro</depend>
<depend>robot_state_publisher</depend>
<depend>joint_state_publisher</depend>
<depend>joint_state_publisher_gui</depend>
<depend>rviz2</depend>
```

**CMakeLists.txt additions**:
```cmake
find_package(urdf REQUIRED)
find_package(xacro REQUIRED)

install(DIRECTORY
  urdf
  meshes
  launch
  config
  rviz
  DESTINATION share/${PROJECT_NAME}/
)
```

### Verification Commands:
```bash
ros2 launch yaseen_differential_robot view_robot.launch.py
ros2 topic echo /joint_states --once
ros2 topic echo /tf_static --once
ros2 run tf2_tools view_frames
```

---

## Phase 2: ROS2 Control Integration ✅

### What We Did:

1. **Created `robot_ros2_control.xacro`** (ODrive-aligned):
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:macro name="yaseen_ros2_control" params="name use_mock_hardware">
    <ros2_control name="${name}" type="system">
      <xacro:unless value="${use_mock_hardware}">
        <hardware>
          <plugin>odrive_ros2_control_plugin/ODriveHardwareInterface</plugin>
          <param name="can">can0</param>
        </hardware>
      </xacro:unless>

      <xacro:if value="${use_mock_hardware}">
        <hardware>
          <plugin>mock_components/GenericSystem</plugin>
          <param name="calculate_dynamics">true</param>
        </hardware>
      </xacro:if>

      <joint name="wheel_left_joint">
        <param name="node_id">0</param>
        <command_interface name="velocity"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
      </joint>

      <joint name="wheel_right_joint">
        <param name="node_id">1</param>
        <command_interface name="velocity"/>
        <state_interface name="position"/>
        <state_interface name="velocity"/>
      </joint>
    </ros2_control>
  </xacro:macro>
</robot>
```

2. **Created `controllers.yaml`**:
```yaml
controller_manager:
  ros__parameters:
    update_rate: 10

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    yaseen_diffbot_controller:
      type: diff_drive_controller/DiffDriveController

yaseen_diffbot_controller:
  ros__parameters:
    left_wheel_names: ["wheel_left_joint"]
    right_wheel_names: ["wheel_right_joint"]
    
    wheel_separation: 0.5064
    wheel_radius: 0.0855
    
    wheel_separation_multiplier: 1.0
    left_wheel_radius_multiplier: -1.0
    right_wheel_radius_multiplier: 1.0
    
    publish_rate: 50.0
    odom_frame_id: odom
    base_frame_id: base_link
    
    open_loop: true
    enable_odom_tf: true
    cmd_vel_timeout: 0.5
    use_stamped_vel: false
    
    linear.x.has_velocity_limits: true
    linear.x.max_velocity: 1.0
    linear.x.min_velocity: -1.0
    linear.x.has_acceleration_limits: true
    linear.x.max_acceleration: 1.0
    
    angular.z.has_velocity_limits: true
    angular.z.max_velocity: 1.0
    angular.z.min_velocity: -1.0
    angular.z.has_acceleration_limits: true
    angular.z.max_acceleration: 1.0
```

3. **Created `control.launch.py`** with **runtime mock/real switching**:
```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Runtime argument for switching hardware
    use_mock_hardware_arg = DeclareLaunchArgument(
        'use_mock_hardware',
        default_value='true',
        description='Use mock hardware (true) or real ODrive hardware (false)'
    )
    
    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution([FindPackageShare("yaseen_differential_robot"), "urdf", "robot.urdf.xacro"]),
        " ",
        "use_mock_hardware:=", LaunchConfiguration('use_mock_hardware'),
    ])
    
    robot_description = {"robot_description": robot_description_content}
    
    robot_controllers = PathJoinSubstitution([
        FindPackageShare("yaseen_differential_robot"), "config", "controllers.yaml"
    ])
    
    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, robot_controllers],
        output="both",
    )
    
    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description],
        output="both",
    )
    
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )
    
    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["yaseen_diffbot_controller", "--controller-manager", "/controller_manager"],
    )
    
    delay_robot_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[robot_controller_spawner],
        )
    )
    
    return LaunchDescription([
        use_mock_hardware_arg,
        control_node,
        robot_state_pub_node,
        joint_state_broadcaster_spawner,
        delay_robot_controller,
    ])
```

### Updated `robot.urdf.xacro`:
```xml
<?xml version="1.0"?>
<robot name="yaseen_differential_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  
  <xacro:arg name="use_mock_hardware" default="true" />

  <xacro:include filename="$(find yaseen_differential_robot)/urdf/robot_description.xacro"/>
  <xacro:include filename="$(find yaseen_differential_robot)/urdf/robot_ros2_control.xacro"/>
  
  <xacro:yaseen_description/>
  <xacro:yaseen_ros2_control name="YaseenDiffBot" use_mock_hardware="$(arg use_mock_hardware)"/>

</robot>
```

---

## Current Working State ✅

### Launch Commands:

**Mock Hardware (default)**:
```bash
ros2 launch yaseen_differential_robot control.launch.py
# OR explicitly:
ros2 launch yaseen_differential_robot control.launch.py use_mock_hardware:=true
```

**Real ODrive Hardware**:
```bash
ros2 launch yaseen_differential_robot control.launch.py use_mock_hardware:=false
```

### Verification Commands:
```bash
# Check hardware interfaces
ros2 control list_hardware_interfaces

# Expected output:
# command interfaces
#   wheel_left_joint/velocity [available] [claimed]
#   wheel_right_joint/velocity [available] [claimed]
# state interfaces
#   wheel_left_joint/position
#   wheel_left_joint/velocity
#   wheel_right_joint/position
#   wheel_right_joint/velocity

# Check controllers
ros2 control list_controllers

# Expected output:
# joint_state_broadcaster   joint_state_broadcaster/JointStateBroadcaster  active
# yaseen_diffbot_controller diff_drive_controller/DiffDriveController      active

# Check topics
ros2 topic list | grep -E "cmd_vel|odom|joint"

# Test manual control
ros2 topic pub /yaseen_diffbot_controller/cmd_vel_unstamped geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.1}}" --rate 10

# Monitor joint states
ros2 topic echo /joint_states

# Monitor odometry
ros2 topic echo /yaseen_diffbot_controller/odom
```

---

## Key Learnings & Fixes Applied

### Issue 1: "no ros2_control tag" Error
**Cause**: Included xacro file had its own `<robot>` tags, preventing macro expansion.  
**Fix**: Converted `robot_description.xacro` to macro format (`yaseen_description`)

### Issue 2: "None of requested interfaces exist"
**Cause**: Mock hardware plugin requires explicit interface definitions.  
**Fix**: Added `<command_interface>` and `<state_interface>` tags to joints.  
**Note**: Real ODrive plugin auto-exposes these, but explicit tags don't hurt.

### Issue 3: Joint names mismatch
**Cause**: YAML used wrong joint names from old package.  
**Fix**: Updated to `wheel_left_joint` and `wheel_right_joint` (matching URDF).

### Issue 4: Stale install cache
**Cause**: Changes in src/ not propagating to install/.  
**Fix**: Clean rebuild: `rm -rf build/yaseen_differential_robot install/yaseen_differential_robot`

---

## Robot Physical Parameters

```yaml
wheel_separation: 0.5064 m  # Distance between left/right wheel centers
wheel_radius: 0.0855 m      # ODrive Botwheel radius
wheel_joint_names:
  - wheel_left_joint        # ODrive node_id: 0
  - wheel_right_joint       # ODrive node_id: 1
```

---

## Phase 3: Gazebo Simulation ✅

### What We Did:

Successfully integrated Gazebo Fortress (gz sim) simulation with complete physics tuning and controller configuration.

### Files Created/Modified:

1. **Created `robot_gazebo.xacro`** - Gazebo-specific physics properties:
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:macro name="gazebo_config">
    <!-- Drive wheels: high friction for traction -->
    <gazebo reference="wheel_left_link">
      <mu1>1.0</mu1>
      <mu2>1.0</mu2>
      <kp>10000.0</kp>
      <kd>1.0</kd>
      <minDepth>0.001</minDepth>
      <maxVel>1.0</maxVel>
    </gazebo>

    <gazebo reference="wheel_right_link">
      <mu1>1.0</mu1>
      <mu2>1.0</mu2>
      <kp>10000.0</kp>
      <kd>1.0</kd>
      <minDepth>0.001</minDepth>
      <maxVel>1.0</maxVel>
    </gazebo>

    <!-- Casters: frictionless for free rotation -->
    <gazebo reference="caster_left_wheel_link">
      <mu1>0.0</mu1>
      <mu2>0.0</mu2>
    </gazebo>

    <gazebo reference="caster_wheel_right_link">
      <mu1>0.0</mu1>
      <mu2>0.0</mu2>
    </gazebo>

    <!-- gz_ros2_control plugin -->
    <gazebo>
      <plugin filename="gz_ros2_control-system" name="gz_ros2_control::GazeboSimROS2ControlPlugin">
        <parameters>$(find yaseen_differential_robot)/config/gz_controllers.yaml</parameters>
      </plugin>
    </gazebo>
  </xacro:macro>
</robot>
```

2. **Created `gz_controllers.yaml`** - Simulation-specific controller parameters:
```yaml
controller_manager:
  ros__parameters:
    update_rate: 50

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    yaseen_diffbot_controller:
      type: diff_drive_controller/DiffDriveController

yaseen_diffbot_controller:
  ros__parameters:
    left_wheel_names: ["wheel_left_joint"]
    right_wheel_names: ["wheel_right_joint"]
    
    wheel_separation: 0.5064
    wheel_radius: 0.0855
    
    # Critical for correct Gazebo kinematics
    wheel_separation_multiplier: 1.0
    left_wheel_radius_multiplier: -1.0
    right_wheel_radius_multiplier: 1.0
    
    publish_rate: 50.0
    odom_frame_id: odom
    base_frame_id: base_footprint
    pose_covariance_diagonal: [0.001, 0.001, 0.0, 0.0, 0.0, 0.01]
    twist_covariance_diagonal: [0.001, 0.0, 0.0, 0.0, 0.0, 0.01]
    
    open_loop: false
    enable_odom_tf: true
    cmd_vel_timeout: 0.5
    
    linear.x.has_velocity_limits: true
    linear.x.max_velocity: 1.0
    linear.x.min_velocity: -1.0
    
    angular.z.has_velocity_limits: true
    angular.z.max_velocity: 2.0
    angular.z.min_velocity: -2.0
```

3. **Created `gz_sim.launch.py`** - Gazebo launch file:
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_share = get_package_share_directory('yaseen_differential_robot')
    
    world_file = os.path.join(pkg_share, 'worlds', 'empty.sdf')
    
    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]),
        " ",
        PathJoinSubstitution([FindPackageShare("yaseen_differential_robot"), "urdf", "robot_gazebo.urdf.xacro"])
    ])
    
    robot_description = {"robot_description": robot_description_content}
    
    robot_controllers = PathJoinSubstitution([
        FindPackageShare("yaseen_differential_robot"), "config", "gz_controllers.yaml"
    ])
    
    robot_state_pub_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[robot_description],
        output="both",
    )
    
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen'
    )
    
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'yaseen_robot',
            '-z', '1.5'
        ],
        output='screen'
    )
    
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )
    
    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["yaseen_diffbot_controller"],
    )
    
    delay_robot_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[robot_controller_spawner],
        )
    )
    
    return LaunchDescription([
        gazebo,
        robot_state_pub_node,
        spawn_entity,
        joint_state_broadcaster_spawner,
        delay_robot_controller,
    ])
```

4. **Created `robot_gazebo.urdf.xacro`** - Main file for Gazebo:
```xml
<?xml version="1.0"?>
<robot name="yaseen_differential_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  
  <xacro:include filename="$(find yaseen_differential_robot)/urdf/robot_description.xacro"/>
  <xacro:include filename="$(find yaseen_differential_robot)/urdf/robot_gazebo.xacro"/>
  
  <xacro:yaseen_description/>
  <xacro:gazebo_config/>

</robot>
```

5. **Modified `robot_description.xacro`** - Critical geometry fixes:
   - **Base height adjustment**: Changed `base_footprint_joint` z from 0.56206 to **0.58365** to account for wheel radius (prevents robot sinking into ground)
   - **Wheel collision geometry**: Replaced complex mesh collisions with **cylinder primitives** (radius=0.0855, length=0.033) for stable physics contact
   - **Caster collision geometry**: Replaced mesh with **sphere primitives** (radius=0.0372) to eliminate ground penetration
   - **Visual geometry**: Kept original STL meshes for accurate appearance
   - Collision rpy set to "0 0 0" for proper orientation

### Major Issues Resolved:

#### Issue 1: Wheel Slipping in Gazebo
**Symptoms**: Robot wouldn't move despite cmd_vel commands, wheels spinning in place  
**Root Cause**: Mesh-based wheel collisions causing unstable contact points  
**Fix Applied**:
- Replaced wheel mesh collisions with cylinder primitives
- Tuned friction coefficients (mu1=1.0, mu2=1.0)
- Set contact parameters (kp=10000.0, kd=1.0)
- Result: ✅ Stable wheel-ground contact achieved

#### Issue 2: Robot Spawning Underground
**Symptoms**: Base link, wheels, and casters partially/fully below ground plane  
**Root Cause**: base_footprint_joint height didn't account for wheel radius offset  
**Fix Applied**:
- Adjusted base_footprint_joint z: 0.49815 → **0.58365**
- This value = original_height + wheel_radius_compensation
- Result: ✅ Robot sits at correct ground clearance

#### Issue 3: Caster Ground Penetration
**Symptoms**: Caster wheels sinking into ground or floating inside robot frame  
**Root Cause**: Complex mesh geometry with coordinate frame mismatches  
**Debugging Process** (15+ iterations):
- Initially tried adjusting visual offsets in rotated frames (failed)
- Key insight: Separate visual (mesh) from collision (primitive) geometry
- Iteratively tuned sphere radius: 0.03 → 0.032 → 0.034 → 0.035 → 0.036 → 0.0365 → **0.0372**
**Final Fix**:
- Caster collision: sphere radius=0.0372 at xyz="0 0 0"
- Caster visual: kept original STL mesh at xyz="0 0 0"
- Caster joints: maintained at xyz="0.26586 ±0.085525 -0.53206"
- Result: ✅ Casters positioned correctly under frame, no ground penetration

#### Issue 4: Inverted Teleop Controls
**Symptoms**: i/comma moved robot left/right instead of forward/back, j/l moved forward/back instead of turning  
**Root Cause**: Wheel radius multipliers not set for Gazebo differential drive kinematics  
**Fix Applied**:
- Added to `gz_controllers.yaml`:
  ```yaml
  left_wheel_radius_multiplier: -1.0
  right_wheel_radius_multiplier: 1.0
  ```
- Note: Real hardware uses different multipliers in `controllers.yaml`
- Result: ✅ All teleop directions correct (i=forward, ,=back, j=left turn, l=right turn)

### Key Parameters for Future Reference:

```yaml
# Critical URDF geometry values
base_footprint_joint z: 0.58365
wheel_collision: cylinder radius=0.0855 length=0.033
caster_collision: sphere radius=0.0372

# Friction coefficients
drive_wheels: mu1=1.0, mu2=1.0, kp=10000.0, kd=1.0
casters: mu1=0.0, mu2=0.0 (frictionless)

# Wheel multipliers (Gazebo-specific)
left_wheel_radius_multiplier: -1.0
right_wheel_radius_multiplier: 1.0
wheel_separation_multiplier: 1.0

# These differ from real hardware controllers.yaml!
```

### Launch Commands:

**Start Gazebo Simulation**:
```bash
ros2 launch yaseen_differential_robot gz_sim.launch.py
```

**Keyboard Teleoperation**:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel_unstamped
```

### Verification Commands:
```bash
# Check Gazebo topics
gz topic -l

# Check ROS topics
ros2 topic list

# Monitor joint states
ros2 topic echo /joint_states

# Check controller status
ros2 control list_controllers

# Test motion
ros2 topic pub /yaseen_diffbot_controller/cmd_vel_unstamped geometry_msgs/msg/Twist "{linear: {x: 0.5}}" --rate 10
```

### Git Repository:

All Gazebo simulation work committed to branch **gazebo_gz_sim**:
```bash
git branch: gazebo_gz_sim
git remote: https://github.com/YaseenRehman786/odrive_ros2_robot.git
Latest commits:
- 4a69912: Add backup of robot_description.xacro
- 69881bb: Tune Gazebo caster contact and diff-drive control mapping
```

**Files tracked**:
- `config/gz_controllers.yaml`
- `launch/gz_sim.launch.py`
- `urdf/robot_description.xacro`
- `urdf/robot_gazebo.xacro`
- `urdf/robot_gazebo.urdf.xacro`
- `urdf/robot_description.xacro.backup`

---

## Next Steps (In Priority Order)

### ✅ Completed - Teleoperation Testing:
1. **Keyboard Teleoperation** ✅
   - Installed: `sudo apt install ros-humble-teleop-twist-keyboard`
   - Working command: `ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel_unstamped`
   - Verified wheels spin in joint_state feedback

2. **RViz Visualization** ✅
   - Fixed TF tree by changing `base_frame_id: base_footprint` in controllers.yaml
   - Robot model displays correctly
   - TF transforms update in real-time during motion
   - Odometry trail visible

3. **Gazebo Simulation** ✅
   - Robot spawns correctly at ground level
   - Physics contact stable (no slipping, sinking, or penetration)
   - Differential drive controller functional
   - All teleop directions correct
   - Code committed to gazebo_gz_sim branch

### Phase 4: Real Hardware Integration
1. **Setup CAN interface** on Jetson:
   ```bash
   sudo ip link set can0 type can bitrate 1000000
   sudo ip link set up can0
   ```

2. **Configure ODrives** (node_id 0 and 1):
   - Follow: https://docs.odriverobotics.com/v/latest/guides/getting-started.html
   - Calibrate motors
   - Set CAN node IDs

3. **Test with real hardware**:
   ```bash
   ros2 launch yaseen_differential_robot control.launch.py use_mock_hardware:=false
   ```

### Phase 5: Sensor Integration
1. RPLidar integration
2. Intel RealSense integration
3. Static transforms for sensor frames

### Phase 6: Autonomous Navigation
1. Nav2 stack setup
2. SLAM (slam_toolbox)
3. Path planning & obstacle avoidance

---

## Important ODrive References

- Main repo: https://github.com/odriverobotics/ros_odrive
- Botwheel Explorer example: `/home/ysn786/ws_odrive_robot/src/ros_odrive/odrive_botwheel_explorer/`
- ODrive docs: https://docs.odriverobotics.com/v/latest/guides/ros-package.html

---

## Common Build/Debug Commands

```bash
# Clean rebuild
cd ~/ws_odrive_robot
rm -rf build/yaseen_differential_robot install/yaseen_differential_robot log
colcon build --packages-select yaseen_differential_robot --symlink-install
source install/setup.bash

# Validate xacro before building
xacro src/yaseen_differential_robot/urdf/robot.urdf.xacro use_mock_hardware:=true > /tmp/check.urdf
grep -n "<ros2_control" /tmp/check.urdf

# Check for errors
get_errors

# List all ROS2 packages
ros2 pkg list | grep yaseen

# Kill all ROS2 nodes
pkill -9 ros
```

---

## Key Design Decisions

1. **Macro-based xacro structure** - Allows clean includes for ros2_control, Gazebo, etc.
2. **Runtime mock/real switching** - No file edits needed, just launch argument
3. **ODrive-aligned interface** - Matches odrive_botwheel_explorer pattern exactly
4. **Explicit interface definitions** - Works with both mock and real hardware

---

## March 10, 2026 Update ✅

### Real Hardware Direction/Steering Final Fix

- Symptom after earlier ROS tuning: linear and angular behavior in RViz did not match real robot behavior consistently.
- Root cause: ODrive axis/node mapping on the real robot was flipped.
- Final fix applied on hardware: node IDs were swapped manually in ODrive tool.
- Result: ✅ Real robot now matches RViz and Gazebo behavior for all teleop keys:
  - `i` = forward
  - `,` = backward
  - `j` = left turn
  - `l` = right turn

### Important Note

- This was a hardware-side ODrive configuration issue, not a Gazebo physics issue.
- Gazebo configuration remains valid and unchanged.

---

## March 14, 2026 Update ✅

### Updated CAD / Mesh Merge Into Existing Robot Description

- A new SolidWorks-exported URDF (`Robot_Assembly_Clean_Design.urdf`) and updated mesh set were introduced.
- Goal: merge the new mechanical design into the existing ROS / Gazebo stack without breaking controller compatibility, launch files, TF naming, or previously tuned simulation behavior.
- Approach used:
  - Preserved all existing link and joint names used by the stack (`base_link`, `wheel_left_joint`, `wheel_right_joint`, `caster_left_wheel_link`, `caster_wheel_right_link`, `lidar_link`, etc.)
  - Updated visual mesh references and inertial properties to match the new CAD export
  - Kept the proven collision primitives / Gazebo tuning intact (box base collision, cylinder wheel collisions, sphere caster collisions)
  - Preserved all controller-facing and ros2_control-facing naming for compatibility

#### Key URDF Merge Details

- Updated `robot_description.xacro` to use the refreshed base / wheel / caster / lidar mesh geometry
- Integrated new caster wheel mesh names:
  - `caster_left_link.STL`
  - `caster_right_link.STL`
- Updated `base_link`, wheel, caster, and lidar inertial values from the new CAD export
- Updated `lidar_joint` mount position to match the revised design
- After validation, mesh paths were normalized back to the main `meshes/` directory

#### Important Compatibility Decision

- The robot architecture did **not** change conceptually, so a completely new robot description file was avoided.
- Instead, the current `robot_description.xacro` remained the canonical source of truth and was carefully evolved in place.

### Caster Contact Re-Tuning After New Mesh Merge

- After the URDF/mesh merge, caster contact needed a final minor correction in Gazebo.
- Symptom: caster wheels were either slightly underground or floating by about 1–2 mm.
- Final stable caster collision sphere radius was tuned to:
  - `0.0382`

This preserved the previously working drive wheel contact behavior while eliminating the remaining caster penetration / floating issue.

### Gazebo LiDAR Simulation Integration

- A 2D LiDAR sensor was added to the Gazebo robot model on `lidar_link`
- Topic standardized to:
  - `/scan`
- Purposefully kept generic so future LiDAR swaps will not require downstream SLAM / Nav2 changes

#### Files Involved

- `urdf/robot_gazebo.xacro`
- `launch/gz_sim.launch.py`
- `worlds/empty.sdf`

#### Key Gazebo Sensor Decisions

- World sensor systems were explicitly loaded in `empty.sdf`
- LiDAR sensor configuration was updated to a Gazebo Fortress-compatible format
- The robot's `lidar_joint` was preserved so the sensor link remains intact in simulation

### Critical LiDAR Breakthrough

The major issue was **not** just sensor syntax — it was the robot spawn path.

#### What failed

- Spawning the robot directly from `robot_description` via topic into Gazebo
- In that path, the robot and controllers spawned, but the LiDAR transport topics never became active

#### What worked

- Generate temporary robot files at launch:
  - `/tmp/yaseen_full.urdf`
  - `/tmp/yaseen_full.sdf`
- Convert URDF → SDF before spawning
- Spawn the robot into Gazebo from the generated SDF file using `ros_gz_sim create -file ...`

This was the decisive fix that caused Gazebo to publish:

- `/scan`
- `/scan/points`

and allowed ROS 2 to receive valid `sensor_msgs/msg/LaserScan` messages on `/scan`.

### Final Working LiDAR State

- Gazebo publishes scan topics successfully
- ROS 2 bridge exposes `/scan`
- `ros2 topic echo /scan --once --qos-reliability best_effort` returns valid scan data
- Scan ranges show real obstacle returns from the simulation environment

### Notes for Future Continuation

- The current Gazebo LiDAR setup is generic and not tied specifically to RPLidar branding
- This makes it easier to reuse the same downstream stack with either:
  - simulated LiDAR in Gazebo, or
  - a real hardware LiDAR driver publishing to `/scan`
- Next recommended cleanup item: normalize scan `frame_id` to `lidar_link` if needed before SLAM / Nav2 tuning

---

## Status Summary

✅ **Working**:
- URDF visualization in RViz
- TF tree (odom → base_footprint → base_link → wheels/casters/lidar)
- ROS2 control with mock hardware
- Differential drive controller active
- Joint state feedback
- Odometry publishing
- Mock/real hardware runtime switching
- **Keyboard teleoperation working in RViz**
- **Robot motion validated (wheels spin, odom updates, TF broadcasts)**
- **Gazebo Fortress simulation fully functional**
- **Physics tuned (friction, contact, geometry)**
- **Teleop controls correct in simulation**
- **Real hardware direction and steering now fully aligned with RViz**
- **ODrive node ID mapping corrected on hardware**
- **Updated CAD / mesh design merged into existing robot description**
- **Gazebo caster contact re-tuned after CAD merge**
- **Gazebo LiDAR simulation publishing valid `/scan` data**
- **Gazebo robot now spawned from generated SDF for reliable sensor support**

🔄 **Next**:
- RViz LiDAR visualization / frame cleanup
- SLAM Toolbox in simulation
- Camera / additional sensor plugins in Gazebo
- Real ODrive + real LiDAR integration
- Nav2 integration

---

## Contact Info for Continuity

If continuing in a new chat, provide this entire file and mention:
- "Continuing from SESSION_LOG.md in yaseen_differential_robot project"
- Current phase completed: Phase 1, 2 & 3
- Ready for: RViz LiDAR validation, SLAM Toolbox in simulation, then Nav2 pipeline
- All files are in: `/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/`
- Gazebo branch: `gazebo_gz_sim` at https://github.com/YaseenRehman786/odrive_ros2_robot.git

**Last verified working**: March 14, 2026

---

## March 15, 2026 — Gazebo Fortress ↔ Harmonic Switching Playbook

This section captures the exact lessons learned while testing Harmonic migration in a separate branch and then returning to Fortress.

### Key conclusions

- For **ROS 2 Humble + Ubuntu 22.04**, Fortress is the native/default pairing and easiest to keep stable.
- Harmonic works, but requires stricter package/environment handling.
- Biggest risk is **environment contamination** from previously sourced overlay workspaces.

### A) Fortress restore (recommended default for this project)

#### 1) Package set to use

```bash
sudo apt remove -y 'ros-humble-ros-gzharmonic*'
sudo apt install -y \
  ros-humble-ros-gz \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-gz-ros2-control \
  ros-humble-gz-ros2-control-demos
```

#### 2) Common launch usage on Fortress

- `ign gazebo` / `ign sdf -p` launch flow is valid on this branch.
- Launch arg must be `world:=...` (not `worlds:=...`).

#### 3) Critical gotcha (actually happened)

Even after package rollback, simulation crashed because `gz_ros2_control` was still being loaded from `~/gz_ros2_control_ws/install/...` instead of apt (`/opt/ros/humble`).

Root cause: `ws_odrive_robot/install/setup.bash` had stale underlay references baked in during previous builds.

#### 4) Fast workaround

Use local setup instead of chained setup:

```bash
source /opt/ros/humble/setup.bash
source ~/ws_odrive_robot/install/local_setup.bash
```

#### 5) Permanent cleanup

Rebuild from a clean shell:

```bash
env -i HOME="$HOME" USER="$USER" TERM="$TERM" PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" bash --noprofile --norc
source /opt/ros/humble/setup.bash
cd ~/ws_odrive_robot
rm -rf build install log
colcon build --symlink-install
```

#### 6) Validation checks

```bash
ros2 pkg prefix gz_ros2_control
# expected: /opt/ros/humble

env | grep -E 'gz_ros2_control_ws|GZ_VERSION' || true
# expected: no output
```

### B) Harmonic migration (if needed later)

Use only on migration branch / isolated workflow.

#### 1) Harmonic ROS bridge packages on Humble

```bash
sudo apt remove -y 'ros-humble-ros-gz*' 'ros-humble-ros-ign*'
sudo apt install -y \
  ros-humble-ros-gzharmonic \
  ros-humble-ros-gzharmonic-sim \
  ros-humble-ros-gzharmonic-bridge \
  ros-humble-ros-gzharmonic-image \
  ros-humble-ros-gzharmonic-interfaces
```

#### 2) `gz_ros2_control` requirement for Humble + Harmonic

Must build `gz_ros2_control` from source with:

```bash
export GZ_VERSION=harmonic
```

If this is missing during build, library may compile in Fortress mode and fail at runtime.

#### 3) Harmonic plugin path requirement

When using source-built control plugin, `GZ_SIM_SYSTEM_PLUGIN_PATH` must include both:

- `~/gz_ros2_control_ws/install/gz_ros2_control/lib`
- `/opt/ros/humble/lib`

#### 4) Harmonic failure signatures observed

- `Unknown message type [8]/[9]`: wrong bridge package line (non-harmonic)
- `Could not find shared library [libgz_ros2_control-system.so]`: missing plugin path
- `symbol [GzPluginHook] missing` / plugin export mismatch: wrong `gz_ros2_control` build mode

### C) Recommended branch strategy going forward

- Keep Fortress as stable default branch for daily dev.
- Keep Harmonic work isolated in migration branch.
- Never build/launch one branch while sourcing overlays from the other stack.

### D) Startup-shell recommendation

- Avoid auto-sourcing many workspaces in `.bashrc` if possible.
- Prefer explicit per-terminal sourcing for the target branch stack.

**Last verified migration/restoration notes added**: March 15, 2026

---

## March 19-20, 2026 — Real Robot LiDAR + SLAM + Joystick Integration

### Summary

Successfully brought up RPLIDAR A2M8 on physical Jetson robot, mapped environment with SLAM Toolbox, and integrated PS4 joystick controller with parametrized launch for seamless sim/real switching.

### A) Real LiDAR Hardware Bring-Up (March 19)

**Hardware Identification**
- Device: RPLIDAR A2M8 (CP2102 USB bridge)
- Serial Port: `/dev/rplidar` (via udev rule)
- Baudrate: 115200
- Scan Mode: **Standard** (12m max range, 10 Hz, 2K points)
- Frame ID: `lidar_link`

**Commissioning Steps**
1. Connected 5V power supply (1A minimum) with shared ground.
2. Ran device discovery:
   ```bash
   ls -l /dev/serial/by-id/
   ```
3. Installed rplidar_ros ROS2 package (cloned into workspace).
4. Set permissions:
   ```bash
   sudo usermod -a -G dialout $USER
   cd ~/ws_odrive_robot/src/rplidar_ros && source scripts/create_udev_rules.sh
   ```
5. Identified scan mode by test-launching A1/A2M8/A2M12/A3 variants (A2M8 matched).

**Key Configuration**
- [src/yaseen_differential_robot/launch/rp_lidar_a2m8.launch.py](src/yaseen_differential_robot/launch/rp_lidar_a2m8.launch.py)
  - `serial_port: /dev/rplidar`
  - `frame_id: lidar_link`
  - `scan_mode: Standard`
  - `inverted: false` (after fixing URDF yaw transform)

**Frame Alignment Fix**
- Initial Left/Right+Front/Back reversal in RViz.
- Root cause: LiDAR mounted backwards relative to base_link.
- **Solution**: In [src/yaseen_differential_robot/urdf/robot_description.xacro](src/yaseen_differential_robot/urdf/robot_description.xacro#L322-L331):
  - Changed `lidar_joint` rpy from `0 0 0` to `0 0 3.14159265359` (180° yaw).
  - Test: hand on right → RViz right; hand forward → RViz forward ✓

### B) SLAM Mapping (March 19-20)

**Successful Mapping Run**
```bash
# Terminal 1: Real robot bringup on Jetson
ros2 launch yaseen_differential_robot control.launch.py use_mock_hardware:=false use_lidar:=true use_rviz:=false

# Terminal 2: Desktop SLAM (used vendor defaults after temp file missing)
ros2 launch slam_toolbox online_async_launch.py slam_params_file:=/tmp/slam_mapping.yaml

# Terminal 3: RViz (set Fixed Frame to 'map', add /map + /scan displays)
rviz2
```

**Outcome**
- Map saved: `/home/ysn786/ws_odrive_robot/maps/my_map_20260319_2336.yaml/.pgm`
- Size: 286 × 205 cells @ 0.05 m/pixel
- Health: Valid for Nav2 localization/navigation

**Minor Observations**
- One TF extrapolation warning (clock sync between Jetson/desktop slightly off).
- Used vendor defaults for scan limits (nominally 0–25m, actual 0.2–12m); no critical blocking.

### C) PS4 Joystick Integration (March 20)

**Working Joystick Setup**
- Package: `joy` + `teleop_twist_joy`
- Config: [src/yaseen_differential_robot/config/joystick.yaml](src/yaseen_differential_robot/config/joystick.yaml)
  - Fixed YAML syntax: `ros_parameters:` → `ros__parameters:` (double underscore required).
- Launch: [src/yaseen_differential_robot/launch/joystick.launch.py](src/yaseen_differential_robot/launch/joystick.launch.py)

**Real/Sim Launcher Flexibility**
- Real robot default: publishes to `/yaseen_diffbot_controller/cmd_vel_unstamped`
- Gazebo sim: needs to target `/cmd_vel` (or controller-specific topic).

**Parametrized Launch Solution**
```python
# In joystick.launch.py
from launch import LaunchDescription, LaunchConfiguration

cmd_vel_topic = LaunchConfiguration('cmd_vel_topic', default='/yaseen_diffbot_controller/cmd_vel_unstamped')
# Inside teleop_node: remappings=[('/cmd_vel', cmd_vel_topic)]
```

**Usage**
- Real robot: `ros2 launch yaseen_differential_robot joystick.launch.py` (uses unstamped default).
- Gazebo: `ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/cmd_vel`.
- Custom: `ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/any_topic`.

### D) Next Steps (Immediate)

1. **Nav2 full stack integration** (in progress):
   - Copy/customize `/opt/ros/humble/share/nav2_bringup/params/nav2_params.yaml` → your package.
   - Set AMCL/controller/planner frame/topic bindings.
   - Test navigation with 2D goals in RViz.

2. **Clock sync tuning** (if TF warnings persist):
   - Consider `chrony` or NTP sync between Jetson and desktop.

3. **Joystick + Nav2 fallback**:
   - Current: joystick works on real (full manual teleop).
   - Future: integrate emergency stop / hybrid nav mode.

### E) Hardware/Software Inventory (As of March 20)

**Physical**
- Jetson Orin Nano Super
- RPLIDAR A2M8 (12m, 10 Hz)
- 2× ODrive S1 motor controllers
- 2× ODrive botwheels
- 2× caster wheels
- PS4 DualShock controller

**ROS2 Stack**
- Humble
- Gazebo Fortress (stable branch)
- SLAM Toolbox (mapping)
- Nav2 (bringup pending)
- ros2_control / diff_drive_controller
- rplidar_ros (A2M8 driver)
- joy / teleop_twist_joy (joystick)

**Saved Artifacts**
- Robot URDF/Xacro
- Gazebo worlds (empty, office, warehouse, hospital)
- SLAM map: `my_map_20260319_2336`
- Launch files parametrized for sim/real switching

**Last verified real hardware run**: March 20, 2026

---

## March 21–22, 2026 — Continuation Addendum (Merged)

### Key fixes completed
- Added Gazebo `/clock` ROS bridge in `gz_sim.launch.py` so sim-time nodes actually advance.
- Confirmed drivetrain motion after clock fix (odom updates + direct velocity motion works).
- Standardized command path to unstamped controller input:
  - controller input: `/yaseen_diffbot_controller/cmd_vel_unstamped`
  - joystick safety input: `/cmd_vel_joy` via `twist_mux`
- Found and resolved instability from multiple `twist_mux` instances.

### Nav2 / localization lessons captured
- If Nav2 shows active but immediately aborts, check localization state first.
- Do not run multiple localization sources simultaneously during navigation.
- In RViz, set `2D Pose Estimate` before dispatching goals.

### Current working launch order (Gazebo)
1. `ros2 launch yaseen_differential_robot gz_sim.launch.py world:=hospital.sdf use_sim_time:=true`
2. `ros2 launch slam_toolbox localization_launch.py slam_params_file:=/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/slam_localization.yaml use_sim_time:=true`
3. `ros2 launch nav2_bringup bringup_launch.py map:=/home/ysn786/ws_odrive_robot/maps/hopital/my_map_hospital20260321_0015.yaml use_sim_time:=true autostart:=true`
4. `ros2 run twist_mux twist_mux --ros-args --params-file /home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/config/twist_mux.yaml -r cmd_vel_out:=/yaseen_diffbot_controller/cmd_vel_unstamped`
5. `ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/cmd_vel_joy use_stamped:=false use_sim_time:=true`

### Map saving convention (new)
Each run saves to a new folder under `maps/<timestamp>/`:

```bash
stamp=$(date +%Y%m%d_%H%M)
session_dir="/home/ysn786/ws_odrive_robot/maps/${stamp}"
mkdir -p "$session_dir"
ros2 run nav2_map_server map_saver_cli -f "$session_dir/map"
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '$session_dir/posegraph'}"
```

### README status
README has been updated to reflect:
- clear section hierarchy (`1`, `2`, `3` as main titles)
- `3A` full Gazebo end-to-end flow
- `3B` full real-robot end-to-end flow
- automatic latest map/posegraph selection commands

