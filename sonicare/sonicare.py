import gatt
import sys
from datetime import datetime
import struct
import time

from .data import *

class SonicareClient:

    def __init__(self, mac, ready_callback): 
        self.callback = ready_callback
        self.manager = gatt.DeviceManager(adapter_name='hci0')
        self.device = SonicareDevice(self.on_ready, mac_address=mac, manager=self.manager)
    
    def on_ready(self):
        self._generate_methods()
        self.callback()

    def connect(self):
        self.device.connect()
        
    def get_gyro(self):
        c = self._get_characteristic(PREFIX + "0005", PREFIX + "4130")
        c.enable_notifications()

    def get_sessions(self, data_type, id):

        c = self._get_characteristic(PREFIX + "0004", PREFIX + "40e0")
        c.enable_notifications()
        c = self._get_characteristic(PREFIX + "0004", PREFIX + "4110")
        c.enable_notifications()
        c = self._get_characteristic(PREFIX + "0004", PREFIX + "4100")
        c.enable_notifications()

        print("write type")
        c = self._get_characteristic(PREFIX + "0004", PREFIX + "40d5")
        c.write_value([3])

        print("write session id")
        c = self._get_characteristic(PREFIX + "0004", PREFIX + "40e0")
        c.write_value([0x40, 0x05])

        print("write control")
        c = self._get_characteristic(PREFIX + "0004", PREFIX + "4110")
        c.write_value([0x00])

    def _generate_methods(self):
        for service in self.device.services:
            service_object = SERVICES.get(service.uuid[-4:])

            if not service_object:
                continue

            self._generate_methods_for_service(service, service_object=service_object)

    def _generate_methods_for_service(self, service, service_object):
        for characteristic in service.characteristics:
            characteristics_object = service_object.characteristics.get(characteristic.uuid[-4:])
            if not characteristics_object:
                continue

            method_name = "get_" + service_object.name.lower() + "_" + characteristics_object.name.lower()
            setattr(self, method_name, self._create_get_value(characteristic, characteristics_object))

    def _create_get_value(self, characteristic, characteristics_object):
        return lambda self: self._get_value(characteristic, characteristics_object)

    def _get_value(self, characteristic, characteristics_object):
        value = characteristic.read_value()
        print(value)
        valuetype = characteristics_object.data_type

        if valuetype == SonicareValueType.INT8:
            if characteristics_object.enum:
                int_value = int(value[0])
                return characteristics_object.enum(int_value).name

            return int(value[0])
        elif valuetype == SonicareValueType.STRING:
            return ''.join([str(v) for v in value])
        elif valuetype == SonicareValueType.INT16:
            return value[1] << 8 | value[0]
        elif valuetype == SonicareValueType.INT32:
            return value[0] | value[1] << 8 | value[2] << 16 | value[3] << 24
        elif valuetype == SonicareValueType.TIMESTAMP:
            return datetime.fromtimestamp(value[0] | value[1] << 8 | value[2] << 16 | value[3] << 24)
        elif valuetype == SonicareValueType.RAW:
            return list(map(lambda i: "{:02x}".format(int(i)), value))

    def _get_service(self, service_uuid):
        return list(filter(lambda s: s.uuid == service_uuid, self.device.services))[0]

    def _get_characteristic(self, service_uuid, characteristic_uuid):
        service = self._get_service(service_uuid)
        return list(filter(lambda c: c.uuid == characteristic_uuid, service.characteristics))[0]

class SonicareDevice(gatt.Device):

    def __init__(self, ready_callback, mac_address, manager, managed=True):
        super().__init__(mac_address, manager, managed)
        self.ready_callback = ready_callback

    def services_resolved(self):
        super().services_resolved()
        self.ready_callback()
    
    def characteristic_value_updated(self, characteristic, value):

        if characteristic.uuid == PREFIX + "4130":
            data_type = struct.unpack("<H", value[:2])[0]
            counter = struct.unpack("<H", value[2:4])[0]

            if data_type == 4:
                v1 = struct.unpack("<h", value[4:6])[0]
                v2 = struct.unpack("<h", value[6:8])[0]
                v3 = struct.unpack("<h", value[8:10])[0]
                v4 = struct.unpack("<h", value[10:12])[0]
                v5 = struct.unpack("<h", value[12:14])[0]
                v6 = struct.unpack("<h", value[14:16])[0]
                print("Type: {:05} Counter: {:05} Acc1: {:05} Acc2: {:05} Acc3: {:05} X: {:05} Gyro2: {:05} Gyro3: {:05}".format(data_type, counter, v1, v2, v3, v4, v5, v6))

            if data_type == 2:
                pass
                v1 = struct.unpack("<h", value[4:6])[0]
                print("Type: {:05} Counter: {:05} V2: {:05}".format(data_type, counter, v1))
            elif data_type == 1:
                v1 = struct.unpack("<h", value[4:6])[0]
                print(value[4:].hex() + " Type: {:05} Counter: {:05} V1: {:05}".format(data_type, counter, v1))
        else:
            print(value.hex())
        
