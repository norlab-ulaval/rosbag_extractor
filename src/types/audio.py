import wave
from pathlib import Path

import numpy as np
from rosbags.highlevel import AnyReader
from rosbags.typesys import get_types_from_msg, get_typestore, Stores
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

# Register custom types with the typestore
typestore = get_typestore(Stores.LATEST)
typestore.register(get_types_from_msg(AUDIO_DATA_MSG, "audio_common_msgs/msg/AudioData"))
typestore.register(get_types_from_msg(AUDIO_DATA_STAMPED_MSG, "audio_common_msgs/msg/AudioDataStamped"))


def extract_audio_from_rosbag(bag_file, topic_name, save_folder, args, overwrite=False):

    ext = args.get("extension", "wav")
    sample_rate = args.get("sample_rate", 44100)

    # Avoid overwriting existing files
    output_file = Path(save_folder) / (Path(save_folder).name + f".{ext}")
    if not overwrite and Path(output_file).exists():
        print(f"Output file {output_file} already exists. Skipping...")
        return

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        audio_data = bytearray()
        print(f"Extracting audio data from topic \"{topic_name}\" to file \"{output_file.name}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        messages = list(reader.messages(connections=connections))
        
        for connection, _, rawdata in tqdm(messages):
            msg = reader.deserialize(rawdata, connection.msgtype)
            if connection.msgtype.endswith("AudioData"):
                audio_data.extend(msg.data)
            elif connection.msgtype.endswith("AudioDataStamped"):
                audio_data.extend(msg.audio.data)
            else:
                print(f"Unknown audio message type: {connection.msgtype}")

    if output_file.suffix == ".wav":
        with wave.open(str(output_file), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(np.frombuffer(audio_data, dtype=np.int16).tobytes())

    elif output_file.suffix == ".mp3":
        with open(output_file, "wb") as mp3_file:
            mp3_file.write(audio_data)

    else:
        print(f"Unsupported output file format: {output_file}")
        return

    print(f"Done! Exported audio data to {output_file}")
