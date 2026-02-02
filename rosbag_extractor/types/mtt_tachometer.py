import pandas as pd
from tqdm import tqdm
from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from mtt_msgs.msg import MttTachometerData

def extract_mtt_tachometer_from_rosbag(bag_file, topic_name, output_file):

    print(
        f'Extracting tachometer data from topic "{topic_name}" '
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

    mtt_data = []

    for _ in tqdm(range(reader.get_metadata().message_count)):
        if not reader.has_next():
            break

        topic, rawdata, _ = reader.read_next()

        if topic != topic_name:
            continue

        msg = deserialize_message(rawdata, msg_type)

        # mtt_msgs/msg/MttTachometerData
        mtt_data.append(
            [
                int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec),
                msg.tachometer_instant,
                msg.tachometer_cumulative,
                msg.speed_ms,
                msg.speed_kmh,
                msg.distance_km,
                msg.direction,
                msg.steer_cmd,
            ]
        )

    mtt_df = pd.DataFrame(
        mtt_data,
        columns=[
            "timestamp",
            "tachometer_instant",
            "tachometer_cumulative",
            "speed_ms",
            "speed_kmh",
            "distance_km",
            "direction",
            "steer_cmd",
        ],
    )

    mtt_df.to_csv(output_file, index=False)
