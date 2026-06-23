from src.base_extractor import CSVExtractor
from src.utils import extract_point, extract_timestamp


class PointExtractor(CSVExtractor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "point"

    def _process_message(self, msg, ros_time, msgtype):
        if msgtype.endswith("PointStamped"):
            point_msg = msg.point
            timestamp = extract_timestamp(msg)
        elif msgtype.endswith("Point"):
            point_msg = msg
            timestamp = ros_time
        else:
            return None

        result = {
            "timestamp": timestamp,
            "ros_time": ros_time,
        }
        result.update(extract_point(point_msg))

        return result
