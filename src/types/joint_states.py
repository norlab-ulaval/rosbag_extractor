import pandas as pd

from src.base_extractor import FolderExtractor
from src.utils import extract_timestamp

class JointStates(FolderExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "joint_states"
        self.joints_data = []
        
    def _process_message(self, msg, ros_time, msgtype):
        timestamp = extract_timestamp(msg)
        
        # --- Joints ---
        joint_row = {"timestamp": timestamp, "ros_time": ros_time}
        for i, name in enumerate(msg.name):
            joint_row[f"{name}_pos"] = msg.position[i]
            joint_row[f"{name}_vel"] = msg.velocity[i]
            joint_row[f"{name}_eff"] = msg.effort[i]
        self.joints_data.append(joint_row)
        
        
        return True
    
    def _save_data(self, data):
        
        pd.DataFrame(self.joints_data).to_csv(
            self.save_folder / "joint_states.csv", index=False
        )