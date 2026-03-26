import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Package Directories
    pkg_ros_gz_sim = FindPackageShare(package="ros_gz_sim").find("ros_gz_sim")
    package_name = FindPackageShare(package="learn_ros_description").find(
        "learn_ros_description"
    )
    model_path = os.path.join(package_name, "urdf/robot.urdf.xacro")

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": Command(["xacro ", model_path])}],
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": "-r -v 4 empty.sdf"}.items(),
    )

    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic",
            "/robot_description",
            "-name",
            "my_robot",
            "-allow_renaming",
            "true",
            "-x",
            "0.0",
            "-y",
            "0.0",
            "-z",
            "0.0",
        ],
        output="screen",
    )

    bridge_cmd_vel = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
        ],
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
