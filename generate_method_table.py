from sonicare import SonicareClient

def ready():
    print("| Name |")
    print("|---|")
    for method in client.__dict__.keys():
        if not method.startswith("get"):
            continue

        print("| {} |".format(method))

client = SonicareClient(mac='24:e5:aa:0d:81:26', ready_callback=lambda: ready())
client.connect()