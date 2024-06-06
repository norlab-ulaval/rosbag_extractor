# Rosbag Extractor
A set of scripts to convert rosbags into human-readable data. It was tested with mcap ROS2 bags only.

# Usage 
To use, create a config in the `configs` folder, which must be a list of dictionaries, each containing the following information: 

| Key      	    | Value             	                                |
|-----------	|-----------------------------------------------------	|
| type      	| Type of data to handle (see supported types below)    |
| topic     	| Name of the topic to extract                          |
| folder    	| Name of the subfolder where to extract the data       |
| extension 	| File extension for the extracted data           	    |

# Supported types
The following types are currently implemented in the tool: 

**basic** -> Any basic data without complex encoding, such as most `std_msgs`, as well as custom messages containing only basic types.

**imu** -> Messages of type `sensor_msgs/msg/Imu`, can be extracted to a single CSV file including timestamps.

**gnss** -> Messages of type `sensor_msgs/msg/NavSatFix`, can be extracted to a single CSV file including timestamps.

**audio** -> Messages of type `audio_common_msgs/msg/AudioData` or `audio_common_msgs/msg/AudioDataStamped`, can be extracted to a single MP3 file. 

**odometry** -> Messages of type `nav_msgs/msg/Odometry`, can be extracted to a single CSV file including timestamps.

**point_cloud** -> Messages of type `sensor_msgs/msg/PointCloud2`, can be extracted to a single CSV file per point cloud, named by timestamp.

**raw_image** -> Messages of type `sensor_msgs/msg/Image`, that will be directly decoded and saved as single PNG images named by timestamps.

**rectified_image** -> Messages of type `sensor_msgs/msg/Image`, that will be directly decoded, then rectified using the corresponding `camera_info` message. 