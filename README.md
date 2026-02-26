This repository will be for my autonomous robot project where I will be using a Jetson Orin Nano Super, Odrive S1 FOC controllers, Odrive Bothweel motors, Intel Realsense D435 camera, and RPLidar.

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
