import gatt
import sys
from datetime import datetime
import struct
import time

from .data import SERVICES, PREFIX
from .device import SonicareDevice
from .enums import SonicareValueType

class SonicareClient(object):

    def __init__(self, mac, ready_callback=None, error_callback=None, disconnect_callback=None):
        self._generate_methods()
        self.ready_callback = ready_callback
        self.manager = gatt.DeviceManager(adapter_name='hci0')
        self.device = SonicareDevice(
            mac_address=mac, 
            manager=self.manager, 
            ready_callback=self._on_ready, 
            error_callback=error_callback, 
            disconnect_callback=disconnect_callback,
            notify_callback=self._on_notify
        )
        self.notify_listeners = []

    def connect(self):
        "Created a new connection to the device specified"
        self.device.connect()

    def _on_ready(self):
        if self.ready_callback:
            self.ready_callback()

    def _on_notify(self, uuid, value):
        for listener in self.notify_listeners:
            listener(uuid, value)

    def add_notify_listener(self, callback):
        self.notify_listeners.append(callback)

    def _generate_methods(self):
        for service_id in SERVICES:
            self._generate_methods_for_service(service_id)

    def _generate_methods_for_service(self, service_id):
        service = SERVICES[service_id]
        for characteristic_id in service.characteristics:
            characteristic = service.characteristics[characteristic_id]
            method_name = service.name.lower() + "_" + characteristic.name.lower()
            self._create_get_method(method_name, service_id, characteristic_id, characteristic)
            self._create_subscribe_method(method_name, service_id, characteristic_id)

    def _create_get_method(self, name, service_id, characteristic_id, description):
        setattr(self, "get_" + name, self._create_get_value(service_id, characteristic_id, description))


    def _create_subscribe_method(self, name, service_id, characteristic_id):
        setattr(self, "subscribe_" + name, self._create_notify(service_id, characteristic_id))

    def _create_get_value(self, service_id, characteristic_id, description):
        return lambda self: self._get_value(service_id, characteristic_id, description)

    def _create_notify(self, service_id, characteristic_id):
        return lambda self: self._notify(service_id, characteristic_id)

    def _get_value(self, service_id, characteristic_id, description):
        characteristics_object = self._get_characteristic(PREFIX + service_id, PREFIX + characteristic_id)
        value = characteristics_object.read_value()
        valuetype = description.data_type

        if valuetype == SonicareValueType.INT8:
            if description.enum:
                int_value = int(value[0])
                return description.enum(int_value).name

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

    def _notify(self, service_id, characteristic_id):
        characteristic_object = self._get_characteristic(PREFIX + service_id, PREFIX + characteristic_id)
        characteristic_object.enable_notifications()

    def _get_service(self, service_uuid):
        return list(filter(lambda s: s.uuid == service_uuid, self.device.services))[0]

    def _get_characteristic(self, service_uuid, characteristic_uuid):
        service = self._get_service(service_uuid)
        return list(filter(lambda c: c.uuid == characteristic_uuid, service.characteristics))[0]