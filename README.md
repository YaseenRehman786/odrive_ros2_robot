------------------------------------------------------------------
# **Updating my Github Repo**  

**CHEAT SHEET**
```
**For main branch**
<workspace_branch> = main

**For my other branches**
<workspace_branch> = branch_name

**For ros_odrive:**  
<submodule_folder> = ros_odrive
<submodule_branch> = main

**For rplidar_ros:**  
<submodule_folder> = rplidar_ros
<submodule_branch> = ros2

```

**1. Update the Main Workspace Only**  
```bash
cd ~/ws_odrive_robot
git add .
git commit -m "Update view_robot_pkg"
git push origin <workspace_branch>
```


**2. Update a Submodule (ros_odrive or rplidar_ros)**  
If you make changes inside a submodule, you must commit there first, then "pin" the new version in the main workspace.  

_Step A - Commit inside the submodule:_
```bash
cd ~/ws_odrive_robot/src/<submodule_folder>
git add .
git commit -m "Update submodule: [Description]"
git push origin <submodule_branch>
```

_Step B - Update the workspace pointer:_
```bash
cd ~/ws_odrive_robot
git add src/<submodule_folder>
git commit -m "Bump <submodule_folder> submodule"
git push origin <workspace_branch>
```

**3. Sync Forked Submodules with Upstream**  
Use this to pull the latest official updates from ODrive or SLAMTEC into your own forks.  

_Step A - Pull official changes into your fork:_
```bash
cd ~/ws_odrive_robot/src/<submodule_folder>
git fetch upstream
git pull --rebase upstream <submodule_branch>
git push origin <submodule_branch>
```  
_Step B - Update the workspace pointer:_
```bash
cd ~/ws_odrive_robot
git add src/<submodule_folder>
git commit -m "Update/Sync <submodule_folder> from upstream"
git push origin <workspace_branch>
```

**4. Change BOTH Workspace and Submodule**  
Always commit the submodule first so the workspace can reference the new commit.  
_Step A - Commit the submodule first:_
```bash
cd ~/ws_odrive_robot/src/<submodule_folder>
git add .
git commit -m "Update submodule"
git push origin <submodule_branch>
```
_Step B - Commit workspace changes:_
```bash
cd ~/ws_odrive_robot
git add .
git commit -m "Update workspace + bump submodule"
git push origin <workspace_branch>
```

**5. Syncing when Local and Remote are both ahead**  
Use this if you made changes on GitHub (web) and your PC at the same time to avoid "merge bubbles."
```bash
cd ~/ws_odrive_robot
git add .
git commit -m "My local changes"
git pull --rebase origin <workspace_branch>
git push origin <workspace_branch>
```

**6. To clone and pull both the workspace repo (odrive_ros2_robot) and submodule (src/ros_odrive or src/rplidar_ros) on another device/computer**
```bash
git clone --recurse-submodules https://github.com/YaseenRehman786/odrive_ros2_robot.git
cd odrive_ros2_robot
```
If you forgot --recursive-submodules
```bash
git submodule update --init --recursive
```

**7. Pulling Updates on another machine (e.g., Jetson)**
```bash
cd ~/ws_odrive_robot
git pull origin <workspace_branch>
git submodule update --init --recursive
```

**8. Update rebotarm_ros2 (Custom Branch)**  
For arm package changes, work on `yaseen-arm-integration` branch only.
```bash
cd ~/ws_odrive_robot/src/rebotarm_ros2
git add .
git commit -m "Custom: [Description]"
# Changes stay local on your custom branch
```

**9. Pull Latest Arm Updates from Seeed (Upstream)**  
Merge official updates without losing your changes.
```bash
cd ~/ws_odrive_robot/src/rebotarm_ros2
git fetch upstream
git merge upstream/main
# Resolve any conflicts, then: git add . && git commit -m "Merged upstream"
```
