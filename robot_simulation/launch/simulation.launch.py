from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable, IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os
import xacro

def generate_launch_description():
    # === Paths ===
    ros_gz_sim_pkg_path = get_package_share_directory('ros_gz_sim')
    robot_description_pkg_path = get_package_share_directory('robot_description')
    robot_simulation_pkg_path = FindPackageShare('robot_simulation')

    gz_launch_path = os.path.join(ros_gz_sim_pkg_path, 'launch', 'gz_sim.launch.py')
    xacro_file = os.path.join(robot_description_pkg_path, 'urdf', '2wd_robot.urdf.xacro')

    # === Process Xacro ===
    doc = xacro.process_file(xacro_file)
    robot_description_config = doc.toxml()
    robot_description = {'robot_description': robot_description_config}

    # === Launch arguments ===
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock'
    )

    static_tf_odom_to_base = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_odom_to_base',
        arguments=[
            '0', '0', '0',
            '0', '0', '0',
            'odom',
            'base_footprint'
        ],
        output='screen'
    )

    # === Robot state publisher ===
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': use_sim_time}]
    )

    # === Joint state publisher (optional) ===
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
    )

    # === Spawn robot using description from parameter ===
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-entity', 'robot','-z', '0.5'],
        output='screen',
    )

    # === Gazebo bridge config ===
    bridge_params = os.path.join(
        get_package_share_directory('robot_simulation'),
        'config',
        'robot_bridge.yaml'
    )

    start_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p', f'config_file:={bridge_params}',
        ],
        output='screen',
    )

    start_gz_image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/camera/image_raw'],
        output='screen',
    )

    # === Launch description ===
    return LaunchDescription([
        use_sim_time_arg,
        SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            PathJoinSubstitution([robot_simulation_pkg_path, 'models'])
        ),
        SetEnvironmentVariable(
            'GZ_SIM_PLUGIN_PATH',
            PathJoinSubstitution([robot_simulation_pkg_path, 'plugins'])
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_launch_path),
            launch_arguments={
                'gz_args': PathJoinSubstitution([
                    FindPackageShare('robot_simulation'),
                    'worlds',
                    'simple.sdf'
                ]),
                'on_exit_shutdown': 'true'
            }.items(),
        ),
        robot_state_publisher,
        joint_state_publisher,
        spawn_entity,
        start_gz_bridge,
        start_gz_image_bridge
    ])