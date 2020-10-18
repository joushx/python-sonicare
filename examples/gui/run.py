import os
from gui import SonicareApplication
import sys
from PyQt5.QtWidgets import QApplication

def get_mac():
    return "24:E5:AA:0D:81:26" #os.environ['SONICARE_MAC']

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SonicareApplication(mac=get_mac())
    sys.exit(app.exec_())