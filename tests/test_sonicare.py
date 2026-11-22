import math
import os
import struct
import sys
import types
import unittest
from datetime import datetime

# the library imports gatt, a minimal stand-in is enough here
class FakeGattDevice:
    def __init__(self, mac_address, manager, managed=True):
        self.services = []

sys.modules.setdefault("gatt", types.SimpleNamespace(Device=FakeGattDevice, DeviceManager=object))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sonicare import parsers
from sonicare.codec import decode, encode
from sonicare.data import SERVICES
from sonicare.enums import SonicareBrushingMode, SonicareBrushType, SonicareSessionType
from sonicare.sonicare import SonicareClient
from sonicare.sessions import SessionDownloader, parse_session, RECORD_TYPES

# Characteristics seen in the GATT table of hci_snoop_2020_10_11_15_19_57.cfa
SNOOP_TABLE = {
    "0001": ['4010', '4020', '4022', '4030', '4040', '4050'],
    "0002": ['4070', '4080', '4082', '4090', '4091', '40a0', '40b0', '40c0'],
    "0004": ['40d0', '40d2', '40d5', '40e0', '4100', '4110'],
    "0005": ['4120', '4130', '4140'],
    "0006": ['4210', '4220', '4230', '4240', '4250', '4254', '4260', '4270', '4280', '4290', '42a0', '42a2', '42a4', '42a6', '42b0', '42c0'],
    "0007": ['4310', '4320', '4330', '4360'],
    "0008": ['4410', '4420'],
    "fff1": ['0001', '0002', '0003', '0004', '0005'],
}

# Sensor/Data notifications from the same capture (brush lying on the desk,
# then picked up and moved)
REAL_FRAMES = [
    "04000000edffda00b6ff8bfac2fcd20e",
    "04000100baffc8006fffb6fa26fcf50e",
    "04004800770c76e60e009ff87ff85e0a",
    "04004a007f09a7e5f7fee3f3eef7d907",
]


class ServiceTableTest(unittest.TestCase):
    def test_matches_snoop_log(self):
        for service_id, characteristics in SNOOP_TABLE.items():
            self.assertEqual(sorted(SERVICES[service_id].characteristics), characteristics, service_id)

    def test_uuids(self):
        self.assertEqual(SERVICES["0004"].uuid("40e0"), "477ea600-a260-11e4-ae37-0002a5d540e0")
        self.assertEqual(SERVICES["fff1"].uuid("fff1"), "a651fff1-4074-4131-bce9-56d4261bc7b1")
        self.assertEqual(SERVICES["180f"].uuid("2a19"), "00002a19-0000-1000-8000-00805f9b34fb")

    def test_method_names_are_unique(self):
        names = [(s.name + "_" + c.name).lower() for s in SERVICES.values() for c in s.characteristics.values()]
        self.assertEqual(len(names), len(set(names)))


class CodecTest(unittest.TestCase):
    def characteristic(self, service, char):
        return SERVICES[service].characteristics[char]

    def test_values_from_the_snoop_log(self):
        # (service, characteristic, bytes read in the capture, expected)
        cases = [
            ("0002", "4091", "7800", 120),
            ("0006", "4280", "6054", 21600),
            ("0006", "4290", "0375", 29955),
            ("0004", "40d0", "e003", 992),
            ("0007", "4310", "48000040", 0x40000048),
            ("0001", "4010", "01", "STANDBY"),
            ("0002", "4080", "00", "CLEAN"),
            ("0002", "40b0", "00", "LOW"),
            ("180a", "2a26", "322e31312e3120302e362e312e30", "2.11.1 0.6.1.0"),
            ("0006", "4230", "04b90302506284", ["04", "b9", "03", "02", "50", "62", "84"]),
        ]
        for service, char, raw, expected in cases:
            self.assertEqual(decode(self.characteristic(service, char), bytes.fromhex(raw)), expected, char)

    def test_timestamp(self):
        decoded = decode(self.characteristic("0001", "4050"), bytes.fromhex("8c06835f"))
        self.assertEqual(decoded, datetime.fromtimestamp(0x5f83068c))

    def test_unknown_enum_value_is_kept(self):
        self.assertEqual(decode(self.characteristic("0001", "4010"), b"\x05"), 5)

    def test_encode(self):
        sensor = self.characteristic("0005", "4120")
        self.assertEqual(encode(sensor, 7), bytes.fromhex("0700"))  # what the app writes
        self.assertEqual(encode(sensor, [7, 0]), bytes.fromhex("0700"))
        self.assertEqual(encode(self.characteristic("0004", "40d5"), SonicareSessionType.GYRO_COMPENSATION_DATA), b"\x06")
        self.assertEqual(encode(self.characteristic("0004", "40e0"), 0x0532), bytes.fromhex("3205"))
        time = self.characteristic("0001", "4050")
        self.assertEqual(encode(time, 0x5f83068d), bytes.fromhex("8d06835f"))
        self.assertEqual(encode(time, datetime.fromtimestamp(0x5f83068d)), bytes.fromhex("8d06835f"))
        with self.assertRaises(TypeError):
            encode(self.characteristic("0005", "4130"), 1)


class SensorFrameTest(unittest.TestCase):
    def test_gyro_frame(self):
        frame = parsers.parse_sensor_frame(bytes.fromhex(REAL_FRAMES[0]))
        self.assertEqual(frame.counter, 0)
        self.assertEqual(frame.gyro, (-19, 218, -74))
        self.assertEqual(frame.acceleration, (-1397, -830, 3794))

    def test_acceleration_is_about_one_g(self):
        for hexdata in REAL_FRAMES[:2]:
            x, y, z = parsers.parse_sensor_frame(bytes.fromhex(hexdata)).acceleration
            g = math.sqrt(x * x + y * y + z * z) / parsers.ACCELERATION_COUNTS_PER_G
            self.assertAlmostEqual(g, 1, delta=0.05)

    def test_gyro_is_small_while_lying_still(self):
        frame = parsers.parse_sensor_frame(bytes.fromhex(REAL_FRAMES[0]))
        self.assertTrue(all(abs(v) < 300 for v in frame.gyro))

    def test_temperature_frame(self):
        frame = parsers.parse_sensor_frame(bytes.fromhex("020000006016"))
        self.assertEqual(frame.temperature, 22.375)
        frame = parsers.parse_sensor_frame(bytes.fromhex("02000a008017"))
        self.assertEqual(frame.temperature, 23.5)

    def test_negative_temperature(self):
        self.assertEqual(parsers.decode_temperature(0x80, 0xff), -0.5)

    def test_errors(self):
        with self.assertRaises(ValueError):
            parsers.parse_sensor_frame(b"\x04\x00")
        with self.assertRaises(ValueError):
            parsers.parse_sensor_frame(bytes.fromhex("0400000000"))
        with self.assertRaises(ValueError):
            parsers.parse_sensor_frame(bytes.fromhex("090000000000"))


def routine_record(end=1602356900, session_id=1330, duration=120, routine_length=120, mode=0):
    return b"\x01" + struct.pack("<IHHHB", end, session_id, duration, routine_length, mode) + b"\x00"

def head_record():
    return b"\x01\x00" + struct.pack("<4H", 1000, 2, 3, 400)

def brush_id_record(head_type=0, serial=bytes.fromhex("04b90302506284"), ring=5):
    return b"\x01" + bytes([head_type]) + serial + struct.pack("<HH", 28889, ring) + b"\x00" * 4


class SessionRecordTest(unittest.TestCase):
    """Synthetic records built from the offsets in the app, not captured ones."""

    def test_routine(self):
        session = parsers.parse_routine_session(routine_record(mode=3))
        self.assertEqual(session.session_id, 1330)
        self.assertEqual(session.mode, SonicareBrushingMode.DEEP_CLEAN_PLUS)
        self.assertEqual((session.end_time - session.start_time).total_seconds(), 120)

    def test_unknown_mode_is_kept(self):
        self.assertEqual(parsers.parse_routine_session(routine_record(mode=9)).mode, 9)

    def test_head_replacement(self):
        data = parsers.parse_brush_head_replacement(head_record())
        self.assertEqual((data.pressure_counter, data.downward_counter), (1000, 400))

    def test_brush_id(self):
        brush = parsers.parse_brush_id(brush_id_record())
        self.assertEqual(brush.serial, "04b90302506284")
        self.assertEqual(brush.head_type, SonicareBrushType.ADAPTIVE_CLEAN)
        self.assertEqual(int(brush.ring_id), 5)
        self.assertEqual(brush.head_usage, 28889)
        self.assertEqual(parsers.parse_brush_id(brush_id_record(ring=19)).ring_id, 19)

    def test_gyro_compensation(self):
        data = parsers.parse_gyro_compensation(b"\x01" + b"\0" * 4 + struct.pack("<3h", 52, -129, 91) + bytes([0x60, 0x16]))
        self.assertEqual((data.gx, data.gy, data.gz, data.temperature), (52, -129, 91, 22.375))

    def test_wrong_length(self):
        for parse in (parsers.parse_routine_session, parsers.parse_brush_head_replacement,
                      parsers.parse_brush_id, parsers.parse_gyro_compensation):
            with self.assertRaises(ValueError):
                parse(b"\x00" * 3)


class FakeCharacteristic:
    def __init__(self, uuid, value=b""):
        self.uuid, self.value, self.written, self.notifying = uuid, value, None, None

    def read_value(self): return list(self.value)
    def write_value(self, value): self.written = value
    def enable_notifications(self, enabled): self.notifying = enabled


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = SonicareClient("00:00:00:00:00:00", device_manager=None)
        self.characteristics = {}
        for service_id, service in SERVICES.items():
            characteristics = []
            for char_id in service.characteristics:
                char = FakeCharacteristic(service.uuid(char_id))
                self.characteristics[(service_id, char_id)] = char
                characteristics.append(char)
            self.client.device.services.append(types.SimpleNamespace(uuid=service.uuid(service_id), characteristics=characteristics))

    def test_methods_exist_for_every_characteristic(self):
        for service in SERVICES.values():
            for char in service.characteristics.values():
                name = (service.name + "_" + char.name).lower()
                for prefix in ("read_", "write_", "subscribe_", "unsubscribe_"):
                    self.assertTrue(callable(getattr(self.client, prefix + name)), prefix + name)

    def test_read_all_uuid_families(self):
        self.characteristics[("0001", "4010")].value = b"\x02"        # vendor
        self.characteristics[("180f", "2a19")].value = b"\x3e"        # standard
        self.characteristics[("fff1", "0005")].value = b"\x03\x14\x14"  # moonshine
        self.assertEqual(self.client.read_handle_state(), "RUN")
        self.assertEqual(self.client.read_battery_level(), 62)
        self.assertEqual(self.client.read_moonshine_info(), ["03", "14", "14"])

    def test_write_and_subscribe(self):
        self.client.write_sensor_enable(7)
        self.assertEqual(self.characteristics[("0005", "4120")].written, b"\x07\x00")
        self.client.write_sensor_enable([7, 0])
        self.assertEqual(self.characteristics[("0005", "4120")].written, b"\x07\x00")
        self.client.subscribe_sensor_data()
        self.assertTrue(self.characteristics[("0005", "4130")].notifying)
        self.client.unsubscribe_sensor_data()
        self.assertFalse(self.characteristics[("0005", "4130")].notifying)

    def test_sync_time(self):
        self.client.sync_time()
        written = int.from_bytes(self.characteristics[("0001", "4050")].written, "little")
        self.assertAlmostEqual(written, datetime.now().timestamp(), delta=5)


class FakeClient:
    "Plays the toothbrush side of the session protocol"

    def __init__(self, records, count=2, last_id=1330):
        self.records = records
        self.writes = []
        self.listeners = []
        self.count, self.last_id = count, last_id
        self._type = None
        self._id = None
        service = SERVICES["0004"]
        self.data_uuid, self.control_uuid = service.uuid("4100"), service.uuid("4110")

    def add_notify_listener(self, cb): self.listeners.append(cb)
    def remove_notify_listener(self, cb): self.listeners.remove(cb)
    def subscribe_session_request(self): pass
    def subscribe_session_data(self): pass
    def subscribe_session_control(self): pass
    def read_session_last_id(self): return self.last_id
    def read_session_count(self): return self.count
    def write_session_type(self, value): self._type = value; self.writes.append(("type", int(value)))
    def write_session_request(self, value): self._id = value; self.writes.append(("request", value))

    def write_session_control(self, value):
        self.writes.append(("control", value))
        for listener in list(self.listeners):
            listener(self.data_uuid, self.records[self._type])
            listener(self.control_uuid, b"\x00")


class DownloaderTest(unittest.TestCase):
    def test_downloads_all_sessions(self):
        records = {
            SonicareSessionType.ROUTINE_SESSION: routine_record(),
            SonicareSessionType.BRUSH_HEAD_REPLACEMENT_DATA: head_record(),
            SonicareSessionType.BRUSH_ID: brush_id_record(),
            SonicareSessionType.SESSION_SUMMARY: b"\x01\x02\x03",
        }
        client = FakeClient(records)
        sessions, done = [], []
        SessionDownloader(client, sessions.append, on_done=lambda: done.append(True)).start()

        self.assertEqual(len(sessions), 2)
        self.assertEqual(done, [True])
        self.assertEqual(client.listeners, [])
        requested = [v for kind, v in client.writes if kind == "request"]
        self.assertEqual(requested, [1329] * 4 + [1330] * 4)
        types_written = [v for kind, v in client.writes if kind == "type"]
        self.assertEqual(types_written[:5], [0, 0, 5, 4, 8])  # initial select, then one per record
        self.assertEqual(sessions[0].brush_id.serial, "04b90302506284")

    def test_nothing_stored(self):
        client = FakeClient({}, count=0)
        done = []
        SessionDownloader(client, lambda s: None, on_done=lambda: done.append(True)).start()
        self.assertEqual(done, [True])

    def test_unreadable_characteristic(self):
        client = SonicareClient("00:00:00:00:00:00", device_manager=None)
        service = SERVICES["0004"]
        char = FakeCharacteristic(service.uuid("4100"))
        char.read_value = lambda: None
        client.device.services.append(types.SimpleNamespace(uuid=service.uuid("0004"), characteristics=[char]))
        with self.assertRaises(IOError):
            client.read_session_data()

    def test_corrupt_record_reports_error(self):
        records = {t: b"\x00" for t in RECORD_TYPES}
        errors = []
        SessionDownloader(FakeClient(records), lambda s: None, on_error=errors.append).start()
        self.assertEqual(len(errors), 1)


if __name__ == "__main__":
    unittest.main()
