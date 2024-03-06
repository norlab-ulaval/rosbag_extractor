import os, shutil
import numpy as np
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

################## PARAMETERS ##################

INPUT_BAG = "/run/user/1000/gvfs/afp-volume:host=bucheron.local,user=norlab_admin,volume=home/olivier_gamache/dataset/forest_04-20-2023/bagfiles/backpack_2023-04-20-09-29-14.bag"
OUTPUT_FOLDER = "/home/jean-michel/Desktop/test"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../configs/config_backpack.json")

################################################


def load_config(config_file):

    with open(config_file, "r") as f:
        return json.load(f)


def check_output_folder(output_folder):
    
    if os.path.exists(output_folder) and len(os.listdir(output_folder)) > 0:
        answer = input("Output folder is not empty, delete content ? [Y|n]")
        if answer.lower() not in ["y", ""]:
            print("Aborted")
            exit()
        shutil.rmtree(output_folder)
    if not os.path.exists(output_folder): 
        os.makedirs(output_folder)


def check_requested_topics(bag_file, requested_topics):

    with AnyReader([Path(bag_file)]) as reader:
        bag_topics = set([x.topic for x in reader.connections])

    for topic in requested_topics:
        if topic not in bag_topics:
            print(f"[WARNING] Topic {topic} not found in bag file, available topics are {bag_topics}")
        else:
            print(f"Topic {topic} will be extracted.")


def extract_rosbag_data(input_bag, config_dict, output_folder):  

    os.makedirs(output_folder, exist_ok=True)

    for data in config_dict:

        if data['type'] == "basic":
            output_file = os.path.join(output_folder, data['filename'])
            extract_basic_data_from_rosbag(input_bag, data['topic'], output_file)
        
        elif data['type'] == "imu":
            output_file = os.path.join(output_folder, data['filename'])
            extract_imu_from_rosbag(input_bag, data['topic'], output_file)
            
        elif data['type'] == "gnss":
            output_file = os.path.join(output_folder, data['filename'])
            extract_gnss_from_rosbag(input_bag, data['topic'], output_file)

        elif data['type'] == "audio":
            output_file = os.path.join(output_folder, data['filename'])
            extract_audio_from_rosbag(input_bag, data['topic'], output_file)

        elif data['type'] == "odometry":
            output_file = os.path.join(output_folder, data['filename'])
            extract_odom_from_rosbag(input_bag, data['topic'], output_file)

        elif data['type'] == "point_cloud":
            output_folder = os.path.join(output_folder, data['folder'])
            extract_point_clouds_from_rosbag(input_bag, data['topic'], output_folder)

        elif data['type'] == "raw_image":
            output_folder = os.path.join(output_folder, data['folder'])
            os.makedirs(output_folder)
            extract_images_from_rosbag(input_bag, data['topic'], output_folder, data['extension'])     

        elif data['type'] == "rectified_image":
            output_folder = os.path.join(output_folder, data['folder'])
            os.makedirs(output_folder)
            extract_images_from_rosbag(input_bag, data['topic'], output_folder, data['extension'], rectify=True)

        elif data['type'] == "bracketing_image":
            output_folder = os.path.join(output_folder, data['folder'])
            os.makedirs(output_folder)
            extract_images_from_rosbag(input_bag, data['topic'], output_folder, data['extension'])
            sort_bracket_images(input_bag, data['metadata_topic'], output_folder, data['brackets'], data['extension'])

def main():

    config_dict = load_config(CONFIG_FILE)
    check_requested_topics(INPUT_BAG, [data['topic'] for data in config_dict])
    check_output_folder(OUTPUT_FOLDER)
    
    extract_rosbag_data(INPUT_BAG, config_dict, OUTPUT_FOLDER)


if __name__ == "__main__":
    main()