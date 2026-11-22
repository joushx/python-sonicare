"""Conversion between characteristic values and python values (no BLE needed)."""
from datetime import datetime

from .enums import SonicareValueType


def _le(raw, size):
    raw = bytes(raw)
    if len(raw) < size:
        raise ValueError("expected at least {} bytes, got {}".format(size, len(raw)))
    return int.from_bytes(raw[:size], "little")


def decode(description, value):
    """Turn the bytes read from a characteristic into a python value.

    `description` is a `model.Characteristic`.
    """
    raw = bytes(value)
    value_type = description.data_type

    if value_type == SonicareValueType.INT8:
        number = _le(raw, 1)
        if description.enum:
            try:
                return description.enum(number).name
            except ValueError:
                return number
        return number
    elif value_type == SonicareValueType.STRING:
        return raw.decode("utf-8", errors="replace").rstrip("\0")
    elif value_type == SonicareValueType.INT16:
        return _le(raw, 2)
    elif value_type == SonicareValueType.INT32:
        return _le(raw, 4)
    elif value_type == SonicareValueType.TIMESTAMP:
        return datetime.fromtimestamp(_le(raw, 4))
    elif value_type == SonicareValueType.RAW:
        return ["{:02x}".format(b) for b in raw]


def encode(description, value):
    """Turn a python value into the bytes to write.

    bytes, bytearray and lists are written unchanged, integers (and datetimes
    for timestamps) are encoded according to the type of the characteristic.
    """
    if isinstance(value, (bytes, bytearray, list, tuple)):
        return bytes(value)

    value_type = description.data_type
    if value_type == SonicareValueType.TIMESTAMP and isinstance(value, datetime):
        value = int(value.timestamp())
    if isinstance(value, str) and value_type == SonicareValueType.STRING:
        return value.encode("utf-8")

    sizes = {
        SonicareValueType.INT8: 1,
        SonicareValueType.INT16: 2,
        SonicareValueType.INT32: 4,
        SonicareValueType.TIMESTAMP: 4,
    }
    if value_type not in sizes:
        raise TypeError("pass bytes to write a {} characteristic".format(value_type.name))
    return int(value).to_bytes(sizes[value_type], "little")
