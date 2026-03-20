------------------------------------------------------------------
**Updating my Github Repo**  

**1. Update the Main Workspace Only**  
```bash
cd ~/ws_odrive_robot
git add .
git commit -m "Update view_robot_pkg"
git push origin <branch_name>
```
**For main branch**  
"<branch_name>" = main  
**For my other branchs**  
<branch_name>" = branch_name


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


