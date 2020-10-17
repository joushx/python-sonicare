import time
import tkinter as tk
import tkinter.ttk as ttk

from sonicare import SonicareClient, SERVICES

def generate_get_data_fn(service, characteristic, inp):
    return lambda: get_data(service, characteristic, inp)

def get_data(service, characteristic, inp):
    print(client.__dict__)
    response = client.__dict__["get_" + service.lower() + "_" + characteristic.lower()](client)
    inp.delete(0, 'end')
    inp.insert(0, response)

def generate_sections(root):

    for service in SERVICES.values():
        w = tk.LabelFrame(root, text=service.name)

        row = 0
        for characteristic in service.characteristics.values():
            label = tk.Label(w, text=characteristic.name)
            label.grid(row=row, column=1)

            inp = tk.Entry(w)
            inp.grid(row=row, column=3)

            button = tk.Button(w, text="Read", command=generate_get_data_fn(service.name, characteristic.name, inp))
            button.grid(row=row, column=2)

            row += 1
        
        w.pack(fill="both", expand="yes")
        
if __name__ == "__main__":
    root = tk.Tk()

    def ready():
        print("ready")
        generate_sections(root)

    client = SonicareClient(mac='<your-mac-address>', ready_callback=lambda: ready())
    button = tk.Button(root, text="Connect", command=lambda: client.connect())
    button.pack()

    root.mainloop()
