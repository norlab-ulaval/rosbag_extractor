import wave
from pathlib import Path
import numpy as np

from src.base_extractor import CSVExtractor

# Message definitions live in src/typestore.py, which is handed to the reader.
AUDIO_CHANNELS = 1
AUDIO_SAMPLE_WIDTH = 2


class AudioExtractor(CSVExtractor):
    
    def __init__(self, bag_file, topic_name, save_folder, args, overwrite=False):
        super().__init__(bag_file, topic_name, save_folder, args, overwrite)
        self.data_type = "audio"
        self.ext = args.get("extension", "wav")
        self.sample_rate = args.get("sample_rate", 44100)
        self.output_file = Path(save_folder) / (Path(save_folder).name + f".{self.ext}")
    
    def _process_message(self, msg, ros_time, msgtype):
        if msgtype.endswith("AudioData"):
            return msg.data
        if msgtype.endswith("AudioDataStamped"):
            return msg.audio.data
        print(f"Warning: Unknown audio message type: {msgtype}")
        return None
    
    def _save_data(self, data):
        audio_data = bytearray(b''.join(data))
        
        if self.output_file.suffix == ".wav":
            with wave.open(str(self.output_file), "wb") as wav_file:
                wav_file.setnchannels(AUDIO_CHANNELS)
                wav_file.setsampwidth(AUDIO_SAMPLE_WIDTH)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(np.frombuffer(audio_data, dtype=np.int16).tobytes())
        elif self.output_file.suffix == ".mp3":
            with open(self.output_file, "wb") as mp3_file:
                mp3_file.write(audio_data)
        else:
            print(f"Unsupported output file format: {self.output_file}")
            return
