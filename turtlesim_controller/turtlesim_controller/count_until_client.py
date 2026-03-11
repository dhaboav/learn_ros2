#!/usr/bin/env python3
import rclpy
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node

from my_robot_interfaces.action import CountUntil


class CountUntilClientNode(Node):
    def __init__(self):
        super().__init__("count_until_client")
        self.count_until_client_ = ActionClient(self, CountUntil, "count_until")
        self.get_logger().info("Action client has been started")

    def send_goal(self, target_number, period):
        # Wait for the server
        self.count_until_client_.wait_for_server()

        # Create a goal
        goal = CountUntil.Goal()
        goal.target_number = target_number
        goal.period = period

        # Send the goal
        self.get_logger().info("Sending the goal")
        self.send_goal_future_ = self.count_until_client_.send_goal_async(
            goal, self.feedback_callback
        )
        self.send_goal_future_.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self.goal_handle_: ClientGoalHandle = future.result()
        if not self.goal_handle_.accepted:
            self.get_logger().info("Goal rejected")
            return

        self.get_logger().info("Goal accepted")
        result = self.goal_handle_.get_result_async()
        result.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        # Canceling by feedback status (Optional)
        if feedback_msg.feedback.current_number == 10:
            self.get_logger().info("Canceling request...")
            future = self.goal_handle_.cancel_goal_async()
            future.add_done_callback(self.cancel_callback)

        self.get_logger().info(f"Feedback: {feedback_msg.feedback.current_number}")

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f"Result: {result.reached_number}")

    def cancel_callback(self, future):
        cancel_response = future.result()
        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info("Cancel accepted")
        else:
            self.get_logger().info("Cancel rejected")


def main(args=None):
    rclpy.init(args=args)
    node = CountUntilClientNode()
    node.send_goal(100, 1.0)
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
