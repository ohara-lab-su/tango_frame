"""Client-side adapters for native and reconstructed TANGO devices."""

from typing import Any, Optional

from tango import DeviceProxy as NativeDeviceProxy

from .config import Config


class DeviceProxy(object):
    """Framework proxy for a native TANGO device.

    This class does not reconstruct a Python device class.  It creates the
    native PyTango ``DeviceProxy`` from ``Config`` and transparently
    delegates the normal TANGO client API to it.

    Args:
        config: TANGO connection configuration.
    """

    def __init__(self, config: Config) -> None:
        """Create a native TANGO proxy from framework configuration.

        Args:
            config: TANGO connection configuration.
        """
        self._config = config
        self._proxy = NativeDeviceProxy(config.device_url())

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown members to the native PyTango proxy.

        Args:
            name: Attribute or command name requested by the caller.

        Returns:
            Member exposed by the native ``tango.DeviceProxy``.
        """
        return getattr(self._proxy, name)

    @property
    def config(self) -> Config:
        """Return the framework connection configuration.

        Returns:
            TANGO connection configuration used by this proxy.
        """
        return self._config

    @property
    def native_proxy(self) -> NativeDeviceProxy:
        """Return the underlying native PyTango proxy.

        Returns:
            Native ``tango.DeviceProxy`` instance.
        """
        return self._proxy


class TangoTransport(object):
    """Transport used by ``AutoDispatchClient`` for reconstructed Python APIs.

    Args:
        config: TANGO connection configuration.
    """

    def __init__(self, config: Config) -> None:
        """Initialize transport through the framework ``DeviceProxy``.

        Args:
            config: TANGO connection configuration.
        """
        self._device = DeviceProxy(config=config)

    def command(self, name: str, value: Any = None) -> Any:
        """Execute a TANGO command.

        Args:
            name: TANGO command name.
            value: Optional command input value.

        Returns:
            Command result returned by PyTango.
        """
        if value is None:
            return self._device.native_proxy.command_inout(name)
        return self._device.native_proxy.command_inout(name, value)

    def read_attribute(self, name: str) -> Any:
        """Read a TANGO attribute value.

        Args:
            name: TANGO attribute name.

        Returns:
            Attribute value.
        """
        return self._device.native_proxy.read_attribute(name).value

    def write_attribute(self, name: str, value: Any) -> None:
        """Write a TANGO attribute value.

        Args:
            name: TANGO attribute name.
            value: Value written to the attribute.
        """
        self._device.native_proxy.write_attribute(name, value)

    def ping(self) -> int:
        """Ping the remote TANGO device.

        Returns:
            Round-trip time reported by PyTango in microseconds.
        """
        return self._device.native_proxy.ping()

    @property
    def proxy(self) -> NativeDeviceProxy:
        """Return the underlying native PyTango proxy.

        Returns:
            Native ``tango.DeviceProxy`` instance.
        """
        return self._device.native_proxy
