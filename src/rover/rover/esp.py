# #!/usr/bin/env python3

# import rclpy
# from rclpy.node import Node
# from trajectory_msgs.msg import JointTrajectory

# import serial
# import math


# class ESPBridge(Node):

#     def __init__(self):
#         super().__init__("esp_bridge")

#         # -------- SERIAL --------
#         self.port = "/dev/ttyUSB0"
#         self.baud = 115200

#         self.connect_serial()

#         # -------- SUBSCRIBE --------
#         self.sub = self.create_subscription(
#             JointTrajectory,
#             "/hexapod_controller/joint_trajectory",
#             self.callback,
#             10
#         )

#         self.get_logger().info("ESP Bridge (FINAL - RAW ANGLES) Started")

#     # -------- SERIAL CONNECT --------
#     def connect_serial(self):
#         try:
#             self.ser = serial.Serial(self.port, self.baud, timeout=1)
#             self.get_logger().info(f"Connected to {self.port}")
#         except Exception as e:
#             self.get_logger().error(f"Serial connection failed: {e}")
#             self.ser = None

#     # -------- SAFE WRITE --------
#     def send_data(self, data):
#         if self.ser is None:
#             self.connect_serial()
#             return

#         try:
#             self.ser.write(data.encode())
#         except Exception as e:
#             self.get_logger().warn(f"Serial error: {e}")
#             try:
#                 self.ser.close()
#             except:
#                 pass
#             self.ser = None

#     # -------- CALLBACK --------
#     def callback(self, msg):

#         if not msg.points:
#             return

#         positions = msg.points[0].positions

#         # -------- EXPECT EXACTLY 18 --------
#         if len(positions) != 18:
#             self.get_logger().warn(f"Expected 18 joints, got {len(positions)}")
#             return

#         # -------- RAD → DEG ONLY --------
#         #angles_deg = [round(math.degrees(p), 2) for p in positions]
#         angles_deg = []

#         for i in range(18):

#             angle_deg = math.degrees(positions[i])

#             joint_type = i % 3

#             if joint_type == 0:       # J1
#                 angle_deg += 45
#             else:                     # J2, J3
#                 angle_deg += 90

#             # optional safety clamp
#             angle_deg = max(0.0, min(180.0, angle_deg))

#             angles_deg.append(round(angle_deg, 2))

#         # -------- FORMAT --------
#         data = " ".join(map(str, angles_deg)) + "\n"

#         # -------- SEND --------
#         self.send_data(data)

#         # Debug
#         self.get_logger().info(f"Sent: {data.strip()}")


# def main(args=None):
#     rclpy.init(args=args)

#     node = ESPBridge()
#     rclpy.spin(node)

#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == "__main__":
#     main()
    
# #!/usr/bin/env python3




# import rclpy
# from rclpy.node import Node
# from sensor_msgs.msg import JointState

# import serial
# import math


# class JointStateToESP(Node):

#     def __init__(self):
#         super().__init__("jointstate_to_esp")

#         # -------- SERIAL --------
#         self.port = "/dev/ttyUSB0"
#         self.baud = 115200
#         self.connect_serial()

#         # -------- SUBSCRIBE --------
#         self.sub = self.create_subscription(
#             JointState,
#             "/joint_states",
#             self.callback,
#             10
#         )

#         self.get_logger().info("JointState → ESP Bridge (FINAL) Started")

#         # -------- REQUIRED ORDER (VERY IMPORTANT) --------
#         self.joint_order = [
#             "NCCUP1_joint","NTHIGH1_joint","NFOOT1_joint",
#             "NCCUP2_joint","NTHIGH2_joint","NFOOT2_joint",
#             "NCCUP3_joint","NTHIGH3_joint","NFOOT3_joint",
#             "NCCUP4_joint","NTHIGH4_joint","NFOOT4_joint",
#             "NCCUP5_joint","NTHIGH5_joint","NFOOT5_joint",
#             "NCCUP6_joint","NTHIGH6_joint","NFOOT6_joint"
#         ]

#     # -------- SERIAL --------
#     def connect_serial(self):
#         try:
#             self.ser = serial.Serial(self.port, self.baud, timeout=1)
#             self.get_logger().info(f"Connected to {self.port}")
#         except Exception as e:
#             self.get_logger().error(f"Serial failed: {e}")
#             self.ser = None

#     def send_data(self, data):
#         if self.ser is None:
#             self.connect_serial()
#             return

#         try:
#             self.ser.write(data.encode())
#         except Exception as e:
#             self.get_logger().warn(f"Serial error: {e}")
#             try:
#                 self.ser.close()
#             except:
#                 pass
#             self.ser = None

#     # -------- CALLBACK --------
#     def callback(self, msg):

#         joint_map = dict(zip(msg.name, msg.position))

#         angles_deg = []

#         for i, joint in enumerate(self.joint_order):

#             if joint not in joint_map:
#                 self.get_logger().warn(f"{joint} missing!")
#                 return

#             angle_deg = math.degrees(joint_map[joint])

#             # -------- YOUR OFFSET LOGIC --------
#             if i % 3 == 0:      # J1
#                 angle_deg += 45
#             else:               # J2, J3
#                 angle_deg += 90

#             angle_deg = max(0.0, min(180.0, angle_deg))

#             angles_deg.append(int(round(angle_deg)))

#         data = " ".join(map(str, angles_deg)) + "\n"

#         self.send_data(data)

#         self.get_logger().info(f"Sent: {data.strip()}")


# def main(args=None):
#     rclpy.init(args=args)

#     node = JointStateToESP()
#     rclpy.spin(node)

#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == "__main__":
#     main()




#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

import serial
import math


class HexapodJointStateToESP(Node):

    def __init__(self):

        super().__init__("hexapod_jointstate_to_esp")

        # =========================================================
        # SERIAL
        # =========================================================

        self.port = "/dev/ttyUSB0"
        self.baud = 115200

        self.connect_serial()

        # =========================================================
        # SUBSCRIBER
        # =========================================================

        self.sub = self.create_subscription(
            JointState,
            "/joint_states",
            self.callback,
            10
        )

        self.get_logger().info("Hexapod JointState → ESP Bridge Started")

        # =========================================================
        # EXACT JOINT ORDER
        # MUST MATCH ESP ORDER
        # =========================================================

        self.joint_order = [

            "NCCUP1_joint", "NTHIGH1_joint", "NFOOT1_joint",
            "NCCUP2_joint", "NTHIGH2_joint", "NFOOT2_joint",
            "NCCUP3_joint", "NTHIGH3_joint", "NFOOT3_joint",

            "NCCUP4_joint", "NTHIGH4_joint", "NFOOT4_joint",
            "NCCUP5_joint", "NTHIGH5_joint", "NFOOT5_joint",
            "NCCUP6_joint", "NTHIGH6_joint", "NFOOT6_joint"
        ]

        # =========================================================
        # JOINT OFFSETS
        # Tune these during calibration
        # =========================================================

        self.offsets = {

            # -------- LEG 1 --------
            "NCCUP1_joint": 45,
            "NTHIGH1_joint": 90,
            "NFOOT1_joint": 90,

            # -------- LEG 2 --------
            "NCCUP2_joint": 45,
            "NTHIGH2_joint": 90,
            "NFOOT2_joint": 90,

            # -------- LEG 3 --------
            "NCCUP3_joint": 45,
            "NTHIGH3_joint": 90,
            "NFOOT3_joint": 90,

            # -------- LEG 4 --------
            "NCCUP4_joint": 45,
            "NTHIGH4_joint": 90,
            "NFOOT4_joint": 90,

            # -------- LEG 5 --------
            "NCCUP5_joint": 45,
            "NTHIGH5_joint": 90,
            "NFOOT5_joint": 90,

            # -------- LEG 6 --------
            "NCCUP6_joint": 45,
            "NTHIGH6_joint": 90,
            "NFOOT6_joint": 90,
        }

        # =========================================================
        # JOINT INVERSION
        # True = invert direction
        # =========================================================

        self.invert = {

            # -------- LEG 1 --------
            "NCCUP1_joint": False,
            "NTHIGH1_joint": False,
            "NFOOT1_joint": False,

            # -------- LEG 2 --------
            "NCCUP2_joint": False,
            "NTHIGH2_joint": False,
            "NFOOT2_joint": False,

            # -------- LEG 3 --------
            "NCCUP3_joint": False,
            "NTHIGH3_joint": False,
            "NFOOT3_joint": False,

            # -------- LEG 4 --------
            "NCCUP4_joint": True,
            "NTHIGH4_joint": True,
            "NFOOT4_joint": True,

            # -------- LEG 5 --------
            "NCCUP5_joint": True,
            "NTHIGH5_joint": True,
            "NFOOT5_joint": True,

            # -------- LEG 6 --------
            "NCCUP6_joint": True,
            "NTHIGH6_joint": True,
            "NFOOT6_joint": True,
        }

        # =========================================================
        # SERVO LIMITS
        # =========================================================

        self.min_angle = 0
        self.max_angle = 180

    # =============================================================
    # SERIAL CONNECTION
    # =============================================================

    def connect_serial(self):

        try:

            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=1
            )

            self.get_logger().info(f"Connected to {self.port}")

        except Exception as e:

            self.get_logger().error(f"Serial connection failed: {e}")
            self.ser = None

    # =============================================================
    # SAFE SERIAL SEND
    # =============================================================
    def send_data(self, data):
        if self.ser is None:
            self.connect_serial()
            return

        try:
            self.ser.write(data.encode())

        except Exception as e:
            self.get_logger().warn(f"Serial error: {e}")
            try:
                self.ser.close()
            except:
                pass
            
            self.ser = None
    # =============================================================
    # MAIN CALLBACK
    # =============================================================
    def callback(self, msg):
        # ---------------------------------------------------------
        # CREATE JOINT MAP
        # ---------------------------------------------------------
        joint_map = dict(zip(msg.name, msg.position))
        servo_angles = []
        # ---------------------------------------------------------
        # PROCESS ALL JOINTS
        # ---------------------------------------------------------
        for joint in self.joint_order:
            # -----------------------------------------------------
            # VERIFY JOINT EXISTS
            # -----------------------------------------------------
            if joint not in joint_map:

                self.get_logger().warn(f"{joint} missing!")
                return
            # -----------------------------------------------------
            # RAD → DEG
            # -----------------------------------------------------
            angle_deg = math.degrees(joint_map[joint])
            # -----------------------------------------------------
            # INVERSION
            # -----------------------------------------------------
            if self.invert[joint]:
                angle_deg = -angle_deg
            # -----------------------------------------------------
            # OFFSET
            # -----------------------------------------------------
            angle_deg += self.offsets[joint]
            # -----------------------------------------------------
            # SAFETY CLAMP
            # -----------------------------------------------------
            angle_deg = max(
                self.min_angle,
                min(self.max_angle, angle_deg)
            )
            # -----------------------------------------------------
            # STORE
            # -----------------------------------------------------
            servo_angles.append(int(round(angle_deg)))
        # ---------------------------------------------------------
        # FORMAT SERIAL DATA
        # ---------------------------------------------------------
        data = " ".join(map(str, servo_angles)) + "\n"
        # ---------------------------------------------------------
        # SEND TO ESP
        # ---------------------------------------------------------
        self.send_data(data)
        # ---------------------------------------------------------
        # DEBUG
        # ---------------------------------------------------------
        self.get_logger().info(f"Sent: {data.strip()}")


# =============================================================
# MAIN
# =============================================================

def main(args=None):
    rclpy.init(args=args)
    node = HexapodJointStateToESP()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()