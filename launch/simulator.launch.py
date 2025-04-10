# Copyright 2024 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch Arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution(
                [FindPackageShare('ros2_ign_p2p_controllers'), 'model', 'forklift_robot.urdf.xacro']
            ),
        ]
    )
    ros2_ign_p2p_controllers = FindPackageShare('ros2_ign_p2p_controllers')
    default_rviz_config_path = PathJoinSubstitution([ros2_ign_p2p_controllers, 'config', 'forklift.rviz'])

    # These parameters are maintained for backwards compatibility
    gui_arg = DeclareLaunchArgument(name='gui', default_value='true', choices=['true', 'false'],
                                    description='Flag to enable joint_state_publisher_gui')
    rviz_arg = DeclareLaunchArgument(name='rvizconfig', default_value=default_rviz_config_path,
                                     description='Absolute path to rviz config file')
    model_arg = DeclareLaunchArgument(name='model', default_value=robot_description_content,
                                        description='Path to robot urdf file relative to urdf_tutorial package')



    rviz_launch = IncludeLaunchDescription(
        PathJoinSubstitution([FindPackageShare('urdf_launch'), 'launch', 'display.launch.py']),
        # launch_arguments={
        #     'urdf_package': 'ros2_ign_p2p_controllers',
        #     'urdf_package_path': LaunchConfiguration('model'),
        #     'rviz_config': LaunchConfiguration('rvizconfig'),
        #     'jsp_gui': LaunchConfiguration('gui')}.items()
    )
    # Get URDF via xacro
    robot_description = {'robot_description': robot_description_content}

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )
    p2p_controller = Node(
        package='ros2_ign_p2p_controllers',
        executable='P2PController',
        output='screen',
    )

    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description', '-name',
                   'ackermann', '-allow_renaming', 'true'],
    )

#     load_joint_state_broadcaster = ExecuteProcess(
#         cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
#              'joint_state_broadcaster'],
#         output='screen'
#     )

#     load_ackermann_controller = ExecuteProcess(
#         cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
#              'ackermann_steering_controller'],
#         output='screen'
#     )
#     load_fork_controller = ExecuteProcess(
#         cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
#              'fork_controller'],
#         output='screen'
#     )
#     control_node = Node(
#     package="controller_manager",
#     executable="ros2_control_node",
#     parameters=[robot_controllers],
#     output="screen",
# )
    load_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    load_ackermann_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['ackermann_steering_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    load_fork_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['fork_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )
    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )
    return LaunchDescription([
        bridge,
        # Launch gazebo environment
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [PathJoinSubstitution([FindPackageShare('ros_gz_sim'),
                                       'launch',
                                       'gz_sim.launch.py'])]),
            launch_arguments=[('gz_args', [' -r -v 4 empty.sdf'])]),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=gz_spawn_entity,
                on_exit=[load_joint_state_broadcaster],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=load_joint_state_broadcaster,
                on_exit=[load_ackermann_controller, load_fork_controller],
            )
        ),
        node_robot_state_publisher,
        gz_spawn_entity,
        p2p_controller,
        # rviz_arg,
        # gui_arg,
        # model_arg,
        # rviz_launch,
        DeclareLaunchArgument(
            'use_sim_time',
            default_value=use_sim_time,
            description='If true, use simulated clock'),
    ])
