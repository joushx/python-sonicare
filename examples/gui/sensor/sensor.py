from PyQt5.QtWidgets import QScrollArea, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from sonicare.enums import SonicareSensor
from sonicare.parsers import parse_sensor_frame, GyroAccelFrame, TemperatureFrame, PressureFrame
from .plot import GyroscopeWidget, TemperatureWidget, PressureWidget

class SensorTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self._init_ui()

        self._gyro_frames = []

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        start_button = QPushButton("Start")
        start_button.clicked.connect(lambda: self._start())
        self.layout.addWidget(start_button)

        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(lambda: self._stop())
        self.layout.addWidget(stop_button)

        self.gyro_plot = GyroscopeWidget()
        self.layout.addWidget(self.gyro_plot)

        self.temperature_plot = TemperatureWidget()
        self.layout.addWidget(self.temperature_plot)

        self.pressure_plot = PressureWidget()
        self.layout.addWidget(self.pressure_plot)

    def _start(self):
        self.client.add_notify_listener(self._on_data)
        self.client.subscribe_sensor_data()
        self.client.write_sensor_enable(sum(SonicareSensor))

    def _stop(self):
        self.client.remove_notify_listener(self._on_data)
        self.client.unsubscribe_sensor_data()
        self.client.write_sensor_enable(0)

    def _on_data(self, uuid, value):
        if not uuid.endswith("4130"):
            return

        try:
            frame = parse_sensor_frame(value)
        except ValueError as error:
            print("Ignoring sensor frame:", error)
            return

        if isinstance(frame, GyroAccelFrame):
            self._on_gyro_data(frame)
        elif isinstance(frame, TemperatureFrame):
            self.temperature_plot.add_points([frame])
        elif isinstance(frame, PressureFrame):
            self.pressure_plot.add_points([frame])

    def _on_gyro_data(self, frame):
        self._gyro_frames.append(frame)

        # throttle graph update
        if len(self._gyro_frames) > 10:
            self.gyro_plot.add_points(self._gyro_frames)
            self._gyro_frames = []
