from src.base_extractor import CSVExtractor
from src.utils import extract_pose, extract_twist, extract_timestamp


class OdometryExtractor(CSVExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "odom"
    
    def _process_message(self, msg, ros_time, msgtype):
        euler = self.args.get("euler", False)
        
        result = {
            "timestamp": extract_timestamp(msg),
            "ros_time": ros_time,
        }
        
        result.update(extract_pose(msg.pose.pose, euler=euler))
        result.update(extract_twist(msg.twist.twist, prefix="vel_"))
        
        return result
