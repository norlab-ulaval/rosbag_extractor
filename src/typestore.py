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

EXTENDED_JOINT_STATE_MSG = """
std_msgs/Header header
string[] name
float64[] position
float64[] velocity
float64[] acceleration
float64[] effort
"""

CONTACT_MSG = """
uint8 STATE_OPEN=0
uint8 STATE_CLOSED=1
uint8 STATE_SLIPPING=2

std_msgs/Header header
string name
uint8 state
geometry_msgs/Wrench wrench
geometry_msgs/Point position
geometry_msgs/Vector3 normal
float64 friction_coefficient
float64 restitution_coefficient
"""

ANYMAL_STATE_MSG = """
std_msgs/Header header

int8 STATE_ERROR_SENSOR = -3
int8 STATE_ERROR_ESTIMATOR = -2
int8 STATE_ERROR_UNKNOWN = -1
int8 STATE_OK = 0
int8 STATE_UNINITIALIZED = 1
int8 state

geometry_msgs/PoseStamped pose
geometry_msgs/TwistStamped twist
any_msgs/ExtendedJointState joints
Contact[] contacts
geometry_msgs/TransformStamped[] frame_transforms
"""

SE_ACTUATOR_STATE_MSG = """
std_msgs/Header header
string name
uint32 statusword
float64 current
float64 gear_position
float64 gear_velocity
float64 joint_position
float64 joint_velocity
float64 joint_acceleration
float64 joint_torque
sensor_msgs/Imu imu
"""

SE_ACTUATOR_COMMAND_MSG = """
std_msgs/Header header
string name

int16 MODE_NA = 0
int16 MODE_FREEZE = 1
int16 MODE_DISABLE = 2
int16 MODE_CURRENT = 3
int16 MODE_MOTOR_POSITION = 4
int16 MODE_MOTOR_VELOCITY = 5
int16 MODE_GEAR_POSITION = 6
int16 MODE_GEAR_VELOCITY = 7
int16 MODE_JOINT_POSITION = 8
int16 MODE_JOINT_VELOCITY = 9
int16 MODE_JOINT_TORQUE = 10
int16 MODE_JOINT_POSITION_VELOCITY = 11
int16 MODE_JOINT_POSITION_VELOCITY_TORQUE = 12
int16 MODE_JOINT_POSITION_VELOCITY_TORQUE_PID_GAINS = 13
int16 mode

float64 current
float64 position
float64 velocity
float64 joint_torque
float32 pid_gains_p
float32 pid_gains_i
float32 pid_gains_d
"""

SE_ACTUATOR_READING_MSG = """
std_msgs/Header header
SeActuatorState state
SeActuatorCommand commanded
"""

SE_ACTUATOR_READINGS_MSG = """
SeActuatorReading[] readings
"""

CUSTOM_TYPES = {
    "audio_common_msgs/msg/AudioData": AUDIO_DATA_MSG,
    "audio_common_msgs/msg/AudioDataStamped": AUDIO_DATA_STAMPED_MSG,
    "any_msgs/msg/ExtendedJointState": EXTENDED_JOINT_STATE_MSG,
    "anymal_msgs/msg/Contact": CONTACT_MSG,
    "anymal_msgs/msg/AnymalState": ANYMAL_STATE_MSG,
    "series_elastic_actuator_msgs/msg/SeActuatorState": SE_ACTUATOR_STATE_MSG,
    "series_elastic_actuator_msgs/msg/SeActuatorCommand": SE_ACTUATOR_COMMAND_MSG,
    "series_elastic_actuator_msgs/msg/SeActuatorReading": SE_ACTUATOR_READING_MSG,
    "series_elastic_actuator_msgs/msg/SeActuatorReadings": SE_ACTUATOR_READINGS_MSG,
}


def build_typestore():
    typestore = get_typestore(Stores.LATEST)
    for typename, definition in CUSTOM_TYPES.items():
        typestore.register(get_types_from_msg(definition, typename))
    return typestore


typestore = build_typestore()
