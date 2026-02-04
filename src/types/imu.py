from src.base_extractor import CSVExtractor
from src.utils import extract_orientation, extract_vector3, extract_timestamp


class IMUExtractor(CSVExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "imu"
    
    def _process_message(self, msg, ros_time, msgtype):
        euler = self.args.get("euler", False)
        
        result = {
            "timestamp": extract_timestamp(msg),
            "ros_time": ros_time,
        }
        
        result.update(extract_orientation(msg.orientation, euler=euler))
        result.update(extract_vector3(msg.angular_velocity, prefix="gyro_"))
        result.update(extract_vector3(msg.linear_acceleration, prefix="acc_"))
        
        return result
