import math
from pathlib import Path

import pandas as pd
from rosbags.highlevel import AnyReader
from tqdm import tqdm

## NOTE: THIS ONLY EXTRACTS THE POSE IN THE ODOMETRY MESSAGE, NOT THE COVARIANCE NOR THE TWIST


def extract_odom_from_rosbag(bag_file, topic_name, output_file):

    odom_data = []

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting odometry data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, ros_time, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            quat = msg.pose.pose.orientation
            roll, pitch, yaw = euler_from_quaternion(quat.x, quat.y, quat.z, quat.w)
            odom_data.append(
                [
                    int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec),
                    ros_time,
                    msg.pose.pose.position.x,
                    msg.pose.pose.position.y,
                    msg.pose.pose.position.z,
                    roll,
                    pitch,
                    yaw,
                    msg.twist.twist.linear.x,
                    msg.twist.twist.linear.y,
                    msg.twist.twist.linear.z,
                    msg.twist.twist.angular.x,
                    msg.twist.twist.angular.y,
                    msg.twist.twist.angular.z,
                ]
            )

        odom_df = pd.DataFrame(
            odom_data,
            columns=[
                "timestamp",
                "ros_time",
                "x",
                "y",
                "z",
                "roll",
                "pitch",
                "yaw",
                "vel_x",
                "vel_y",
                "vel_z",
                "vel_roll",
                "vel_pitch",
                "vel_yaw",
            ],
        )
        odom_df.to_csv(output_file, index=False)


def euler_from_quaternion(x, y, z, w):

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)

    return roll_x, pitch_y, yaw_z  # in radians
