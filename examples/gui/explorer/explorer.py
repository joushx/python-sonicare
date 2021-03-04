from PyQt5.QtWidgets import QScrollArea, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel

from sonicare import SERVICES
from .characteristic import CharacteristicRow

class ExplorerTab(QScrollArea):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self._init_ui()

    def _init_ui(self):
        self.widget = QWidget()
        self.layout = QVBoxLayout(self)
        self.widget.setLayout(self.layout)
        self.layout.addStretch()

        self.setWidgetResizable(True)
        self.setWidget(self.widget)

        self._generate_services()

    def _generate_services(self):
        values = list(SERVICES.values())
        for i in range(len(values)):
            service = values[i]
            self._generate_service(i, service)
    
    def _generate_service(self, index, service):
        service_box = QGroupBox(service.name)
        self.layout.addWidget(service_box)

        service_box_layout = QVBoxLayout()
        service_box.setLayout(service_box_layout)

        self._generate_characteristics(service, service_box_layout)

    def _generate_characteristics(self, service, parent):
        for characteristic in service.characteristics.values():
            self._generate_characteristic(service, characteristic, parent)

    def _generate_characteristic(self, service, characteristic, parent):
        def on_read():
            self._read_data(service.name, characteristic.name, characteristic_row)

        characteristic_row = CharacteristicRow(characteristic, on_read=on_read)
        parent.addWidget(characteristic_row)

    def _read_data(self, service, characteristic, row):
        read_fn = self.client.__dict__["get_" + service.lower() + "_" + characteristic.lower()]
        response = read_fn()
        row.set_value(response)