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
```

## Notes from official migration guide

- Harmonic introduces broad tick-tocks (aliases/deprecations), but migration to Gazebo naming is strongly recommended.
- Some old forms may still run with warnings, but using `gz`/`GZ_` avoids ambiguity and future breakage.
- For long-term maintainability, treat all new code as Gazebo (`gz`) only.
