from types import MethodType
from typing import Any, Type

from tango import AttrWriteType, DevState
from tango.server import Device, attribute, command

from .codec import pack_call, pack_value, unpack_call, unpack_value
from .introspection import public_methods, public_properties
from .type_mapping import (
    input_type,
    output_type,
    tango_value_type,
    uses_encoded_input,
    uses_encoded_output,
)


class AutoDispatchDevice(Device):
    device_class = None
    excluded_commands = set()

    def init_device(self) -> None:
        Device.init_device(self)
        if self.device_class is None:
            raise RuntimeError("device_class is not configured")
        self._device_object = self.device_class()
        self.set_state(DevState.ON)

    def delete_device(self) -> None:
        device_object = getattr(self, "_device_object", None)
        if device_object is not None:
            release = getattr(device_object, "release", None)
            if callable(release):
                release()

    def initialize_dynamic_attributes(self) -> None:
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
    if not has_input:
        def handler(device_self: AutoDispatchDevice) -> Any:
            target = getattr(device_self._device_object, name)
            result = target()
            if encoded_output:
                return pack_value(result)
            return result
    else:
        def handler(device_self: AutoDispatchDevice, value: Any) -> Any:
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

        # add_command() installs the supplied callable directly on this device
        # instance. Bind the generated method explicitly before decorating it.
        bound_handler = MethodType(handler, device)
        tango_command = command(
            bound_handler,
            dtype_in=input_type(spec.signature),
            dtype_out=output_type(spec.signature),
        )
        device.add_command(tango_command, device_level=True)


def _property_reader(name: str, encoded: bool) -> Any:
    def reader(device_self: AutoDispatchDevice, attr: Any) -> Any:
        value = getattr(device_self._device_object, name)
        if encoded:
            return pack_value(value)
        return value

    reader.__name__ = "read_" + name
    return reader


def _property_writer(name: str, encoded: bool) -> Any:
    def writer(device_self: AutoDispatchDevice, attr: Any) -> None:
        value = attr.get_write_value()
        if encoded:
            value = unpack_value(value)
        setattr(device_self._device_object, name, value)

    writer.__name__ = "write_" + name
    return writer


def _install_attributes(device: AutoDispatchDevice, device_class: Type[Any]) -> None:
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
    device_class = None

    def __init__(self, device_name: str) -> None:
        from .client import TangoTransport

        if self.device_class is None:
            raise RuntimeError("device_class is not configured")

        object.__setattr__(self, "_transport", TangoTransport(device_name))
        object.__setattr__(
            self,
            "_property_specs",
            {
                item.name: item
                for item in public_properties(self.device_class)
            },
        )
        _install_client_methods(self)

    def __getattr__(self, name: str) -> Any:
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


def _client_method(name: str, signature: Any) -> Any:
    encoded_input = uses_encoded_input(signature)
    encoded_output = uses_encoded_output(signature)

    def method(
        client_self: AutoDispatchClient,
        *args: Any,
        **kwargs: Any
    ) -> Any:
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
    client_class = type(client)

    for spec in public_methods(client.device_class):
        # A method explicitly implemented by the device-specific client class
        # is a local override and must not be replaced by remote dispatch.
        if spec.name in client_class.__dict__:
            continue

        method = _client_method(spec.name, spec.signature)
        object.__setattr__(
            client,
            spec.name,
            MethodType(method, client),
        )
