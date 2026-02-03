import math
from pathlib import Path

import pandas as pd
from rosbags.highlevel import AnyReader
from tqdm import tqdm
from scipy.spatial.transform import Rotation

## NOTE: THIS ONLY EXTRACTS THE POSE IN THE ODOMETRY MESSAGE, NOT THE COVARIANCE NOR THE TWIST


def extract_odom_from_rosbag(bag_file, topic_name, save_folder, args, overwrite=False):

    euler = args.get("euler", False)

    odom_data = []

    # Avoid overwriting existing files
    output_file = Path(save_folder) / (Path(save_folder).name + ".csv")
    if not overwrite and Path(output_file).exists():
        print(f"Output file {output_file} already exists. Skipping...")
        return

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting odometry data from topic \"{topic_name}\" to file \"{output_file.name}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]

        for connection, ros_time, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)

            position = [msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z]
            orientation = [msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w]
            if euler:
                orientation = Rotation.from_quat(orientation).as_euler("xyz", degrees=False)
            linear_velocity = [msg.twist.twist.linear.x, msg.twist.twist.linear.y, msg.twist.twist.linear.z]
            angular_velocity = [msg.twist.twist.angular.x, msg.twist.twist.angular.y, msg.twist.twist.angular.z]

            odom_data.append(
                [
                    int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec),
                    ros_time,
                    *position,
                    *orientation,
                    *linear_velocity,
                    *angular_velocity
                ]
            )

        # Define the columns for the DataFrame
        columns = ["timestamp", "ros_time", "x", "y", "z"]
        columns += ["roll", "pitch", "yaw"] if euler else ["qx", "qy", "qz", "qw"]
        columns += ["vel_x", "vel_y", "vel_z", "vel_roll", "vel_pitch", "vel_yaw"]

        odom_df = pd.DataFrame(
            odom_data,
            columns=columns
        )
        odom_df.to_csv(output_file, index=False)

    print(f"Done ! Exported odometry data to {output_file}")
