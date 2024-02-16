import pandas as pd
from pathlib import Path
from tqdm import tqdm
from rosbags.highlevel import AnyReader


def extract_imu_from_rosbag(bag_file, topic_name, output_file):
        
    imu_data = []

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting IMU data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            imu_data.append([
                int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec), 
                msg.angular_velocity.x, 
                msg.angular_velocity.y, 
                msg.angular_velocity.z, 
                msg.linear_acceleration.x, 
                msg.linear_acceleration.y, 
                msg.linear_acceleration.z
            ])
            
        imu_df = pd.DataFrame(imu_data, columns=["timestamp", "gyro_x", "gyro_y", "gyro_z", "acc_x", "acc_y", "acc_z"])
        imu_df.to_csv(output_file, index=False)

    print(f"Done ! Exported images to {output_file}")