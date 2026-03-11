#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class PoseSubsNode(Node):

    def __init__(self):
        super().__init__("pose_subs")
        self.pose_subs_ = self.create_subscription(
            Pose, "/turtle1/pose", self.pose_callback, 10
        )

    def pose_callback(self, msg: Pose):
        self.get_logger().info(f"X: {msg.x:.1f}, Y:{msg.y:.1f}, Z: {msg.theta}")


def main(args=None):
    rclpy.init(args=args)
    node = PoseSubsNode()
    rclpy.spin(node)
    rclpy.shutdown()
