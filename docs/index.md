# tango-frame

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/tango_frame/en/index.html) [![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://ohara-lab-su.github.io/tango_frame/ja/index.html)

[GitHub repository](https://github.com/ohara-lab-su/tango_frame/) · [Project documentation](https://ohara-lab-su.github.io/)

`tango-frame` automatically constructs a TANGO Device Server and a corresponding Python client wrapper from an ordinary
Python device-control class.

```{toctree}
:maxdepth: 2
:caption: Contents:

overview
api/modules
```

## Purpose

The existing Python device-control API is used as the definition of the device API, without rewriting the device class
for TANGO.

```text
Python device class
      |
      +--> public method --> TANGO command
      |
      +--> @property     --> TANGO attribute
```

The device class remains independent of TANGO. Public methods are exposed as named TANGO commands, and Python properties
are exposed as TANGO attributes.

The client communicates through TANGO `DeviceProxy` while presenting Python methods and properties corresponding to the
original device API.

## Design boundaries

`src/tango_frame/` is a reusable framework that does not depend on a concrete device class.

A device-specific package keeps its TANGO-independent device-control class and uses `AutoDispatchDevice` /
`AutoDispatchClient` in a device-specific `server_tango` layer.

Native TANGO-compatible values are transported as native TANGO types. JSON encoding is used only when a Python call or
return value cannot be represented directly by the TANGO command model.

## Version

Current version: **0.1.0**
