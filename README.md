This repository will be for my autonomous robot project where I will be using a Jetson Orin Nano Super, Odrive S1 FOC controllers, Odrive Bothweel motors, Intel Realsense D435 camera, and RPLidar.

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

**Controlling Odrive and Motors**
**_APPROACH A -> odrive_node_**
1. Initialize CAN node
```bash
ros2 launch odrive_can example_launch.yaml
``` 
2. Request ODrive State (one for each motor, node id 0, node id 1)
```bash
ros2 service call /odrive_axis0/request_axis_state odrive_can/srv/AxisState "{axis_requested_state: 8}"
ros2 service call /odrive_axis1/request_axis_state odrive_can/srv/AxisState "{axis_requested_state: 8}"
```

**_APPROACH B -> odrive_ros2_control_**
