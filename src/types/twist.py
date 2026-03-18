from src.base_extractor import CSVExtractor
from src.utils import extract_twist, extract_timestamp


class TwistExtractor(CSVExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "twist"
    
    def _process_message(self, msg, ros_time, msgtype):
        euler = self.args.get("euler", False)
        
        if msgtype.endswith("TwistStamped"):
            twist_msg = msg.twist
            timestamp = extract_timestamp(msg)
        elif msgtype.endswith("Twist"):
            twist_msg = msg
            timestamp = ros_time
        else:
            return None
        
        result = {
            "timestamp": timestamp,
            "ros_time": ros_time,
        }
        result.update(extract_twist(twist_msg, euler=euler))
        
        return result