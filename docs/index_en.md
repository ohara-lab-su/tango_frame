# tango-frame

`tango-frame` automatically constructs a TANGO Device Server and a corresponding Python client wrapper from an ordinary Python device-control class.

[GitHub](https://github.com/ohara-lab-su/tango_frame/) / [日本語](index.md)

The device class remains independent of TANGO. Public methods are exposed as named TANGO commands and Python properties are exposed as TANGO attributes.

The client communicates through TANGO `DeviceProxy` while presenting Python methods and properties corresponding to the original device API.

Native TANGO-compatible values are transported as native TANGO types. JSON encoding is used only when a Python call or return value cannot be represented directly by the TANGO command model.

For the architecture and usage details, see [Overview](overview.md).

Current version: **0.1.0**
