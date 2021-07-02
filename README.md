# python-sonicare

Python library to communicate with a Phillips Sonicare toothbrush via Bluetooth Low Energy

## GUI

```
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
python examples/gui/run.py
```

## Lib

All methods are auto-generated from the services definition (see `sonicare/data.py`) in the form `get_servicename_characteristicname`. E.g. `Handle` `Current_Time` can be called using `get_handle_current_time`.

```python
def ready():
    current_time = client.get_handle_current_time(client)
    print(current_time)

client = SonicareClient(mac='<your-mac-address>', ready_callback=lambda: ready())
client.connect()
```

### Methods

| Name |
|---|
| get_0008_4420 |
| get_0008_4410 |
| get_0007_4360 |
| get_0007_4330 |
| get_0007_4320 |
| get_0007_4310 |
| get_brush_42c0 |
| get_brush_payload |
| get_brush_42a6 |
| get_brush_42a4 |
| get_brush_42a2 |
| get_brush_usage |
| get_brush_lifetime |
| get_brush_4270 |
| get_brush_4260 |
| get_brush_4254 |
| get_brush_4250 |
| get_brush_date |
| get_brush_serial |
| get_brush_4220 |
| get_brush_nfc_version |
| get_session_40d2 |
| get_session_4100 |
| get_session_4110 |
| get_session_type |
| get_session_last_id |
| get_0005_4140 |
| get_0005_gyro_data |
| get_0005_4120 |
| get_handle_current_time |
| get_handle_4040 |
| get_handle_4030 |
| get_handle_4022 |
| get_handle_4020 |
| get_handle_state |
| get_state_state |
| get_state_strength |
| get_state_brushing_mode2 |
| get_state_active_time |
| get_state_brushing_mode |
| get_state_current_session |

## Article

https://blog.johannes-mittendorfer.com/artikel/2020/10/my-toothbrush-streams-gyroscope-data
