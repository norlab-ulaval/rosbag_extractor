import os, shutil
from pathlib import Path
import numpy as np
from tqdm import tqdm
import pandas as pd
import cv2
from cv_bridge import CvBridge

from rosbags.highlevel import AnyReader
import custom_message_definitions
from point_cloud import extract_point_clouds_from_rosbag

################## PARAMETERS ##################

INPUT_BAG = "/media/effie/SSD_JM/Data/FM_20231123/Bags/rosbag2_2023_11_23-11_32_46"
OUTPUT_FOLDER = "/media/effie/SSD_JM/Data/FM_20231123/Bags/export_2023_11_23-11_32_46"
BRACKETING_VALUES = np.array([1.0, 2.0, 4.0, 8.0, 16.0, 32.0])
IMAGE_EXT = "png"
TOPICS_TO_EXPORT = [
    {
        "topic": "/rslidar32_points",
        "folder": "lidar",
        "type": "point_cloud"
    },
    # {
    #     "topic": "/zed2i/zed_node/right_raw/image_raw_color",
    #     "folder": "camera_right",
    #     "type": "image"
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


def extract_images_from_rosbag(bag_file, topic_name, output_folder, num_bits=8):
    
    os.makedirs(output_folder)
    bridge = CvBridge()

    with ([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting images from topic \"{topic_name}\" to folder \"{output_folder.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            timestamp = msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec  
            cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
            if num_bits == 8:
                cv_image.astype(np.uint8)
            else:
                cv_image.astype(np.uint16)
            cv2.imwrite(os.path.join(output_folder, f"{int(timestamp):d}.{IMAGE_EXT}"), cv_image)

    print(f"Done ! Exported images to {output_folder}")
        
        
def sort_bracket_images(bag_file, metadata_topic, images_folder, bracketing_values):
    
    for bracketing_value in bracketing_values:
        check_output_folder(os.path.join(images_folder, f"{bracketing_value:.1f}"))
        
    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Sorting images from folder \"{images_folder}\"")
        connections = [x for x in reader.connections if x.topic == metadata_topic]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            timestamp = msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec
            idx = (np.abs(bracketing_values - msg.ExposureTime)).argmin()
            bracketing_value = bracketing_values[idx]
            image_name = f"{int(timestamp):d}.{IMAGE_EXT}"
            image_path = Path(images_folder, image_name)
            if os.path.exists(image_path):
                os.rename(image_path, os.path.join(images_folder, f"{bracketing_value:.1f}", image_name))

    print(f"Done ! Sorted images to {images_folder}")
        

def extract_imu_from_rosbag(bag_file, topic_name, output_file):
        
    imu_data = []

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting IMU data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            imu_data.append([
                int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec), 
                msg.angular_velocity.x, 
                msg.angular_velocity.y, 
                msg.angular_velocity.z, 
                msg.linear_acceleration.x, 
                msg.linear_acceleration.y, 
                msg.linear_acceleration.z
            ])
            
        imu_df = pd.DataFrame(imu_data, columns=["timestamp", "gyro_x", "gyro_y", "gyro_z", "acc_x", "acc_y", "acc_z"])
        imu_df.to_csv(output_file, index=False)

    print(f"Done ! Exported images to {output_file}")
        
        
def extract_gnss_from_rosbag(bag_file, topic_name, output_file):
        
    gnss_data = []

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting GNSS data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            gnss_data.append([
                int(msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec),
                msg.latitude, 
                msg.longitude, 
                msg.altitude
            ])
            
        imu_df = pd.DataFrame(gnss_data, columns=["timestamp", "latitude", "longitude", "altitude"])
        imu_df.to_csv(output_file, index=False)

    print(f"Done ! Exported images to {output_file}")


def extract_audio_from_rosbag(bag_file, topic_name, output_file):

    mp3_file = open(output_file, 'wb')

    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Extracting audio data from topic \"{topic_name}\" to file \"{output_file.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            if connection.msgtype == "audio_common_msgs/msg/AudioData":
                mp3_file.write(b''.join(msg.data))
            elif connection.msgtype == "audio_common_msgs/msg/AudioDataStamped":
                mp3_file.write(b''.join(msg.audio.data))
            else:
                print(f"Unknown audio message type: {connection.msgtype}")
        
    mp3_file.close()
    print(f"Done ! Exported audio to {output_file}")


def main():
    
    check_output_folder(OUTPUT_FOLDER)
    
    for data in TOPICS_TO_EXPORT:
        
        if data['type'] == "bracketing_image":
            output_folder = os.path.join(OUTPUT_FOLDER, data['folder'])
            extract_images_from_rosbag(INPUT_BAG, data['topic'], output_folder)
            sort_bracket_images(INPUT_BAG, data['metadata_topic'], output_folder, BRACKETING_VALUES)

        elif data['type'] == "image":
            output_folder = os.path.join(OUTPUT_FOLDER, data['folder'])
            extract_images_from_rosbag(INPUT_BAG, data['topic'], output_folder)

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


if __name__ == "__main__":
    main()