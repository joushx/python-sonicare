from enum import Enum, IntEnum

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
    """Raw mode id as sent by the HX992X.

    The app maps the id through a per-model table (HX960X, HX9120, HX961X and
    HX991X use shorter ones); this is the table of the models that fall back to
    the default, which includes the HX992X the traces were taken from.
    """
    CLEAN = 0
    WHITE_PLUS = 1
    GUM_HEALTH = 2
    DEEP_CLEAN_PLUS = 3
    TONGUE_CLEAN = 4

class SonicareStrength(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

class SonicareBrushType(Enum):
    """Brush head type, as in the `Brush ID` session payload (app: BRUSH_HEAD_TYPES)."""
    ADAPTIVE_CLEAN = 0
    ADAPTIVE_WHITE = 1
    ADAPTIVE_GUMS = 2
    TONGUE_CLEAN = 3
    NON_RFID = 4

class SonicareBrushRing(IntEnum):
    """Brush head ring id (app: NebraskaBrushHead, ring id = ordinal + 1)."""
    PREMIUM_PLAQUE_CONTROL_WHITE = 1
    PREMIUM_PLAQUE_CONTROL_BLACK = 2
    PREMIUM_GUM_CARE_WHITE = 3
    PREMIUM_GUM_CARE_BLACK = 4
    PREMIUM_WHITE_WHITE = 5
    PREMIUM_WHITE_BLACK = 6
    OPTIMAL_PLAQUE_CONTROL_WHITE = 7
    OPTIMAL_GUM_CARE_WHITE = 8
    OPTIMAL_WHITE_WHITE = 9
    OPTIMAL_WHITE_BLACK = 10
    OPTIMAL_WHITE_WHITE_COMPACT = 11
    INTER_CARE_WHITE = 12
    INTER_CARE_WHITE_COMPACT = 13
    TONGUE_CARE_WHITE = 14
    TONGUE_CARE_BLACK = 15

class SonicareSessionType(IntEnum):
    """Value written to Session/Type (40d5) to select which record is served."""
    ROUTINE_SESSION = 0
    PRESSURE = 1
    TEMP = 2
    ACC_GYRO = 3
    BRUSH_ID = 4
    BRUSH_HEAD_REPLACEMENT_DATA = 5
    GYRO_COMPENSATION_DATA = 6
    DIAGNOSTICS = 7
    SESSION_SUMMARY = 8
    UNDEFINED = 9

class SonicareSensor(IntEnum):
    """Bits of Sensor/Enable (4120); the app writes 7 (all three)."""
    GYRO_ACCEL = 1
    TEMPERATURE = 1 << 1
    PRESSURE = 1 << 2
