import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    package_name = "learn_ros"

    pkg_share = FindPackageShare(package_name).find(package_name)
    xacro_file = os.path.join(pkg_share, "description", "urdf", "robot.urdf.xacro")

    # Convert xacro → robot_description
    robot_description = Command(["xacro ", xacro_file])

    # Start Gazebo Harmonic
    gazebo = ExecuteProcess(cmd=["gz", "sim", "-r", "empty.sdf"], output="screen")

    ld = LaunchDescription()

    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=["-name", "my_robot", "-topic", "robot_description"],
    )

    # Publish robot_description
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
        output="screen",
    )

    bridge_cmd_vel = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=["/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist"],
        output="screen",
    )

    ld.add_action(gazebo)
    ld.add_action(robot_state_publisher)
    ld.add_action(spawn_entity)
    ld.add_action(bridge_cmd_vel)

    return ld
