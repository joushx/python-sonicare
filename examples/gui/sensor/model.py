from enum import IntEnum

class SensorFrame:
    def __init__(self, type, counter):
        self.type = type
        self.counter = counter

class GyroscopeFrame(SensorFrame):
    def __init__(self, counter, acceleration1, acceleration2, acceleration3, gyro1, gyro2, gyro3):
        super().__init__(SensorFrameType.GYROSCOPE, counter)
        self.acceleration1 = acceleration1
        self.acceleration2 = acceleration2
        self.acceleration3 = acceleration3
        self.gyro1 = gyro1
        self.gyro2 = gyro2
        self.gyro3 = gyro3

class TemperatureFrame(SensorFrame):
    def __init__(self, counter, temperature):
        super().__init__(SensorFrameType.TEMPERATURE, counter)
        self.temperature = temperature

class PressureFrame(SensorFrame):
    def __init__(self, counter, pressure, alarm):
        super().__init__(SensorFrameType.PRESSURE, counter)
        self.pressure = pressure
        self.alarm = alarm

class SensorFrameType(IntEnum):
    GYROSCOPE = 4
    TEMPERATURE = 2
    PRESSURE = 1