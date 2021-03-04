import time
from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QLabel, QWidget, QVBoxLayout, QPushButton
import os
import sys
sys.path.append(os.path.dirname(__file__) + "/../../")

from sonicare import SonicareClient, SERVICES
from explorer import ExplorerTab
from sensor import SensorTab
import gatt

class SonicareApplication(QMainWindow):
    def __init__(self, mac):
        super().__init__()
        self.setWindowTitle('Sonicare')

        self.client = SonicareClient(
            mac=mac, 
            device_manager=gatt.DeviceManager(adapter_name='hci0'),
            ready_callback=self._on_ready, 
            error_callback=self._on_error, 
            disconnect_callback=self._on_disconnect
        )

        self.setCentralWidget(self._build_main_widget())
        self.show()

    def _build_main_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        widget.setLayout(layout)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(lambda: self._connect())
        layout.addWidget(self.connect_button)

        tabs = self._build_tabs()
        layout.addWidget(tabs)

        return widget

    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(ExplorerTab(self.client), "Explorer")
        self.tabs.addTab(SensorTab(self.client), "Sensor")
        self.tabs.setEnabled(False)
        return self.tabs

    def _connect(self):
        self.client.connect()

    def _on_ready(self):
        print("Ready")
        self.connect_button.setEnabled(False)
        self.tabs.setEnabled(True)

    def _on_error(self):
        self.connect_button.setEnabled(True)
        print("Connection failed")

    def _on_disconnect(self):
        self.connect_button.setEnabled(True)
        print("Disconnected")