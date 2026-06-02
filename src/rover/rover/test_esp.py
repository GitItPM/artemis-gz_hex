#joint caliberation testing
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

import serial
import math


class JointStateToESP(Node):

    def __init__(self):
        super().__init__("jointstate_to_esp")

        # -------- SERIAL --------
        self.ser = serial.Serial(
            port="/dev/ttyUSB0",
            baudrate=115200,
            timeout=1
        )

        # -------- SUBSCRIBE --------
        self.sub = self.create_subscription(
            JointState,
            "/joint_states",
            self.callback,
            10
        )

        self.get_logger().info("JointState → ESP Bridge Started")

        # -------- EXACT JOINT ORDER --------
        self.joint_order = [
            "NCCUP1_joint", "NTHIGH1_joint", "NFOOT1_joint",
            "NCCUP2_joint", "NTHIGH2_joint", "NFOOT2_joint",
            "NCCUP3_joint", "NTHIGH3_joint", "NFOOT3_joint",
            "NCCUP4_joint", "NTHIGH4_joint", "NFOOT4_joint",
            "NCCUP5_joint", "NTHIGH5_joint", "NFOOT5_joint",
            "NCCUP6_joint", "NTHIGH6_joint", "NFOOT6_joint",
        ]


    def callback(self, msg):

        joint_map = dict(zip(msg.name, msg.position))

        angles_deg = []

        for i, joint in enumerate(self.joint_order):

            if joint not in joint_map:
                self.get_logger().warn(f"{joint} missing!")
                return

            angle_rad = joint_map[joint]
            angle_deg = math.degrees(angle_rad)

            # shift to servo range
            angle_deg = 90 + angle_deg

            # clamp
            angle_deg = max(0.0, min(180.0, angle_deg))

            angles_deg.append(int(round(angle_deg)))

        # -------- SEND --------
        data = " ".join(map(str, angles_deg)) + "\n"

        try:
            self.ser.write(data.encode())
        except Exception as e:
            self.get_logger().warn(f"Serial error: {e}")

        self.get_logger().info(f"Sent: {data.strip()}")


def main(args=None):
    rclpy.init(args=args)

    node = JointStateToESP()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()