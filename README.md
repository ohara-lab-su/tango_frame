# tango-frame

This repository contains two clearly separated layers.

```text
src/tango_frame/
```

is the reusable TANGO framework.

```text
example/device_server/
```

is one concrete device-server project built with that framework.

## Layout

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
    │       ├── __init__.py
    │       ├── device_class.py
    │       └── server_tango/
    │           ├── __init__.py
    │           ├── tango_ds.py
    │           └── device_client.py
    │
    └── example/
        ├── server_start.py
        └── client.py
```

`src/tango_frame` contains no concrete device implementation.

`example/device_server/src/device` is the device module.  `device_class.py`
is TANGO-independent.  `server_tango` is the device-specific TANGO adapter
layer built by subclassing/using `tango_frame`.

`example/device_server/example` contains only executable examples which use
the module under `example/device_server/src`.

`DeviceClient.save()` is a device-specific client-side override: data is
obtained remotely but the file is written on the client machine.
