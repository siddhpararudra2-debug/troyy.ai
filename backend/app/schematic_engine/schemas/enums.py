from enum import Enum

class NetType(str, Enum):
    POWER = "POWER"
    GROUND = "GROUND"
    SIGNAL = "SIGNAL"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

class PinDirection(str, Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    BIDIR = "BIDIR"
    POWER_IN = "POWER_IN"
    POWER_OUT = "POWER_OUT"
    PASSIVE = "PASSIVE"

class ERCSeverity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
