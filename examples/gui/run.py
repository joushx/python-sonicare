import os
from gui import SonicareApplication

def get_mac():
    return os.environ['SONICARE_MAC']

if __name__ == "__main__":
    app = SonicareApplication(mac=get_mac())
    app.start()