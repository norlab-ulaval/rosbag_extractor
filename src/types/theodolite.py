from src.base_extractor import CSVExtractor
from src.utils import extract_timestamp


class TheodoliteExtractor(CSVExtractor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "theodolite"

    def _process_message(self, msg, ros_time, msgtype):
        return {
            "timestamp": extract_timestamp(msg),
            "ros_time": ros_time,
            "theodolite_timestamp": int(msg.theodolite_time.sec * 1e9 + msg.theodolite_time.nanosec),
            "theodolite_id": msg.theodolite_id,
            "status": msg.status,
            "azimuth": msg.azimuth,
            "elevation": msg.elevation,
            "distance": msg.distance,
        }
