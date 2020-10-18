import gatt
import struct

from .data import PREFIX

class SonicareDevice(gatt.Device):

    def __init__(self, mac_address, manager, managed=True, ready_callback=None, error_callback=None, disconnect_callback=None):
        super().__init__(mac_address, manager, managed)
        self.ready_callback = ready_callback
        self.error_callback = error_callback
        self.disconnect_callback = disconnect_callback

    def services_resolved(self):
        super().services_resolved()

        if self.ready_callback:
            self.ready_callback()

    def connect_failed(self, error):
        super().connect_failed(error)

        if self.error_callback:
            self.error_callback()

    def disconnect_succeeded(self):
        super().disconnect_succeeded()

        if self.disconnect_callback:
            self.disconnect_callback()
    
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
        
