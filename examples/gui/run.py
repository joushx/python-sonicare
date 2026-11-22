import os
from gui import SonicareApplication
import sys
from PyQt5.QtWidgets import QApplication

def get_mac():
    return os.environ.get('SONICARE_MAC', "24:E5:AA:0D:81:26")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SonicareApplication(mac=get_mac())
    sys.exit(app.exec_())