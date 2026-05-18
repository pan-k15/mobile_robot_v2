from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    teleop = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix='xterm -e',  # opens in its own terminal so keystrokes are captured
        remappings=[('/cmd_vel', '/cmd_vel')],
    )

    return LaunchDescription([teleop])
