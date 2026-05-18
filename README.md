# ROS2 2WD Robot — Simulation & Navigation

A ROS2 (Humble/Iron) project simulating a differential-drive robot in Gazebo with SLAM, localisation, and Nav2 navigation.

## Packages

| Package | Description |
|---|---|
| `robot_description` | URDF/Xacro robot model (body, wheels, LiDAR, RGBD camera, IMU) |
| `robot_simulation` | Gazebo worlds, bridge config, simulation launchers |
| `slam_pkg` | SLAM Toolbox mapping, AMCL localisation, Nav2 params, bringup launcher |
| `odom_to_tf` | Republishes `/odom` odometry as a TF transform |

## Quick start

### Build
```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## How to run
**1. Simulation**
```bash
# Choose a world: simple | warehouse | empty_warehouse
ros2 launch robot_simulation simulation.launch.py
```

**2. SLAM (mapping)**
```bash
ros2 launch slam_pkg online_async_launch.py use_sim_time:=true
```

**3. Localisation (after you have a map)**
```bash
ros2 launch slam_pkg localization_launch.py map:=/path/to/map.yaml
```

**4. Teleop (keyboard driving)**
```bash
ros2 launch robot_simulation teleop.launch.py
```

**5. Save map** (after SLAM)
```bash
ros2 run nav2_map_server map_saver_cli -f ~/map
```

**6. Navigation
```bash
ros2 launch slam_pkg navigation.launch.py
```

## Robot sensors

| Sensor | ROS topic | Rate |
|---|---|---|
| 2D LiDAR | `/scan` | 50 Hz |
| RGBD Camera (colour) | `/camera/image_raw` | 30 Hz |
| RGBD Camera (info) | `/camera/camera_info` | 30 Hz |
| IMU | `/imu` | 50 Hz |
| Odometry (raw) | `/odom` | 50 Hz |
| Odometry (EKF filtered) | `/odom/filtered` | 30 Hz (EKF only) |

## World files

| Launch argument | File |
|---|---|
| `simple` | `worlds/simple.sdf` |
| `warehouse` | `worlds/warehouse.sdf` |
| `empty_warehouse` | `worlds/empty_warehouse.sdf` |

## Dependencies

```bash
sudo apt install \
  ros-$ROS_DISTRO-nav2-bringup \
  ros-$ROS_DISTRO-slam-toolbox \
  ros-$ROS_DISTRO-robot-localization \
  ros-$ROS_DISTRO-ros-gz \
  ros-$ROS_DISTRO-teleop-twist-keyboard
```
