from src.base_extractor import CSVExtractor
from src.utils import extract_timestamp


class BasicExtractor(CSVExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "basic"
    
    def _pre_extract(self, reader):
        connections = [x for x in reader.connections if x.topic == self.topic_name]
        if connections:
            self.columns = self._init_columns(reader, connections)
    
    def _process_message(self, msg, ros_time, msgtype):
        msg_dict = self._class_to_dict(msg)

        if msg_dict.get("header"):
            timestamp = extract_timestamp(msg)
            frame_id = msg.header.frame_id
            data = {"ros_time": ros_time, "timestamp": timestamp, "frame_id": frame_id}
        else:
            data = {"ros_time": ros_time}

        for key, value in msg_dict.items():
            if key not in ["header", "__msgtype__"]:
                data[key] = value

        return data
    
    def _init_columns(self, reader, connections):
        if not connections:
            return []

        connection, _, rawdata = next(reader.messages(connections=connections))
        msg = reader.deserialize(rawdata, connection.msgtype)
        msg_dict = self._class_to_dict(msg)
        
        columns = ["ros_time"]
        if msg_dict.get("header"):
            columns += ["timestamp", "frame_id"]
        columns += [key for key in msg_dict.keys() if key not in ["header", "__msgtype__"]]

        return columns
    
    def _class_to_dict(self, obj):
        if isinstance(obj, dict):
            return {key: self._class_to_dict(value) for key, value in obj.items()}
        if hasattr(obj, "__dict__"):
            return {key: self._class_to_dict(value) for key, value in obj.__dict__.items()}
        if isinstance(obj, (list, tuple)):
            return [self._class_to_dict(item) for item in obj]
        return obj
