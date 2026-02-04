import pandas as pd

from src.base_extractor import FolderExtractor
from src.utils import extract_timestamp, extract_point, extract_vector3, extract_orientation


class AnymalStateExtractor(FolderExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "anymal_state"
        self.odom_data = []
        self.joints_data = []
        self.contacts_data = []
    
    def _process_message(self, msg, ros_time, msgtype):
        timestamp = extract_timestamp(msg)
        
        # --- Odometry ---
        odom_row = {
            "timestamp": timestamp,
            "ros_time": ros_time,
            **extract_point(msg.pose.pose.position, prefix="pos_"),
            **extract_orientation(msg.pose.pose.orientation, euler=True),
            **extract_vector3(msg.twist.twist.linear, prefix="vel_lin_"),
            **extract_vector3(msg.twist.twist.angular, prefix="vel_ang_"),
        }
        self.odom_data.append(odom_row)
        
        # --- Joints ---
        joint_row = {"timestamp": timestamp, "ros_time": ros_time}
        for i, name in enumerate(msg.joints.name):
            joint_row[f"{name}_pos"] = msg.joints.position[i]
            joint_row[f"{name}_vel"] = msg.joints.velocity[i]
            joint_row[f"{name}_acc"] = msg.joints.acceleration[i]
            joint_row[f"{name}_eff"] = msg.joints.effort[i]
        self.joints_data.append(joint_row)
        
        # --- Contacts ---
        contact_row = {"timestamp": timestamp, "ros_time": ros_time}
        for contact in msg.contacts:
            contact_row[f"{contact.name}_state"] = contact.state
            contact_row.update(extract_point(contact.position, prefix=f"{contact.name}_pos_"))
            contact_row.update(extract_vector3(contact.wrench.force, prefix=f"{contact.name}_force_"))
        self.contacts_data.append(contact_row)
        
        return True
    
    def _post_extract(self, reader):
        pd.DataFrame(self.odom_data).to_csv(
            self.save_folder / "anymal_odom.csv", index=False
        )
        pd.DataFrame(self.joints_data).to_csv(
            self.save_folder / "anymal_joints.csv", index=False
        )
        pd.DataFrame(self.contacts_data).to_csv(
            self.save_folder / "anymal_contacts.csv", index=False
        )