import gatt
import struct

from .data import PREFIX

class SonicareDevice(gatt.Device):

    def __init__(self, mac_address, manager, managed=True, ready_callback=None, error_callback=None, disconnect_callback=None, notify_callback=None):
        super().__init__(mac_address, manager, managed)
        self.ready_callback = ready_callback
        self.error_callback = error_callback
        self.disconnect_callback = disconnect_callback
        self.notify_callback = notify_callback

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
        if self.notify_callback:
            self.notify_callback(characteristic.uuid, value)
        
