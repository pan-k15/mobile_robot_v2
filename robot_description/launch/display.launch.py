import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    # Get path to xacro file
    robot_model_path = get_package_share_directory('robot_description')
    xacro_file = os.path.join(robot_model_path, 'urdf', '2wd_robot.urdf.xacro')

    # Process xacro file
    doc = xacro.process_file(xacro_file)
    robot_description_config = doc.toxml()
    params = {'robot_description': robot_description_config}

    # Nodes
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[params],
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
    )

    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
    )


    rviz_config_path = os.path.join(
        get_package_share_directory('robot_description'),
        'config',
        'display.rviz'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
    )
    
    return LaunchDescription([
       
        joint_state_publisher,
        joint_state_publisher_gui,
        robot_state_publisher,
        rviz
    ])