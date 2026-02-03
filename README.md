# Rosbag Extractor

A python utility to convert rosbags into human-readable data.

# Installation

It is suggested to install the module with pip: 

```bash
pip install -e .
```

# Usage

```bash
usage: rosbag_extractor [-h] [-i INPUT] [-c CONFIG] [-o OUTPUT] [--ignore-missing] [--overwrite] [--silent]

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
  --silent              Silent mode - suppress all output to terminal.
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

**pose** -> Messages of type `geometry_msgs/msg/PoseStamped`, can be extracted to a single CSV file including timestamps.

**point_cloud** -> Messages of type `sensor_msgs/msg/PointCloud2`, can be extracted to a single CSV file per point cloud, named by timestamp.

**image** -> Messages of type `sensor_msgs/msg/Image` or `sensor_msgs/msg/CompressedImage`, that will be directly decoded and saved as single images named by timestamps.

**tf** -> Extract TF transforms from `/tf` and `/tf_static` topics between a base frame and multiple target frames to CSV files.

## Images

Images extraction include extra parameters to achieve the desired output:

| Args              | Type      | Description                                                                             |
| ----------------- | --------- | --------------------------------------------------------------------------------------- |
| rectify           | bool      | Whether to rectify the images (will look for <cam_topic>/camera_info). Supports fisheye/equidistant distortion models |
| scale             | float     | Factor to rescale the images (1.0 will leave them unchanged)                            |
| debayer           | bool      | Whether to convert the bayer image to RGB before saving                                 |
| gray_scale        | bool      | Whether to convert images to grayscale before saving                                    |
| quality_factor    | float     | Compress extracted images to reduce size on disk (use with JPEG2000), needs to be 1.0 or lower |
| convert_12to8bits | bool      | Whether to convert 12 bits images to 8 bits before saving                               |
| brackets          | list[int] | Sort extracted images in specified brackets folder (will look for <cam_topic>/metadata) |
| basler_decompress | bool      | (Basler only) Decompress images, message type should be packets                         |


## TF Transforms

TF extraction allows extracting transform data between frames:

| Args           | Type       | Description                                                             |
| -------------- | ---------- | ----------------------------------------------------------------------- |
| base_frame     | str        | Source frame for transforms (e.g., 'odom') - **required**               |
| target_frames  | list       | List of target frames to extract (e.g., ['base_link']) - **required**   |
| use_euler      | bool       | Output Euler angles (roll, pitch, yaw) instead of quaternions           |
| sample_rate    | float      | Downsample transforms to specified frequency (e.g., 100.0)              |

