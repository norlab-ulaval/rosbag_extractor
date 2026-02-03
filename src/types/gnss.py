from pathlib import Path

import pandas as pd
from rosbags.highlevel import AnyReader
from tqdm import tqdm


def extract_gnss_from_rosbag(bag_file, topic_name, save_folder, args, overwrite=False):

    gnss_data = []

    # Avoid overwriting existing files
    output_file = Path(save_folder) / (Path(save_folder).name + ".csv")
    if not overwrite and Path(output_file).exists():
        print(f"Output file {output_file} already exists. Skipping...")
        return

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting GNSS data from topic \"{topic_name}\" to file \"{output_file.name}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, ros_time, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            gnss_data.append(
                [
                    int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec),
                    ros_time,
                    msg.latitude,
                    msg.longitude,
                    msg.altitude,
                    *msg.position_covariance
                ]
            )

        gnss_df = pd.DataFrame(gnss_data, columns=[
            "timestamp", "ros_time", "latitude", "longitude", "altitude", 
            "cov_xx", "cov_xy", "cov_xz", "cov_yx", "cov_yy", "cov_yz", "cov_zx", "cov_zy", "cov_zz"
        ])
        gnss_df.to_csv(output_file, index=False)

    print(f"Done ! Exported gnss data to {output_file}")
