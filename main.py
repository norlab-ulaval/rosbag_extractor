import argparse
import os
from pathlib import Path
from typing import Union

import yaml
from src.rosbag_extractor import RosbagExtractor

################## PARAMETERS ##################

INPUT_BAG = "/media/nicolassamson/Expansion/arcxhive/drive_FR/drive_FR/jm_ice/high-level/exp1/rosbag2_2024_07_30-16_28_53"
OUTPUT_FOLDER = "/media/nicolassamson/Expansion/arcxhive/drive_FR/drive_FR/jm_ice/high-level/dougnut_cmd_vel"
CONFIG = "warthog_cmd_vel"  # Config file name without extension, should exist in the configs folder

################################################


def load_config(name) -> dict:
    if not name.endswith(".yaml"):
        name += ".yaml"
    config_path = os.path.join(os.path.dirname(__file__), "configs", f"{name}")
    return yaml.safe_load(open(config_path))


def parse_args():
    parser = argparse.ArgumentParser(description="Extract data from a rosbag file to a directory.")
    parser.add_argument("-i", "--input", type=str, help="Path to the ROS1 or ROS2 bag.", default=INPUT_BAG)
    parser.add_argument("-c", "--config", type=str, help="Configuration file name (see configs folder)", default=CONFIG)
    parser.add_argument("-o", "--output", type=str, help="Output directory.", default=OUTPUT_FOLDER)
    parser.add_argument("--ignore-missing", action="store_true", help="Ignore missing topics in the config file.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files in the output directory.")
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)
    rosbag_extractor = RosbagExtractor(args.input, config)
    rosbag_extractor.extract_data(args.output, overwrite=args.overwrite, ignore_missing=args.ignore_missing)


if __name__ == "__main__":
    main()
