from enum import Enum

class SonicareHandleState(Enum):
    OFF = 0
    STANDBY = 1
    RUN = 2
    CHARGE = 3
    SHUTDOWN = 4
    VALIDATE = 6
    UNKNOWN = 7

class SonicareValueType(Enum):
    STRING = 0
    INT8 = 1
    INT16 = 2
    INT32 = 3
    TIMESTAMP = 4
    RAW = 5

class SonicareState(Enum):
    OFF = 0
    ON = 1
    PAUSE = 2

class SonicareBrushingMode(Enum):
    CLEAN = 0
    WHITE_PLUS = 1
    GUM_HEALTH = 2
    DEEP_CLEAN_PLUS = 3

class SonicareStrength(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

class SonicareBrushType(Enum):
    UNKNOWN = 0
    ADAPTIVE_CLEAN = 1
    ADAPTIVE_WHITE = 2
    TONGUE_CARE = 3
    ADAPTIVE_GUMS = 4