import time
import tkinter as tk
import tkinter.ttk as ttk
import os
import sys
sys.path.append(os.path.dirname(__file__) + "/../../")

from sonicare import SonicareClient, SERVICES

class SonicareApplication:
    def __init__(self, mac):
        self.client = SonicareClient(
            mac=mac, 
            ready_callback=self._on_ready, 
            error_callback=self._on_error, 
            disconnect_callback=self._on_disconnect
        )

    def start(self):
        self._init_ui()

    def _init_ui(self):
        self.gui_root = tk.Tk()

        connect_button = tk.Button(self.gui_root, text="Connect", command=lambda: self._connect())
        connect_button.grid(row=0, column=0)

        self._generate_services()
        self.gui_root.mainloop()

    def _connect(self):
        self.client.connect()

    def _on_ready(self):
        print("Ready")

    def _on_error(self):
        print("Connection failed")

    def _on_disconnect(self):
        print("Disconnected")

    def _generate_services(self):
        values = list(SERVICES.values())
        for i in range(len(values)):
            service = values[i]
            self._generate_service(i, service)
    
    def _generate_service(self, index, service):
        service_frame = tk.LabelFrame(self.gui_root, text=service.name)
        service_frame.grid(row=int(index/2)+1, column=index%2, sticky="nsew")
        self._generate_characteristics(service, service_frame)

    def _generate_characteristics(self, service, parent):
        row = 0
        for characteristic in service.characteristics.values():
            self._generate_characteristic(service, characteristic, parent, row)
            row += 1

    def _generate_characteristic(self, service, characteristic, parent, row):
        name_label = tk.Label(parent, text=characteristic.name)
        name_label.grid(row=row, column=1)

        value_display = tk.Entry(parent)
        value_display.grid(row=row, column=3)

        read_button = tk.Button(parent, text="Read", command=self._generate_get_data_fn(service.name, characteristic.name, value_display))
        read_button.grid(row=row, column=2)

    def _generate_get_data_fn(self, service, characteristic, inp):
        return lambda: self._read_data(service, characteristic, inp)

    def _read_data(self, service, characteristic, inp):
        read_fn = self.client.__dict__["get_" + service.lower() + "_" + characteristic.lower()]
        response = read_fn(self.client)
        inp.delete(0, 'end')
        inp.insert(0, response)