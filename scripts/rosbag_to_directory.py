import os
import json
from rosbag_extractor import RosbagExtractor

################## PARAMETERS ##################

# INPUT_BAG = "/run/user/1000/gvfs/afp-volume:host=bucheron.local,user=norlab_admin,volume=home/olivier_gamache/dataset/forest_04-20-2023/bagfiles/backpack_2023-04-20-09-29-14.bag"
INPUT_BAG = "/media/jean-michel/SSD_JM/Data/UL_20240416/merged_2024-04-16_10-04-45"
OUTPUT_FOLDER = "/media/jean-michel/SSD_JM/Data/UL_20240416/exported_2024-04-16_10-04-45"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../configs/config_marmotte.json")

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