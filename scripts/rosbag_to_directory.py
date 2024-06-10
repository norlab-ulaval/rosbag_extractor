import os
import json
from rosbag_extractor import RosbagExtractor

################## PARAMETERS ##################

# INPUT_BAG = "/run/user/1000/gvfs/afp-volume:host=bucheron.local,user=norlab_admin,volume=home/olivier_gamache/dataset/forest_04-20-2023/bagfiles/backpack_2023-04-20-09-29-14.bag"
INPUT_BAG = "/home/olivier_g/Desktop/tmp/decompressed_backpack.bag"
OUTPUT_FOLDER = "/home/olivier_g/Desktop/tmp/export"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../configs/config_backpack.json")

################################################


def load_config(config_file):

    config_file = open(config_file, "r")
    return json.load(config_file)
    

def main(): 

    config = load_config(CONFIG_FILE)
    rosbag_extractor = RosbagExtractor(INPUT_BAG, config)
    rosbag_extractor.extract_data(OUTPUT_FOLDER, overwrite=True, ignore_missing=True)


if __name__ == "__main__":
    main()