"""Automatic adaptation between ordinary Python classes and TANGO devices."""

from types import MethodType
from typing import Any, Dict, Optional, Set, Type

from tango import AttrWriteType, DevState
from tango.server import Device, attribute, command

from .codec import pack_call, pack_value, unpack_call, unpack_value
from .config import Config
from .introspection import PropertySpec, public_methods, public_properties
from .type_mapping import (
    input_type,
    output_type,
    tango_value_type,
    uses_encoded_input,
    uses_encoded_output,
)


class AutoDispatchDevice(Device):
    """Expose an ordinary Python device class as a TANGO device server.

    Subclasses set ``device_class`` to the transport-independent Python class.
    Public methods become TANGO commands and public properties become TANGO
    attributes.
    """

    device_class = None  # type: Optional[Type[Any]]
    excluded_commands = set()  # type: Set[str]

    def init_device(self) -> None:
        """Create the local Python device object when TANGO initializes it.

        Raises:
            RuntimeError: If no Python device class has been configured.
        """
        Device.init_device(self)
        if self.device_class is None:
            raise RuntimeError("device_class is not configured")

        # The authoritative local device class is reconstructed inside the
        # TANGO device server process.
        self._device_object = self.device_class()
        self.set_state(DevState.ON)

    def delete_device(self) -> None:
        """Release the wrapped Python device object when available."""
        device_object = getattr(self, "_device_object", None)
        if device_object is not None:
            release = getattr(device_object, "release", None)
            if callable(release):
                release()

    def initialize_dynamic_attributes(self) -> None:
        """Install TANGO commands and attributes from the Python class.

        Raises:
            RuntimeError: If no Python device class has been configured.
        """
        if self.device_class is None:
            raise RuntimeError("device_class is not configured")

        _install_commands(self, self.device_class)
        _install_attributes(self, self.device_class)


def _command_handler(
    name: str,
    has_input: bool,
    encoded_input: bool,
    encoded_output: bool,
) -> Any:
    """Build a dynamic TANGO command handler.

    Args:
        name: Python method and TANGO command name.
        has_input: Whether the command accepts a TANGO input value.
        encoded_input: Whether the input uses the JSON call envelope.
        encoded_output: Whether the result uses JSON value encoding.

    Returns:
        Unbound handler function ready to bind to a device instance.
    """
    if not has_input:
        def handler(device_self: AutoDispatchDevice) -> Any:
            """Dispatch a command without TANGO input."""
            target = getattr(device_self._device_object, name)
            result = target()
            if encoded_output:
                return pack_value(result)
            return result
    else:
        def handler(device_self: AutoDispatchDevice, value: Any) -> Any:
            """Dispatch a command with native or encoded TANGO input."""
            target = getattr(device_self._device_object, name)
            if encoded_input:
                args, kwargs = unpack_call(value)
                result = target(*args, **kwargs)
            else:
                result = target(value)
            if encoded_output:
                return pack_value(result)
            return result

    handler.__name__ = name
    return handler


def _install_commands(device: AutoDispatchDevice, device_class: Type[Any]) -> None:
    """Install public Python methods as dynamic TANGO commands.

    Args:
        device: Running PyTango device instance.
        device_class: Ordinary Python device class being exposed.
    """
    for spec in public_methods(device_class):
        if spec.name in device.excluded_commands:
            continue

        parameters = list(spec.signature.parameters.values())
        has_input = len(parameters) != 0
        encoded_input = uses_encoded_input(spec.signature)
        encoded_output = uses_encoded_output(spec.signature)
        handler = _command_handler(
            spec.name,
            has_input,
            encoded_input,
            encoded_output,
        )

        # add_command() installs the supplied callable on this device instance.
        # Bind the generated method explicitly before creating the command.
        bound_handler = MethodType(handler, device)
        tango_command = command(
            bound_handler,
            dtype_in=input_type(spec.signature),
            dtype_out=output_type(spec.signature),
        )
        device.add_command(tango_command, device_level=True)


def _property_reader(name: str, encoded: bool) -> Any:
    """Build a dynamic TANGO attribute reader.

    Args:
        name: Python property and TANGO attribute name.
        encoded: Whether the value uses JSON encoding.

    Returns:
        Unbound attribute reader.
    """
    def reader(device_self: AutoDispatchDevice, attr: Any) -> Any:
        """Read a wrapped Python property."""
        value = getattr(device_self._device_object, name)
        if encoded:
            return pack_value(value)
        return value

    reader.__name__ = "read_" + name
    return reader


def _property_writer(name: str, encoded: bool) -> Any:
    """Build a dynamic TANGO attribute writer.

    Args:
        name: Python property and TANGO attribute name.
        encoded: Whether the value uses JSON encoding.

    Returns:
        Unbound attribute writer.
    """
    def writer(device_self: AutoDispatchDevice, attr: Any) -> None:
        """Write a wrapped Python property."""
        value = attr.get_write_value()
        if encoded:
            value = unpack_value(value)
        setattr(device_self._device_object, name, value)

    writer.__name__ = "write_" + name
    return writer


def _install_attributes(device: AutoDispatchDevice, device_class: Type[Any]) -> None:
    """Install public Python properties as dynamic TANGO attributes.

    Args:
        device: Running PyTango device instance.
        device_class: Ordinary Python device class being exposed.
    """
    for spec in public_properties(device_class):
        dtype = tango_value_type(spec.annotation)
        encoded = dtype is None
        if encoded:
            dtype = str

        access = AttrWriteType.READ
        if spec.writable:
            access = AttrWriteType.READ_WRITE

        reader = MethodType(_property_reader(spec.name, encoded), device)
        kwargs = {
            "name": spec.name,
            "dtype": dtype,
            "access": access,
            "fget": reader,
        }

        if spec.writable:
            writer = MethodType(_property_writer(spec.name, encoded), device)
            kwargs["fset"] = writer

        tango_attribute = attribute(**kwargs)
        device.add_attribute(tango_attribute)


class AutoDispatchClient(object):
    """Reconstruct a Python device API over a TANGO connection.

    ``device_class`` defines the local Python interface.  The remote TANGO
    device may be generated by this framework or independently implemented, as
    long as its commands and attributes match that interface.
    """

    device_class = None  # type: Optional[Type[Any]]
    config = None  # type: Optional[Config]

    def __init__(self, config: Optional[Config] = None) -> None:
        """Create a reconstructed client for a TANGO device.

        Args:
            config: Connection configuration.  If omitted, the class-level
                ``config`` value is used.

        Raises:
            RuntimeError: If ``device_class`` or connection configuration is
                missing.
        """
        from .client import TangoTransport

        if self.device_class is None:
            raise RuntimeError("device_class is not configured")

        selected_config = config
        if selected_config is None:
            selected_config = type(self).config
        if selected_config is None:
            raise RuntimeError("config is not configured")

        object.__setattr__(self, "_config", selected_config)
        object.__setattr__(self, "_transport", TangoTransport(selected_config))

        property_specs = {}  # type: Dict[str, PropertySpec]
        for item in public_properties(self.device_class):
            property_specs[item.name] = item
        object.__setattr__(self, "_property_specs", property_specs)
        _install_client_methods(self)

    def __getattr__(self, name: str) -> Any:
        """Read a reconstructed Python property through TANGO.

        Args:
            name: Python property name.

        Returns:
            Remote attribute value.

        Raises:
            AttributeError: If the name is not a reconstructed property.
        """
        specs = object.__getattribute__(self, "_property_specs")
        if name in specs:
            spec = specs[name]
            encoded = tango_value_type(spec.annotation) is None
            value = self._transport.read_attribute(name)
            if encoded:
                return unpack_value(value)
            return value
        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Write a reconstructed Python property through TANGO.

        Args:
            name: Python property name.
            value: Value to assign.

        Raises:
            AttributeError: If a reconstructed property is read-only.
        """
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return

        specs = object.__getattribute__(self, "_property_specs")
        if name in specs:
            spec = specs[name]
            if not spec.writable:
                raise AttributeError("read-only property: " + name)

            encoded = tango_value_type(spec.annotation) is None
            if encoded:
                value = pack_value(value)

            self._transport.write_attribute(name, value)
            return

        object.__setattr__(self, name, value)

    @property
    def tango_config(self) -> Config:
        """Return the TANGO connection configuration.

        Returns:
            Configuration used by this reconstructed client.
        """
        return object.__getattribute__(self, "_config")


def _client_method(name: str, signature: Any) -> Any:
    """Build a client method that dispatches a TANGO command.

    Args:
        name: Python method and TANGO command name.
        signature: Original Python method signature without ``self``.

    Returns:
        Unbound client method ready to bind to a client instance.
    """
    encoded_input = uses_encoded_input(signature)
    encoded_output = uses_encoded_output(signature)

    def method(
        client_self: AutoDispatchClient,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """Dispatch one reconstructed Python method through TANGO."""
        if encoded_input:
            value = pack_call(tuple(args), dict(kwargs))
            result = client_self._transport.command(name, value)
        else:
            parameters = list(signature.parameters.values())
            if len(parameters) == 0:
                result = client_self._transport.command(name)
            else:
                bound = signature.bind(*args, **kwargs)
                bound.apply_defaults()
                value = next(iter(bound.arguments.values()))
                result = client_self._transport.command(name, value)

        if encoded_output:
            return unpack_value(result)
        return result

    method.__name__ = name
    method.__signature__ = signature
    return method


def _install_client_methods(client: AutoDispatchClient) -> None:
    """Install reconstructed remote methods on one client instance.

    Args:
        client: Auto-dispatch client instance.
    """
    client_class = type(client)
    if client.device_class is None:
        raise RuntimeError("device_class is not configured")

    for spec in public_methods(client.device_class):
        # Device-specific client methods are local overrides and must not be
        # replaced by automatically generated remote dispatch methods.
        if spec.name in client_class.__dict__:
            continue

        method = _client_method(spec.name, spec.signature)
        object.__setattr__(client, spec.name, MethodType(method, client))
