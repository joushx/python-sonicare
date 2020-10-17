# python-sonicare

Python library to communicate with a Phillips Sonicare toothbrush via Bluetooth Low Energy

## Usage

All methods are auto-generated from the services definition (see `sonicare/data.py`) in the form `get_servicename_characteristicname`. E.g. `Handle` `Current_Time` can be called using `get_handle_current_time`.

```python
def ready():
    current_time = client.get_handle_current_time(client)
    print(current_time)

client = SonicareClient(mac='<your-mac-address>', ready_callback=lambda: ready())
client.connect()
```

## Article

https://blog.johannes-mittendorfer.com/artikel/2020/10/my-toothbrush-streams-gyroscope-data
