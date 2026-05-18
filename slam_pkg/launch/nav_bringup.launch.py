"""
Navigation-only bringup (no Gazebo). Run simulation separately first.

Modes:
  slam  -- SLAM Toolbox (build a new map)
  nav   -- AMCL localisation + Nav2 (navigate with an existing map)

Usage examples:
  ros2 launch slam_pkg nav_bringup.launch.py mode:=slam
  ros2 launch slam_pkg nav_bringup.launch.py mode:=nav map:=/path/to/map.yaml
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    mode      = LaunchConfiguration('mode').perform(context)
    use_rviz  = LaunchConfiguration('use_rviz').perform(context)
    use_ekf   = LaunchConfiguration('use_ekf').perform(context)
    map_file  = LaunchConfiguration('map').perform(context)

    slam_pkg_share = get_package_share_directory('slam_pkg')

    actions = []

    # ── EKF (optional sensor fusion) ────────────────────────────────────────
    if use_ekf.lower() in ('true', '1', 'yes'):
        actions.append(Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[
                os.path.join(slam_pkg_share, 'config', 'ekf_params.yaml'),
                {'use_sim_time': True},
            ],
        ))

    # ── SLAM Toolbox (mapping mode) ─────────────────────────────────────────
    if mode == 'slam':
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(slam_pkg_share, 'launch', 'online_async_launch.py')
            ),
            launch_arguments={'use_sim_time': 'true'}.items(),
        ))

    # ── Localisation + Nav2 (navigation mode) ───────────────────────────────
    if mode == 'nav':
        # AMCL + map server
        actions.append(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(slam_pkg_share, 'launch', 'localization_launch.py')
            ),
            launch_arguments={
                'map': map_file,
                'use_sim_time': 'true',
            }.items(),
        ))

        nav2_params = os.path.join(slam_pkg_share, 'config', 'nav2_params.yaml')

        # Full Nav2 stack
        nav2_nodes = [
            Node(package='nav2_controller',       executable='controller_server',    output='screen', parameters=[nav2_params, {'use_sim_time': True}]),
            Node(package='nav2_smoother',          executable='smoother_server',      output='screen', parameters=[nav2_params, {'use_sim_time': True}]),
            Node(package='nav2_planner',           executable='planner_server',       output='screen', parameters=[nav2_params, {'use_sim_time': True}]),
            Node(package='nav2_behaviors',         executable='behavior_server',      output='screen', parameters=[nav2_params, {'use_sim_time': True}]),
            Node(package='nav2_bt_navigator',      executable='bt_navigator',         output='screen', parameters=[nav2_params, {'use_sim_time': True}]),
            Node(package='nav2_waypoint_follower', executable='waypoint_follower',    output='screen', parameters=[nav2_params, {'use_sim_time': True}]),
            Node(package='nav2_velocity_smoother', executable='velocity_smoother',   output='screen', parameters=[nav2_params, {'use_sim_time': True}]),
            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_navigation',
                output='screen',
                parameters=[
                    {'use_sim_time': True},
                    {'autostart': True},
                    {'node_names': [
                        'controller_server', 'smoother_server', 'planner_server',
                        'behavior_server', 'bt_navigator', 'waypoint_follower',
                        'velocity_smoother',
                    ]},
                ],
            ),
        ]
        actions.extend(nav2_nodes)

    # ── RViz2 ───────────────────────────────────────────────────────────────
    if use_rviz.lower() in ('true', '1', 'yes'):
        rviz_config = os.path.join(slam_pkg_share, 'config', 'slam.rviz')
        actions.append(Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': True}],
            output='screen',
        ))

    return actions


def generate_launch_description():
    slam_pkg_share = get_package_share_directory('slam_pkg')
    default_map = os.path.join(slam_pkg_share, 'maps', 'obstacle_maps.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'mode', default_value='slam',
            description='slam = build map | nav = navigate with existing map',
        ),
        DeclareLaunchArgument(
            'map', default_value=default_map,
            description='Path to map YAML (nav mode only)',
        ),
        DeclareLaunchArgument(
            'use_rviz', default_value='false',
            description='Launch RViz2',
        ),
        DeclareLaunchArgument(
            'use_ekf', default_value='false',
            description='Run robot_localization EKF (requires robot_localization package)',
        ),
        OpaqueFunction(function=launch_setup),
    ])
