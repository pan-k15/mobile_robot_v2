import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument, IncludeLaunchDescription,
    OpaqueFunction, SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    world_name = LaunchConfiguration('world').perform(context)
    use_sim_time = LaunchConfiguration('use_sim_time')

    robot_description_pkg = get_package_share_directory('robot_description')
    robot_simulation_pkg = get_package_share_directory('robot_simulation')
    ros_gz_sim_pkg = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(robot_description_pkg, 'urdf', '2wd_robot.urdf.xacro')
    doc = xacro.process_file(xacro_file)
    robot_description = {'robot_description': doc.toxml()}

    gz_launch_path = os.path.join(ros_gz_sim_pkg, 'launch', 'gz_sim.launch.py')
    world_path = os.path.join(robot_simulation_pkg, 'worlds', f'{world_name}.sdf')
    bridge_params = os.path.join(robot_simulation_pkg, 'config', 'robot_bridge.yaml')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gz_launch_path),
        launch_arguments={
            'gz_args': world_path,
            'on_exit_shutdown': 'true',
        }.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}],
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-entity', 'robot', '-z', '0.5'],
        output='screen',
    )

    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', f'config_file:={bridge_params}'],
        output='screen',
    )

    gz_image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['camera/image'],
        output='screen',
    )

    return [gz_sim, robot_state_publisher, spawn_entity, gz_bridge, gz_image_bridge]


def generate_launch_description():
    robot_simulation_pkg = FindPackageShare('robot_simulation')

    return LaunchDescription([
        DeclareLaunchArgument(
            'world', default_value='simple',
            description='World name (file under worlds/ without .sdf): simple, warehouse, empty_warehouse',
        ),
        DeclareLaunchArgument(
            'use_sim_time', default_value='true',
            description='Use simulation (Gazebo) clock',
        ),
        SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            PathJoinSubstitution([robot_simulation_pkg, 'models']),
        ),
        SetEnvironmentVariable(
            'GZ_SIM_PLUGIN_PATH',
            PathJoinSubstitution([robot_simulation_pkg, 'plugins']),
        ),
        OpaqueFunction(function=launch_setup),
    ])
