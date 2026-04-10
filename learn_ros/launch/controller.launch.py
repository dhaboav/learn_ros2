from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    lidar_control_node = Node(
        package="learn_ros", executable="lidar_control", name="lidar"
    )

    camera_node = Node(
        package="learn_ros",
        executable="camera",
    )

    return LaunchDescription([lidar_control_node, camera_node])
