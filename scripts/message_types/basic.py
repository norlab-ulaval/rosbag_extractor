import pandas as pd
from pathlib import Path
from tqdm import tqdm
from rosbags.highlevel import AnyReader


def extract_basic_data_from_rosbag(bag_file, topic_name, output_file):

    # Basic data includes : int, float, string, bool, char, etc.
        
    basic_data = []
    columns = []  
    first = True
    timestamp = None
    frame_id = None

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting basic data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, ros_time, rawdata in tqdm(reader.messages(connections=connections)):

            msg = reader.deserialize(rawdata, connection.msgtype)
            msg_dict = _class_to_dict(msg)

            # Add the header information if available
            if msg_dict.get("header"):
                timestamp = int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec)
                frame_id = msg.header.frame_id
                data = [ros_time, timestamp, frame_id]
            else:
                data = [ros_time]

            # Add the rest of the data
            for key, value in msg_dict.items():
                if key not in ["header", "__msgtype__"]:
                    data.append(value)

            # Initialize the DF columns
            if first:
                columns = _init_columns(msg_dict)
                first = False
            
            basic_data.append(data)
            
        basic_df = pd.DataFrame(basic_data, columns=columns)
        basic_df.to_csv(output_file, index=False)

    print(f"Done ! Exported basic data to {output_file}")


def _class_to_dict(obj):
    if isinstance(obj, dict):
        return {key: _class_to_dict(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):
        return {key: _class_to_dict(value) for key, value in obj.__dict__.items()}
    elif isinstance(obj, (list, tuple)):
        return [_class_to_dict(item) for item in obj]
    else:
        return obj
    

def _init_columns(msg_dict):
    columns = ["ros_time"]
    if msg_dict.get("header"):
        columns += ["timestamp", "frame_id"]
    columns += [key for key in list(msg_dict.keys()) if key not in ["header", "__msgtype__"]]
    return columns