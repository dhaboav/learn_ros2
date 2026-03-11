#!/usr/bin/env python3
from math import atan2, sqrt

import rclpy
from geometry_msgs.msg import Twist
from rclpy.action import ActionServer, GoalResponse
from rclpy.action.server import ServerGoalHandle
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from turtlesim.msg import Pose

from turtlesim_interfaces.action import MoveToXY


class TurtleActionMoveServer(Node):
    def __init__(self):
        super().__init__("turtle_action_move_server")
        self._server = ActionServer(
            self,
            MoveToXY,
            "move_to_xy",
            execute_callback=self.execute_callback,
            callback_group=ReentrantCallbackGroup(),
            goal_callback=self.goal_callback,
        )

        self._twist_pubs = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self._pose_subs = self.create_subscription(
            Pose, "/turtle1/pose", self.pose_callback, 10
        )

        self._turtle_pose = Pose()
        self._status = "ongoing"
        self.get_logger().info("turle action move server has been started")

    # Subs
    def pose_callback(self, pose: Pose):
        self._turtle_pose = pose

    def goal_callback(self, goal_handle):
        if goal_handle.target_x > 11.0 and goal_handle.target_y:
            self.get_logger().warn("Goal out of bounds! Rejecting...")
            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def execute_callback(self, goal_handle: ServerGoalHandle):
        target_x = goal_handle.request.target_x
        target_y = goal_handle.request.target_y
        self._status = "ongoing"

        while rclpy.ok():
            msg = Twist()

            dx = target_x - self._turtle_pose.x
            dy = target_y - self._turtle_pose.y
            distance = sqrt(dx**2 + dy**2)
            angle_to_target = atan2(dy, dx)
            angle_error = angle_to_target - self._turtle_pose.theta

            if abs(angle_error) > 0.01:
                msg.angular.z = angle_error
            elif distance > 0.1:
                msg.linear.x = distance * 1.5
            else:
                self._status = "done"
                break

            self._twist_pubs.publish(msg)

            # Publish feedback
            feedback = MoveToXY.Feedback()
            feedback.current_x = self._turtle_pose.x
            feedback.current_y = self._turtle_pose.y
            feedback.current_status = self._status
            goal_handle.publish_feedback(feedback)
            self.get_logger().info(
                f"X:{self._turtle_pose.x:.1f}, Y:{self._turtle_pose.y:.1f}"
            )

        goal_handle.succeed()
        result = MoveToXY.Result()
        result.status = self._status
        self.get_logger().info(f"{self._status}")
        return result


def main(args=None):
    rclpy.init(args=args)
    node = TurtleActionMoveServer()
    executor = MultiThreadedExecutor()
    try:
        rclpy.spin(node, executor=executor)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            rclpy.shutdown()
