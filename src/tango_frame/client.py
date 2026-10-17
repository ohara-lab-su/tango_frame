from typing import Any

from tango import DeviceProxy


class TangoTransport(object):
    def __init__(self, device_name: str) -> None:
        self._proxy = DeviceProxy(device_name)

    def command(self, name: str, value: Any = None) -> Any:
        if value is None:
            return self._proxy.command_inout(name)
        return self._proxy.command_inout(name, value)

    def read_attribute(self, name: str) -> Any:
        return self._proxy.read_attribute(name).value

    def write_attribute(self, name: str, value: Any) -> None:
        self._proxy.write_attribute(name, value)

    def ping(self) -> int:
        return self._proxy.ping()

    @property
    def proxy(self) -> DeviceProxy:
        return self._proxy
