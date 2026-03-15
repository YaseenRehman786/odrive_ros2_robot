# Gazebo Harmonic Migration Notes

This package has been migrated following the official guide:
- https://gazebosim.org/docs/harmonic/migration_from_ignition/

## Important compatibility note for ROS 2 Humble

According to the official Gazebo Harmonic ROS installation docs, ROS 2 Humble + Gazebo Harmonic is a non-default pairing.

- The standard `ros-humble-ros-gz*` packages are for Humble's default Gazebo pairing.
- For Harmonic on Humble, use the Harmonic-specific packages:
	- `ros-humble-ros-gzharmonic`
	- `ros-humble-ros-gzharmonic-sim`
	- `ros-humble-ros-gzharmonic-bridge`

If Gazebo Harmonic is installed but the standard `ros-humble-ros-gz*` packages are used, runtime issues such as spawn failures, transport errors, or `Unknown message type [...]` can occur.

## Official references used

- Harmonic migration guide:
	- https://gazebosim.org/docs/harmonic/migration_from_ignition/
- ROS / Gazebo compatibility and installation:
	- https://gazebosim.org/docs/harmonic/ros_installation/
- ROS 2 integration:
	- https://gazebosim.org/docs/harmonic/ros2_integration/
- `gz_ros2_control` docs + compatibility matrix:
	- https://control.ros.org/master/doc/gz_ros2_control/doc/index.html
	- https://github.com/ros-controls/gz_ros2_control/tree/humble

## What was migrated in this package

### CLI / tooling
- `ign gazebo` -> `gz sim`
- `ign sdf -p` -> `gz sdf -p`

### Environment variables
- `IGN_GAZEBO_RESOURCE_PATH` -> `GZ_SIM_RESOURCE_PATH`
- `IGN_GAZEBO_SYSTEM_PLUGIN_PATH` -> `GZ_SIM_SYSTEM_PLUGIN_PATH`

### SDF plugin names and namespaces
- `libignition-gazebo6-*-system.so` -> `gz-sim-*-system`
- `ignition::gazebo::systems::*` -> `gz::sim::systems::*`

### ROS integration
- Keep using `ros_gz_sim` and `ros_gz_bridge` (post-rename from `ros_ign`).

## Working migration procedure (Humble + Harmonic)

### 1) Install Harmonic-compatible ROS bridge packages

```bash
sudo apt remove -y 'ros-humble-ros-gz*' 'ros-humble-ros-ign*'
sudo apt install -y \
	ros-humble-ros-gzharmonic \
	ros-humble-ros-gzharmonic-sim \
	ros-humble-ros-gzharmonic-bridge \
	ros-humble-ros-gzharmonic-image \
	ros-humble-ros-gzharmonic-interfaces
```

### 2) Build `gz_ros2_control` from source for Harmonic

Humble + Harmonic needs source build for `gz_ros2_control` (per matrix).

```bash
mkdir -p ~/gz_ros2_control_ws/src
cd ~/gz_ros2_control_ws/src
git clone -b humble https://github.com/ros-controls/gz_ros2_control.git

cd ~/gz_ros2_control_ws
rm -rf build install log
source /opt/ros/humble/setup.bash
export GZ_VERSION=harmonic
rosdep install -r --from-paths src --ignore-src --rosdistro humble -y
colcon build --symlink-install
```

### 3) Source order for runtime

```bash
source /opt/ros/humble/setup.bash
export GZ_VERSION=harmonic
source ~/gz_ros2_control_ws/install/setup.bash
source ~/ws_odrive_robot/install/setup.bash
```

### 4) Plugin path requirement in launch

`gz_sim.launch.py` must include both paths in `GZ_SIM_SYSTEM_PLUGIN_PATH`:

- `/home/ysn786/gz_ros2_control_ws/install/gz_ros2_control/lib`
- `/opt/ros/humble/lib`

If only `/opt/ros/humble/lib` is set, Gazebo cannot find the source-built plugin.

## Common failure signatures and meaning

- `Unknown message type [8]` / `[9]` and create node timing out:
	- Usually wrong ROS Gazebo bridge packages (`ros-humble-ros-gz*` instead of `ros-humble-ros-gzharmonic*`).
- `Could not find shared library [libgz_ros2_control-system.so]`:
	- Plugin path not including overlay workspace lib directory.
- `Library ... does not export any plugins. The symbol [GzPluginHook] is missing`:
	- `gz_ros2_control` built in Fortress mode (missing `export GZ_VERSION=harmonic` during build).

## Current launch usage

Run any world with:

```bash
ros2 launch yaseen_differential_robot gz_sim.launch.py world:=empty.sdf
ros2 launch yaseen_differential_robot gz_sim.launch.py world:=office.sdf
ros2 launch yaseen_differential_robot gz_sim.launch.py world:=warehouse.sdf
ros2 launch yaseen_differential_robot gz_sim.launch.py world:=hospital.sdf
```

## Migration checklist for future edits

When adding or modifying sim files, keep these rules:

1. Use `gz` CLI only (`gz sim`, `gz sdf`).
2. Use `GZ_*` env vars only.
3. Use `gz-sim-*` plugin filenames in SDF.
4. Use `gz::sim::*` plugin namespaces in SDF/C++.
5. Prefer `ros_gz_*` packages, never `ros_ign_*`.
6. If copying examples from old posts, convert all `ign` references.

## Quick verification commands

```bash
# Check no legacy Ignition references remain in this package:
grep -RInE '\bign\b|Ignition|IGN_GAZEBO|ignition::gazebo|libignition-gazebo|ros_ign' src/yaseen_differential_robot

# Validate launch/world files quickly:
python3 -m py_compile src/yaseen_differential_robot/launch/gz_sim.launch.py

# Check Harmonic-specific ROS bridge packages:
dpkg -l | grep -E 'ros-humble-ros-gzharmonic|ros-humble-ros-gz\b|ros-humble-ros-ign' 

# Confirm gz_ros2_control was configured for Harmonic:
grep -E 'gz-sim8|ignition-gazebo6' ~/gz_ros2_control_ws/build/gz_ros2_control/CMakeCache.txt

# Confirm plugin exists in overlay:
find ~/gz_ros2_control_ws/install -name 'libgz_ros2_control-system.so'
```

Expected for Harmonic build:
- `CMakeCache.txt` shows `gz-sim8` (not `ignition-gazebo6`).
- Launch logs should not contain plugin load errors and should show controller spawners proceeding.

## Recommended branch strategy

- Keep Fortress as your stable/default branch for daily development.
- Keep Harmonic migration work isolated in a dedicated branch (e.g. `gz_ignition_migration`).
- Only merge Harmonic branch into mainline when:
	- launch is stable,
	- controller manager comes up reliably,
	- SLAM / Nav2 workflow is validated end-to-end.

## Notes from official migration guide

- Harmonic introduces broad tick-tocks (aliases/deprecations), but migration to Gazebo naming is strongly recommended.
- Some old forms may still run with warnings, but using `gz`/`GZ_` avoids ambiguity and future breakage.
- For long-term maintainability, treat all new code as Gazebo (`gz`) only.
