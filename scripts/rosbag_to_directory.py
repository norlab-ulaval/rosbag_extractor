import os
import json
from rosbag_extractor import RosbagExtractor
import argparse

################## PARAMETERS ##################


INPUT_BAG = "/home/alienware/Desktop/tmp/decompressed_backpack.bag"
OUTPUT_FOLDER = "/home/alienware/Desktop/tmp/export"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../configs/config_backpack.json")

################################################


def load_config(config_file):

    config_file = open(config_file, "r")
    return json.load(config_file)
    

def main(): 
    parser = argparse.ArgumentParser(description="Extract data from rosbag")
    parser.add_argument("-i", "--input_bagfile", help="Input bagfile name", required=False, default=INPUT_BAG)
    parser.add_argument("-o", "--output_folder", help="Output folder name", required=False, default=OUTPUT_FOLDER)
    args = parser.parse_args()
    config = load_config(CONFIG_FILE)
    rosbag_extractor = RosbagExtractor(args.input_bagfile, config)
    rosbag_extractor.extract_data(args.output_folder, overwrite=True, ignore_missing=True)


if __name__ == "__main__":
    main()