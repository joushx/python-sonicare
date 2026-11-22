"""Decoders for the binary records the toothbrush sends (no BLE needed).

Sensor frames (Sensor/Data, 4130) were checked against a HCI snoop log of an
HX992X, the session records (Session/Data, 4100) follow the offsets of the
Philips app's OfflineDataParser and were run against an HX991X (routine
session, brush head replacement data, brush id and session summary; gyro
compensation data has not been fetched from a real brush).
All numbers are little endian.
"""
import struct
from dataclasses import dataclass
from datetime import datetime, timedelta

from .enums import SonicareBrushingMode, SonicareBrushType, SonicareBrushRing

# The accelerometer reads 4096 +- 4 % counts while the brush lies still, so
# 1 g = 4096 counts (+-8 g range). The scale of the gyroscope is not known.
ACCELERATION_COUNTS_PER_G = 4096

FRAME_PRESSURE = 1
FRAME_TEMPERATURE = 2
FRAME_GYRO_ACCEL = 4


@dataclass
class SensorFrame:
    counter: int


@dataclass
class GyroAccelFrame(SensorFrame):
    gyro: tuple          # x, y, z raw counts
    acceleration: tuple  # x, y, z raw counts, see ACCELERATION_COUNTS_PER_G


@dataclass
class TemperatureFrame(SensorFrame):
    temperature: float   # degree celsius


@dataclass
class PressureFrame(SensorFrame):
    # Layout taken from the first version of the GUI, never seen in a capture
    # (brush was idle) so unverified.
    pressure: int
    alarm: int


def _check_length(data, expected, what):
    if len(data) != expected:
        raise ValueError("{} must be {} bytes, got {}".format(what, expected, len(data)))


def decode_temperature(low, high):
    "8.8 fixed point, high byte signed (also used by the gyro compensation record)"
    return struct.unpack("<h", bytes([low, high]))[0] / 256


def parse_sensor_frame(data):
    """Decode one notification of Sensor/Data (4130).

    Layout: u16 type, u16 counter, payload. Gyro/accel frames (type 4, 16 bytes)
    arrive at ~31 Hz with six s16: gyroscope xyz first, acceleration xyz second.
    Temperature frames (type 2, 6 bytes) come about every 2 s.
    """
    data = bytes(data)
    if len(data) < 4:
        raise ValueError("sensor frame too short: {}".format(data.hex()))
    frame_type, counter = struct.unpack("<HH", data[:4])

    if frame_type == FRAME_GYRO_ACCEL:
        _check_length(data, 16, "gyro frame")
        values = struct.unpack("<6h", data[4:])
        return GyroAccelFrame(counter, values[:3], values[3:])
    if frame_type == FRAME_TEMPERATURE:
        _check_length(data, 6, "temperature frame")
        return TemperatureFrame(counter, decode_temperature(data[4], data[5]))
    if frame_type == FRAME_PRESSURE:
        if len(data) < 7:
            raise ValueError("pressure frame too short: {}".format(data.hex()))
        return PressureFrame(counter, struct.unpack("<h", data[4:6])[0], data[6])
    raise ValueError("unknown sensor frame type {}".format(frame_type))


# ---------------------------------------------------------------- sessions

@dataclass
class RoutineSession:
    "Session/Type ROUTINE_SESSION, 13 bytes"
    session_id: int
    end_time: datetime
    duration: int         # seconds, the app discards sessions outside 10..210
    routine_length: int   # seconds
    mode: object          # SonicareBrushingMode, or the raw id if unknown

    @property
    def start_time(self):
        return self.end_time - timedelta(seconds=self.duration)


@dataclass
class BrushHeadReplacementData:
    """Session/Type BRUSH_HEAD_REPLACEMENT_DATA, 10 bytes.

    The app turns `pressure_counter` into a pressure time (x 0.33) and
    `downward_counter` into seconds (x 0.01) for the brush head wear.
    Seen on an HX991X: the counters are in 1/100 s, `downward_counter` is
    always `unknown_4 + unknown_6` and about 100 x the session duration.
    """
    pressure_counter: int
    unknown_4: int
    unknown_6: int
    downward_counter: int


@dataclass
class BrushId:
    "Session/Type BRUSH_ID, 17 bytes"
    head_type: object     # SonicareBrushType, or the raw id if unknown
    serial: str           # 7 byte NFC uid, hex (same as Brush/Serial)
    head_usage: int       # Brush/Usage of the head at the end of the session, seconds
    ring_id: object       # SonicareBrushRing, or the raw id if unknown (19 on an HX991X)


@dataclass
class GyroCompensation:
    "Session/Type GYRO_COMPENSATION_DATA, 13 bytes: gyroscope offset at rest"
    gx: int
    gy: int
    gz: int
    temperature: float


def _enum_or_raw(enum, value):
    try:
        return enum(value)
    except ValueError:
        return value


def parse_routine_session(data):
    data = bytes(data)
    _check_length(data, 13, "routine session")
    end, session_id, duration, routine_length, mode = struct.unpack("<IHHHB", data[1:12])
    return RoutineSession(
        session_id=session_id,
        end_time=datetime.fromtimestamp(end),
        duration=duration,
        routine_length=routine_length,
        mode=_enum_or_raw(SonicareBrushingMode, mode),
    )


def parse_brush_head_replacement(data):
    data = bytes(data)
    _check_length(data, 10, "brush head replacement data")
    return BrushHeadReplacementData(*struct.unpack("<4H", data[2:10]))


def parse_brush_id(data):
    data = bytes(data)
    _check_length(data, 17, "brush id")
    head_type = data[1]
    serial = data[2:9].hex()
    head_usage, ring_id = struct.unpack("<HH", data[9:13])
    return BrushId(
        head_type=_enum_or_raw(SonicareBrushType, head_type),
        serial=serial,
        head_usage=head_usage,
        ring_id=_enum_or_raw(SonicareBrushRing, ring_id),
    )


def parse_gyro_compensation(data):
    data = bytes(data)
    _check_length(data, 13, "gyro compensation data")
    gx, gy, gz = struct.unpack("<3h", data[5:11])
    return GyroCompensation(gx, gy, gz, decode_temperature(data[11], data[12]))
