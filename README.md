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

The BLE description of the toothbrush lives in `sonicare/data.py` and the client generates its methods from it, in the form
`read_<service>_<characteristic>`, `write_...`, `subscribe_...` and `unsubscribe_...`. E.g. the characteristic
`Current_Time` of the service `Handle` is read using `read_handle_current_time`.
Reads return decoded values, writes take bytes or, for integer and timestamp characteristics, a number or `datetime`.
Notifications are passed to the listeners registered with `add_notify_listener`.

```python
import gatt
from sonicare import SonicareClient

manager = gatt.DeviceManager(adapter_name='hci0')

def ready():
    print(client.read_handle_current_time())
    print(client.read_battery_level())

client = SonicareClient(mac='<your-mac-address>', device_manager=manager, ready_callback=ready)
client.connect()
manager.run()
```

`sonicare.parsers` decodes the sensor stream (`Sensor Data`, enable it by writing `7` to `Sensor Enable`) and the session
records without needing a connection:

```python
from sonicare.parsers import parse_sensor_frame

def on_notify(uuid, value):
    if uuid.endswith("4130"):
        frame = parse_sensor_frame(value)  # GyroAccelFrame, TemperatureFrame or PressureFrame
        print(frame)

client.add_notify_listener(on_notify)
client.subscribe_sensor_data()
client.write_sensor_enable(7)
```

`sonicare.sessions.SessionDownloader` fetches the stored brushing sessions (`SessionDownloader(client, print).start()`).
It follows the protocol of the Philips app and has been run against an HX991X; the sensor stream and the
gyro compensation record have only been checked against an HX992X capture and not yet while brushing.

What is known about the protocol, and how sure, is in [docs/PROTOCOL.md](docs/PROTOCOL.md).

### Tests

The tests need no toothbrush: `python -m unittest discover -s tests`

### Methods

| Characteristic | UUID | Type | Methods |
|---|---|---|---|
| Handle State | `477ea600-a260-11e4-ae37-0002a5d54010` | INT8 (SonicareHandleState) | `read_handle_state`, `write_handle_state`, `subscribe_handle_state`, `unsubscribe_handle_state` |
| Handle 4020 | `477ea600-a260-11e4-ae37-0002a5d54020` | INT16 | `read_handle_4020`, `write_handle_4020`, `subscribe_handle_4020`, `unsubscribe_handle_4020` |
| Handle 4022 | `477ea600-a260-11e4-ae37-0002a5d54022` | RAW | `read_handle_4022`, `write_handle_4022`, `subscribe_handle_4022`, `unsubscribe_handle_4022` |
| Handle 4030 | `477ea600-a260-11e4-ae37-0002a5d54030` | INT16 | `read_handle_4030`, `write_handle_4030`, `subscribe_handle_4030`, `unsubscribe_handle_4030` |
| Handle 4040 | `477ea600-a260-11e4-ae37-0002a5d54040` | RAW | `read_handle_4040`, `write_handle_4040`, `subscribe_handle_4040`, `unsubscribe_handle_4040` |
| Handle Current_Time | `477ea600-a260-11e4-ae37-0002a5d54050` | TIMESTAMP | `read_handle_current_time`, `write_handle_current_time`, `subscribe_handle_current_time`, `unsubscribe_handle_current_time` |
| State Current_session | `477ea600-a260-11e4-ae37-0002a5d54070` | INT16 | `read_state_current_session`, `write_state_current_session`, `subscribe_state_current_session`, `unsubscribe_state_current_session` |
| State Brushing_Mode | `477ea600-a260-11e4-ae37-0002a5d54080` | INT8 (SonicareBrushingMode) | `read_state_brushing_mode`, `write_state_brushing_mode`, `subscribe_state_brushing_mode`, `unsubscribe_state_brushing_mode` |
| State State | `477ea600-a260-11e4-ae37-0002a5d54082` | INT8 | `read_state_state`, `write_state_state`, `subscribe_state_state`, `unsubscribe_state_state` |
| State Active_time | `477ea600-a260-11e4-ae37-0002a5d54090` | INT16 | `read_state_active_time`, `write_state_active_time`, `subscribe_state_active_time`, `unsubscribe_state_active_time` |
| State Routine_length | `477ea600-a260-11e4-ae37-0002a5d54091` | INT16 | `read_state_routine_length`, `write_state_routine_length`, `subscribe_state_routine_length`, `unsubscribe_state_routine_length` |
| State 40a0 | `477ea600-a260-11e4-ae37-0002a5d540a0` | INT8 | `read_state_40a0`, `write_state_40a0`, `subscribe_state_40a0`, `unsubscribe_state_40a0` |
| State Strength | `477ea600-a260-11e4-ae37-0002a5d540b0` | INT8 (SonicareStrength) | `read_state_strength`, `write_state_strength`, `subscribe_state_strength`, `unsubscribe_state_strength` |
| State 40c0 | `477ea600-a260-11e4-ae37-0002a5d540c0` | INT8 | `read_state_40c0`, `write_state_40c0`, `subscribe_state_40c0`, `unsubscribe_state_40c0` |
| Session Last_id | `477ea600-a260-11e4-ae37-0002a5d540d0` | INT16 | `read_session_last_id`, `write_session_last_id`, `subscribe_session_last_id`, `unsubscribe_session_last_id` |
| Session Count | `477ea600-a260-11e4-ae37-0002a5d540d2` | INT16 | `read_session_count`, `write_session_count`, `subscribe_session_count`, `unsubscribe_session_count` |
| Session Type | `477ea600-a260-11e4-ae37-0002a5d540d5` | INT8 (SonicareSessionType) | `read_session_type`, `write_session_type`, `subscribe_session_type`, `unsubscribe_session_type` |
| Session Request | `477ea600-a260-11e4-ae37-0002a5d540e0` | INT16 | `read_session_request`, `write_session_request`, `subscribe_session_request`, `unsubscribe_session_request` |
| Session Data | `477ea600-a260-11e4-ae37-0002a5d54100` | RAW | `read_session_data`, `write_session_data`, `subscribe_session_data`, `unsubscribe_session_data` |
| Session Control | `477ea600-a260-11e4-ae37-0002a5d54110` | INT8 | `read_session_control`, `write_session_control`, `subscribe_session_control`, `unsubscribe_session_control` |
| Sensor Enable | `477ea600-a260-11e4-ae37-0002a5d54120` | INT16 | `read_sensor_enable`, `write_sensor_enable`, `subscribe_sensor_enable`, `unsubscribe_sensor_enable` |
| Sensor Data | `477ea600-a260-11e4-ae37-0002a5d54130` | RAW | `read_sensor_data`, `write_sensor_data`, `subscribe_sensor_data`, `unsubscribe_sensor_data` |
| Sensor 4140 | `477ea600-a260-11e4-ae37-0002a5d54140` | RAW | `read_sensor_4140`, `write_sensor_4140`, `subscribe_sensor_4140`, `unsubscribe_sensor_4140` |
| Brush NFC_Version | `477ea600-a260-11e4-ae37-0002a5d54210` | RAW | `read_brush_nfc_version`, `write_brush_nfc_version`, `subscribe_brush_nfc_version`, `unsubscribe_brush_nfc_version` |
| Brush 4220 | `477ea600-a260-11e4-ae37-0002a5d54220` | INT8 | `read_brush_4220`, `write_brush_4220`, `subscribe_brush_4220`, `unsubscribe_brush_4220` |
| Brush Serial | `477ea600-a260-11e4-ae37-0002a5d54230` | RAW | `read_brush_serial`, `write_brush_serial`, `subscribe_brush_serial`, `unsubscribe_brush_serial` |
| Brush Date | `477ea600-a260-11e4-ae37-0002a5d54240` | STRING | `read_brush_date`, `write_brush_date`, `subscribe_brush_date`, `unsubscribe_brush_date` |
| Brush 4250 | `477ea600-a260-11e4-ae37-0002a5d54250` | INT8 | `read_brush_4250`, `write_brush_4250`, `subscribe_brush_4250`, `unsubscribe_brush_4250` |
| Brush 4254 | `477ea600-a260-11e4-ae37-0002a5d54254` | INT8 | `read_brush_4254`, `write_brush_4254`, `subscribe_brush_4254`, `unsubscribe_brush_4254` |
| Brush 4260 | `477ea600-a260-11e4-ae37-0002a5d54260` | INT8 | `read_brush_4260`, `write_brush_4260`, `subscribe_brush_4260`, `unsubscribe_brush_4260` |
| Brush 4270 | `477ea600-a260-11e4-ae37-0002a5d54270` | INT8 | `read_brush_4270`, `write_brush_4270`, `subscribe_brush_4270`, `unsubscribe_brush_4270` |
| Brush Lifetime | `477ea600-a260-11e4-ae37-0002a5d54280` | INT16 | `read_brush_lifetime`, `write_brush_lifetime`, `subscribe_brush_lifetime`, `unsubscribe_brush_lifetime` |
| Brush Usage | `477ea600-a260-11e4-ae37-0002a5d54290` | INT16 | `read_brush_usage`, `write_brush_usage`, `subscribe_brush_usage`, `unsubscribe_brush_usage` |
| Brush 42a0 | `477ea600-a260-11e4-ae37-0002a5d542a0` | INT8 | `read_brush_42a0`, `write_brush_42a0`, `subscribe_brush_42a0`, `unsubscribe_brush_42a0` |
| Brush 42a2 | `477ea600-a260-11e4-ae37-0002a5d542a2` | INT8 | `read_brush_42a2`, `write_brush_42a2`, `subscribe_brush_42a2`, `unsubscribe_brush_42a2` |
| Brush 42a4 | `477ea600-a260-11e4-ae37-0002a5d542a4` | RAW | `read_brush_42a4`, `write_brush_42a4`, `subscribe_brush_42a4`, `unsubscribe_brush_42a4` |
| Brush 42a6 | `477ea600-a260-11e4-ae37-0002a5d542a6` | INT8 | `read_brush_42a6`, `write_brush_42a6`, `subscribe_brush_42a6`, `unsubscribe_brush_42a6` |
| Brush Payload | `477ea600-a260-11e4-ae37-0002a5d542b0` | STRING | `read_brush_payload`, `write_brush_payload`, `subscribe_brush_payload`, `unsubscribe_brush_payload` |
| Brush 42c0 | `477ea600-a260-11e4-ae37-0002a5d542c0` | INT16 | `read_brush_42c0`, `write_brush_42c0`, `subscribe_brush_42c0`, `unsubscribe_brush_42c0` |
| Diagnostics 4310 | `477ea600-a260-11e4-ae37-0002a5d54310` | INT32 | `read_diagnostics_4310`, `write_diagnostics_4310`, `subscribe_diagnostics_4310`, `unsubscribe_diagnostics_4310` |
| Diagnostics 4320 | `477ea600-a260-11e4-ae37-0002a5d54320` | INT32 | `read_diagnostics_4320`, `write_diagnostics_4320`, `subscribe_diagnostics_4320`, `unsubscribe_diagnostics_4320` |
| Diagnostics 4330 | `477ea600-a260-11e4-ae37-0002a5d54330` | RAW | `read_diagnostics_4330`, `write_diagnostics_4330`, `subscribe_diagnostics_4330`, `unsubscribe_diagnostics_4330` |
| Diagnostics 4360 | `477ea600-a260-11e4-ae37-0002a5d54360` | RAW | `read_diagnostics_4360`, `write_diagnostics_4360`, `subscribe_diagnostics_4360`, `unsubscribe_diagnostics_4360` |
| 0008 4410 | `477ea600-a260-11e4-ae37-0002a5d54410` | RAW | `read_0008_4410`, `write_0008_4410`, `subscribe_0008_4410`, `unsubscribe_0008_4410` |
| 0008 4420 | `477ea600-a260-11e4-ae37-0002a5d54420` | RAW | `read_0008_4420`, `write_0008_4420`, `subscribe_0008_4420`, `unsubscribe_0008_4420` |
| Moonshine Tx | `a6510001-4074-4131-bce9-56d4261bc7b1` | RAW | `read_moonshine_tx`, `write_moonshine_tx`, `subscribe_moonshine_tx`, `unsubscribe_moonshine_tx` |
| Moonshine Rx_ack | `a6510002-4074-4131-bce9-56d4261bc7b1` | RAW | `read_moonshine_rx_ack`, `write_moonshine_rx_ack`, `subscribe_moonshine_rx_ack`, `unsubscribe_moonshine_rx_ack` |
| Moonshine Rx | `a6510003-4074-4131-bce9-56d4261bc7b1` | RAW | `read_moonshine_rx`, `write_moonshine_rx`, `subscribe_moonshine_rx`, `unsubscribe_moonshine_rx` |
| Moonshine Control | `a6510004-4074-4131-bce9-56d4261bc7b1` | RAW | `read_moonshine_control`, `write_moonshine_control`, `subscribe_moonshine_control`, `unsubscribe_moonshine_control` |
| Moonshine Info | `a6510005-4074-4131-bce9-56d4261bc7b1` | RAW | `read_moonshine_info`, `write_moonshine_info`, `subscribe_moonshine_info`, `unsubscribe_moonshine_info` |
| Battery Level | `00002a19-0000-1000-8000-00805f9b34fb` | INT8 | `read_battery_level`, `write_battery_level`, `subscribe_battery_level`, `unsubscribe_battery_level` |
| Device_Information Manufacturer | `00002a29-0000-1000-8000-00805f9b34fb` | STRING | `read_device_information_manufacturer`, `write_device_information_manufacturer`, `subscribe_device_information_manufacturer`, `unsubscribe_device_information_manufacturer` |
| Device_Information Model | `00002a24-0000-1000-8000-00805f9b34fb` | STRING | `read_device_information_model`, `write_device_information_model`, `subscribe_device_information_model`, `unsubscribe_device_information_model` |
| Device_Information Serial | `00002a25-0000-1000-8000-00805f9b34fb` | STRING | `read_device_information_serial`, `write_device_information_serial`, `subscribe_device_information_serial`, `unsubscribe_device_information_serial` |
| Device_Information Hardware | `00002a27-0000-1000-8000-00805f9b34fb` | STRING | `read_device_information_hardware`, `write_device_information_hardware`, `subscribe_device_information_hardware`, `unsubscribe_device_information_hardware` |
| Device_Information Firmware | `00002a26-0000-1000-8000-00805f9b34fb` | STRING | `read_device_information_firmware`, `write_device_information_firmware`, `subscribe_device_information_firmware`, `unsubscribe_device_information_firmware` |
| Device_Information Software | `00002a28-0000-1000-8000-00805f9b34fb` | STRING | `read_device_information_software`, `write_device_information_software`, `subscribe_device_information_software`, `unsubscribe_device_information_software` |
| Device_Information System_ID | `00002a23-0000-1000-8000-00805f9b34fb` | RAW | `read_device_information_system_id`, `write_device_information_system_id`, `subscribe_device_information_system_id`, `unsubscribe_device_information_system_id` |
| Device_Information IEEE_Cert | `00002a2a-0000-1000-8000-00805f9b34fb` | RAW | `read_device_information_ieee_cert`, `write_device_information_ieee_cert`, `subscribe_device_information_ieee_cert`, `unsubscribe_device_information_ieee_cert` |
| Device_Information PnP_ID | `00002a50-0000-1000-8000-00805f9b34fb` | RAW | `read_device_information_pnp_id`, `write_device_information_pnp_id`, `subscribe_device_information_pnp_id`, `unsubscribe_device_information_pnp_id` |

## Article

https://blog.johannes-mittendorfer.com/artikel/2020/10/my-toothbrush-streams-gyroscope-data
