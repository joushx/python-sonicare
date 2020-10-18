import gatt
import sys
from datetime import datetime
import struct
import time

from .data import SERVICES, PREFIX
from .device import SonicareDevice
from .enums import SonicareValueType

class SonicareClient:

    def __init__(self, mac, ready_callback=None, error_callback=None, disconnect_callback=None):
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
        self.device.connect()

    def _on_ready(self):
        self._generate_methods()

        if self.ready_callback:
            self.ready_callback()

    def _on_notify(self, uuid, value):
        for listener in self.notify_listeners:
            listener(uuid, value)

    def add_notify_listener(self, callback):
        self.notify_listeners.append(callback)

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

            method_name = service_object.name.lower() + "_" + characteristics_object.name.lower()
            self._create_get_method(method_name, characteristic, characteristics_object)
            self._create_subscribe_method(method_name, characteristic, characteristics_object)

    def _create_get_method(self, name, characteristic, characteristics_object):
        setattr(self, "get_" + name, self._create_get_value(characteristic, characteristics_object))

    def _create_subscribe_method(self, name, characteristic, characteristics_object):
        setattr(self, "subscribe_" + name, self._create_notify(characteristic, characteristics_object))

    def _create_get_value(self, characteristic, characteristics_object):
        return lambda self: self._get_value(characteristic, characteristics_object)

    def _create_notify(self, characteristic, characteristics_object):
        return lambda self: self._notify(characteristic)

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

    def _notify(self, characteristic):
        characteristic.enable_notifications()

    def _get_service(self, service_uuid):
        return list(filter(lambda s: s.uuid == service_uuid, self.device.services))[0]

    def _get_characteristic(self, service_uuid, characteristic_uuid):
        service = self._get_service(service_uuid)
        return list(filter(lambda c: c.uuid == characteristic_uuid, service.characteristics))[0]