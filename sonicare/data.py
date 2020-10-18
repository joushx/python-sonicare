from .model import Service, Characteristic
from .enums import SonicareState, SonicareBrushType, SonicareValueType, SonicareHandleState, SonicareBrushingMode, SonicareStrength

PREFIX = "477ea600-a260-11e4-ae37-0002a5d5"

SERVICES = {
    "0001": Service(
        "Handle", 
        {
            "4010": Characteristic("State", SonicareValueType.INT8, SonicareHandleState),
            "4020": Characteristic("4020", SonicareValueType.INT16),
            "4022": Characteristic("4022", SonicareValueType.RAW),
            "4030": Characteristic("4030", SonicareValueType.INT16),
            "4040": Characteristic("4040", SonicareValueType.RAW),
            "4050": Characteristic("Current_Time", SonicareValueType.TIMESTAMP),
        }
    ),
    "0002": Service(
        "State",
        {
            "4070": Characteristic("Current_session", SonicareValueType.INT16),
            "4080": Characteristic("Brushing_Mode", SonicareValueType.INT8, SonicareBrushingMode),
            "4082": Characteristic("State", SonicareValueType.INT8),
            "4090": Characteristic("Active_time", SonicareValueType.INT16),
            "4091": Characteristic("Brushing_Mode2", SonicareValueType.INT8),
            "40b0": Characteristic("Strength", SonicareValueType.INT8, SonicareStrength),
        }
    ),
    "0004": Service(
        "Session",
        {
            "40d0": Characteristic("Last_id", SonicareValueType.INT16),
            "40d2": Characteristic("40d2", SonicareValueType.INT16),
            "40d5": Characteristic("Type", SonicareValueType.INT8),
            "4100": Characteristic("4100", SonicareValueType.INT8),
            "4110": Characteristic("4110", SonicareValueType.RAW),
        }
    ),
    "0005": Service(
        "Gyro",
        {
            "4120": Characteristic("4120", SonicareValueType.INT16),
            "4130": Characteristic("Data", SonicareValueType.RAW),
            "4140": Characteristic("4140", SonicareValueType.RAW),
        }
    ),
    "0006": Service(
        "Brush",
        {
            "4210": Characteristic("NFC_Version", SonicareValueType.RAW),
            "4220": Characteristic("4220", SonicareValueType.INT8),
            "4230": Characteristic("Serial", SonicareValueType.RAW),
            "4240": Characteristic("Date", SonicareValueType.STRING),
            "4250": Characteristic("4250", SonicareValueType.INT8),
            "4254": Characteristic("4254", SonicareValueType.INT8),
            "4260": Characteristic("4260", SonicareValueType.INT8),
            "4270": Characteristic("4270", SonicareValueType.INT8),
            "4280": Characteristic("Lifetime", SonicareValueType.INT16),
            "4290": Characteristic("Usage", SonicareValueType.INT16),
            "42a2": Characteristic("42a2", SonicareValueType.INT8),
            "42a4": Characteristic("42a4", SonicareValueType.RAW),
            "42a6": Characteristic("42a6", SonicareValueType.INT8),
            "42b0": Characteristic("Payload", SonicareValueType.STRING),
            "42c0": Characteristic("42c0", SonicareValueType.INT16),
        }
    ),
    "0007": Service(
        "0007",
        {
            "4310": Characteristic("4310", SonicareValueType.INT16),
            "4320": Characteristic("4320", SonicareValueType.INT16),
            "4330": Characteristic("4330", SonicareValueType.RAW),
            "4360": Characteristic("4360", SonicareValueType.RAW),
        }
    ),
    "0008": Service(
        "0008",
        {
            "4410": Characteristic("4410", SonicareValueType.RAW),
            "4420": Characteristic("4420", SonicareValueType.RAW),
        }
    )
}