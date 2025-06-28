username=jean-michel
save_folder_name="/home/$username/Desktop/tmp/"
search_dir=/media/$username/SSD_JM/dataset_og

sleep 2
# for folder in "$search_dir"/*
# do
echo "#################################"
folder=$search_dir/belair-09-27-2023
folder_name=$(basename "$folder")
folder_name_no_extension=${folder_name%.*}
echo "FOLDER NAME: $folder_name"
mkdir $folder/data_high_resolution/
for file in "$folder/bagfiles"/*
do
    echo "#################################"
    file_name=$(basename "$file")
    file_name_no_extension=${file_name%.*}
    echo $file
    # echo "Downloading bagfile into computer: $file_name"
    # rsync --progress "$folder/bagfiles/$file_name" $save_folder_name
    python3 /home/$username/repos/rosbag_extractor/main.py -i $folder/bagfiles/$file_name -o $folder/data_high_resolution/$file_name_no_extension/ -c backpack --ignore-missing
    # echo "Transferring extracted data into SSD: $search_dir/$folder_name/data_high_resolution/$file_name_no_extension/"
    # rsync -a $save_folder_name$file_name_no_extension/ $folder/data_high_resolution/$file_name_no_extension/
    # echo "Deleting bagfile from computer: $save_folder_name$file_name"
    # rm $save_folder_name$file_name
    # echo "Deleting extracted data from computer: $save_folder_name$file_name_no_extension/"
    # rm -r $save_folder_name$file_name_no_extension
    echo "Deleting bagfile from SSD: $folder/bagfiles/$file_name"
    rm $folder/bagfiles/$file_name
done
# done