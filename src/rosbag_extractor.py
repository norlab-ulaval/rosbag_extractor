import os
from pathlib import Path

from rosbags.highlevel import AnyReader
from src.types.audio import extract_audio_from_rosbag
from src.types.basic import extract_basic_data_from_rosbag
from src.types.gnss import extract_gnss_from_rosbag
from src.types.image import extract_images_from_rosbag
from src.types.imu import extract_imu_from_rosbag
from src.types.odom import extract_odom_from_rosbag
from src.types.pose import extract_pose_from_rosbag
from src.types.point_cloud import extract_point_clouds_from_rosbag
from src.types.tf import extract_tf_from_rosbag


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


class RosbagExtractor:

    def __init__(self, bag_file, config):

        self.bag_file = bag_file
        self.config = config
        if not os.path.exists(bag_file):
            raise Exception(f"Bag file {bag_file} not found.")


    def extract_data(self, output_folder, overwrite=False, ignore_missing=False):

        self.output_folder = output_folder
        self._check_requested_topics(ignore_missing)
        os.makedirs(self.output_folder, exist_ok=True)

        for data in self.config:

            if not data["folder"]:
                raise Exception("Folder name not provided in config file.")

            save_folder = os.path.join(self.output_folder, data["folder"])
            os.makedirs(save_folder, exist_ok=True)

            args = data.get("args", {})

            extractors = {
                "basic": extract_basic_data_from_rosbag,
                "imu": extract_imu_from_rosbag,
                "gnss": extract_gnss_from_rosbag,
                "audio": extract_audio_from_rosbag,
                "odometry": extract_odom_from_rosbag,
                "pose": extract_pose_from_rosbag,
                "point_cloud": extract_point_clouds_from_rosbag,
                "image": extract_images_from_rosbag,
                "tf": extract_tf_from_rosbag,
            }

            extractor = extractors.get(data["type"])
            if extractor:
                extractor(self.bag_file, data["topic"], save_folder, args, overwrite)
            else:
                raise Exception(f"{bcolors.FAIL}Unsupported data type: {data['type']}!{bcolors.ENDC}")

            print("-" * 50)


    def _check_requested_topics(self, ignore_missing=False):

        with AnyReader([Path(self.bag_file)]) as reader:
            bag_topics = set([x.topic for x in reader.connections])

        to_remove = []
        for i, data in enumerate(self.config):
            topic_name = data["topic"]
            if topic_name not in bag_topics:
                if ignore_missing:
                    print(f"{bcolors.WARNING}Warning: Topic {topic_name} not found in bag file. Ignoring...{bcolors.ENDC}")
                    to_remove.append(i)
                    continue
                else:
                    raise Exception(f"Topic {topic_name} not found in bag file.")

        to_remove.sort(reverse=True)
        for i in to_remove:
            self.config.pop(i)
