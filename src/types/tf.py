from pathlib import Path

import pandas as pd
from rosbags.highlevel import AnyReader
from tqdm import tqdm

from src.utils import TFBuffer, euler_from_quaternion


def extract_tf_from_rosbag(bag_file, topic_name, save_folder, args, overwrite):

    base_frame = args.get('base_frame')
    target_frames = args.get('target_frames', [])
    
    if not base_frame:
        raise ValueError("base_frame must be specified in args")
    if not target_frames:
        raise ValueError("target_frames must be specified in args")
    
    use_euler = args.get('use_euler', False)
    sample_rate = args.get('sample_rate', None)
    
    # Avoid overwriting existing files
    if not overwrite and Path(save_folder).exists() and any(Path(save_folder).iterdir()):
        print(f"Output folder {save_folder} already exists and not empty. Skipping...")
        return
    
    print(f"Extracting TF transforms from '{base_frame}' to {len(target_frames)} target frames")
    if sample_rate:
        print(f"  Sampling at {sample_rate} Hz")
    
    tf_buffer = TFBuffer()
    _load_static_transforms(bag_file, tf_buffer)
    messages = _load_dynamic_transforms(bag_file)
    frame_data = _extract_transforms(messages, tf_buffer, base_frame, target_frames, use_euler, sample_rate)
    _save_transforms_to_csv(frame_data, base_frame, target_frames, save_folder, use_euler)

    print(f"Done! Extracted transforms to {save_folder}")


def _load_static_transforms(bag_file, tf_buffer):
    """Load static transforms from /tf_static topic."""
    with AnyReader([Path(bag_file)]) as reader:
        print("Reading static transforms...", end="", flush=True)
        static_connections = [x for x in reader.connections if x.topic == '/tf_static']
        
        for connection, ros_time, rawdata in reader.messages(connections=static_connections):
            msg = reader.deserialize(rawdata, connection.msgtype)
            for transform in msg.transforms:
                t = transform.transform
                tf_buffer.set_transform(
                    transform.header.frame_id, transform.child_frame_id,
                    [t.translation.x, t.translation.y, t.translation.z],
                    [t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w])
        
        print(f" Done ({len(tf_buffer.transforms)} transforms)")


def _load_dynamic_transforms(bag_file):
    """Load all /tf messages and sort by timestamp."""
    with AnyReader([Path(bag_file)]) as reader:
        print("Reading and sorting dynamic transforms...", end="", flush=True)
        tf_connections = [x for x in reader.connections if x.topic == '/tf']
        
        messages = []
        for connection, ros_time, rawdata in reader.messages(connections=tf_connections):
            msg = reader.deserialize(rawdata, connection.msgtype)
            if len(msg.transforms) > 0:
                first_stamp = msg.transforms[0].header.stamp
                timestamp_ns = int(first_stamp.sec * 1e9 + first_stamp.nanosec)
                messages.append((timestamp_ns, msg))
        
        messages.sort(key=lambda x: x[0])
        print(f" Done ({len(messages)} messages)")
        return messages


def _extract_transforms(messages, tf_buffer, base_frame, target_frames, use_euler, sample_rate):
    """Extract transforms for target frames from sorted messages."""
    frame_data = {target: [] for target in target_frames}
    last_sample_time = {target: 0 for target in target_frames} if sample_rate else None
    sample_period_ns = int(1e9 / sample_rate) if sample_rate else 0
    
    for timestamp_ns, msg in tqdm(messages, desc="Extracting"):

        for tf in msg.transforms:
            t, r = tf.transform.translation, tf.transform.rotation
            tf_buffer.set_transform(tf.header.frame_id, tf.child_frame_id,
                                   [t.x, t.y, t.z], [r.x, r.y, r.z, r.w])
        
        for target_frame in target_frames:

            if sample_rate and timestamp_ns - last_sample_time[target_frame] < sample_period_ns:
                continue

            last_sample_time[target_frame] = timestamp_ns
            
            try:
                trans, rot = tf_buffer.lookup_transform(target_frame, base_frame)
                if use_euler:
                    rot = euler_from_quaternion(*rot)

                frame_data[target_frame].append([timestamp_ns, *trans, *rot])
            except Exception:
                pass
    
    return frame_data


def _save_transforms_to_csv(frame_data, base_frame, target_frames, output_folder, use_euler):
    """Save extracted transforms to CSV files."""
    safe_base = base_frame.replace('/', '_').lower()
    columns = ['timestamp', 'x', 'y', 'z', 'roll', 'pitch', 'yaw'] if use_euler else \
              ['timestamp', 'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw']
    
    for target_frame in target_frames:
        transform_data = frame_data[target_frame]
        if transform_data:
            safe_target = target_frame.replace('/', '_').lower()
            output_file = f"{output_folder}/{safe_base}_to_{safe_target}.csv"
            df = pd.DataFrame(transform_data, columns=columns)
            df.to_csv(output_file, index=False)
