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
        self.stop_dist = 0.8
        self.brake_dist = 1.5
        self.get_logger().info("Lidar Control has been started")

    def lidar_callback(self, msg: LaserScan) -> None:
        """Lidar callback for lidar topics subs"""
        zones = self.get_clean_zones(msg)
        linear_x, angular_z = self.navigation_guide(zones)
        self.move_robot(linear_x, angular_z)

    def get_clean_zones(self, msg: LaserScan) -> dict[str, float]:
        """Filters raw LiDAR data and partitions the environment into three safety zones.

        This function performs a 180-degree front-facing slice, applies a median
        filter to remove sensor noise, and identifies the minimum distance in
        the Right (45°), Front (90°), and Left (45°) sectors.

        Args:
            msg (LaserScan): The raw ROS 2 LaserScan message from the sensor.

        Returns:
            dict[str, float]: A dictionary containing the closest valid distance
                for 'left', 'front', and 'right' zones. All values are capped
                at msg.range_max.

        Note:
            Points outside the [range_min, range_max] or invalid floats (NaN/Inf)
            are discarded before zone calculation.
        """
        raw_front = msg.ranges[90:271]
        zones = {"left": msg.range_max, "front": msg.range_max, "right": msg.range_max}

        for i in range(1, len(raw_front) - 1):
            r = raw_front[i]
            if math.isinf(r) or math.isnan(r) or r < msg.range_min or r > msg.range_max:
                continue

            # Median Filter
            neighbors = [raw_front[i - 1], r, raw_front[i + 1]]
            r_smooth = sorted(neighbors)[1]

            if i < 45:
                zones["right"] = min(zones["right"], r_smooth)
            elif i < 135:
                zones["front"] = min(zones["front"], r_smooth)
            else:
                zones["left"] = min(zones["left"], r_smooth)

        return zones

    def navigation_guide(self, zones: dict) -> tuple[float, float]:
        """Evaluates processed LiDAR zones to determine safe robot velocities.
        Args:
            zones (dict): Dict containing 'front', 'left', and 'right'. Minimum float distances in meters.

        Returns:
            tuple[float, float]: (linear_x, angular_z) velocities in m/s and rad/s.
        """
        dist_front = zones["front"]
        dist_left = zones["left"]
        dist_right = zones["right"]
        self.get_logger().info(
            f"L:{dist_left:.2f} | F:{dist_front:.2f} | R:{dist_right:.2f}"
        )

        linear_x, angular_z = 1.0, 0.0
        if dist_front < self.stop_dist:
            linear_x = 0.0
            if dist_left > dist_right:
                angular_z = 0.5
                self.get_logger().info("Turn left")

            else:
                angular_z = -0.5
                self.get_logger().info("Turn right")

        elif dist_front < self.brake_dist:
            self.get_logger().info("Beware: There an object...")
            linear_x, angular_z = 0.6, 0.0

        else:
            self.get_logger().info("Nothing in our way! Full Drive!")

        return linear_x, angular_z

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
