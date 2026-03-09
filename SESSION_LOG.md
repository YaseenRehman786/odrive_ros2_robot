# ROS2 Differential Drive Robot Development Session Log
**Date**: March 8-9, 2026  
**Project**: yaseen_differential_robot - ODrive S1 Differential Drive Robot  
**ROS2 Version**: Humble  
**Status**: ✅ Phase 1, 2 & 3 Complete - Gazebo Simulation Working

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

🔄 **Next**:
- Sensor plugins in Gazebo (lidar, camera)
- Real ODrive hardware testing
- Nav2 integration

---

## Contact Info for Continuity

If continuing in a new chat, provide this entire file and mention:
- "Continuing from SESSION_LOG.md in yaseen_differential_robot project"
- Current phase completed: Phase 1, 2 & 3
- Ready for: Sensor integration in Gazebo or Real hardware testing
- All files are in: `/home/ysn786/ws_odrive_robot/src/yaseen_differential_robot/`
- Gazebo branch: `gazebo_gz_sim` at https://github.com/YaseenRehman786/odrive_ros2_robot.git

**Last verified working**: March 9, 2026
