import pandas as pd
from src.base_extractor import FolderExtractor
# Assuming you have a utility for header/timestamp extraction
from src.utils import extract_timestamp

class HuskyStateExtractor(FolderExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "robot_status"
        self.status_data = []
    
    def _process_message(self, msg, ros_time, msgtype):
        # 1. Extract timing from the Header
        # If your extract_timestamp utility handles msg.header:
        header_time = extract_timestamp(msg.header) 
        
        # 2. Build the row
        status_row = {
            "header_stamp": header_time,
            "ros_arrival_time": ros_time,
            "frame_id": msg.header.frame_id,
            "uptime": msg.uptime,
            "ros_control_loop_freq": msg.ros_control_loop_freq,
            "mcu_current": msg.mcu_and_user_port_current,
            "left_driver_current": msg.left_driver_current,
            "right_driver_current": msg.right_driver_current,
            "battery_voltage": msg.battery_voltage,
            "left_driver_temp": msg.left_driver_temp,
            "right_driver_temp": msg.right_driver_temp,
            "left_motor_temp": msg.left_motor_temp,
            "right_motor_temp": msg.right_motor_temp,
            "capacity_estimate": msg.capacity_estimate,
            "charge_estimate": msg.charge_estimate,
            "e_stop": msg.e_stop,
            "battery_connected": msg.battery_connected,
            "timeout": msg.timeout,
            "lockout": msg.lockout
        }
        
        self.status_data.append(status_row)
        return True
        
    
        
    def _save_data(self, data):
        pd.DataFrame(self.status_data).to_csv(
            self.save_folder / "husky_status.csv", index=False
        )
        