import os
from pathlib import Path

import numpy as np
import pandas as pd
from rosbags.highlevel import AnyReader
from tqdm import tqdm

DATA_TYPES = {
    1: np.int8,
    2: np.uint8,
    3: np.int16,
    4: np.uint16,
    5: np.int32,
    6: np.uint32,
    7: np.float32,
    8: np.float64,
}


def extract_point_clouds_from_rosbag(bag_file, topic_name, save_folder, args, overwrite=False):

    # Avoid overwriting existing files
    if not overwrite and Path(save_folder).exists() and any(Path(save_folder).iterdir()):
        print(f"Output folder {save_folder} already exists and not empty. Skipping...")
        return

    with AnyReader([Path(bag_file)]) as reader:
        print(f"Extracting point clouds from topic \"{topic_name}\" to folder \"{save_folder.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            timestamp = msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec
            df = pd.DataFrame()
            data = np.frombuffer(msg.data, dtype=np.uint8).reshape(-1, msg.point_step)
            for field in msg.fields:
                type = DATA_TYPES[field.datatype]
                n_bytes = np.dtype(type).itemsize
                df[field.name] = data[:, field.offset : field.offset + n_bytes].flatten().view(dtype=type)
            df.to_csv(os.path.join(save_folder, f"{int(timestamp):d}.csv"), index=False)

    print(f"Done! Extracted point clouds to {save_folder}")
