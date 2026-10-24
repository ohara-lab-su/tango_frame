# CHANGELOG

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/tango_frame/blob/main/CHANGELOG.en.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/tango_frame/blob/main/CHANGELOG.md)

## v0.1.1 - 2026-10-17

Added configuration and client support for standard TANGO environments.

- Added `tango_frame.config.Config` for defining TANGO connection settings.
    - Device name can be specified with `device_name`.
    - TANGO Database host can be specified with `tango_host`.
    - Database and database-less connections can be selected with `database`.
- Added a `DeviceProxy` wrapper to `tango_frame`.
    - The wrapper creates and uses the native PyTango `DeviceProxy` internally.
    - Standard TANGO devices can therefore be accessed without requiring a `device_class`.
    - TANGO commands, attributes, and other native `DeviceProxy` operations remain accessible through the wrapper.
- Added support for normal TANGO Database-based operation.
    - With `database=True`, devices are resolved through the standard TANGO namespace.
    - A device can be addressed by its TANGO device name, such as `domain/family/member`.
    - `tango_host` can be used to specify the TANGO Database endpoint.
- Retained database-less operation for local testing.
    - With `database=False`, the client uses a database-less TANGO URL with `#dbase=no`.
    - Database-less operation is intended for local tests and is not required by the framework architecture.
- Updated `AutoDispatchClient` to accept `Config`.
    - When a `device_class` is supplied, its Python API is reconstructed on the client and dispatched to the TANGO
      device.
    - When accessing a native TANGO device, a `device_class` is not required; the framework `DeviceProxy` can be used
      directly.
- The server framework remains compatible with normal TANGO Device Server operation.
    - The framework does not require `-nodb`.
    - `-nodb` remains an option for local Device Server testing.
    - In a standard TANGO deployment, generated Device Servers can be registered in the TANGO Database and accessed
      through the normal TANGO namespace.
- Added Google-style docstrings and source comments.
- Updated type annotations for Python 3.7 compatibility.
- Removed conditional expressions (ternary operators) from the source code.

## v0.1.0 - 2026-10-17

Initial version of `tango-frame`.

- Added automatic TANGO Device Server construction from an ordinary Python device-control class.
- Added automatic mapping of public methods to named TANGO commands.
- Added automatic mapping of Python properties to TANGO attributes, including writable attributes.
- Added native TANGO type mapping for supported scalar and homogeneous array values.
- Added JSON fallback encoding for call signatures and return values that cannot be represented directly by native TANGO
  command types.
- Added a Python client wrapper based on TANGO `DeviceProxy`.
- Added support for device-specific client overrides and server-side command exclusion.
- Added a TANGO-independent example device class and corresponding Device Server/client example.
- Added English and Japanese README files.
- Added Sphinx/MyST documentation and GitHub Pages workflow.
