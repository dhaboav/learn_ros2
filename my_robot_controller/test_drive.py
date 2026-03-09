#!/usr/bin/env python3
from functools import partial

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Pose
from turtlesim.srv import Kill


class TestDrive(Node):

    def __init__(self):
        super().__init__("test_drive")
        self.state = "off"

        self.pubs_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.subs_ = self.create_subscription(
            Pose, "/turtle1/pose", self.movement_callback, 10
        )
        self.get_logger().info("Test Drive has started!")

    def movement_callback(self, pose: Pose):
        msg = Twist()

        if self.state == "off":
            msg.linear.x = 1.0

            if pose.x > 9.5:
                self.state = "b"

        elif self.state == "b":
            msg.linear.x = 1.0

            if pose.x > 9.0:
                msg.angular.z = 1.0

            elif pose.x < 2.5:
                self.state = "c"

        elif self.state == "c":
            msg.linear.x = 1.0

            if pose.x < 3.5:
                msg.angular.z = -1.0
                msg.linear.x = 3.0

            elif pose.x >= 5.5:
                msg.linear.x = 0.0
                self.state = "stop"

        elif self.state == "stop":
            self.call_kill_service("turtle1")

        self.pubs_.publish(msg)

        self.get_logger().info(
            f"cons: {self.state}, cmd.x: {msg.linear.x}, ang.z {msg.angular.z}"
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
    node = TestDrive()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
