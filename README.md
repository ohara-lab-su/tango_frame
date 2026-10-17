# tango-frame

A transport adapter that exposes a normal Python device-control class as a TANGO Device Server without requiring the control class to inherit from `tango.server.Device`.

## Mapping

- public Python method -> TANGO command with `DevString` input/output
- Python `@property` -> TANGO string attribute
- method arguments/keyword arguments/results -> JSON payload inside the single TANGO string value
- TANGO command and attribute names remain the original Python API names

The control class itself has no TANGO dependency.

## Why JSON/DevString

A TANGO command has one input value and one output value. TANGO array types are homogeneous and cannot directly represent an arbitrary Python call such as `move(position, speed, wait=False)`. `tango-frame` therefore converts the Python call into one JSON string and reconstructs `*args` and `**kwargs` in the server handler.

## DB-less example

`examples/test_server.py` uses standard TANGO server options `-nodb`, `-dlist`, and `-ORBendPoint` only for the example launch. The generated Device Server class is not DB-less-specific; the same class can be started normally with a TANGO database.
