import os

from extract_data_from_rosbag import extract_rosbag_data, check_output_folder, check_requested_topics, load_config

################## PARAMETERS ##################

INPUT_BAGS = []
INPUT_FOLDERS = [
    "/run/user/1000/gvfs/afp-volume:host=bucheron.local,user=norlab_admin,volume=home/olivier_gamache/dataset/forest_04-20-2023/bagfiles/",
    "/run/user/1000/gvfs/afp-volume:host=bucheron.local,user=norlab_admin,volume=home/olivier_gamache/dataset/forest_04-21-2023/bagfiles/",
    "/run/user/1000/gvfs/afp-volume:host=bucheron.local,user=norlab_admin,volume=home/olivier_gamache/dataset/belair_09-27-2023/bagfiles/"
]
OUTPUT_FOLDER = "/home/jean-michel/Desktop/test"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../configs/config_backpack.json")

################################################

def main():
    
    config_dict = load_config(CONFIG_FILE)
    check_output_folder(OUTPUT_FOLDER)

    if len(INPUT_BAGS) > 0:
        for bag_file in INPUT_BAGS:
            check_requested_topics(bag_file, [x['topic'] for x in config_dict])
            output_folder = os.path.join(OUTPUT_FOLDER, bag_file.split(".")[0])
            extract_rosbag_data(bag_file, config_dict, output_folder)

    elif len(INPUT_FOLDERS) > 0:
        for INPUT_FOLDER in INPUT_FOLDERS:
            for bag_file in os.listdir(INPUT_FOLDER):
                output_folder = os.path.join(OUTPUT_FOLDER, bag_file.split(".")[0])
                bag_file = os.path.join(INPUT_FOLDER, bag_file)
                # check_requested_topics(bag_file, [x['topic'] for x in config_dict])
                extract_rosbag_data(bag_file, config_dict, output_folder)


if __name__ == "__main__":
    main()