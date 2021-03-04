from PyQt5.QtWidgets import QScrollArea, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import struct

from .model import GyroscopeFrame, TemperatureFrame, SensorFrameType, PressureFrame
from .plot import GyroscopeWidget, TemperatureWidget, PressureWidget

GYRO = 1
TEMP = 1 << 1
PRESSURE = 1 << 2

class SensorTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self._init_ui()

        self._gyro_frames = []
        self._pressure_frames = []

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
        self.client.write_sensor_enable([GYRO | TEMP | PRESSURE, 0])

    def _stop(self):
        self.client.remove_notify_listener(self._on_data)
        self.client.unsubscribe_sensor_data()
        self.client.write_sensor_enable([0, 0])

    def _on_data(self, uuid, value):

        if not uuid[-4:] == "4130":
            return

        data_type = struct.unpack("<H", value[:2])[0]
        counter = struct.unpack("<H", value[2:4])[0]

        if data_type == SensorFrameType.GYROSCOPE:
            self._on_gyro_data(counter, value)
        elif data_type == SensorFrameType.TEMPERATURE:
            self._on_temperature_data(counter, value)
        elif data_type == SensorFrameType.PRESSURE:
            self._on_pressure_data(counter, value)

    def _on_gyro_data(self, counter, value):
        acc1 = struct.unpack("<h", value[4:6])[0]
        acc2 = struct.unpack("<h", value[6:8])[0]
        acc3 = struct.unpack("<h", value[8:10])[0]
        gyro1 = struct.unpack("<h", value[10:12])[0]
        gyro2 = struct.unpack("<h", value[12:14])[0]
        gyro3 = struct.unpack("<h", value[14:16])[0]

        frame = GyroscopeFrame(counter, acc1, acc2, acc3, gyro1, gyro2, gyro3)

        self._gyro_frames.append(frame)

        # throttle graph update
        if len(self._gyro_frames) > 10:
            self.gyro_plot.add_points(self._gyro_frames)
            self._gyro_frames = []

    def _on_temperature_data(self, counter, value):
        temperature = value[4]/256 + value[5]
        frame = TemperatureFrame(counter, temperature)
        self.temperature_plot.add_points([frame])

    def _on_pressure_data(self, counter, value):
        pressure = struct.unpack("<h", value[4:6])[0]
        alarm = value[6]
        frame = PressureFrame(counter, pressure, alarm)
        self.pressure_plot.add_points(self._pressure_frames)