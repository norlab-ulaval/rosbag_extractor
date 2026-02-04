#!/usr/bin/env python3

import argparse
import os
import sys
import yaml
from pathlib import Path
from rosbags.highlevel import AnyReader

from src.utils import Colors
from src.types.anymal_state import AnymalStateExtractor
from src.types.audio import AudioExtractor
from src.types.basic import BasicExtractor
from src.types.gnss import GNSSExtractor
from src.types.image import ImageExtractor
from src.types.imu import IMUExtractor
from src.types.odom import OdometryExtractor
from src.types.pose import PoseExtractor
from src.types.point_cloud import PointCloudExtractor
from src.types.tf import TFExtractor


EXTRACTORS = {
    "pose": PoseExtractor,
    "imu": IMUExtractor,
    "odometry": OdometryExtractor,
    "gnss": GNSSExtractor,
    "point_cloud": PointCloudExtractor,
    "image": ImageExtractor,
    "basic": BasicExtractor,
    "audio": AudioExtractor,
    "tf": TFExtractor,
    "anymal_state": AnymalStateExtractor,
}


def load_config(name) -> dict:
    if not name.endswith(".yaml"):
        name += ".yaml"
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", f"{name}")
    return yaml.safe_load(open(config_path))


def parse_args():
    parser = argparse.ArgumentParser(description="Extract data from a rosbag file to a directory.")
    parser.add_argument("-i", "--input", type=str, help="Path to the ROS1 or ROS2 bag.", required=True)
    parser.add_argument("-c", "--config", type=str, help="Configuration file name (see configs folder)", required=True)
    parser.add_argument("-o", "--output", type=str, help="Output directory.", required=True)
    parser.add_argument("--ignore-missing", action="store_true", help="Ignore missing topics in the config file.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files in the output directory.")
    parser.add_argument("--silent", action="store_true", help="Silent mode - suppress all output to terminal.")
    return parser.parse_args()


def check_requested_topics(reader, config, ignore_missing=False):
    bag_topics = {x.topic for x in reader.connections}

    to_remove = []
    for i, data in enumerate(config):
        topic_name = data["topic"]
        if topic_name not in bag_topics:
            if ignore_missing:
                print(f"{Colors.WARNING}Warning: Topic {topic_name} not found in bag file. Ignoring...{Colors.ENDC}")
                to_remove.append(i)
            else:
                raise ValueError(f"Topic {topic_name} not found in bag file.")

    for i in reversed(to_remove):
        config.pop(i)


def extract_data(bag_file, config, output_folder, overwrite=False, ignore_missing=False):
    bag_file = Path(bag_file)
    if not bag_file.exists():
        raise FileNotFoundError(f"Bag file {bag_file} not found.")
    
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    with AnyReader([bag_file]) as reader:
        check_requested_topics(reader, config, ignore_missing)
        
        for data in config:
            if not data["folder"]:
                raise ValueError("Folder name not provided in config file.")

            save_folder = output_folder / data["folder"]
            save_folder.mkdir(parents=True, exist_ok=True)
            args = data.get("args", {})
            extractor_type = data["type"]

            if extractor_type in EXTRACTORS:
                extractor = EXTRACTORS[extractor_type](
                    bag_file, data["topic"], save_folder, args, overwrite
                )
                extractor.extract(reader)
            else:
                raise ValueError(f"{Colors.FAIL}Unsupported data type: {extractor_type}!{Colors.ENDC}")

            print("-" * 50)


def main():
    args = parse_args()
    config = load_config(args.config)
    
    if args.silent:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
    
    extract_data(args.input, config, args.output, overwrite=args.overwrite, ignore_missing=args.ignore_missing)


if __name__ == "__main__":
    main()
