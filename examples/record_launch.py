from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='demo_nodes_cpp', executable='talker'),
        ExecuteProcess(
            cmd=['ros2', 'bag', 'record', '-o', 'talker_run',
                 '--storage-preset-profile', 'zstd_fast',
                 '--topics', '/chatter'],
            output='screen',
        ),
    ])
