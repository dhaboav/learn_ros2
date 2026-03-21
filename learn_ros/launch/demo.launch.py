from launch_ros.actions import Node

from launch import LaunchDescription


def generate_launch_description():
    ld = LaunchDescription()

    turltesim_node = Node(
        package="turtlesim",
        executable="turtlesim_node",
        name="turtle_node",
    )

    turtle_act_server_node = Node(
        package="learn_ros",
        executable="turtle_act_server",
    )

    ld.add_action(turltesim_node)
    ld.add_action(turtle_act_server_node)

    return ld
