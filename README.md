# Rosbag Extractor

A python utility to convert rosbags into human-readable data.

# Installation

It is suggested to install the module with pip: 

```bash
pip install -e .
```

# Usage

```bash
usage: rosbag_extractor [-h] [-i INPUT] [-c CONFIG] [-o OUTPUT] [--ignore-missing] [--overwrite]

Extract data from a rosbag file to a directory.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Path to the ROS1 or ROS2 bag.
  -c CONFIG, --config CONFIG
                        Configuration file name (see configs folder)
  -o OUTPUT, --output OUTPUT
                        Output directory.
  --ignore-missing      Ignore missing topics in the config file.
  --overwrite           Overwrite existing files in the output directory.
```

To use, create a config in the `configs` folder, which must be a list of dictionaries, each containing the following information:

| Key       | Value                                              |
| --------- | -------------------------------------------------- |
| type      | Type of data to handle (see supported types below) |
| topic     | Name of the topic to extract                       |
| folder    | Name of the subfolder where to extract the data    |
| extension | File extension for the extracted data              |
| args      | Extra arguments for some data types                |

# Supported types

The following types are currently implemented in the tool:

**basic** -> Any basic data without complex encoding, such as most `std_msgs`, as well as custom messages containing only basic types.

**imu** -> Messages of type `sensor_msgs/msg/Imu`, can be extracted to a single CSV file including timestamps.

**gnss** -> Messages of type `sensor_msgs/msg/NavSatFix`, can be extracted to a single CSV file including timestamps.

**audio** -> Messages of type `audio_common_msgs/msg/AudioData` or `audio_common_msgs/msg/AudioDataStamped`, can be extracted to a single MP3 or WAV file.

**odometry** -> Messages of type `nav_msgs/msg/Odometry`, can be extracted to a single CSV file including timestamps.

**point_cloud** -> Messages of type `sensor_msgs/msg/PointCloud2`, can be extracted to a single CSV file per point cloud, named by timestamp.

**image** -> Messages of type `sensor_msgs/msg/Image`, that will be directly decoded and saved as single images named by timestamps.

## Images

Images extraction include extra parameters to achieve the desired output:

| Args              | Type      | Description                                                                             |
| ----------------- | --------- | --------------------------------------------------------------------------------------- |
| rectify           | bool      | Whether to rectify the images (will look for <cam_topic>/camera_info)                   |
| scale             | float     | Factor to rescale the images (1.0 will leave them unchanged)                            |
| debayer           | bool      | Whether to convert the bayer image to RGB before saving                                 |
| quality_factor    | float     | (JPG-only) Compress extracted images to reduce size on disk, needs to be 1.0 or lower   |
| convert_12to8bits | bool      | Whether to convert 12 bits images to 8 bits before saving                               |
| brackets          | list[int] | Sort extracted images in specified brackets folder (will look for <cam_topic>/metadata) |
| basler_decompress | bool      | (Basler only) Decompress images, message type should be packets                         |


# TF 

To extract the tf:

1. Add the tf into your config file like it is down in the test_fp.yaml

2. Reinstall rosbagextractor

3. Run the rosbag extractor




### Request TF

Two classes have been develop to request tf that are not saved by default in the rosbags. Currently this two classes respect the folowing assumption : 

1. The desired rate to compute the tf is the tf with the highest publication rate. 
2. The tf are not interpolated. The last published tf is repeated to fit the fastest tf publicaiton rate.
3. Tf are considered static when they are published less than 5 times. Therefore, tf with less than 5 pulication will only load the first tf. (TODO in the next version)
4. Only .csv are supported
5. dynamic joints are not supported (to validate)

#### Example (request)


1. Go in ./src/tf_utils/compute_tf.py
2. Write the path to your tf folder created by rosbag extractor
3. Create a Tfquery object using that path
4. Use the method query.request_tf_a_in_frame_B(<tf to extract>,< Frame of reference>,debug=False)
5. Use the save_tf() method to save the requested tf. 

The requested tf are saved in .../tf/requested_tf/< frame of reference >/<tf to extract>_in_< frame of reference>.csv


###### THERE IS A BUG WITH REQUEST THE ROOT, do not use it with root. 
Multiple tf can be requested before a save because save export all the requested tf that are log at each calculation. 

'''

    path_ = "<path to your folder>/tf"
    query = Tfquery(path_)  
    query.request_tf_a_in_frame_B("tong_left_tips","zedx_left_camera_optical_frame",debug=False)
    query.save_tf()
'''
#### Example (visualization of the tf)
To vizualize the tf :

1. Go in ./src/tf_utils/animation_validation.py
2. Write the path to your tf/requested_tf/< Frame of reference>
3. Create a TfVisualizer 
4. Load the data using that path
4. Use the method query.create_animation to create the animation

The folowing code will create the animation for all the tf computed in the < Frame of reference>. 

'''

    path_ = tf/requested_tf/< Frame of reference>
    visualizer = TfVisualizer()
    visualizer.load_data(path_)
    visualizer.create_animation(save_results=True,camera_view=True,max_iter=0)

'''