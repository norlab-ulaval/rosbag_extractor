from rosbags.typesys import get_types_from_msg, get_typestore, Stores
from src.utils import extract_timestamp
from src.base_extractor import CSVExtractor

MTT_TACHOMETER_MSG = """
std_msgs/Header header

float64 main_sensor_temp_a
float64 main_sensor_temp_b

uint16 tachometer_instant     
uint32 tachometer_cumulative  

float64 speed_ms    
float64 speed_kmh   

float64 distance_km 
string direction    

float64 steer_cmd    
"""

typestore = get_typestore(Stores.LATEST)
typestore.register(get_types_from_msg(MTT_TACHOMETER_MSG, "mtt_msgs/msg/MttTachometerData"))

class MttTachometerExtractor(CSVExtractor):
    
    def __init__(self, bag_file, topic_name, save_folder, args, overwrite=False):
        super().__init__(bag_file, topic_name, save_folder, args, overwrite)
        self.data_type = "mtt_tachometer"
    
    def _process_message(self, msg, ros_time, msgtype):
        result = {
            "timestamp": extract_timestamp(msg),
            "ros_time": ros_time,
            "tachometer_instant": msg.tachometer_instant,
            "tachometer_cumulative": msg.tachometer_cumulative,
            "speed_ms": msg.speed_ms,
            "speed_kmh": msg.speed_kmh,
            "distance_km": msg.distance_km,
            "direction": msg.direction,
            "steer_cmd": msg.steer_cmd,
        }
        return result