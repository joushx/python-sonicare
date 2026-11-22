import gatt
from datetime import datetime

from .codec import decode, encode
from .data import SERVICES
from .device import SonicareDevice

class SonicareClient(object):

    def __init__(self, mac, device_manager: gatt.DeviceManager, ready_callback=None, error_callback=None, disconnect_callback=None):
        self._generate_methods()
        self.ready_callback = ready_callback
        self.manager = device_manager
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

    def remove_notify_listener(self, callback):
        self.notify_listeners.remove(callback)

    def _generate_methods(self):
        for service_id in SERVICES:
            self._generate_methods_for_service(service_id)

    def _generate_methods_for_service(self, service_id):
        service = SERVICES[service_id]
        for characteristic_id in service.characteristics:
            characteristic = service.characteristics[characteristic_id]
            method_name = service.name.lower() + "_" + characteristic.name.lower()
            self._create_read_method(method_name, service_id, characteristic_id, characteristic)
            self._create_write_method(method_name, service_id,  characteristic_id, characteristic)
            self._create_subscribe_method(method_name, service_id, characteristic_id)
            self._create_unsubscribe_method(method_name, service_id, characteristic_id)

    def _create_read_method(self, name, service_id, characteristic_id, description):
        setattr(self, "read_" + name, self._create_read(service_id, characteristic_id, description))

    def _create_write_method(self, name, service_id, characteristic_id, description):
        setattr(self, "write_" + name, self._create_write(service_id, characteristic_id, description))

    def _create_subscribe_method(self, name, service_id, characteristic_id):
        setattr(self, "subscribe_" + name, self._create_subscribe(service_id, characteristic_id))

    def _create_unsubscribe_method(self, name, service_id, characteristic_id):
        setattr(self, "unsubscribe_" + name, self._create_unsubscribe(service_id, characteristic_id))

    def _create_read(self, service_id, characteristic_id, description):
        return lambda: self._read(service_id, characteristic_id, description)

    def _create_write(self, service_id, characteristic_id, description):
        return lambda value: self._write(service_id, characteristic_id, description, value)

    def _create_subscribe(self, service_id, characteristic_id):
        return lambda: self._subscribe(service_id, characteristic_id)

    def _create_unsubscribe(self, service_id, characteristic_id):
        return lambda: self._unsubscribe(service_id, characteristic_id)

    def _read(self, service_id, characteristic_id, description):
        characteristics_object = self._get_characteristic(service_id, characteristic_id)
        value = characteristics_object.read_value()
        if value is None:
            raise IOError("{} cannot be read, it is probably notify or write only".format(description.name))
        return decode(description, value)

    def _write(self, service_id, characteristic_id, description, value):
        characteristics_object = self._get_characteristic(service_id, characteristic_id)
        characteristics_object.write_value(encode(description, value))

    def _subscribe(self, service_id, characteristic_id):
        characteristic_object = self._get_characteristic(service_id, characteristic_id)
        characteristic_object.enable_notifications(True)

    def _unsubscribe(self, service_id, characteristic_id):
        characteristic_object = self._get_characteristic(service_id, characteristic_id)
        characteristic_object.enable_notifications(False)

    def sync_time(self):
        "Set the clock of the handle to the current time, like the app does after connecting"
        self.write_handle_current_time(datetime.now())

    def _get_service(self, service_id):
        uuid = SERVICES[service_id].uuid(service_id)
        return next(s for s in self.device.services if s.uuid == uuid)

    def _get_characteristic(self, service_id, characteristic_id):
        service = self._get_service(service_id)
        uuid = SERVICES[service_id].uuid(characteristic_id)
        return next(c for c in service.characteristics if c.uuid == uuid)
