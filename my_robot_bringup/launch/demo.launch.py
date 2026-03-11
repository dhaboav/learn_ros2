from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    ld = LaunchDescription()

    turltesim_node = Node(
        package="turtlesim",
        executable="turtlesim_node",
        name="turtle_node",
    )

    turtle_action_move_server_node = Node(
        package="turtlesim_controller",
        executable="turtle_act_move_server",
        name="action_server_node",
    )

    ld.add_action(turltesim_node)
    ld.add_action(turtle_action_move_server_node)

    return ld
