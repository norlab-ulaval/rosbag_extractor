import os
import json
from rosbag_extractor import RosbagExtractor
from pathlib import Path
from typing import Union


################## PARAMETERS ##################

# INPUT_BAG = "/run/user/1000/gvfs/afp-volume:host=bucheron.local,user=norlab_admin,volume=home/olivier_gamache/dataset/forest_04-20-2023/bagfiles/backpack_2023-04-20-09-29-14.bag"
INPUT_BAG = "/media/jean-michel/ssd_NS/jm/trav_2024-06-18_15-30-33"
OUTPUT_FOLDER = "/home/jean-michel/Desktop/calib_warthog"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../configs/config_warthog.json")

################################################


def load_config(config_file: Union[Path, str]) -> dict:
    config_path = Path(config_file)
    return json.loads(config_path.read_text(encoding="utf-8"))


def main():
    config = load_config(CONFIG_FILE)
    rosbag_extractor = RosbagExtractor(INPUT_BAG, config)
    rosbag_extractor.extract_data(OUTPUT_FOLDER, overwrite=True, ignore_missing=True)


if __name__ == "__main__":
    main()
