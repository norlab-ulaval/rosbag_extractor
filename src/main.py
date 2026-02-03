#!/usr/bin/env python3

import argparse
import os
import sys
import yaml
from src.rosbag_extractor import RosbagExtractor


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


def main():
    args = parse_args()
    config = load_config(args.config)
    
    if args.silent:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
    
    rosbag_extractor = RosbagExtractor(args.input, config)
    rosbag_extractor.extract_data(args.output, overwrite=args.overwrite, ignore_missing=args.ignore_missing)


if __name__ == "__main__":
    main()
