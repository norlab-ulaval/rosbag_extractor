import pandas as pd
from tqdm import tqdm
from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from geometry_msgs.msg import TwistStamped

def extract_cmd_vel_data_from_rosbag(bag_file, topic_name, output_file):

    print(
        f'Extracting cmd_vel data from topic "{topic_name}" '
        f'to file "{output_file.split("/")[-1]}"'
    )

    reader = SequentialReader()
    reader.open(
        StorageOptions(uri=bag_file, storage_id="mcap"),
        ConverterOptions("cdr", "cdr"),
    )

    # Build topic → type map
    topics_metadata = reader.get_all_topics_and_types()
    topic_type_map = {t.name: t.type for t in topics_metadata}

    if topic_name not in topic_type_map:
        raise RuntimeError(f"Topic {topic_name} not found in bag")

    # Get message class
    msg_type = get_message(topic_type_map[topic_name])

    cmd_vel = []

    for _ in tqdm(range(reader.get_metadata().message_count)):
        if not reader.has_next():
            break

        topic, rawdata, _ = reader.read_next()

        if topic != topic_name:
            continue

        msg = deserialize_message(rawdata, msg_type)

        msg = deserialize_message(rawdata, TwistStamped)

        cmd_vel.append([
            int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec),  # timestamp in ns
            msg.header.frame_id,
            msg.twist.linear.x,
            msg.twist.linear.y,
            msg.twist.linear.z,
            msg.twist.angular.x,
            msg.twist.angular.y,
            msg.twist.angular.z,
        ])

    cmd_vel_dataframe = pd.DataFrame(
        cmd_vel,
        columns=[
            "timestamp",
            "frame_id",
            "linear_x",
            "linear_y",
            "linear_z",
            "angular_x",
            "angular_y",
            "angular_z",
        ],
    )
    cmd_vel_dataframe.to_csv(output_file, index=False)
    print(f"Done! Exported to {output_file}")
