import math
from pathlib import Path

import pandas as pd
from rosbags.highlevel import AnyReader
from tqdm import tqdm
from scipy.spatial.transform import Rotation


def extract_imu_from_rosbag(bag_file, topic_name, save_folder, args, overwrite=False):

    euler = args.get("euler", False)

    imu_data = []

    # Avoid overwriting existing files
    output_file = Path(save_folder) / (Path(save_folder).name + ".csv")
    if not overwrite and Path(output_file).exists():
        print(f"Output file {output_file} already exists. Skipping...")
        return

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting IMU data from topic \"{topic_name}\" to file \"{output_file.name}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]

        for connection, ros_time, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)

            orientation = [msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w]
            if euler:
                orientation = Rotation.from_quat(orientation).as_euler("xyz", degrees=False)
            angular_velocity = [msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z]
            linear_acceleration = [msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z]

            imu_data.append(
                [
                    int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec),
                    ros_time,
                    *orientation,
                    *angular_velocity,
                    *linear_acceleration
                ]
            )

        columns = ["timestamp", "ros_time"]
        columns += ["roll", "pitch", "yaw"] if euler else ["qx", "qy", "qz", "qw"]
        columns += ["gyro_x", "gyro_y", "gyro_z", "acc_x", "acc_y", "acc_z"]

        imu_df = pd.DataFrame(
            imu_data,
            columns=columns,
        )
        imu_df.to_csv(output_file, index=False)

    print(f"Done ! Exported imu data to {output_file}")
