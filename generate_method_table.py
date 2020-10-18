from sonicare import SonicareClient

def ready():
    print("| Name |")
    print("|---|")
    for method in client.__dict__.keys():
        if not method.startswith("get"):
            continue

        print("| {} |".format(method))

client = SonicareClient(mac='<your-mac-address>', ready_callback=lambda: ready())
client.connect()