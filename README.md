This repository will be for my autonomous robot project where I will be using a Jetson Orin Nano Super, Odrive S1 FOC controllers, Odrive Bothweel motors, Intel Realsense D435 camera, and RPLidar.

------------------------------------------------------------------
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

**Controlling Odrive and Motors**  (https://docs.odriverobotics.com/v/latest/guides/ros-package.html)

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


------------------------------------------------------------------
**_APPROACH B -> odrive_ros2_control_ (my implementation)**

1. Running in RVIZ2 or on real robot  
  a.
  ```bash
  ros2 launch yaseen_differential_robot control.launch.py
  ```
  b. 
  ```bash
  ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel_unstamped
  ```
2. Running in Gazebo  
  a.
  ```bash
  ros2 launch yaseen_differential_robot gz_sim.launch.py
  ```
  b. 
  ```bash
  run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel
  ```

------------------------------------------------------------------
**Updating Github Repo**  
I have two git worlds:  
**1. I make changes to odrive_ros2_robot (my main repo) -> commit changes in workspace repo**
```bash
cd ~/ws_odrive_robot
git add .
git commit -m "Update view_robot_pkg"
git push origin main
```

**2. I make changes to ros_odrive (a submodule, its own repo, my fork) -> commit changes inside submodule first, then "pin" it in workspace**

  Step A - Commit inside the submodule
```bash
cd ~/ws_odrive_robot/src/ros_odrive
git add .
git commit -m "My ros_odrive changes"
git push origin main
```

  Step B - Tell your workspace repo the submodule moved to a new commit:
```bash
cd ~/ws_odrive_robot
git add src/ros_odrive
git commit -m "Bump ros_odrive submodule"
git push origin main
```

**3. Official odriverobotics update their repo and I want the updates**

  Step A - go inside the submodule (pull official changes, keeps my edits, updates my fork)
```bash
cd ~/ws_odrive_robot/src/ros_odrive
git fetch upstream
git pull --rebase upstream main
git push origin main
```
  Step B - update workspace pointer
```bash
cd ~/ws_odrive_robot
git add src/ros_odrive
git commit -m "Update ros_odrive from upstream"
git push origin main
```

**4. I change BOTH packages inside my main workspace AND ros_odrive inside my fork**

  Step A - Commit ros_odrive first:
```bash
cd ~/ws_odrive_robot/src/ros_odrive
git add .
git commit -m "Update ros_odrive"
git push origin main
```

  Step B - Commit workspace changes:
```bash
cd ~/ws_odrive_robot
git add .
git commit -m "Update workspace + bump submodule"
git push origin main
```

**5. I make changes on my actual github repo, but also make changes to files on my PC, both repo and github are ahead of eachother**

  Step A - Commit my local changes FIRST
```bash
cd ~/ws_odrive_robot
git add .
git commit -m "My local changes"
```

  Step B - Pull my report changes safely (temporarily removes my local commit, download github changes, re-applies my commits ontop)
```bash
git pull --rebase origin main
```

  Step C - 
```bash
git push origin main
```
**6. To clone and pull both the workspace repo (odrive_ros2_robot) and submodule (src/ros_odrive) on another device/computer**
```bash
git clone --recurse-submodules https://github.com/YaseenRehman786/odrive_ros2_robot.git
cd odrive_ros2_robot
```
If you forgot --recursive-submodules
```bash
git submodule update --init --recursive
```

Pull updates later on that machine
```bash
git pull
git submodule update --init --recursive
```


