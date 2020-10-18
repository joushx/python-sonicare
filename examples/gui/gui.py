import time
from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QLabel, QWidget, QVBoxLayout, QPushButton
import os
import sys
sys.path.append(os.path.dirname(__file__) + "/../../")

from sonicare import SonicareClient, SERVICES
from explorer import ExplorerTab

class SonicareApplication(QMainWindow):
    def __init__(self, mac):
        super().__init__()
        self.setWindowTitle('Sonicare')

        self.client = SonicareClient(
            mac=mac, 
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

        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(lambda: self._connect())
        layout.addWidget(connect_button)

        tabs = self._build_tabs()
        layout.addWidget(tabs)

        return widget

    def _build_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(ExplorerTab(self.client), "Explorer")
        self.tabs.setEnabled(False)
        return self.tabs

    def _connect(self):
        self.client.connect()

    def _on_ready(self):
        print("Ready")
        self.tabs.setEnabled(True)

    def _on_error(self):
        print("Connection failed")

    def _on_disconnect(self):
        print("Disconnected")