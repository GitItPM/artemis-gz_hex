from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    pkg_share = get_package_share_directory('rover')

    urdf_file = os.path.join(
        pkg_share,
        'urdf',
        'hexa.urdf'
    )

    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    return LaunchDescription([

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[
                {
                    'robot_description': robot_desc,
                    'use_sim_time': True
                }
            ]
        ),

        ExecuteProcess(
            cmd=['gz', 'sim', '-r', 'empty.sdf'],
            output='screen'
        ),

        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-topic',
                'robot_description',
                '-name',
                'rover'
            ],
            output='screen'
        )

    ])