from src.base_extractor import CSVExtractor
from src.utils import extract_timestamp


class GNSSExtractor(CSVExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "gnss"
    
    def _process_message(self, msg, ros_time, msgtype):
        result = {
            "timestamp": extract_timestamp(msg),
            "ros_time": ros_time,
            "latitude": msg.latitude,
            "longitude": msg.longitude,
            "altitude": msg.altitude,
        }
        
        cov_names = ["cov_xx", "cov_xy", "cov_xz", "cov_yx", "cov_yy", "cov_yz", "cov_zx", "cov_zy", "cov_zz"]
        for i, name in enumerate(cov_names):
            result[name] = msg.position_covariance[i]
        
        return result
