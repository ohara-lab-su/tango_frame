# CHANGELOG

## v0.1.0 - 2026-10-17

Initial version of `tango-frame`.

- Added automatic TANGO Device Server construction from an ordinary Python device-control class.
- Added automatic mapping of public methods to named TANGO commands.
- Added automatic mapping of Python properties to TANGO attributes, including writable attributes.
- Added native TANGO type mapping for supported scalar and homogeneous array values.
- Added JSON fallback encoding for call signatures and return values that cannot be represented directly by native TANGO command types.
- Added a Python client wrapper based on TANGO `DeviceProxy`.
- Added support for device-specific client overrides and server-side command exclusion.
- Added a TANGO-independent example device class and corresponding Device Server/client example.
- Added English and Japanese README files.
- Added Sphinx/MyST documentation and GitHub Pages workflow.
