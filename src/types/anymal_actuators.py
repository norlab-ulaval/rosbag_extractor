import pandas as pd

from src.base_extractor import FolderExtractor

JOINT_NAMES = [
    "LF_HAA", "LF_HFE", "LF_KFE",
    "RF_HAA", "RF_HFE", "RF_KFE",
    "LH_HAA", "LH_HFE", "LH_KFE",
    "RH_HAA", "RH_HFE", "RH_KFE",
]

class AnymalActuatorsExtractor(FolderExtractor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "anymal_actuators"
        self.measured_data = []
        self.commanded_data = []

    def _process_message(self, msg, ros_time, msgtype):
        # Use the first reading's header stamp as the message timestamp
        if msg.readings:
            stamp = msg.readings[0].header.stamp
            timestamp = int(stamp.sec * 1e9 + stamp.nanosec)
        else:
            timestamp = None

        measured_row = {"timestamp": timestamp, "ros_time": ros_time}
        commanded_row = {"timestamp": timestamp, "ros_time": ros_time}

        for i, reading in enumerate(msg.readings):
            name = JOINT_NAMES[i]

            # --- Readings ---
            s = reading.state
            measured_row[f"{name}_pos"] = s.joint_position
            measured_row[f"{name}_vel"] = s.joint_velocity
            measured_row[f"{name}_accel"] = s.joint_acceleration
            measured_row[f"{name}_torque"] = s.joint_torque
            measured_row[f"{name}_current"] = s.current

            # --- Commanded ---
            c = reading.commanded
            commanded_row[f"{name}_mode"] = c.mode
            commanded_row[f"{name}_pos"] = c.position
            commanded_row[f"{name}_vel"] = c.velocity
            commanded_row[f"{name}_torque"] = c.joint_torque
            commanded_row[f"{name}_current"] = c.current

        self.measured_data.append(measured_row)
        self.commanded_data.append(commanded_row)

        return True

    def _save_data(self, data):
        pd.DataFrame(self.measured_data).to_csv(
            self.save_folder / "measured.csv", index=False
        )
        pd.DataFrame(self.commanded_data).to_csv(
            self.save_folder / "commanded.csv", index=False
        )
