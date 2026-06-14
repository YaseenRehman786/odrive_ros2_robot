# New Computer Setup

This file is for rebuilding the old robotics computer on a fresh Ubuntu
22.04 machine. It was written from the installed packages and workspace state
on the old computer, not from guesses.

## How To Use This File

1. Install **Ubuntu 22.04 LTS** on the new computer.
2. Open this file on the new computer.
3. Copy the full terminal block under **Main Install**.
4. Paste it into a terminal and let it finish.
5. Restart the computer.
6. Open a new terminal and start development:

```bash
cd ~/ws_odrive_robot
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --symlink-install
```

After the first successful build, normal development can start with:

```bash
cd ~/ws_odrive_robot
source install/setup.bash
```

If you also need Jetson/CUDA development tools, run the **NVIDIA CUDA /
Jetson Tooling** section after installing NVIDIA SDK Manager or the local
NVIDIA CUDA repo `.deb` files.

The old computer was:

- Ubuntu 22.04.5 LTS / Jammy
- ROS 2 Humble
- Gazebo Harmonic and Ignition Fortress
- NVIDIA driver packages, CUDA 12.6, Jetson/L4T cross-development packages
- Intel RealSense packages
- ODrive tools
- RPLidar tools
- TurtleBot, Nav2, MoveIt, ros2_control, ros_gz, and related ROS packages

## Main Install

On the new computer, install Ubuntu 22.04 first. Then copy and paste this
whole block into a terminal:

```bash
set -e

echo "=== Base system packages ==="
sudo apt update
sudo apt install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  software-properties-common \
  wget

echo "=== Apt repositories ==="
sudo mkdir -p /etc/apt/keyrings /usr/share/keyrings

# ROS 2 Humble
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list >/dev/null

# Gazebo / OSRF
sudo curl -sSL https://packages.osrfoundation.org/gazebo.gpg \
  -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable jammy main" \
  | sudo tee /etc/apt/sources.list.d/gazebo-stable.list >/dev/null

# Intel RealSense
curl -sSf https://librealsense.intel.com/Debian/librealsense.pgp \
  | sudo tee /etc/apt/keyrings/librealsenseai.gpg >/dev/null
echo "deb [signed-by=/etc/apt/keyrings/librealsenseai.gpg] https://librealsense.realsenseai.com/Debian/apt-repo jammy main" \
  | sudo tee /etc/apt/sources.list.d/librealsense.list >/dev/null

# Google Chrome
curl -sSL https://dl.google.com/linux/linux_signing_key.pub \
  | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] https://dl.google.com/linux/chrome/deb/ stable main" \
  | sudo tee /etc/apt/sources.list.d/google-chrome.list >/dev/null

# Slack
curl -sSL https://packagecloud.io/slacktechnologies/slack/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/slack.gpg
echo "deb [signed-by=/usr/share/keyrings/slack.gpg] https://packagecloud.io/slacktechnologies/slack/debian/ jessie main" \
  | sudo tee /etc/apt/sources.list.d/slack.list >/dev/null

sudo apt update

echo "=== Ubuntu, robotics, ROS, simulation, hardware, and desktop packages ==="
sudo apt install -y \
  abootimg \
  binfmt-support \
  binutils \
  bison \
  bsdutils \
  btop \
  build-essential \
  can-utils \
  chrony \
  clang-tidy \
  cmake \
  conky-all \
  cpio \
  cpp \
  dash \
  device-tree-compiler \
  dfu-util \
  diffutils \
  dosfstools \
  efibootmgr \
  evtest \
  fancontrol \
  file \
  findutils \
  flex \
  fonts-indic \
  g++ \
  g++-aarch64-linux-gnu \
  gcc-aarch64-linux-gnu \
  gcm \
  gdisk \
  gedit \
  git \
  google-chrome-stable \
  grep \
  gzip \
  hostname \
  hyphen-en-ca \
  hyphen-en-us \
  ignition-fortress \
  iproute2 \
  iputils-ping \
  joystick \
  jstest-gtk \
  language-pack-en \
  language-pack-en-base \
  language-pack-gnome-en \
  language-pack-gnome-en-base \
  lbzip2 \
  libasio-dev \
  libfuse2 \
  libncurses-dev \
  librealsense2-dbg \
  librealsense2-dev \
  librealsense2-dkms \
  librealsense2-utils \
  libreoffice-help-common \
  libreoffice-help-en-us \
  libxml2-utils \
  linux-generic-hwe-22.04 \
  lm-sensors \
  locales \
  lsb-release \
  lz4 \
  mangohud \
  mesa-utils \
  mokutil \
  mythes-en-us \
  netcat \
  netcat-openbsd \
  nfs-kernel-server \
  nvidia-driver-535 \
  nvidia-prime \
  openssl \
  os-prober \
  p7zip-full \
  parted \
  psensor \
  python-is-python3 \
  python3-colcon-common-extensions \
  python3-pip \
  python3-rosdep \
  python3-tqdm \
  python3-vcstool \
  python3-yaml \
  qemu-user-static \
  ros-humble-ament-cmake \
  ros-humble-ament-cmake-core \
  ros-humble-control-msgs \
  ros-humble-desktop \
  ros-humble-gz-ros2-control \
  ros-humble-gz-ros2-control-demos \
  ros-humble-image-transport-plugins \
  ros-humble-joint-state-publisher-gui \
  ros-humble-joy \
  ros-humble-launch-pytest \
  ros-humble-moveit \
  ros-humble-moveit-configs-utils \
  ros-humble-nav2-bringup \
  ros-humble-nav2-map-server \
  ros-humble-navigation2 \
  ros-humble-pinocchio \
  ros-humble-pluginlib \
  ros-humble-realsense2-camera \
  ros-humble-realsense2-camera-msgs \
  ros-humble-realsense2-description \
  ros-humble-rmw-cyclonedds-cpp \
  ros-humble-robot-state-publisher \
  ros-humble-ros-base \
  ros-humble-ros-gz \
  ros-humble-ros-gz-bridge \
  ros-humble-ros-gz-sim \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-ros2controlcli \
  ros-humble-rplidar-ros \
  ros-humble-rqt-image-view \
  ros-humble-rviz2 \
  ros-humble-slam-toolbox \
  ros-humble-teleop-twist-joy \
  ros-humble-teleop-twist-keyboard \
  ros-humble-tf-transformations \
  ros-humble-tf2-tools \
  ros-humble-trajectory-msgs \
  ros-humble-turtle-nest \
  ros-humble-turtle-tf2-cpp \
  ros-humble-turtle-tf2-py \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-applications \
  ros-humble-turtlebot3-aruco-tracker \
  ros-humble-turtlebot3-automatic-parking \
  ros-humble-turtlebot3-automatic-parking-vision \
  ros-humble-turtlebot3-autorace \
  ros-humble-turtlebot3-bringup \
  ros-humble-turtlebot3-cartographer \
  ros-humble-turtlebot3-description \
  ros-humble-turtlebot3-example \
  ros-humble-turtlebot3-fake-node \
  ros-humble-turtlebot3-follower \
  ros-humble-turtlebot3-home-service-challenge \
  ros-humble-turtlebot3-manipulation \
  ros-humble-turtlebot3-msgs \
  ros-humble-turtlebot3-navigation2 \
  ros-humble-turtlebot3-node \
  ros-humble-turtlebot3-panorama \
  ros-humble-turtlebot3-teleop \
  ros-humble-turtlebot3-yolo-object-detection \
  ros-humble-turtlebot4-base \
  ros-humble-turtlebot4-bringup \
  ros-humble-turtlebot4-description \
  ros-humble-turtlebot4-desktop \
  ros-humble-turtlebot4-diagnostics \
  ros-humble-turtlebot4-msgs \
  ros-humble-turtlebot4-navigation \
  ros-humble-turtlebot4-node \
  ros-humble-turtlebot4-python-tutorials \
  ros-humble-turtlebot4-robot \
  ros-humble-turtlebot4-setup \
  ros-humble-turtlebot4-tests \
  ros-humble-turtlebot4-tutorials \
  ros-humble-turtlebot4-viz \
  ros-humble-turtlesim \
  ros-humble-twist-mux \
  ros-humble-twist-stamper \
  ros-humble-xacro \
  rsync \
  slack-desktop \
  sshpass \
  terminator \
  thunderbird-locale-en \
  thunderbird-locale-en-us \
  ubuntu-desktop \
  ubuntu-desktop-minimal \
  ubuntu-minimal \
  ubuntu-restricted-addons \
  ubuntu-standard \
  ubuntu-wallpapers \
  ufw \
  usbutils \
  uuid-runtime \
  v4l-utils \
  whois \
  xmlstarlet \
  xxd \
  zlib1g \
  zstd

echo "=== Gazebo Harmonic ==="
sudo apt install -y gz-harmonic

echo "=== Snap desktop apps from old computer ==="
sudo snap install code --classic
sudo snap install discord
sudo snap install firefox
sudo snap install gitkraken
sudo snap install vlc

echo "=== Python packages from old computer ==="
python3 -m pip install --user --upgrade pip
python3 -m pip install --user \
  boto3==1.35.65 \
  botocore==1.35.65 \
  dynamixel-easy-sdk==4.0.3 \
  dynamixel-sdk==4.0.3 \
  exceptiongroup==1.3.1 \
  filetype==1.2.0 \
  fire==0.7.0 \
  fsspec==2024.10.0 \
  GitPython==3.1.43 \
  grpcio==1.68.0 \
  huggingface-hub==0.24.7 \
  ipython==8.38.0 \
  jedi==0.19.2 \
  Jinja2==3.1.4 \
  jmespath==1.0.1 \
  Markdown==3.7 \
  MarkupSafe==3.0.2 \
  matplotlib-inline==0.2.1 \
  motorbridge==0.4.1 \
  multidict==6.7.1 \
  networkx==3.4.2 \
  numpy==1.26.4 \
  nvidia-cublas-cu12==12.4.5.8 \
  nvidia-cuda-cupti-cu12==12.4.127 \
  nvidia-cuda-nvrtc-cu12==12.4.127 \
  nvidia-cuda-runtime-cu12==12.4.127 \
  nvidia-cudnn-cu12==9.1.0.70 \
  nvidia-cufft-cu12==11.2.1.3 \
  nvidia-curand-cu12==10.3.5.147 \
  nvidia-cusolver-cu12==11.6.1.9 \
  nvidia-cusparse-cu12==12.3.1.170 \
  nvidia-nccl-cu12==2.21.5 \
  nvidia-nvjitlink-cu12==12.4.127 \
  nvidia-nvtx-cu12==12.4.127 \
  odrive==0.6.10.post0 \
  opencv-python==4.9.0.80 \
  opencv-python-headless==4.10.0.84 \
  packaging==26.0 \
  pandas==2.2.3 \
  parso==0.8.6 \
  propcache==0.4.1 \
  protobuf==5.28.3 \
  py-cpuinfo==9.0.0 \
  pybboxes==0.1.6 \
  python-can==4.6.1 \
  python-dotenv==1.0.1 \
  requests-toolbelt==0.9.1 \
  roboflow==1.1.49 \
  s3transfer==0.10.3 \
  sahi==0.11.18 \
  seaborn==0.13.2 \
  shapely==2.0.6 \
  smmap==5.0.1 \
  sympy==1.13.1 \
  tensorboard==2.18.0 \
  tensorboard-data-server==0.7.2 \
  termcolor==2.5.0 \
  terminaltables==3.1.10 \
  thop==0.1.1.post2209072238 \
  torch==2.5.1 \
  torchvision==0.20.1 \
  tqdm==4.67.0 \
  traitlets==5.14.3 \
  triton==3.1.0 \
  typing_extensions==4.12.2 \
  tzdata==2024.2 \
  ultralytics==8.3.34 \
  ultralytics-thop==2.0.12 \
  urllib3==2.2.3 \
  Werkzeug==3.1.3 \
  yarl==1.22.0 \
  yolov5==7.0.14 \
  yolov8==0.0.2

echo "=== Shell setup ==="
if ! grep -q 'Old computer robotics environment' ~/.bashrc; then
  cat >> ~/.bashrc <<'EOF'

# Old computer robotics environment
source /opt/ros/humble/setup.bash

if [ -f /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash ]; then
  source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
fi

if [ -f "$HOME/ws_odrive_robot/install/local_setup.bash" ]; then
  source "$HOME/ws_odrive_robot/install/local_setup.bash"
fi

export ROS_DOMAIN_ID=42
export GZ_SIM_SYSTEM_PLUGIN_PATH="${GZ_SIM_SYSTEM_PLUGIN_PATH}:/opt/ros/humble/lib"
export IGN_GAZEBO_SYSTEM_PLUGIN_PATH="${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}:/opt/ros/humble/lib"
export GZ_SIM_RESOURCE_PATH="${GZ_SIM_RESOURCE_PATH}:$HOME/ws_odrive_robot/install/yaseen_differential_robot/share"
export IGN_GAZEBO_RESOURCE_PATH="${IGN_GAZEBO_RESOURCE_PATH}:$HOME/ws_odrive_robot/install/yaseen_differential_robot/share"

export PATH="$HOME/.local/bin:$PATH"
export PATH="/usr/local/cuda-12.6/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda-12.6/lib64:${LD_LIBRARY_PATH}"
EOF
fi

echo "=== ROS dependency database ==="
sudo rosdep init 2>/dev/null || true
rosdep update

echo "=== Workspace clone/build ==="
cd ~
if [ ! -d "$HOME/ws_odrive_robot/.git" ]; then
  git clone https://github.com/YaseenRehman786/odrive_ros2_robot.git ws_odrive_robot
fi
cd "$HOME/ws_odrive_robot"
git submodule update --init --recursive

if [ ! -d "$HOME/ws_odrive_robot/src/rebotarm_ros2/.git" ]; then
  if [ -e "$HOME/ws_odrive_robot/src/rebotarm_ros2" ]; then
    mv "$HOME/ws_odrive_robot/src/rebotarm_ros2" "$HOME/ws_odrive_robot/src/rebotarm_ros2.backup.$(date +%Y%m%d-%H%M%S)"
  fi
  git clone https://github.com/EclipseaHime017/reBotArmController_ROS2.git "$HOME/ws_odrive_robot/src/rebotarm_ros2"
fi
cd "$HOME/ws_odrive_robot/src/rebotarm_ros2"
git fetch origin
git switch yaseen-arm-integration 2>/dev/null || git switch -c yaseen-arm-integration
git remote get-url upstream >/dev/null 2>&1 || git remote add upstream https://github.com/Seeed-Projects/reBotArmController_ROS2.git
git fetch upstream

if [ ! -d "$HOME/ws_odrive_robot/src/rebotarm_ros2/third_party/reBotArm_control_py/.git" ]; then
  mkdir -p "$HOME/ws_odrive_robot/src/rebotarm_ros2/third_party"
  git clone https://github.com/vectorBH6/reBotArm_control_py.git "$HOME/ws_odrive_robot/src/rebotarm_ros2/third_party/reBotArm_control_py"
fi

echo "=== Robot hardware permissions and udev ==="
sudo usermod -a -G dialout,video,plugdev "$USER"
cd "$HOME/ws_odrive_robot/src/rplidar_ros"
source scripts/create_udev_rules.sh

echo "=== CAN modules ==="
sudo modprobe can
sudo modprobe can_raw
sudo modprobe gs_usb
printf "can\ncan_raw\ngs_usb\n" | sudo tee /etc/modules-load.d/robot-can.conf >/dev/null

source /opt/ros/humble/setup.bash
cd "$HOME/ws_odrive_robot"
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install

echo "=== Done. Restart the computer so group membership, udev, and kernel-module changes fully apply. ==="
```

## Session Log Bring-Up Commands

These are the operational commands from `SESSION_LOG.md` that matter on the
new computer after the main install has finished.

### Clean Shell Rebuild

Use this if Gazebo, `gz_ros2_control`, or mesh/resource paths act stale after
switching branches or after the first install:

```bash
env -i HOME="$HOME" USER="$USER" TERM="$TERM" PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" bash --noprofile --norc
source /opt/ros/humble/setup.bash
cd ~/ws_odrive_robot
rm -rf build install log
colcon build --symlink-install
source install/local_setup.bash
```

### CAN Bring-Up For ODrive

The old robot used `can0`. Normal ODrive/CAN setup used 1 Mbps; the debug
fallback in the log used 250 kbps with a larger transmit queue.

```bash
sudo modprobe can
sudo modprobe can_raw
sudo modprobe gs_usb

sudo ip link set can0 down 2>/dev/null || true
sudo ip link set can0 type can bitrate 1000000
sudo ip link set can0 txqueuelen 1000
sudo ip link set can0 up

ip -details -statistics link show can0
```

Fallback if CAN crashes when motors start moving:

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 250000
sudo ip link set can0 txqueuelen 1000
ip -details -statistics link show can0
dmesg | tail -n 20
```

### RPLidar A2M8

The real robot used RPLidar A2M8 through the `/dev/rplidar` udev rule, 115200
baud, `Standard` scan mode, and `lidar_link`.

```bash
sudo usermod -a -G dialout "$USER"
cd ~/ws_odrive_robot/src/rplidar_ros
source scripts/create_udev_rules.sh

# Restart or log out/in after this, then verify:
ls -l /dev/rplidar
ls -l /dev/serial/by-id/
```

### RealSense D435

Preferred real-hardware launch from the log:

```bash
ros2 launch realsense2_camera rs_launch.py \
  align_depth.enable:=true \
  rgb_camera.color_profile:=424x240x5 \
  depth_module.depth_profile:=424x240x5 \
  enable_sync:=true
```

Jetson working point-cloud configuration:

```bash
ros2 launch realsense2_camera rs_launch.py \
  pointcloud__neon_.enable:=true \
  decimation_filter.enable:=true \
  decimation_filter.filter_magnitude:=4 \
  depth_module.depth_profile:=424x240x15 \
  rgb_camera.color_profile:=424x240x15
```

Low-bandwidth Wi-Fi fallback without point cloud:

```bash
ros2 launch realsense2_camera rs_launch.py \
  align_depth.enable:=true \
  rgb_camera.color_profile:=424x240x10 \
  depth_module.depth_profile:=424x240x10
```

### Gazebo Fortress Daily Setup

For this Ubuntu 22.04 + ROS 2 Humble workspace, the session log recommends
Fortress as the stable daily setup.

```bash
sudo apt remove -y 'ros-humble-ros-gzharmonic*'
sudo apt install -y \
  ros-humble-ros-gz \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz-bridge \
  ros-humble-gz-ros2-control \
  ros-humble-gz-ros2-control-demos

source /opt/ros/humble/setup.bash
source ~/ws_odrive_robot/install/local_setup.bash

ros2 pkg prefix gz_ros2_control
env | grep -E 'gz_ros2_control_ws|GZ_VERSION' || true
```

If only `main` appears after cloning but you need another branch:

```bash
cd ~/ws_odrive_robot
git fetch --all
git branch -a
git switch <branch-name>
```

If `rplidar_ros` ever builds with ROS 1 / `catkin` errors, the wrong branch
was cloned. The workspace should use the ROS 2 / `ament_cmake` version.

### Optional Harmonic Migration

Only use this on an isolated migration branch. Daily development should stay
on the Fortress setup above.

```bash
sudo apt remove -y 'ros-humble-ros-gz*' 'ros-humble-ros-ign*'
sudo apt install -y \
  ros-humble-ros-gzharmonic \
  ros-humble-ros-gzharmonic-sim \
  ros-humble-ros-gzharmonic-bridge \
  ros-humble-ros-gzharmonic-image \
  ros-humble-ros-gzharmonic-interfaces

export GZ_VERSION=harmonic
```

If using a source-built Harmonic `gz_ros2_control`, also include both plugin
paths:

```bash
export GZ_SIM_SYSTEM_PLUGIN_PATH="$HOME/gz_ros2_control_ws/install/gz_ros2_control/lib:/opt/ros/humble/lib:${GZ_SIM_SYSTEM_PLUGIN_PATH}"
```

### Common Development Launches

```bash
# Gazebo simulation
ros2 launch yaseen_differential_robot gz_sim.launch.py world:=hospital.sdf use_sim_time:=true

# Keyboard teleop for controller input
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args \
  -r /cmd_vel:=/yaseen_diffbot_controller/cmd_vel_unstamped

# Real robot bringup with LiDAR
ros2 launch yaseen_differential_robot control.launch.py use_mock_hardware:=false use_lidar:=true use_rviz:=false

# Joystick real robot
ros2 launch yaseen_differential_robot joystick.launch.py

# Joystick in Gazebo through twist_mux safety input
ros2 launch yaseen_differential_robot joystick.launch.py cmd_vel_topic:=/cmd_vel_joy use_stamped:=false use_sim_time:=true
```

### Nav2 / SLAM Workflow Notes

Do not run multiple localization sources at the same time. In RViz, set
`2D Pose Estimate` before sending goals.

```bash
# Save map and posegraph into a timestamped folder
stamp=$(date +%Y%m%d_%H%M)
session_dir="$HOME/ws_odrive_robot/maps/${stamp}"
mkdir -p "$session_dir"
ros2 run nav2_map_server map_saver_cli -f "$session_dir/map"
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '$session_dir/posegraph'}"
```

### Cross-Machine RViz / ROS Networking

The session log captured this as a working PC-side RViz reset path:

```bash
ros2 daemon stop
ros2 daemon start
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file:///home/$USER/cyclonedds.xml
rviz2
```

Clock and network reminders when Jetson/desktop discovery or TF timing is
weird:

```bash
sudo chronyc -a makestep
sudo ufw disable
ros2 daemon stop
ros2 daemon start
```

### reBot Arm B601-DM

The arm integration uses `/dev/ttyACM0` for the USB2CAN serial bridge.

```bash
cd ~/ws_odrive_robot/src/rebotarm_ros2
git switch yaseen-arm-integration
git remote get-url upstream >/dev/null 2>&1 || git remote add upstream https://github.com/Seeed-Projects/reBotArmController_ROS2.git
git fetch upstream

cd ~/ws_odrive_robot
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash

ros2 pkg executables rebotarmcontroller
ls /dev/ttyACM*
ros2 launch rebotarm_bringup bringup.launch.py channel:=/dev/ttyACM0
```

## NVIDIA CUDA / Jetson Tooling

The old computer had CUDA 12.6 and Jetson/L4T cross-development packages from
local NVIDIA repositories:

- `cuda-toolkit-12-6`
- `cuda-cross-aarch64-12-6`
- `l4t-cuda-repo-ubuntu2204-12-6-local`
- `l4t-cuda-repo-cross-aarch64-ubuntu2204-12-6-local`
- `nsight-graphics-for-embeddedlinux-2024.2.0.0`
- `nsight-systems-2024.5.4`
- `vpi3-cross-aarch64-l4t`
- `vpi3-dev`
- `vpi3-samples`
- `sdkmanager`
- `nomachine`

These packages came from NVIDIA/NoMachine `.deb` installers, not standard
Ubuntu apt. After installing NVIDIA SDK Manager and/or the local CUDA repo
`.deb` files, paste this:

```bash
sudo apt update
sudo apt install -y \
  cuda-toolkit-12-6 \
  cuda-cross-aarch64-12-6 \
  l4t-cuda-repo-ubuntu2204-12-6-local \
  l4t-cuda-repo-cross-aarch64-ubuntu2204-12-6-local \
  nsight-graphics-for-embeddedlinux-2024.2.0.0 \
  nsight-systems-2024.5.4 \
  vpi3-cross-aarch64-l4t \
  vpi3-dev \
  vpi3-samples \
  sdkmanager \
  nomachine
```

## What I Found On The Old Computer

This setup file was based on:

- manually installed apt packages from `apt-mark showmanual`
- Python libraries from `python3 -m pip freeze`
- ROS workspace packages from `colcon list`
- installed snap package files under `/var/lib/snapd/snaps`
- apt repositories under `/etc/apt/sources.list.d`

The old computer did not have Node/npm, pipx, Docker, or Conda installed.
