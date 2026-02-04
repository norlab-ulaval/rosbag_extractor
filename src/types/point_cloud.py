import numpy as np
import pandas as pd

from src.base_extractor import FolderExtractor
from src.utils import extract_timestamp

DATA_TYPES = {
    1: np.int8, 
    2: np.uint8, 
    3: np.int16, 
    4: np.uint16,
    5: np.int32, 
    6: np.uint32, 
    7: np.float32, 
    8: np.float64,
}


class PointCloudExtractor(FolderExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "point_clouds"
    
    def _process_message(self, msg, ros_time, msgtype):
        timestamp = extract_timestamp(msg)
        df = pd.DataFrame()
        data = np.frombuffer(msg.data, dtype=np.uint8).reshape(-1, msg.point_step)
        
        for field in msg.fields:
            if field.datatype not in DATA_TYPES:
                raise ValueError(f"Unknown point cloud field datatype: {field.datatype}")
            dtype = DATA_TYPES[field.datatype]
            n_bytes = np.dtype(dtype).itemsize
            df[field.name] = data[:, field.offset : field.offset + n_bytes].flatten().view(dtype=dtype)
        
        output_file = self.save_folder / f"{int(timestamp):d}.csv"
        df.to_csv(output_file, index=False)
        return True
