from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit

from sonicare import SERVICES

class CharacteristicRow(QWidget):
    def __init__(self, characteristic, on_read=None):
        super().__init__()
        self.characteristic = characteristic
        self._init_ui()

        name_label = QLabel(self.characteristic.name)
        self.layout.addWidget(name_label)

        read_button = QPushButton("Read")
        read_button.clicked.connect(lambda: on_read())
        self.layout.addWidget(read_button)

        self.value_display = QLineEdit()
        self.value_display.setReadOnly(True)
        self.value_display.setFixedWidth(200)
        self.layout.addWidget(self.value_display)

    def set_value(self, value):
        self.value_display.setText(str(value))

    def _init_ui(self):
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)