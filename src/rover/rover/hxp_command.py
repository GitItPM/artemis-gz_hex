# #!/usr/bin/env python3

# import math
# import rclpy
# from rclpy.node import Node

# from sensor_msgs.msg import JointState

# import threading


# class IKController(Node):

#     def __init__(self):
#         super().__init__('ik_controller')

#         # -------- Publisher --------
#         self.publisher = self.create_publisher(
#             JointState,
#             '/joint_states',
#             10
#         )

#         # -------- Timing --------
#         self.dt = 0.1
#         self.timer = self.create_timer(self.dt, self.update)

#         self.step_time = 0.5
#         self.step_timer = 0.0
#         self.step_index = 0
#         self.num_steps = 4   # IMPORTANT: now 4 steps

#         # -------- Command --------
#         self.command = 'f'

#         # -------- Joint order --------
#         self.joint_names = [
#             "NCCUP1_joint","NTHIGH1_joint","NFOOT1_joint",
#             "NCCUP2_joint","NTHIGH2_joint","NFOOT2_joint",
#             "NCCUP3_joint","NTHIGH3_joint","NFOOT3_joint",
#             "NCCUP4_joint","NTHIGH4_joint","NFOOT4_joint",
#             "NCCUP5_joint","NTHIGH5_joint","NFOOT5_joint",
#             "NCCUP6_joint","NTHIGH6_joint","NFOOT6_joint"
#         ]

#         self.positions = [0.0]*18

#         # -------- FORWARD GAIT --------
#         self.forward_gait = {
#             1: [(77.8,77.8,120), (95.8,59.8,120), (77.8,77.8,100), (59.8,95.8,120)],
#             6: [(55,80,120), (80,80,120), (55,80,100), (30,80,120)],
#             5: [(80,55,120), (80,80,120), (80,55,100), (80,30,120)],
#             4: [(77.8,77.8,120), (59.8,95.8,120), (77.8,77.8,100), (95.8,59.8,120)],
#             3: [(55,80,120), (30,80,120), (55,80,100), (80,80,120)],
#             2: [(80,55,120), (80,30,120), (80,55,100), (80,80,120)],
#         }

#         # -------- RIGHT TURN GAIT --------
#         self.right_gait = {
#             1: [(77.8,77.8,120), (59.3,95.0,120), (77.8,77.8,100), (95.0,59.3,120)],
#             2: [(77.8,77.8,120), (59.3,95.0,120), (77.8,77.8,100), (95.0,59.3,120)],
#             3: [(77.8,77.8,120), (59.3,95.0,120), (77.8,77.8,100), (95.0,59.3,120)],
#             4: [(77.8,77.8,120), (59.3,95.0,120), (77.8,77.8,100), (95.0,59.3,120)],
#             5: [(77.8,77.8,120), (59.3,95.0,120), (77.8,77.8,100), (95.0,59.3,120)],
#             6: [(77.8,77.8,120), (59.3,95.0,120), (77.8,77.8,100), (95.0,59.3,120)],
#         }

#         # -------- Tripod groups --------
#         self.tripod_A = [1,3,5]
#         self.tripod_B = [2,4,6]

#         # -------- Start input thread --------
#         threading.Thread(target=self.keyboard_input, daemon=True).start()

#         self.get_logger().info("Controller started (f/b/l/r from terminal)")

#     # -------- Keyboard Input --------
#     def keyboard_input(self):
#         while True:
#             cmd = input("Enter command (f/b/l/r): ").strip().lower()
#             if cmd in ['f','b','l','r']:
#                 self.command = cmd
#                 print(f"Switched to: {cmd}")

#     # -------- Gait Selection --------
#     def get_gait(self):

#         if self.command == 'f':
#             return self.forward_gait

#         elif self.command == 'b':
#             return {leg: list(reversed(points)) for leg, points in self.forward_gait.items()}

#         elif self.command == 'r':
#             return self.right_gait

#         elif self.command == 'l':
#             return {leg: list(reversed(points)) for leg, points in self.right_gait.items()}

#         return self.forward_gait

#     # -------- Inverse Kinematics --------
#     def inverse_kinematics(self, x, y, z):

#         J1L = 35.0
#         J2L = 75.0
#         J3L = 160.0

#         J1 = math.atan2(x, y)

#         H = math.sqrt(x*x + y*y)
#         L = math.sqrt(z*z + (H - J1L)*(H - J1L))

#         def clamp(v):
#             return max(-1.0, min(1.0, v))

#         J3 = 1.57 - math.acos(clamp((J3L*J3L + J2L*J2L - L*L)/(2*J2L*J3L)))

#         B = math.acos(clamp((L*L + J2L*J2L - J3L*J3L)/(2*L*J2L)))
#         A = math.atan2(z, H - J1L)

#         J2 = (B - A)

#         return J1, J2, J3

#     # -------- Gait update --------
#     def update_gait(self):

#         self.step_timer += self.dt

#         if self.step_timer >= self.step_time:
#             self.step_timer = 0.0
#             self.step_index = (self.step_index + 1) % self.num_steps

#     # -------- Main Loop --------
#     def update(self):

#         self.update_gait()
#         gait = self.get_gait()

#         for leg_id in range(1,7):

#             if leg_id in self.tripod_A:
#                 idx = self.step_index
#             else:
#                 idx = (self.step_index + self.num_steps//2) % self.num_steps

#             x, y, z = gait[leg_id][idx]

#             q1, q2, q3 = self.inverse_kinematics(x, y, z)

#             base = (leg_id-1)*3
#             self.positions[base]   = q1
#             self.positions[base+1] = q2
#             self.positions[base+2] = q3

#         self.publish_joint_states()

#     # -------- Publish --------
#     # def publish_trajectory(self):

#     #     msg = JointTrajectory()
#     #     msg.joint_names = self.joint_names

#     #     point = JointTrajectoryPoint()
#     #     point.positions = self.positions
#     #     point.time_from_start.sec = 1

#     #     msg.points.append(point)
#     #     self.publisher.publish(msg)

#     def publish_joint_states(self):

#         msg = JointState()
#         # Timestamp
#         msg.header.stamp = self.get_clock().now().to_msg()
#         # Joint names
#         msg.name = self.joint_names
#         # Joint angles
#         msg.position = self.positions
#         self.publisher.publish(msg)


# def main(args=None):

#     rclpy.init(args=args)
#     node = IKController()
#     rclpy.spin(node)

#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node

# from trajectory_msgs.msg import JointTrajectory
# from trajectory_msgs.msg import JointTrajectoryPoint
from sensor_msgs.msg import JointState

import threading


class IKController(Node):

    def __init__(self):
        super().__init__('ik_controller')

        # -------- Publisher --------
        # self.publisher = self.create_publisher(
        #     JointTrajectory,
        #     '/hexapod_controller/joint_trajectory',
        #     10
        # )
        self.publisher = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        # -------- Timing --------
        self.dt = 0.1
        self.timer = self.create_timer(self.dt, self.update)

        self.step_time = 0.25
        self.step_timer = 0.0
        self.step_index = 0
        self.num_steps = 4   # IMPORTANT: now 4 steps

        # -------- Command --------
        self.command = 'f'

        # -------- Joint order --------
        self.joint_names = [
            "NCCUP1_joint","NTHIGH1_joint","NFOOT1_joint",
            "NCCUP2_joint","NTHIGH2_joint","NFOOT2_joint",
            "NCCUP3_joint","NTHIGH3_joint","NFOOT3_joint",
            "NCCUP4_joint","NTHIGH4_joint","NFOOT4_joint",
            "NCCUP5_joint","NTHIGH5_joint","NFOOT5_joint",
            "NCCUP6_joint","NTHIGH6_joint","NFOOT6_joint"
        ]

        self.positions = [0.0]*18

        # -------- FORWARD GAIT --------
        self.forward_gait = {
            1: [(77.8,77.8,150), (95.8,59.8,150), (77.8,77.8,100), (59.8,95.8,150)],
            6: [(55,80,150), (80,80,150), (55,80,100), (30,80,150)],
            5: [(80,55,150), (80,80,150), (80,55,100), (80,30,150)],
            4: [(77.8,77.8,150), (59.8,95.8,150), (77.8,77.8,100), (95.8,59.8,150)],
            3: [(55,80,150), (30,80,150), (55,80,100), (80,80,150)],
            2: [(80,55,150), (80,30,150), (80,55,100), (80,80,150)],
        }

        # -------- RIGHT TURN GAIT --------
        self.right_gait = {
            1: [(77.8,77.8,150), (59.3,95.0,150), (77.8,77.8,100), (95.0,59.3,150)],
            2: [(77.8,77.8,150), (59.3,95.0,150), (77.8,77.8,100), (95.0,59.3,150)],
            3: [(77.8,77.8,150), (59.3,95.0,150), (77.8,77.8,100), (95.0,59.3,150)],
            4: [(77.8,77.8,150), (59.3,95.0,150), (77.8,77.8,100), (95.0,59.3,150)],
            5: [(77.8,77.8,150), (59.3,95.0,150), (77.8,77.8,100), (95.0,59.3,150)],
            6: [(77.8,77.8,150), (59.3,95.0,150), (77.8,77.8,100), (95.0,59.3,150)],
        }

        # -------- Tripod groups --------
        self.tripod_A = [1,3,5]
        self.tripod_B = [2,4,6]

        # -------- Start input thread --------
        threading.Thread(target=self.keyboard_input, daemon=True).start()

        self.get_logger().info("Controller started (f/b/l/r from terminal)")

    # -------- Keyboard Input --------
    def keyboard_input(self):
        while True:
            cmd = input("Enter command (f/b/l/r): ").strip().lower()
            if cmd in ['f','b','l','r']:
                self.command = cmd
                print(f"Switched to: {cmd}")

    # -------- Gait Selection --------
    def get_gait(self):

        if self.command == 'f':
            return self.forward_gait

        elif self.command == 'b':
            return {leg: list(reversed(points)) for leg, points in self.forward_gait.items()}

        elif self.command == 'r':
            return self.right_gait

        elif self.command == 'l':
            return {leg: list(reversed(points)) for leg, points in self.right_gait.items()}

        return self.forward_gait

    # -------- Inverse Kinematics --------
    def inverse_kinematics(self, x, y, z):

        J1L = 35.0
        J2L = 75.0
        J3L = 160.0

        J1 = math.atan2(x, y)

        H = math.sqrt(x*x + y*y)
        L = math.sqrt(z*z + (H - J1L)*(H - J1L))

        def clamp(v):
            return max(-1.0, min(1.0, v))

        J3 = 1.57 - math.acos(clamp((J3L*J3L + J2L*J2L - L*L)/(2*J2L*J3L)))

        B = math.acos(clamp((L*L + J2L*J2L - J3L*J3L)/(2*L*J2L)))
        A = math.atan2(z, H - J1L)

        J2 = (B - A)

        return J1, J2, J3

    # -------- Gait update --------
    def update_gait(self):

        self.step_timer += self.dt

        if self.step_timer >= self.step_time:
            self.step_timer = 0.0
            self.step_index = (self.step_index + 1) % self.num_steps

    # -------- Main Loop --------
    def update(self):

        self.update_gait()
        gait = self.get_gait()

        for leg_id in range(1,7):

            if leg_id in self.tripod_A:
                idx = self.step_index
            else:
                idx = (self.step_index + self.num_steps//2) % self.num_steps

            x, y, z = gait[leg_id][idx]

            q1, q2, q3 = self.inverse_kinematics(x, y, z)

            base = (leg_id-1)*3
            self.positions[base]   = q1
            self.positions[base+1] = q2
            self.positions[base+2] = q3

        # self.publish_trajectory()
        self.publish_joint_states()

    # -------- Publish --------
    # def publish_trajectory(self):

    #     msg = JointTrajectory()
    #     msg.joint_names = self.joint_names

    #     point = JointTrajectoryPoint()
    #     point.positions = self.positions
    #     point.time_from_start.sec = 1

    #     msg.points.append(point)
    #     self.publisher.publish(msg)

    def publish_joint_states(self):
        msg = JointState()
        # timestamp
        msg.header.stamp = self.get_clock().now().to_msg()
        # joint names
        msg.name = self.joint_names
        # joint positions
        msg.position = self.positions
        self.publisher.publish(msg)


def main(args=None):

    rclpy.init(args=args)
    node = IKController()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()