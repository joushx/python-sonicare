"""GATT description of the Sonicare (HX992X "Tuscany" family).

Names marked "(inferred)" are educated guesses, everything else is backed by
the decompiled Philips app and/or a HCI snoop log. Characteristics that are
still a mystery keep their numeric id as name. See docs/PROTOCOL.md for the
evidence behind every entry.
"""
from .model import Service, Characteristic, VENDOR_UUID, STANDARD_UUID, MOONSHINE_UUID
from .enums import (
    SonicareBrushingMode,
    SonicareHandleState,
    SonicareSessionType,
    SonicareStrength,
    SonicareValueType as T,
)

PREFIX = VENDOR_UUID.format("")

SERVICES = {
    "0001": Service(
        "Handle",
        {
            "4010": Characteristic("State", T.INT8, SonicareHandleState),
            "4020": Characteristic("4020", T.INT16),
            "4022": Characteristic("4022", T.RAW),
            "4030": Characteristic("4030", T.INT16),
            "4040": Characteristic("4040", T.RAW),
            "4050": Characteristic("Current_Time", T.TIMESTAMP),
        }
    ),
    "0002": Service(
        "State",
        {
            "4070": Characteristic("Current_session", T.INT16),
            "4080": Characteristic("Brushing_Mode", T.INT8, SonicareBrushingMode),
            "4082": Characteristic("State", T.INT8),
            "4090": Characteristic("Active_time", T.INT16),
            # 120 in every capture, same word the app uses for the session
            # payload field ("routine length"): length of the mode in seconds. (inferred)
            "4091": Characteristic("Routine_length", T.INT16),
            "40a0": Characteristic("40a0", T.INT8),
            "40b0": Characteristic("Strength", T.INT8, SonicareStrength),
            "40c0": Characteristic("40c0", T.INT8),
        }
    ),
    "0004": Service(
        "Session",
        {
            "40d0": Characteristic("Last_id", T.INT16),
            # number of stored sessions of the type selected in 40d5
            "40d2": Characteristic("Count", T.INT16),
            "40d5": Characteristic("Type", T.INT8, SonicareSessionType),
            # write a session id (u16) to request it, notifies with the id
            "40e0": Characteristic("Request", T.INT16),
            # notifies the record of the selected type, see sonicare.parsers
            "4100": Characteristic("Data", T.RAW),
            # access control point: write 0 to start a transfer, notifies
            # 0 / 1 when the record has been sent completely
            "4110": Characteristic("Control", T.INT8),
        }
    ),
    "0005": Service(
        "Sensor",
        {
            # bit mask of SonicareSensor; 7 = everything
            "4120": Characteristic("Enable", T.INT16),
            # notifies frames, see sonicare.parsers.parse_sensor_frame
            "4130": Characteristic("Data", T.RAW),
            "4140": Characteristic("4140", T.RAW),
        }
    ),
    "0006": Service(
        "Brush",
        {
            "4210": Characteristic("NFC_Version", T.RAW),
            "4220": Characteristic("4220", T.INT8),
            # 7 byte NFC uid of the brush head, notifies when the head changes
            "4230": Characteristic("Serial", T.RAW),
            "4240": Characteristic("Date", T.STRING),
            "4250": Characteristic("4250", T.INT8),
            "4254": Characteristic("4254", T.INT8),
            "4260": Characteristic("4260", T.INT8),
            "4270": Characteristic("4270", T.INT8),
            # 21600 = 6 h = 3 months of 2 x 2 min; Usage is in the same unit,
            # seconds (inferred)
            "4280": Characteristic("Lifetime", T.INT16),
            "4290": Characteristic("Usage", T.INT16),
            "42a0": Characteristic("42a0", T.INT8),
            "42a2": Characteristic("42a2", T.INT8),
            "42a4": Characteristic("42a4", T.RAW),
            "42a6": Characteristic("42a6", T.INT8),
            "42b0": Characteristic("Payload", T.STRING),
            "42c0": Characteristic("42c0", T.INT16),
        }
    ),
    "0007": Service(
        "Diagnostics",
        {
            # the app reads 4310 and 4320 as 32 bit little endian (64 and 0 on an
            # HX991X), 4360 byte 2
            "4310": Characteristic("4310", T.INT32),
            "4320": Characteristic("4320", T.INT32),
            "4330": Characteristic("4330", T.RAW),
            "4360": Characteristic("4360", T.RAW),
        }
    ),
    "0008": Service(
        "0008",
        {
            "4410": Characteristic("4410", T.RAW),
            "4420": Characteristic("4420", T.RAW),
        }
    ),
    # Philips "Moonshine" DiComm channel, used for the firmware upgrade.
    # Not decoded yet, the names are guesses from the traffic, see docs/PROTOCOL.md.
    "fff1": Service(
        "Moonshine",
        {
            "0001": Characteristic("Tx", T.RAW),
            "0002": Characteristic("Rx_ack", T.RAW),
            "0003": Characteristic("Rx", T.RAW),
            "0004": Characteristic("Control", T.RAW),
            "0005": Characteristic("Info", T.RAW),
        },
        uuid_template=MOONSHINE_UUID,
    ),
    "180f": Service(
        "Battery",
        {
            "2a19": Characteristic("Level", T.INT8),
        },
        uuid_template=STANDARD_UUID,
    ),
    "180a": Service(
        "Device_Information",
        {
            "2a29": Characteristic("Manufacturer", T.STRING),
            "2a24": Characteristic("Model", T.STRING),
            "2a25": Characteristic("Serial", T.STRING),
            "2a27": Characteristic("Hardware", T.STRING),
            "2a26": Characteristic("Firmware", T.STRING),
            "2a28": Characteristic("Software", T.STRING),
            "2a23": Characteristic("System_ID", T.RAW),
            "2a2a": Characteristic("IEEE_Cert", T.RAW),
            "2a50": Characteristic("PnP_ID", T.RAW),
        },
        uuid_template=STANDARD_UUID,
    ),
}
