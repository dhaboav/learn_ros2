#!/usr/bin/env python3
import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage


class Camera(Node):
    def __init__(self):
        super().__init__("camera")
        self._image_subs = self.create_subscription(
            CompressedImage,
            "/camera/image_raw/compressed",
            self.camera_callback,
            qos_profile_sensor_data,
        )

        self._image_pubs = self.create_publisher(
            CompressedImage, "/camera/process_image/compressed", 10
        )

        self.bridge = CvBridge()
        self.lower_gray = np.array([0, 0, 160])
        self.upper_gray = np.array([179, 255, 255])
        self.get_logger().info("Camera Control has been started")

    def detect_object(self, img):
        """Evaluates processed LiDAR zones to determine safe robot velocities.
        Args:
            img (any): An image from OpenCV.

        Returns:
            any: (output_frame) frame with object detection.
        """
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        color_mask = cv2.inRange(hsv, self.lower_gray, self.upper_gray)
        inv_mask = cv2.bitwise_not(color_mask)
        contours, _ = cv2.findContours(
            inv_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        output_frame = img.copy()

        # Object detection with color
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                M = cv2.moments(cnt)

                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    # 4. Draw for each object
                    cv2.drawContours(output_frame, [cnt], -1, (0, 255, 0), 2)
                    cv2.circle(output_frame, (cx, cy), 5, (0, 0, 255), -1)

                    cv2.putText(
                        output_frame,
                        f"{cx},{cy}",
                        (cx - 20, cy - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 255, 255),
                        1,
                    )

        return output_frame

    def camera_callback(self, msg: CompressedImage):
        """Callback for image subs"""
        try:
            frame = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding="bgr8")
            if frame is not None:
                result = self.detect_object(frame)
                publish_msg = self.bridge.cv2_to_compressed_imgmsg(result)
                publish_msg.header = msg.header
                publish_msg.format = msg.format
                self._image_pubs.publish(publish_msg)

            else:
                self.get_logger().warn("Failed to decode compressed image")

        except Exception as e:
            self.get_logger().error(f"Error in camera_callback: {str(e)}")


def main(args=None):
    rclpy.init(args=args)
    node = Camera()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
