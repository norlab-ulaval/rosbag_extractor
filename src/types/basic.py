from pathlib import Path

import pandas as pd
from rosbags.highlevel import AnyReader
from tqdm import tqdm


def extract_basic_data_from_rosbag(bag_file, topic_name, save_folder, args, overwrite=False):

    # Basic data includes : int, float, string, bool, char, etc.

    basic_data = []
    columns = []
    timestamp = None
    frame_id = None

    # Avoid overwriting existing files
    output_file = Path(save_folder) / (Path(save_folder).name + ".csv")
    if not overwrite and Path(output_file).exists():
        print(f"Output file {output_file} already exists. Skipping...")
        return

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting basic data from topic \"{topic_name}\" to file \"{output_file.name}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        columns = _init_columns(reader, connections)
        messages = list(reader.messages(connections=connections))

        for connection, ros_time, rawdata in tqdm(messages):

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

            basic_data.append(data)

        basic_df = pd.DataFrame(basic_data, columns=columns)
        basic_df.to_csv(output_file, index=False)

    print(f"Done! Exported basic data to {output_file}")


def _init_columns(reader, connections):

    if connections is None or len(connections) == 0:
        return []

    # Peek at the first message to get the columns
    connection, _, rawdata = next(reader.messages(connections=connections))
    msg = reader.deserialize(rawdata, connection.msgtype)
    msg_dict = _class_to_dict(msg)
    
    columns = ["ros_time"]
    if msg_dict.get("header"):
        columns += ["timestamp", "frame_id"]
    columns += [key for key in list(msg_dict.keys()) if key not in ["header", "__msgtype__"]]

    return columns


def _class_to_dict(obj):

    if isinstance(obj, dict):
        return {key: _class_to_dict(value) for key, value in obj.items()}
    elif hasattr(obj, "__dict__"):
        return {key: _class_to_dict(value) for key, value in obj.__dict__.items()}
    elif isinstance(obj, (list, tuple)):
        return [_class_to_dict(item) for item in obj]
    else:
        return obj
