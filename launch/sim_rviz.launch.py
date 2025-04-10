import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    urdf_file_name = 'forklift_rviz.urdf'
    urdf = os.path.join(
        get_package_share_directory('ros2_ign_p2p_controllers'), 'model',
        urdf_file_name)
    with open(urdf, 'r') as infp:
        robot_desc = infp.read()

    # Optional: RViz config file
    rviz_config_file = os.path.join(
        get_package_share_directory('ros2_ign_p2p_controllers'),
        'config',
        'forklift.rviz'  # Make sure this file exists or adjust accordingly
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_map_to_base',
            arguments=['0', '0', '0', '0', '0', '0', 'map', 'base_link'],  # Adjust values as needed
            output='screen'
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_desc}],
            arguments=[urdf]),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file],
            parameters=[{'use_sim_time': use_sim_time}]
        ),
    ])
