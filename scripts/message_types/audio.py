import pandas as pd
from pathlib import Path
from tqdm import tqdm
from rosbags.highlevel import AnyReader

from rosbags.typesys import get_types_from_msg, register_types

# Audio message
AUDIO_DATA_MSG = """
uint8[] data
"""

# Audio stamped message
AUDIO_DATA_STAMPED_MSG = """
std_msgs/Header header
audio_common_msgs/AudioData audio
"""

register_types(get_types_from_msg(AUDIO_DATA_MSG, 'audio_common_msgs/msg/AudioData'))
register_types(get_types_from_msg(AUDIO_DATA_STAMPED_MSG, 'audio_common_msgs/msg/AudioDataStamped'))


def extract_audio_from_rosbag(bag_file, topic_name, output_file):

    mp3_file = open(output_file, 'wb')

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting audio data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            if connection.msgtype == "audio_common_msgs/msg/AudioData":
                mp3_file.write(b''.join(msg.data))
            elif connection.msgtype == "audio_common_msgs/msg/AudioDataStamped":
                mp3_file.write(b''.join(msg.audio.data))
            else:
                print(f"Unknown audio message type: {connection.msgtype}")
        
    mp3_file.close()
    print(f"Done ! Exported audio to {output_file}")