from .enums import SonicareValueType

class Service:
    def __init__(self, name, characteristics):
        self.name = name
        self.characteristics = characteristics

class Characteristic:
    def __init__(self, name, data_type=SonicareValueType.RAW, enum=None):
        self.name = name
        self.data_type = data_type
        self.enum = enum