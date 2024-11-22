import os
from pathlib import Path

import numpy as np
import pandas as pd
from rosbags.highlevel import AnyReader
from tqdm import tqdm




def extract_cmd_vel_from_rosbag(bag_file, topic_name, output_file):

    cmd_vel = []

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting CMD_VEL data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, ros_time, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            
            cmd_vel.append(
                [   msg.linear.x,
                    msg.angular.z,
                ]
            )

        cmd_vel_dataframe = pd.DataFrame(
            cmd_vel,
            columns=[
                "cmd_vx",
                "cmd_vyaw",
            ],
        )
        cmd_vel_dataframe.to_csv(output_file, index=False)
