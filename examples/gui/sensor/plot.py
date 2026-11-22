from matplotlib.backends.backend_qt5agg import FigureCanvas
import matplotlib as mpl
from matplotlib.figure import Figure
import matplotlib.animation as anim
import numpy as np
import time

class PlotWidget(FigureCanvas):
    def __init__(self) -> None:
        super().__init__(Figure())
        self.points = []

        self.ax = self.figure.subplots()

    def add_points(self, points):
        self.points.extend(points)
        self.points = self.points[-500:]

        self.ax.cla()
        self.draw_data(points)

        self.ax.legend()
        self.draw()

    def draw_data(self, points):
        pass

class GyroscopeWidget(PlotWidget):
    def draw_data(self, points):
        self.ax.set_ylim((-32768,32768))

        for axis, name in enumerate("XYZ"):
            self.ax.plot([p.acceleration[axis] for p in self.points], "--", label="Acceleration " + name)
        for axis, name in enumerate("XYZ"):
            self.ax.plot([p.gyro[axis] for p in self.points], label="Gyroscope " + name)

class TemperatureWidget(PlotWidget):
    def draw_data(self, points):
        self.ax.set_ylim((0,40))
        self.ax.plot(list(map(lambda p: p.temperature, self.points)), label="Temperature °C")

class PressureWidget(PlotWidget):
    def draw_data(self, points):
        self.ax.plot(list(map(lambda p: p.pressure, self.points)), label="Pressure")
        self.ax.plot(list(map(lambda p: p.alarm, self.points)), "--", label="Alarm")