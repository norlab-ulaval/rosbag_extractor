import wave
from pathlib import Path

import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import get_types_from_msg, register_types
from tqdm import tqdm

# Audio message
AUDIO_DATA_MSG = """
uint8[] data
"""

# Audio stamped message
AUDIO_DATA_STAMPED_MSG = """
std_msgs/Header header
audio_common_msgs/AudioData audio
"""

register_types(get_types_from_msg(AUDIO_DATA_MSG, "audio_common_msgs/msg/AudioData"))
register_types(get_types_from_msg(AUDIO_DATA_STAMPED_MSG, "audio_common_msgs/msg/AudioDataStamped"))


def extract_audio_from_rosbag(bag_file, topic_name, output_file, args):

    sample_rate = 44100
    if "sample_rate" in args and args["sample_rate"]:
        sample_rate = int(args["sample_rate"])

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        audio_data = bytearray()
        print(f"Extracting audio data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            if connection.msgtype == "audio_common_msgs/msg/AudioData":
                audio_data.extend(msg.data)
            elif connection.msgtype == "audio_common_msgs/msg/AudioDataStamped":
                audio_data.extend(msg.audio.data)
            else:
                print(f"Unknown audio message type: {connection.msgtype}")

    if output_file.endswith(".wav"):
        with wave.open(output_file, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(np.frombuffer(audio_data, dtype=np.int16).tobytes())

    elif output_file.endswith(".mp3"):
        with open(output_file, "wb") as mp3_file:
            mp3_file.write(audio_data)

    else:
        print(f"Unsupported output file format: {output_file}")
