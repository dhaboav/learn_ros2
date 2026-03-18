#!/usr/bin/env python3
import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node

from learn_ros_interfaces.action import MoveToXY


class TurtleActClientNode(Node):
    def __init__(self):
        super().__init__("turtle_act_client")
        self._client = ActionClient(self, MoveToXY, "move_to_xy")
        self.get_logger().info("Turtle act client has been started")

    def send_goal(self, x: float, y: float):
        # Wait for the server
        self._client.wait_for_server()

        # Create a goal
        goal = MoveToXY.Goal()
        goal.target_x, goal.target_y = x, y

        # Send the goal
        self.get_logger().info("Sending the goal..")
        self._send_goal = self._client.send_goal_async(goal, self.feedback_callback)
        self._send_goal.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self._goal_handle: ClientGoalHandle = future.result()
        if not self._goal_handle.accepted:
            self.get_logger().info("Goal rejected")
            rclpy.shutdown()
            return

        self.get_logger().info("Goal accepted")
        result = self._goal_handle.get_result_async()
        result.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().status  # Use ros2 action status topics default code

        self.get_logger().info(f"Code result: {result}")
        if result == 4:
            self.get_logger().info("Shutdown node...")
            rclpy.shutdown()

    def feedback_callback(self, feedback):
        msg = feedback.feedback
        self.get_logger().info(
            f"stat: {msg.current_status}, x: {msg.current_x:.1f}, y: {msg.current_y:.1f}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = TurtleActClientNode()
    input_target_x = float(sys.argv[1])
    input_target_y = float(sys.argv[2])
    node.send_goal(input_target_x, input_target_y)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()
