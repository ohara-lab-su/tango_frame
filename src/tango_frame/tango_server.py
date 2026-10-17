import inspect
from typing import Any, Callable, Dict, List, Optional, Type

from tango import AttrWriteType, DevState
from tango.server import Device, attribute, command, run

from .adapter import dumps, loads, unpack_call
from .dispatch_core import (
    JSON_ARGS_MARKER,
    JSON_ATTRIBUTE_MARKER,
    JSON_RESULT_MARKER,
    command_input_type,
    command_output_type,
    command_uses_json_input,
    command_uses_json_output,
    public_method_names,
    public_property_names,
)
from .type_mapping import tango_native_type


def _make_command(method_name: str, method: Any) -> Callable[..., Any]:
    input_type = command_input_type(method)
    output_type = command_output_type(method)
    json_input = command_uses_json_input(method)
    json_output = command_uses_json_output(method)

    if input_type is None:
        def handler(self: Device) -> Any:
            result = getattr(self._target, method_name)()
            if json_output:
                return dumps(result)
            return result
    elif json_input:
        def handler(self: Device, request: str) -> Any:
            args, kwargs = unpack_call(request)
            result = getattr(self._target, method_name)(*args, **kwargs)
            if json_output:
                return dumps(result)
            return result
    else:
        def handler(self: Device, value: Any) -> Any:
            result = getattr(self._target, method_name)(value)
            if json_output:
                return dumps(result)
            return result

    handler.__name__ = method_name
    doc_in = JSON_ARGS_MARKER if json_input else ""
    doc_out = JSON_RESULT_MARKER if json_output else ""
    return command(
        dtype_in=input_type,
        dtype_out=output_type,
        doc_in=doc_in,
        doc_out=doc_out,
    )(handler)


def _make_attribute(property_name: str, prop: property) -> Any:
    annotation = inspect.signature(prop.fget).return_annotation
    native_type = tango_native_type(annotation)
    json_value = native_type is None
    dtype = str if json_value else native_type

    def reader(self: Device) -> Any:
        value = getattr(self._target, property_name)
        if json_value:
            return dumps(value)
        return value

    reader.__name__ = "read_" + property_name
    kwargs = {
        "name": property_name,
        "dtype": dtype,
        "fget": reader,
        "doc": JSON_ATTRIBUTE_MARKER if json_value else "",
    }  # type: Dict[str, Any]

    if prop.fset is None:
        return attribute(**kwargs)

    def writer(self: Device, value: Any) -> None:
        actual = loads(value) if json_value else value
        setattr(self._target, property_name, actual)

    writer.__name__ = "write_" + property_name
    kwargs["access"] = AttrWriteType.READ_WRITE
    kwargs["fset"] = writer
    return attribute(**kwargs)


def create_device_server_class(
    interface_class: Type[Any],
    target_factory: Optional[Callable[[], Any]] = None,
    class_name: Optional[str] = None,
) -> Type[Device]:
    factory = target_factory
    if factory is None:
        factory = interface_class

    namespace = {}  # type: Dict[str, Any]
    namespace["_target_factory"] = staticmethod(factory)

    def init_device(self: Device) -> None:
        Device.init_device(self)
        self._target = type(self)._target_factory()
        self.set_state(DevState.ON)

    def delete_device(self: Device) -> None:
        target = getattr(self, "_target", None)
        if target is not None:
            release = getattr(target, "release", None)
            if callable(release):
                release()

    namespace["init_device"] = init_device
    namespace["delete_device"] = delete_device

    for method_name in public_method_names(interface_class):
        method = getattr(interface_class, method_name)
        namespace[method_name] = _make_command(method_name, method)

    for property_name in public_property_names(interface_class):
        prop = getattr(interface_class, property_name)
        namespace[property_name] = _make_attribute(property_name, prop)

    device_class_name = class_name
    if device_class_name is None:
        device_class_name = interface_class.__name__ + "TangoDevice"
    return type(device_class_name, (Device,), namespace)


def run_device_server(
    device_class: Type[Device],
    server_name: str,
    instance_name: str,
    extra_args: Optional[List[str]] = None,
) -> None:
    args = [server_name, instance_name]
    if extra_args is not None:
        args.extend(extra_args)
    run((device_class,), args=args, raises=True)
