# Architecture and usage

## Separation of responsibilities

```text
src/tango_frame/
    reusable TANGO adaptation framework

device package/
    ordinary device-control class
    server_tango/
        device-specific TANGO server/client adaptation
```

The reusable framework must not depend on a concrete device class.

## Server side

A device-specific TANGO Device class binds the ordinary Python device class to `AutoDispatchDevice`.

```python
class TangoDevice(AutoDispatchDevice):
    device_class = DeviceClass
```

`tango-frame` inspects the public API and creates TANGO commands and attributes dynamically.

A method that should not be available as a remote command can be excluded by the device-specific server class.

```python
class TangoDevice(AutoDispatchDevice):
    device_class = DeviceClass
    excluded_commands = {"save"}
```

## Client side

A device-specific client binds the same device class to `AutoDispatchClient`.

```python
class DeviceClient(AutoDispatchClient):
    device_class = DeviceClass
```

Calls are transported through TANGO `DeviceProxy`.

An explicitly implemented method in the device-specific client takes precedence over automatic remote dispatch. This is used for operations whose semantics belong to the client machine, such as saving remotely obtained data to a local path.

## Type conversion

Supported scalar values and homogeneous arrays use native TANGO-compatible types.

Python calls requiring multiple heterogeneous arguments are encoded into one JSON string because a TANGO command has one input value. Complex unsupported return values use the same JSON fallback.

This conversion is an adaptation of the Python API to the TANGO command model; it is not a separate RPC protocol.
