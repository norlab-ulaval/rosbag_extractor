from rosbags.typesys import get_types_from_msg, register_types

# Audio message
AUDIO_DATA_MSG = """
uint8[] data
"""

# Audio stamped message
AUDIO_DATA_STAMPED_MSG = """
std_msgs/Header header
audio_common_msgs/AudioData audio
"""


register_types(get_types_from_msg(AUDIO_DATA_MSG, 'audio_common_msgs/msg/AudioData'))
register_types(get_types_from_msg(AUDIO_DATA_STAMPED_MSG, 'audio_common_msgs/msg/AudioDataStamped'))