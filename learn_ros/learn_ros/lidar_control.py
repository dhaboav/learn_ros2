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

    def get_min(self, data_slice: list):
        sorted_data = sorted(data_slice)
        return sorted_data[min(5, len(sorted_data) - 1)]

    def lidar_callback(self, sensor_data: LaserScan):
        clean_data = []
        CRITICAL_DIST = 0.8
        SAFE_DIST = 1.5

        # Filtered the data
        for val in sensor_data.ranges:
            if (
                math.isinf(val)
                or math.isnan(val)
                or val < sensor_data.range_min
                or val > sensor_data.range_max
            ):
                clean_data.append(sensor_data.range_max)
            else:
                clean_data.append(val)

        # Navigation
        angle_45_rad = math.pi / 4
        step = int(angle_45_rad / sensor_data.angle_increment)
        center = len(clean_data) // 2

        front_side = clean_data[center - step : center + step]
        left_side = clean_data[center + step : center + 3 * step]
        right_side = clean_data[center - 3 * step : center - step]

        dist_front = self.get_min(front_side)
        dist_left = self.get_min(left_side)
        dist_right = self.get_min(right_side)

        self.get_logger().info(
            f"L: {dist_left:.2f} | F: {dist_front:.2f} | R: {dist_right:.2f}"
        )

        if dist_front < CRITICAL_DIST:
            if dist_left > dist_right:
                turn = 0.5
                self.get_logger().info("Turn left")
            else:
                turn = -0.5
                self.get_logger().info("Turn right")

            self.move_robot(0.0, turn)

        elif dist_front < SAFE_DIST:
            self.get_logger().info("Beware: There an object...")
            self.move_robot(0.5, 0.0)

        else:
            self.get_logger().info("Nothing in our way! Full Drive!")
            self.move_robot(1.0, 0.0)

    def move_robot(self, linear_x: float, angular_z: float) -> None:
        """Moves the robot based on linear and angular velocities.

        Args:
            linear_x (float): Linear speed along the x-axis in m/s.
            angular_z (float): Angular speed around the z-axis in rad/s.
        """
        drive = Twist()
        drive.linear.x = linear_x
        drive.angular.z = angular_z
        self._cmd_vel_pubs.publish(drive)


def main(args=None):
    rclpy.init(args=args)
    node = LidarControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
