import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    
    # Package Directories
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    package_name = get_package_share_directory("learn_ros")

    # Xacro Process
    robot_desc_file = os.path.join(package_name, "description", "urdf", "robot.urdf.xacro")
    
    robot_desc_config = xacro.process_file(robot_desc_file).toxml()


    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description":robot_desc_config}],
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")),
        launch_arguments={
            "gz_args": "-r -v 4 empty.sdf"
        }.items()
    )

    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "/robot_description",
            "-name", "my_robot",
            "-allow_renaming", "true",
            "-x", "0.0",
            "-y", "0.0",
            "-z", "0.0",
        ],
        output="screen",
    )

    bridge_cmd_vel = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=["/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist"],
        output="screen",
    )

    return LaunchDescription(
        [
            gazebo,
            spawn,
            bridge_cmd_vel, 
            robot_state_publisher,
        ]
    )