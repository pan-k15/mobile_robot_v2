#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
import tf2_ros

class OdomToTF(Node):
    def __init__(self):
        super().__init__('odom_to_tf')
        # TF broadcaster
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        # Subscribe to the odometry topic from Gazebo diff-drive plugin
        self.sub = self.create_subscription(
            Odometry,
            'odom',  # Topic from your URDF plugin
            self.odom_callback,
            10
        )

    def odom_callback(self, msg):
        # Create a TransformStamped message
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = 'odom'          # Parent frame
        t.child_frame_id = 'base_footprint' # Child frame
        # Copy position
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        # Copy orientation
        t.transform.rotation = msg.pose.pose.orientation
        # Publish the transform
        self.tf_broadcaster.sendTransform(t)

def main():
    rclpy.init()
    node = OdomToTF()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
