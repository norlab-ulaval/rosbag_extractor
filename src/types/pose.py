from pathlib import Path

import pandas as pd
from rosbags.highlevel import AnyReader
from tqdm import tqdm
from scipy.spatial.transform import Rotation


def extract_pose_from_rosbag(bag_file, topic_name, save_folder, args, overwrite=False):

    euler = args.get("euler", False)

    pose_data = []

    # Avoid overwriting existing files
    output_file = Path(save_folder) / (Path(save_folder).name + ".csv")
    if not overwrite and Path(output_file).exists():
        print(f"Output file {output_file} already exists. Skipping...")
        return

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting pose data from topic \"{topic_name}\" to file \"{output_file.name}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        messages = list(reader.messages(connections=connections))

        for connection, ros_time, rawdata in tqdm(messages):
            msg = reader.deserialize(rawdata, connection.msgtype)

            position = [msg.pose.position.x, msg.pose.position.y, msg.pose.position.z]
            orientation = [msg.pose.orientation.x, msg.pose.orientation.y, msg.pose.orientation.z, msg.pose.orientation.w]
            if euler:
                orientation = Rotation.from_quat(orientation).as_euler("xyz", degrees=False)

            pose_data.append(
                [
                    int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec),
                    ros_time,
                    *position,
                    *orientation
                ]
            )

        # Define the columns for the DataFrame
        columns = ["timestamp", "ros_time", "x", "y", "z"]
        columns += ["roll", "pitch", "yaw"] if euler else ["qx", "qy", "qz", "qw"]

        pose_df = pd.DataFrame(
            pose_data,
            columns=columns
        )
        pose_df.to_csv(output_file, index=False)

    print(f"Done ! Exported pose data to {output_file}")