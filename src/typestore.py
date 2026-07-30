"""Central typestore holding message definitions that are not part of stock ROS.

ROS1 bags and MCAP files embed their message definitions, so ``AnyReader`` can
build its own typestore from the bag itself and this module is never consulted.
ROS2 sqlite3 bags carry no definitions, and ``AnyReader`` then falls back to the
``default_typestore`` it was given. Registering the custom types here is what
makes those bags readable without having the message packages installed.
"""

from rosbags.typesys import Stores, get_types_from_msg, get_typestore

AUDIO_DATA_MSG = """
uint8[] data
"""

AUDIO_DATA_STAMPED_MSG = """
std_msgs/Header header
audio_common_msgs/AudioData audio
"""

CUSTOM_TYPES = {
    "audio_common_msgs/msg/AudioData": AUDIO_DATA_MSG,
    "audio_common_msgs/msg/AudioDataStamped": AUDIO_DATA_STAMPED_MSG,
}


def build_typestore():
    typestore = get_typestore(Stores.LATEST)
    for typename, definition in CUSTOM_TYPES.items():
        typestore.register(get_types_from_msg(definition, typename))
    return typestore


typestore = build_typestore()
