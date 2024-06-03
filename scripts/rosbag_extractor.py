import os
from pathlib import Path
from rosbags.highlevel import AnyReader
import json

from message_types.point_cloud import extract_point_clouds_from_rosbag
from message_types.image import extract_images_from_rosbag, sort_bracket_images
from message_types.imu import extract_imu_from_rosbag
from message_types.gnss import extract_gnss_from_rosbag
from message_types.audio import extract_audio_from_rosbag
from message_types.odom import extract_odom_from_rosbag
from message_types.basic import extract_basic_data_from_rosbag


class RosbagExtractor:

    def __init__(self, bag_file, output_folder, config_file):

        self.bag_file = bag_file
        self.output_folder = output_folder
        self.load_config(config_file)
        self.create_output_folder()


    def load_config(self, config_file):

        config_file = open(config_file, "r")
        self.config = json.load(config_file)
        print(self.config)


    def create_output_folder(self):

        os.makedirs(self.output_folder, exist_ok=True)

        if len(os.listdir(self.output_folder)) > 0:
            raise Exception(f"Output folder {self.output_folder} already exists and is not empty.")
        

    def check_requested_topics(self):

        with AnyReader([Path(self.bag_file)]) as reader:
            bag_topics = set([x.topic for x in reader.connections])

        for data in self.config:
            topic_name = data["topic"]
            if topic_name not in bag_topics:
                raise Exception(f"Topic {topic_name} not found in bag file.")
            

    def extract_data(self):  

        self.check_requested_topics()
        os.makedirs(self.output_folder, exist_ok=True)

        for data in self.config:

            if data['type'] == "basic":
                output_file = os.path.join(self.output_folder, data['filename'])
                extract_basic_data_from_rosbag(self.bag_file, data['topic'], output_file)
            
            elif data['type'] == "imu":
                output_file = os.path.join(self.output_folder, data['filename'])
                extract_imu_from_rosbag(self.bag_file, data['topic'], output_file)
                
            elif data['type'] == "gnss":
                output_file = os.path.join(self.output_folder, data['filename'])
                extract_gnss_from_rosbag(self.bag_file, data['topic'], output_file)

            elif data['type'] == "audio":
                output_file = os.path.join(self.output_folder, data['filename'])
                extract_audio_from_rosbag(self.bag_file, data['topic'], output_file)

            elif data['type'] == "odometry":
                output_file = os.path.join(self.output_folder, data['filename'])
                extract_odom_from_rosbag(self.bag_file, data['topic'], output_file)

            elif data['type'] == "point_cloud":
                output_folder = os.path.join(self.output_folder, data['folder'])
                extract_point_clouds_from_rosbag(self.bag_file, data['topic'], output_folder)

            elif data['type'] == "raw_image":
                output_folder = os.path.join(self.output_folder, data['folder'])
                os.makedirs(output_folder)
                extract_images_from_rosbag(self.bag_file, data['topic'], output_folder, data['extension'])     

            elif data['type'] == "rectified_image":
                output_folder = os.path.join(self.output_folder, data['folder'])
                os.makedirs(output_folder)
                extract_images_from_rosbag(self.bag_file, data['topic'], output_folder, data['extension'], rectify=True)

            elif data['type'] == "bracketing_image":
                output_folder = os.path.join(self.output_folder, data['folder'])
                os.makedirs(output_folder)
                extract_images_from_rosbag(self.bag_file, data['topic'], output_folder, data['extension'])
                sort_bracket_images(self.bag_file, data['metadata_topic'], output_folder, data['brackets'], data['extension'])


def main():

    INPUT_BAG = "/media/jean-michel/SSD_JM/Data/UL_20240416/merged_2024-04-16_09-57-31"
    OUTPUT_FOLDER = "/media/jean-michel/SSD_JM/Data/UL_20240416/exported_2024-04-16_09-57-31"
    CONFIG_FILE = "../configs/config_temp.json"   

    rosbag_extractor = RosbagExtractor(INPUT_BAG, OUTPUT_FOLDER, CONFIG_FILE)
    rosbag_extractor.extract_data()


if __name__ == "__main__":
    main()