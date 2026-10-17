# DB-less example

This example verifies the complete path:

`TestDevice` -> `tango_frame` -> TANGO Device Server -> `TangoClient` -> Python-like API.

`TestDevice` itself imports no TANGO module.

## Terminal 1: start the server

From the project root after installing the package:

```text
python examples/test_server.py
```

The server is started without a TANGO database on TCP port 10000.  The device
name is `test/nodb/testdevice`.

## Terminal 2: run the client

```text
python examples/test_client.py
```

The client connects with the DB-less TANGO URL:

```text
tango://127.0.0.1:10000/test/nodb/testdevice#dbase=no
```

Expected final output:

```text
tango_frame DB-less test: OK
device: tango://127.0.0.1:10000/test/nodb/testdevice#dbase=no
name: test-device
value: 0.0
enabled: True
```
