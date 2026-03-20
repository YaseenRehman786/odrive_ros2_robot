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

1. Running in RVIZ2 
  ```bash
  ros2 launch yaseen_differential_robot control.launch.py
  ```
a. running on real robot
```bash
ros2 launch yaseen_differential_robot control.launch.py use_mock_hardware:=false use_rviz:=false
```

  ```bash
  ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel_unstamped
  ```
2. Running in Gazebo
  ```bash
  ros2 launch yaseen_differential_robot gz_sim.launch.py
  ```
  ```bash
  ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel
  ```

------------------------------------------------------------------
**Updating my Github Repo**  

**1. Update the Main Workspace Only**  
```bash
cd ~/ws_odrive_robot
git add .
git commit -m "Update view_robot_pkg"
git push origin <set origin>
```
**For main branch**
"<set origin>" = main  
**For my other branchs**
"<set origin>" = branch_name


**2. Update a Submodule (ros_odrive or rplidar_ros)**  
If you make changes inside a submodule, you must commit there first, then "pin" the new version in the main workspace.  

_Step A - Commit inside the submodule:_
```bash
cd ~/ws_odrive_robot/src/<submodule_folder>
git add .
git commit -m "Update submodule: [Description]"
git push origin <set origin>
```  
**For ros_odrive:**  
<submodule_folder> = ros_odrive
<set origin> = origin main
**For rplidar_ros:**  
<submodule_folder> = rplidar_ros
<set origin> = origin ros2  

_Step B - Update the workspace pointer:_
```bash
cd ~/ws_odrive_robot
git add src/<submodule_folder>
git commit -m "Bump <submodule_name> submodule"
git push origin <set origin>
```
**For main branch**
<set origin> = main
**For my other branchs**
<set origin> = branch_name 


**3. Sync Forked Submodules with Upstream**  
Use this to pull the latest official updates from ODrive or SLAMTEC into your own forks.  

Step A - Pull official changes into your fork:
```bash
cd ~/ws_odrive_robot/src/<submodule_folder>
git fetch upstream
git pull --rebase upstream <branch_name>
git push origin <branch_name>
```  
Step B - Update the workspace pointer:
```bash
cd ~/ws_odrive_robot
git add src/<submodule_folder>
git commit -m "Update <submodule_name> from upstream"
git push origin lidar
```

**4. Change BOTH Workspace and Submodule**  
Always commit the submodule first so the workspace can reference the new commit.  
Step A - Submodule first:
```bash
cd ~/ws_odrive_robot/src/<submodule_folder>
git add .
git commit -m "Update submodule"
git push origin <branch_name>
```
Step B - Workspace second:
```bash
cd ~/ws_odrive_robot
git add .
git commit -m "Update workspace + bump submodule"
git push origin lidar
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


