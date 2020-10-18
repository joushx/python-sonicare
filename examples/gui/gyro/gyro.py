from PyQt5.QtWidgets import QScrollArea, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import struct

from .model import GyroscopeFrame, FrameType
from .plot import PlotWidget

class GyroTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self._init_ui()
        self._frames = []

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        start_button = QPushButton("Start")
        start_button.clicked.connect(lambda: self._start())
        self.layout.addWidget(start_button)

        self.plot = PlotWidget()
        self.layout.addWidget(self.plot)

    def _start(self):
        self.client.add_notify_listener(self._on_data)
        self.client.subscribe_gyro_data(self.client)

    def _on_data(self, uuid, value):

        if not uuid[-4:] == "4130":
            return

        data_type = struct.unpack("<H", value[:2])[0]
        counter = struct.unpack("<H", value[2:4])[0]

        if data_type == FrameType.GYROSCOPE:
            v1 = struct.unpack("<h", value[4:6])[0]
            v2 = struct.unpack("<h", value[6:8])[0]
            v3 = struct.unpack("<h", value[8:10])[0]
            v4 = struct.unpack("<h", value[10:12])[0]
            v5 = struct.unpack("<h", value[12:14])[0]
            v6 = struct.unpack("<h", value[14:16])[0]
            frame = GyroscopeFrame(counter, v1, v2, v3, v4, v5, v6)

            self._frames.append(frame)

            if len(self._frames) > 10:
                self._add_frames(self._frames)
                self._frames = []

        """elif data_type == 2:
            v1 = struct.unpack("<h", value[4:6])[0]
            print("Type: {:05} Counter: {:05} V2: {:05}".format(data_type, counter, v1))
        elif data_type == 1:
            v1 = struct.unpack("<h", value[4:6])[0]
            print(value[4:].hex() + " Type: {:05} Counter: {:05} V1: {:05}".format(data_type, counter, v1))"""

    def _add_frames(self, frames):
        self.plot.add_points(frames)