import os

from ament_index_python import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command


def generate_launch_description():

    # Package Directories
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    pkg_learn_ros_description = get_package_share_directory("learn_ros_description")

    # Configuration
    model_name = "my_robot"
    model_path = os.path.join(pkg_learn_ros_description, "urdf", "robot.urdf.xacro")
    rviz_config_path = os.path.join(pkg_learn_ros_description, "rviz", "config.rviz")

    # Node
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "use_sim_time": True,
                "robot_description": Command(["xacro ", model_path]),
            }
        ],
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        parameters=[
            {
                "use_sim_time": True,
            }
        ],
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config_path],
        output="screen",
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": "-r empty.sdf"}.items(),
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

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            f"/world/empty/model/{model_name}/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model",
            f"/model/{model_name}/pose@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
        ],
        remappings=[
            (f"/model/{model_name}/pose", "/tf"),
            (f"/world/empty/model/{model_name}/joint_state", "/joint_states"),
        ],
        output="screen",
    )

    return LaunchDescription(
        [
            gz_sim,
            spawn,
            bridge,
            robot_state_publisher,
            joint_state_publisher,
            rviz,
        ]
    )
