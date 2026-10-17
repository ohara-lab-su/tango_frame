# tango-frame

`tango-frame` automatically exposes an ordinary Python device-control class as a TANGO Device Server and provides a corresponding Python client wrapper.

The device-control class itself does not need to import PyTango or inherit from `tango.server.Device`. Public methods are mapped to TANGO commands and Python properties are mapped to TANGO attributes.

[日本語 README](README_ja.md)

## Concept

The framework keeps the device implementation and the communication layer separate.

```text
ordinary Python device class
        |
        +---- tango-frame ----> TANGO Device Server
        |                        method   -> command
        |                        property -> attribute
        |
        +---- tango-frame ----> Python client wrapper
                                 |
                                 +---- TANGO DeviceProxy
```

`tango-frame` is not a separate RPC protocol layered on top of TANGO. It generates and uses normal TANGO commands and attributes.

## Features

- An ordinary Python class is used as the device API definition.
- Public methods are exposed as named TANGO commands.
- `@property` values are exposed as TANGO attributes.
- Read/write Python properties become read/write TANGO attributes.
- Native TANGO-compatible scalar and homogeneous array types are used when possible.
- Calls that cannot be represented directly by one TANGO command input, such as heterogeneous multiple arguments, are packed into one JSON string input.
- Complex return values that cannot be represented by a native TANGO type are encoded as JSON strings.
- The client presents the device API as Python methods and properties while communicating through `tango.DeviceProxy`.
- Device-specific client behavior can override automatic remote dispatch.

## Package layout

```text
src/
└── tango_frame/
    ├── __init__.py
    ├── auto_dispatch.py
    ├── client.py
    ├── codec.py
    ├── introspection.py
    ├── server.py
    └── type_mapping.py

example/
└── device_server/
    ├── src/
    │   └── device/
    │       ├── device_class.py
    │       └── server_tango/
    │           ├── tango_ds.py
    │           └── device_client.py
    └── example/
        ├── server_start.py
        └── client.py
```

`src/tango_frame/` is the reusable framework and contains no concrete device implementation.

`example/device_server/src/device/` is a concrete example device module. `device_class.py` is independent of TANGO. `server_tango/` contains only the TANGO-specific adaptation for that device.

## Installation

```bash
pip install .
```

The package requires PyTango 10 or later.

## Device class

A device class remains an ordinary Python class.

```python
from typing import List


class DeviceClass(object):
    def __init__(self) -> None:
        self._position = 0.0

    def add(self, value: float) -> float:
        self._position += value
        return self._position

    def move(
        self,
        position: float,
        speed: float = 1.0,
        wait: bool = True,
    ) -> bool:
        self._position = position
        return wait

    def get_samples(self) -> List[float]:
        return [1.0, 2.0, 3.0]

    @property
    def position(self) -> float:
        return self._position

    @position.setter
    def position(self, value: float) -> None:
        self._position = value
```

The class can still be instantiated and used directly without TANGO.

## TANGO Device Server

A device-specific TANGO server class only binds the device class to `AutoDispatchDevice`.

```python
from tango_frame import AutoDispatchDevice

from device.device_class import DeviceClass


class TangoDevice(AutoDispatchDevice):
    device_class = DeviceClass
```

The public API is converted automatically. For the example above:

```text
add(value: float) -> float
    TANGO command: float -> float

move(position: float, speed: float, wait: bool) -> bool
    TANGO command: JSON string -> bool

get_samples() -> List[float]
    TANGO command: void -> homogeneous float array

position: float
    TANGO read/write attribute
```

A device-specific server can exclude methods that must not be executed remotely:

```python
class TangoDevice(AutoDispatchDevice):
    device_class = DeviceClass
    excluded_commands = {"save"}
```

The actual server is started with the normal PyTango server runtime. The example uses `-nodb` only to run locally without a TANGO database.

## Client

The corresponding client is defined by binding the same device class to `AutoDispatchClient`.

```python
from tango_frame import AutoDispatchClient

from device.device_class import DeviceClass


class DeviceClient(AutoDispatchClient):
    device_class = DeviceClass
```

The client uses TANGO `DeviceProxy` internally, while the caller uses Python-style methods and properties.

```python
device = DeviceClient(
    "tango://127.0.0.1:10000/test/tango/device#dbase=no"
)

print(device.position)
print(device.add(2.5))
device.position = 20.0
```

Device-specific client operations can be implemented normally. For example, a `save(path)` method should write on the client machine rather than on the Device Server machine:

```python
from pathlib import Path


class DeviceClient(AutoDispatchClient):
    device_class = DeviceClass

    def save(self, path: str) -> str:
        data = self.get_data()
        Path(path).write_bytes(data)
        return path
```

The explicitly implemented client method takes precedence over automatic remote dispatch.

## Type conversion

`tango-frame` prefers native TANGO values.

| Python API | TANGO representation |
| --- | --- |
| `bool` | native boolean |
| `int` | native integer |
| `float` | native double |
| `str` | native string |
| homogeneous `List[T]` | native TANGO array/spectrum |
| no argument / no return | void |
| multiple or heterogeneous arguments | one JSON string input |
| unsupported complex return value | JSON string |

JSON is therefore a fallback for Python call structures that do not map directly to TANGO's command model; it is not the default transport format.

## Documentation

Sphinx/MyST documentation is under `docs/`.

```bash
cd docs
./build.sh
```

## Version

Current version: **0.1.0**

See [CHANGELOG.md](CHANGELOG.md).
