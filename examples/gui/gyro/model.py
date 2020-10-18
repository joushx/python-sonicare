from enum import IntEnum

class DataFrame:
    def __init__(self, counter):
        self.counter = counter

class GyroscopeFrame(DataFrame):
    def __init__(self, counter, acceleration1, acceleration2, acceleration3, gyro1, gyro2, gyro3):
        super().__init__(counter)
        self.acceleration1 = acceleration1
        self.acceleration2 = acceleration2
        self.acceleration3 = acceleration3
        self.gyro1 = gyro1
        self.gyro2 = gyro2
        self.gyro3 = gyro3

class FrameType(IntEnum):
    GYROSCOPE = 4