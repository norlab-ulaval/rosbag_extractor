import os
from pathlib import Path

import numpy as np
from message_types.audio import extract_audio_from_rosbag
from message_types.basic import extract_basic_data_from_rosbag
from message_types.gnss import extract_gnss_from_rosbag
from message_types.image import extract_images_from_rosbag, sort_bracket_images
from message_types.imu import extract_imu_from_rosbag
from message_types.odom import extract_odom_from_rosbag
from message_types.point_cloud import extract_point_clouds_from_rosbag
from rosbags.highlevel import AnyReader

########## EXAMPLE OF CONFIG FILE ##########

# - type: odometry
#   topic: /warthog_velocity_controller/odom
#   folder: wheel_odom
#   extension: csv

# - type: rectified_image
#   topic: /zed_node/left_raw/image_raw_color
#   folder: camera_left
#   extension: png

# See full examples in ./configs folder

############################################


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

            if data["folder"]:
                data_folder = os.path.join(self.output_folder, data["folder"])
            else:
                data_folder = self.output_folder
            os.makedirs(data_folder, exist_ok=True)

            output_file = os.path.join(data_folder, f"{data['folder']}.{data['extension']}")
            if not overwrite and os.path.exists(output_file):
                print(f"{bcolors.WARNING}Output file {output_file} already exists. Skipping...{bcolors.ENDC}")
                continue

            if data["type"] == "basic":
                extract_basic_data_from_rosbag(self.bag_file, data["topic"], output_file)

            elif data["type"] == "imu":
                extract_imu_from_rosbag(self.bag_file, data["topic"], output_file)

            elif data["type"] == "gnss":
                extract_gnss_from_rosbag(self.bag_file, data["topic"], output_file)

            elif data["type"] == "audio":
                extract_audio_from_rosbag(self.bag_file, data["topic"], output_file)

            elif data["type"] == "odometry":
                extract_odom_from_rosbag(self.bag_file, data["topic"], output_file)

            elif data["type"] == "point_cloud":
                extract_point_clouds_from_rosbag(self.bag_file, data["topic"], data_folder)

            elif data["type"] == "raw_image":
                extract_images_from_rosbag(self.bag_file, data["topic"], data_folder, data["extension"])

            elif data["type"] == "rectified_image":
                extract_images_from_rosbag(self.bag_file, data["topic"], data_folder, data["extension"], rectify=True)

            elif data["type"] == "bracketing_image":
                extract_images_from_rosbag(self.bag_file, data["topic"], data_folder, data["extension"])
                sort_bracket_images(self.bag_file, data["topic"], data_folder, data["extension"], data["args"])

            print(f"{bcolors.OKGREEN}Done! Exported to {data_folder}.{bcolors.ENDC}")

    def _check_requested_topics(self, ignore_missing=False):

        with AnyReader([Path(self.bag_file)]) as reader:
            bag_topics = set([x.topic for x in reader.connections])

        for data in self.config:
            topic_name = data["topic"]
            if topic_name not in bag_topics:
                if ignore_missing:
                    print(
                        f"{bcolors.WARNING}Warning: Topic {topic_name} not found in bag file. Ignoring...{bcolors.ENDC}"
                    )
                    self.config.remove(data)
                    continue
                else:
                    raise Exception(f"Topic {topic_name} not found in bag file.")
