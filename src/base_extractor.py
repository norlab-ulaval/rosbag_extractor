from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from tqdm import tqdm


class BaseExtractor(ABC):
    
    def __init__(self, bag_file, topic_name, save_folder, args, overwrite=False):
        self.bag_file = Path(bag_file)
        self.topic_name = topic_name
        self.save_folder = Path(save_folder)
        self.args = args
        self.overwrite = overwrite
        
    def extract(self, reader):
        self._pre_extract(reader)
        
        if not self._check_overwrite():
            return
        
        connections = [x for x in reader.connections if x.topic == self.topic_name]
        if not connections:
            print(f"Warning: No messages found for topic {self.topic_name}")
            return
        
        messages = list(reader.messages(connections=connections))
        self._log_start()
        
        data = []
        for connection, ros_time, rawdata in tqdm(messages):
            msg = reader.deserialize(rawdata, connection.msgtype)
            row_data = self._process_message(msg, ros_time, connection.msgtype)
            if row_data is not None:
                data.append(row_data)
        
        self._save_data(data)
        self._log_complete()
        self._post_extract(reader)
    
    def _pre_extract(self, reader):
        pass
    
    def _post_extract(self, reader):
        pass
    
    @abstractmethod
    def _check_overwrite(self):
        pass
    
    @abstractmethod
    def _process_message(self, msg, ros_time, msgtype):
        pass
    
    @abstractmethod
    def _save_data(self, data):
        pass
    
    @abstractmethod
    def _log_start(self):
        pass
    
    @abstractmethod
    def _log_complete(self):
        pass


class CSVExtractor(BaseExtractor):
    
    def __init__(self, bag_file, topic_name, save_folder, args, overwrite=False):
        super().__init__(bag_file, topic_name, save_folder, args, overwrite)
        self.output_file = self.save_folder / (self.save_folder.name + ".csv")
    
    def _check_overwrite(self):
        if not self.overwrite and self.output_file.exists():
            print(f"Output file {self.output_file} already exists. Skipping...")
            return False
        return True
    
    def _save_data(self, data):
        df = pd.DataFrame(data)
        df.to_csv(self.output_file, index=False)
    
    def _log_start(self):
        print(f"Extracting {self.data_type} data from topic \"{self.topic_name}\" to file \"{self.output_file.name}\"")
    
    def _log_complete(self):
        print(f"Done! Exported {self.data_type} data to {self.output_file}")


class FolderExtractor(BaseExtractor):
    
    def _check_overwrite(self):
        if not self.overwrite and self.save_folder.exists() and any(self.save_folder.iterdir()):
            print(f"Output folder {self.save_folder} already exists and not empty. Skipping...")
            return False
        self.save_folder.mkdir(parents=True, exist_ok=True)
        return True
    
    def _save_data(self, data):
        pass
    
    def _log_start(self):
        print(f"Extracting {self.data_type} data from topic \"{self.topic_name}\" to folder \"{self.save_folder}\"")
    
    def _log_complete(self):
        print(f"Done! Exported {self.data_type} data to {self.save_folder}")
