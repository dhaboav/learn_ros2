#!/usr/bin/env python3
from functools import partial
from math import atan2, sqrt

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Pose
from turtlesim.srv import Kill


class TurtleMathNode(Node):

    def __init__(self):
        super().__init__("test_drive")
        self.state = "off"
        self.pubs_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.subs_ = self.create_subscription(
            Pose, "/turtle1/pose", self.movement_callback, 10
        )
        self.get_logger().info("Test Drive has started!")

    def distance_calc(
        self, goal_x: float, goal_y: float, current_x: float, current_y: float
    ) -> float:
        distance = sqrt((goal_x - current_x) ** 2 + (goal_y - current_y) ** 2)
        return distance

    def angle_calc(
        self, goal_x: float, goal_y: float, current_x: float, current_y: float
    ) -> float:
        angle = atan2(goal_y - current_y, goal_x - current_x)
        return angle

    def movement_callback(self, pose: Pose):
        msg = Twist()
        point_x, point_y = 0, 0
        point_ax, point_ay = 2.5, 3
        point_bx, point_by = 7.5, 3
        point_cx, point_cy = 5.5, 5.5

        ANGLE_TOLERANCE = 0.01
        DISTANCE_TOLERANCE = 0.1

        if self.state == "off":
            point_x, point_y = point_ax, point_ay

        elif self.state == "b":
            point_x, point_y = point_bx, point_by

        else:
            point_x, point_y = point_cx, point_cy

        distance = self.distance_calc(point_x, point_y, pose.x, pose.y)
        angle = self.angle_calc(point_x, point_y, pose.x, pose.y)
        angle_error = angle - pose.theta

        if abs(angle_error) > ANGLE_TOLERANCE:
            msg.angular.z = angle_error
        else:
            if distance > DISTANCE_TOLERANCE:
                msg.linear.x = distance * 1.5
            else:
                if self.state == "off":
                    self.state = "b"

                elif self.state == "b":
                    self.state = "c"

                else:
                    self.get_logger().info("Done")
                    self.call_kill_service("turtle1")
                    quit()

        self.pubs_.publish(msg)

        self.get_logger().info(
            f"state: {self.state}, cmd.x: {distance}, ang.z {angle_error}"
        )

    def call_kill_service(self, turtle_name: str):
        client = self.create_client(Kill, "/kill")
        while not client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for service...")

        request = Kill.Request()
        request.name = turtle_name

        future = client.call_async(request)
        future.add_done_callback(partial(self.callback_kill))

    def callback_kill(self, future):
        try:
            response = future.result()
        except Exception as e:
            self.get_logger().error(f"srv call failed: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = TurtleMathNode()
    rclpy.spin(node)
