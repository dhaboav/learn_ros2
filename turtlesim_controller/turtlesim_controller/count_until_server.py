#!/usr/bin/env python3
import time

import rclpy
from rclpy.action import ActionServer, CancelResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from my_robot_interfaces.action import CountUntil


class CountUntilServerNode(Node):
    def __init__(self):
        super().__init__("count_until_server")
        self.count_until_server_ = ActionServer(
            self,
            CountUntil,
            "count_until",
            execute_callback=self.excute_callback,
            callback_group=ReentrantCallbackGroup(),
            cancel_callback=self.cancel_callback,
        )
        self.get_logger().info("Action server has been started")

    def cancel_callback(self, goal_handle):
        self.get_logger().info("Received cancel request")
        return CancelResponse.ACCEPT

    def excute_callback(self, goal_handle: ServerGoalHandle):
        self.get_logger().info("Excuting the  goal")

        # This enable feedback (optional, can be removed)
        feedback_msg = CountUntil.Feedback()

        # Excute the action
        counter = 0
        for i in range(goal_handle.request.target_number):

            # Canceled handle (Optional if not use it)
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info("Goal canceled")
                result = CountUntil.Result()
                result.reached_number = counter
                return result

            counter += 1

            # Here we updated feedback
            feedback_msg.current_number = counter
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f"Feedback: {feedback_msg.current_number}")

            time.sleep(goal_handle.request.period)

        # Once done, set goal final state
        goal_handle.succeed()

        # Send the result
        result = CountUntil.Result()
        result.reached_number = counter
        self.get_logger().info(f"Result: {result.reached_number}")
        return result


def main(args=None):
    rclpy.init(args=args)
    node = CountUntilServerNode()

    # Must use multi thread for canceling features to work
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
