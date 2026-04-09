import os

from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node


def generate_launch_description():

    # Package Directories
    pkg_ros_gz_sim = get_package_share_directory("ros_gz_sim")
    pkg_learn_ros_description = get_package_share_directory("learn_ros_description")

    # Configuration
    model_name = "my_robot"
    model_path = os.path.join(pkg_learn_ros_description, "urdf", "robot.urdf.xacro")
    rviz_config_path = os.path.join(pkg_learn_ros_description, "rviz", "gz.rviz")

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

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config_path],
        output="screen",
        parameters=[{"use_sim_time": True}],
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": "-v 4 -r empty.sdf"}.items(),
    )

    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic",
            "/robot_description",
            "-name",
            model_name,
            "-allow_renaming",
            "false",
        ],
        output="screen",
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
            f"/model/{model_name}/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model",
            "/lidar@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
        ],
        remappings=[
            (f"/model/{model_name}/joint_state", "/joint_states"),
        ],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    ros_gz_image_bridge = Node(
        package="ros_gz_image",
        executable="image_bridge",
        arguments=["/camera/image_raw"],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    return LaunchDescription(
        [
            gz_sim,
            spawn,
            bridge,
            ros_gz_image_bridge,
            robot_state_publisher,
            rviz,
        ]
    )
