import os

from rosbag_extractor import RosbagExtractor
from rosbag_to_directory import load_config
from pathlib import Path

################## PARAMETERS ##################

INPUT_BAGS = []
INPUT_FOLDERS = [
    "/run/user/1000/gvfs/afp-volume:host=bucheron.local,user=norlab_admin,volume=home/olivier_gamache/dataset/forest_04-20-2023/bagfiles/",
    "/run/user/1000/gvfs/afp-volume:host=bucheron.local,user=norlab_admin,volume=home/olivier_gamache/dataset/forest_04-21-2023/bagfiles/",
    "/run/user/1000/gvfs/afp-volume:host=bucheron.local,user=norlab_admin,volume=home/olivier_gamache/dataset/belair_09-27-2023/bagfiles/",
]
OUTPUT_FOLDER = "/home/jean-michel/Desktop/test"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../configs/config_backpack.json")

################################################


def main():
    config_dict = load_config(CONFIG_FILE)

    if len(INPUT_BAGS) > 0:
        for bag_file in INPUT_BAGS:
            output_folder = os.path.join(OUTPUT_FOLDER, bag_file.split(".")[0])
            rosbag_extractor = RosbagExtractor(bag_file, config_dict)
            rosbag_extractor.extract_data(output_folder, overwrite=True)

    elif len(INPUT_FOLDERS) > 0:
        for INPUT_FOLDER in INPUT_FOLDERS:
            input_dir = Path(INPUT_FOLDER)
            bag_files = (f.parent for f in input_dir.glob("**/metadata.yaml"))
            for bag_file in bag_files:
                output_folder = os.path.join(OUTPUT_FOLDER, bag_file.stem)
                rosbag_extractor = RosbagExtractor(bag_file, config_dict)
                rosbag_extractor.extract_data(output_folder, overwrite=True)


if __name__ == "__main__":
    main()
