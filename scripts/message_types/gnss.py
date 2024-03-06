import pandas as pd
from pathlib import Path
from tqdm import tqdm
from rosbags.highlevel import AnyReader


def extract_gnss_from_rosbag(bag_file, topic_name, output_file):
        
    gnss_data = []

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting GNSS data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, ros_time, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            gnss_data.append([
                int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec),
                ros_time, 
                msg.latitude, 
                msg.longitude, 
                msg.altitude
            ])
            
        imu_df = pd.DataFrame(gnss_data, columns=["timestamp", "ros_time", "latitude", "longitude", "altitude"])
        imu_df.to_csv(output_file, index=False)

    print(f"Done ! Exported images to {output_file}")