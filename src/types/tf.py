import pandas as pd
from scipy.spatial.transform import Rotation
from tqdm import tqdm

from src.base_extractor import FolderExtractor
from src.utils import TFBuffer


class TFExtractor(FolderExtractor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_type = "TF transforms"
        
        self.base_frame = self.args.get('base_frame')
        self.target_frames = self.args.get('target_frames', [])
        
        if not self.base_frame:
            raise ValueError("base_frame must be specified in args")
        if not self.target_frames:
            raise ValueError("target_frames must be specified in args")
        
        self.euler = self.args.get('euler', False)
        self.sample_rate = self.args.get('sample_rate', None)
    
    def _pre_extract(self, reader):      
        self.tf_buffer = TFBuffer()
        self._load_static_transforms(reader)
        
        self.frame_data = {target: [] for target in self.target_frames}
        self.last_sample_time = {target: 0 for target in self.target_frames}
        if self.sample_rate:
            self.sample_period_ns = int(1e9 / self.sample_rate)
    
    def _process_message(self, msg, ros_time, msgtype):
        if not msg.transforms:
            return None
        
        first_stamp = msg.transforms[0].header.stamp
        timestamp_ns = int(first_stamp.sec * 1e9 + first_stamp.nanosec)
        
        for tf in msg.transforms:
            t, r = tf.transform.translation, tf.transform.rotation
            self.tf_buffer.set_transform(tf.header.frame_id, tf.child_frame_id,
                                       [t.x, t.y, t.z], [r.x, r.y, r.z, r.w])
        
        for target_frame in self.target_frames:
            if self.sample_rate and timestamp_ns - self.last_sample_time[target_frame] < self.sample_period_ns:
                continue
            
            self.last_sample_time[target_frame] = timestamp_ns
            
            try:
                trans, rot = self.tf_buffer.lookup_transform(target_frame, self.base_frame)
                if self.euler:
                    rot = Rotation.from_quat(rot).as_euler('xyz', degrees=False)
                self.frame_data[target_frame].append([timestamp_ns, *trans, *rot])
            except Exception:
                pass
        
        return None
    
    def _post_extract(self, reader):
        safe_base = self.base_frame.replace('/', '_').lower()
        columns = ['timestamp', 'x', 'y', 'z', 'roll', 'pitch', 'yaw'] if self.euler else \
                  ['timestamp', 'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw']
        
        for target_frame in self.target_frames:
            transform_data = self.frame_data[target_frame]
            if transform_data:
                safe_target = target_frame.replace('/', '_').lower()
                output_file = self.save_folder / f"{safe_base}_to_{safe_target}.csv"
                df = pd.DataFrame(transform_data, columns=columns)
                df.to_csv(output_file, index=False)
    
    def _load_static_transforms(self, reader):
        print("Reading static transforms...", end="", flush=True)
        static_connections = [x for x in reader.connections if x.topic == '/tf_static']
        
        for connection, ros_time, rawdata in reader.messages(connections=static_connections):
            msg = reader.deserialize(rawdata, connection.msgtype)
            for transform in msg.transforms:
                t = transform.transform
                self.tf_buffer.set_transform(
                    transform.header.frame_id, transform.child_frame_id,
                    [t.translation.x, t.translation.y, t.translation.z],
                    [t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w])
        
        print(f" Done ({len(self.tf_buffer.transforms)} transforms)")
