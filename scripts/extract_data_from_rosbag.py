import os, shutil
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader

from message_types.point_cloud import extract_point_clouds_from_rosbag
from message_types.image import extract_images_from_rosbag, sort_bracket_images
from message_types.imu import extract_imu_from_rosbag
from message_types.gnss import extract_gnss_from_rosbag
from message_types.audio import extract_audio_from_rosbag
from message_types.odom import extract_odom_from_rosbag

################## PARAMETERS ##################

INPUT_BAG = "/home/jean-michel/ros/bags/active_probing_parking/merged_2024-02-18_15-01-58_processed"
OUTPUT_FOLDER = "/home/jean-michel/ros/bags/active_probing_parking/merged_2024-02-18_15-01-58_extracted"
BRACKETING_VALUES = np.array([1.0, 2.0, 4.0, 8.0, 16.0, 32.0])
IMAGE_EXT = "png"
TOPICS_TO_EXPORT = [
    {
        "topic": "/icp_odom",
        "filename": "icp_odom.csv",
        "type": "odometry"
    },
    {
        "topic": "/odom_roboclaw",
        "filename": "wheel_odom.csv",
        "type": "odometry"
    },
    {
        "topic": "/imu_and_wheel_odom",
        "filename": "imu_and_wheel_odom.csv",
        "type": "odometry"
    },
    # {
    #     "topic": "/zed_node/left_raw/image_raw_color",
    #     "calibration": "/zed_node/left_raw/camera_info",
    #     "folder": "camera_left",
    #     "type": "rectified_image"
    # },
    # {
    #     "topic": "/zed_node/right_raw/image_raw_color",
    #     "calibration": "/zed_node/right_raw/camera_info",
    #     "folder": "camera_right",
    #     "type": "rectified_image"
    # },
    # {
    #     "topic": "/lslidar_point_cloud",
    #     "folder": "lidar",
    #     "type": "point_cloud"
    # },
    # {
    #     "topic": "/audio/audio_stamped",
    #     "filename": "audio.mp3",
    #     "type": "audio"
    # },
    # {
    #     "topic": "/gps_data_raw", 
    #     "filename": "gnss.csv",
    #     "type": "gnss"
    # },
    # {
    #     "topic": "/MTI_imu/data", 
    #     "filename": "imu.csv",
    #     "type": "imu"
    # },
    # {
    #     "topic": "/stereo/camera1/image_decompressed", 
    #     "folder": "camera_left",
    #     "type": "bracketing_image",
    #     "metadata_topic": "/stereo/camera1/metadata"
    # },
    # {
    #     "topic": "/stereo/camera2/image_decompressed", 
    #     "folder": "camera_right",
    #     "type": "bracketing_image",
    #     "metadata_topic": "/stereo/camera2/metadata"
    # },
]

################################################


def check_output_folder(output_folder):
    
    # Check if output folder exists and is empty
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
            raise ValueError(f"Topic {topic} not found in bag file, available topics are {bag_topics}")

def main():

    check_requested_topics(INPUT_BAG, [data['topic'] for data in TOPICS_TO_EXPORT])
    check_output_folder(OUTPUT_FOLDER)
    
    for data in TOPICS_TO_EXPORT:
        
        if data['type'] == "bracketing_image":
            output_folder = os.path.join(OUTPUT_FOLDER, data['folder'])
            os.makedirs(output_folder)
            extract_images_from_rosbag(INPUT_BAG, data['topic'], output_folder, IMAGE_EXT)
            sort_bracket_images(INPUT_BAG, data['metadata_topic'], output_folder, BRACKETING_VALUES, IMAGE_EXT)

        elif data['type'] == "rectified_image":
            output_folder = os.path.join(OUTPUT_FOLDER, data['folder'])
            os.makedirs(output_folder)
            extract_images_from_rosbag(INPUT_BAG, data['topic'], output_folder, IMAGE_EXT, rectify=True)

        elif data['type'] == "raw_image":
            output_folder = os.path.join(OUTPUT_FOLDER, data['folder'])
            os.makedirs(output_folder)
            extract_images_from_rosbag(INPUT_BAG, data['topic'], output_folder, IMAGE_EXT)

        elif data['type'] == "imu":
            output_file = os.path.join(OUTPUT_FOLDER, data['filename'])
            extract_imu_from_rosbag(INPUT_BAG, data['topic'], output_file)
            
        elif data['type'] == "gnss":
            output_file = os.path.join(OUTPUT_FOLDER, data['filename'])
            extract_gnss_from_rosbag(INPUT_BAG, data['topic'], output_file)

        elif data['type'] == "audio":
            output_file = os.path.join(OUTPUT_FOLDER, data['filename'])
            extract_audio_from_rosbag(INPUT_BAG, data['topic'], output_file)

        elif data['type'] == "point_cloud":
            output_folder = os.path.join(OUTPUT_FOLDER, data['folder'])
            extract_point_clouds_from_rosbag(INPUT_BAG, data['topic'], output_folder)

        elif data['type'] == "odometry":
            output_file = os.path.join(OUTPUT_FOLDER, data['filename'])
            extract_odom_from_rosbag(INPUT_BAG, data['topic'], output_file)


if __name__ == "__main__":
    main()