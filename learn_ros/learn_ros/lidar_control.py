#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class LidarControl(Node):
    def __init__(self):
        super().__init__("lidar_control")
        self._lidar_subs = self.create_subscription(
            LaserScan, "/lidar", self.lidar_callback, qos_profile_sensor_data
        )
        self._cmd_vel_pubs = self.create_publisher(Twist, "/cmd_vel", 10)
        self.get_logger().info("Lidar Control has been started")

    def lidar_callback(self, sensor_data: LaserScan):
        drive = Twist()
        middle_index = len(sensor_data.ranges) // 2
        distance_front = sensor_data.ranges[middle_index]
        is_empty_front = math.isinf(distance_front)

        self.get_logger().info(f"{distance_front}")

        if is_empty_front:
            drive.linear.x = 1.0
            self.get_logger().info("Move!")

        else:
            if distance_front < 1.2:
                drive.linear.x = 0.0
                self.get_logger().info(f"Stop!")
            else:
                drive.linear.x = 1.0
                self.get_logger().info("Move!")

        self._cmd_vel_pubs.publish(drive)


def main(args=None):
    rclpy.init(args=args)
    node = LidarControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
