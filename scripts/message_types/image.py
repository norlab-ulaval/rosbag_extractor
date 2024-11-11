import os
import numpy as np
from pathlib import Path
from rosbags.highlevel import AnyReader
from tqdm import tqdm
import cv2
from glymur import Jp2k

ENCODINGS = {  # COMMENTED ENCODINGS ARE NOT TESTED
    "rgb8":    (np.uint8,  3),
    "rgba8":   (np.uint8,  4),
    # "rgb16":   (np.uint16, 3),
    # "rgba16":  (np.uint16, 4),
    "bgr8":    (np.uint8,  3),
    "bgra8":   (np.uint8,  4),
    # "bgr16":   (np.uint16, 3),
    # "bgra16":  (np.uint16, 4),
    # "mono8":   (np.uint8,  1),
    # "mono16":  (np.uint16, 1),

    # for bayer image 
    "bayer_rggb8":      (np.uint8,  1),
    # "bayer_bggr8":      (np.uint8,  1),
    # "bayer_gbrg8":      (np.uint8,  1),
    # "bayer_grbg8":      (np.uint8,  1),
    "bayer_rggb16":     (np.uint16, 1),
    # "bayer_bggr16":     (np.uint16, 1),
    # "bayer_gbrg16":     (np.uint16, 1),
    # "bayer_grbg16":     (np.uint16, 1),
}


def extract_images_from_rosbag(bag_file, topic_name, output_folder, args, image_ext="png"):
    if "quality_factor" in args and args["quality_factor"] < 1 and image_ext == "png":
        raise ValueError("Quality factor can not be used with PNG images.")
    with AnyReader([Path(bag_file)]) as reader:
        if args['rectify']:
            K, D = get_camera_calibration_matrix(reader, topic_name)

        # iterate over messages
        print(f"Extracting images from topic \"{topic_name}\" to folder \"{output_folder.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            timestamp = msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec  
            np_image = image_to_numpy(msg)
            if ("convert_12bits_to_8bits" in args and args["convert_12bits_to_8bits"]):
                np_image = (np_image/16).astype(np.uint8)
            if "remove_bayer_pattern" in args and args["remove_bayer_pattern"]:
                np_image = cv2.cvtColor(np_image, cv2.COLOR_BayerRG2RGB)
            if "rgb" in msg.encoding:
                np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
            if args['rectify']:
                np_image = cv2.undistort(np_image, K, D)
            if ("gray_scale" in args and args["gray_scale"]):
                np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
            if ("scaling_factor" in args and args["scaling_factor"] != 1):
                np_image = cv2.resize(np_image, (int(np_image.shape[1]*args["scaling_factor"]), int(np_image.shape[0]*args["scaling_factor"])), interpolation=cv2.INTER_AREA)
            if ("quality_factor" in args and args["quality_factor"] < 1):
                jp2 = Jp2k(os.path.join(output_folder, f"{int(timestamp):d}.{image_ext}"), data=np_image, cratios=[args["quality_factor"]])
            else:
                cv2.imwrite(os.path.join(output_folder, f"{int(timestamp):d}.{image_ext}"), np_image)
        
    if "brackets" in args:
        sort_bracket_images(bag_file, topic_name, output_folder, image_ext, args)

    print(f"Done ! Exported images to {output_folder}")


def get_camera_calibration_matrix(reader, topic_name):
    """Extract camera calibration matrix from rosbag."""

    camera_info_topic = "/".join(topic_name.split('/')[:-1] + ["camera_info"])
    connections = [x for x in reader.connections if x.topic == camera_info_topic] 

    if not connections:
        raise ValueError(f"Camera info topic {camera_info_topic} not found in rosbag.")

    for connection, _, rawdata in reader.messages(connections=connections):
        camera_info = reader.deserialize(rawdata, connection.msgtype)
        try:
            K = np.array(camera_info.k).reshape([3, 3])
            D = np.array(camera_info.d)
        except:
            K = np.array(camera_info.K).reshape([3, 3])
            D = np.array(camera_info.D)
        break  

    return K, D


def image_to_numpy(msg):
    if not msg.encoding in ENCODINGS:
        raise TypeError('Unrecognized encoding {}'.format(msg.encoding))

    dtype_class, channels = ENCODINGS[msg.encoding]
    dtype = np.dtype(dtype_class)
    dtype = dtype.newbyteorder('>' if msg.is_bigendian else '<')
    shape = (msg.height, msg.width, channels)

    data = np.frombuffer(msg.data, dtype=dtype).reshape(shape)
    data.strides = (
        msg.step,
        dtype.itemsize * channels,
        dtype.itemsize
    )

    if channels == 1:
        data = data[...,0]
    return data


def sort_bracket_images(bag_file, image_topic, images_folder, image_ext, args):

    metadata_topic = "/".join(image_topic.split('/')[:-1] + ["metadata"])
    brackets = np.array(args["brackets"])
    
    for bracketing_value in brackets:
        os.mkdir(os.path.join(images_folder, f"{bracketing_value:.1f}"))
        
    with AnyReader([Path(bag_file)]) as reader:
        # iterate over messages
        print(f"Sorting images from folder \"{images_folder}\"")
        connections = [x for x in reader.connections if x.topic == metadata_topic]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            timestamp = msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec
            idx = (np.abs(brackets - msg.ExposureTime)).argmin()
            bracketing_value = brackets[idx]
            image_name = f"{int(timestamp):d}.{image_ext}"
            image_path = Path(images_folder, image_name)
            if os.path.exists(image_path):
                os.rename(image_path, os.path.join(images_folder, f"{bracketing_value:.1f}", image_name))

    print(f"Done ! Sorted images to {images_folder}")