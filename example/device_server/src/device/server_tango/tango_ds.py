from tango_frame import AutoDispatchDevice

from device.device_class import DeviceClass


class TangoDevice(AutoDispatchDevice):
    device_class = DeviceClass
    excluded_commands = {"save"}
