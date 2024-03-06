import pandas as pd
from pathlib import Path
from tqdm import tqdm
from rosbags.highlevel import AnyReader


def extract_basic_data_from_rosbag(bag_file, topic_name, output_file):

    # Basic data includes : int, float, string, bool, char, etc.
        
    basic_data = []

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting basic data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, ros_time, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            basic_data.append([
                ros_time, 
                msg.data
            ])
            
        basic_df = pd.DataFrame(basic_data, columns=["ros_time", "data"])
        basic_df.to_csv(output_file, index=False)

    print(f"Done ! Exported basic data to {output_file}")