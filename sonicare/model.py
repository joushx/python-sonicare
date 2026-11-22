from .enums import SonicareValueType

# UUID templates. The id of a service / characteristic is substituted for `{}`.
VENDOR_UUID = "477ea600-a260-11e4-ae37-0002a5d5{}"
STANDARD_UUID = "0000{}-0000-1000-8000-00805f9b34fb"
MOONSHINE_UUID = "a651{}-4074-4131-bce9-56d4261bc7b1"

class Service:
    def __init__(self, name, characteristics, uuid_template=VENDOR_UUID):
        self.name = name
        self.characteristics = characteristics
        self.uuid_template = uuid_template

    def uuid(self, short_id):
        "Full 128 bit uuid of the service or one of its characteristics"
        return self.uuid_template.format(short_id)

class Characteristic:
    def __init__(self, name, data_type=SonicareValueType.RAW, enum=None):
        self.name = name
        self.data_type = data_type
        self.enum = enum
