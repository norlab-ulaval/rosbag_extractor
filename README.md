# Rosbag Extractor

A python utility to convert rosbags into human-readable data.

# Usage

```bash
usage: main.py [-h] [-i INPUT] [-c CONFIG] [-o OUTPUT] [--ignore-missing] [--overwrite]

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

# Supported types

The following types are currently implemented in the tool:

**basic** -> Any basic data without complex encoding, such as most `std_msgs`, as well as custom messages containing only basic types.

**imu** -> Messages of type `sensor_msgs/msg/Imu`, can be extracted to a single CSV file including timestamps.

**gnss** -> Messages of type `sensor_msgs/msg/NavSatFix`, can be extracted to a single CSV file including timestamps.

**audio** -> Messages of type `audio_common_msgs/msg/AudioData` or `audio_common_msgs/msg/AudioDataStamped`, can be extracted to a single MP3 or WAV file.

**odometry** -> Messages of type `nav_msgs/msg/Odometry`, can be extracted to a single CSV file including timestamps.

**point_cloud** -> Messages of type `sensor_msgs/msg/PointCloud2`, can be extracted to a single CSV file per point cloud, named by timestamp.

**image** -> Messages of type `sensor_msgs/msg/Image`, that will be directly decoded and saved as single images named by timestamps.
