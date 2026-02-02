import wave
from pathlib import Path

import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import get_types_from_msg, register_types
from tqdm import tqdm
import pandas as pd


MTT_TACHOMETER = """
std_msgs/Header header

float64 main_sensor_temp_a
float64 main_sensor_temp_b

uint16 tachometer_instant     
uint32 tachometer_cumulative  

float64 speed_ms    
float64 speed_kmh   

float64 distance_km 
string direction    

float64 steer_cmd    
"""

register_types(get_types_from_msg(MTT_TACHOMETER, "mtt_msgs/msg/MttTachometerData"))


def extract_audio_from_rosbag(bag_file, topic_name, output_file):

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        audio_data = bytearray()
        print(f"Extracting audio data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        mtt_data = []
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            if connection.msgtype == "mtt_msgs/msg/MttTachometerData":
                audio_data.extend(msg.data)
                mtt_data.append(
                [
                    int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec),
                    msg.tachometer_instant,
                    msg.tachometer_cumulative,
                    msg.speed_ms,
                    msg.speed_kmh,
                    msg.distance_km,
                    msg.direction,
                    msg.steer_cmd
                ]
                )
            else:
                print(f"Unknown audio message type: {connection.msgtype}")
        mtt_df = pd.DataFrame(
            mtt_data,
            columns=[
                "timestamp",
                "tachometer_instant",
                "tachometer_cumulative",
                "speed_ms",
                "speed_kmh",
                "distance_km",
                "direction",
                "steer_cmd",
            ],
        )
        mtt_df.to_csv(output_file, index=False)
    
    