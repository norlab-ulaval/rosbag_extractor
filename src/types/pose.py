from src.base_extractor import CSVExtractor
from src.utils import extract_pose, extract_timestamp


class PoseExtractor(CSVExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "pose"
    
    def _process_message(self, msg, ros_time, msgtype):
        euler = self.args.get("euler", False)
        
        if msgtype.endswith("PoseStamped"):
            pose_msg = msg.pose
            timestamp = extract_timestamp(msg)
        elif msgtype.endswith("Pose"):
            pose_msg = msg
            timestamp = ros_time
        else:
            return None
        
        result = {
            "timestamp": timestamp,
            "ros_time": ros_time,
        }
        result.update(extract_pose(pose_msg, euler=euler))
        
        return result