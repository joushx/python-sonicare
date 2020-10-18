import sys
sys.path.append("../..")
import os
from sonicare import SonicareClient

def get_mac():
    return os.environ['SONICARE_MAC']

def ready():
    print("| Name |")
    print("|---|")
    for method in client.__dict__.keys():
        if not method.startswith("get"):
            continue

        print("| {} |".format(method))

client = SonicareClient(mac=get_mac(), ready_callback=lambda: ready())
client.connect()