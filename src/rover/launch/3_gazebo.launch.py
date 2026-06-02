import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from launch.actions import TimerAction


def generate_launch_description():

    package_dir = get_package_share_directory('rover')
    urdf_path = os.path.join(package_dir, 'urdf', 'hexa.urdf')

    with open(urdf_path, 'r') as infp:
        urdf_content = infp.read()

    return LaunchDescription([

        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[
                {'robot_description': urdf_content},
                {'use_sim_time': True}
            ]
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            parameters=[
                {'use_sim_time': True}
            ]
        ),

        # Start Gazebo
        ExecuteProcess(
            cmd=[
                'gazebo',
                '--verbose',
                '/usr/share/gazebo-11/worlds/willowgarage.world',
                '-s', 'libgazebo_ros_factory.so'
            ],
            output='screen'
        ),

        TimerAction(
            period=3.0,   # 3 second delay
            actions=[

                Node(
                    package='gazebo_ros',
                    executable='spawn_entity.py',
                    output='screen',
                    arguments=[
                        '-topic', 'robot_description',
                        '-entity', 'rover',
                        '-x', '0.0',      # forward
                        '-y', '0.0',      # sideways
                        '-z', '0.15',      # height above ground
                        '-R', '0.0',      # roll (rad)
                        '-P', '0.0',      # pitch (rad)
                        '-Y', '0.0'       # yaw (rad)
                    ]
                ),

                # Spawn Joint State Broadcaster
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["joint_state_broadcaster"],
                    output="screen"
                ),

                # Spawn Hexapod Controller
                Node(
                    package="controller_manager",
                    executable="spawner",
                    arguments=["hexapod_controller"],
                    output="screen"
                ),
            ]
        ),
    ])