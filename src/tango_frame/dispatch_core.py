import inspect
from typing import Any, List, Type

from .type_mapping import return_transport_type, tango_native_type

JSON_ARGS_MARKER = "tango-frame:json-args"
JSON_RESULT_MARKER = "tango-frame:json-result"
JSON_ATTRIBUTE_MARKER = "tango-frame:json-value"


def public_method_names(interface_class: Type[Any]) -> List[str]:
    names = []  # type: List[str]
    for name, member in inspect.getmembers(interface_class):
        if name.startswith("_"):
            continue
        if isinstance(getattr(interface_class, name, None), property):
            continue
        if callable(member):
            names.append(name)
    return names


def public_property_names(interface_class: Type[Any]) -> List[str]:
    names = []  # type: List[str]
    for name, member in inspect.getmembers(interface_class):
        if name.startswith("_"):
            continue
        if isinstance(member, property):
            names.append(name)
    return names


def command_input_type(method: Any) -> Any:
    signature = inspect.signature(method)
    params = [p for p in signature.parameters.values() if p.name != "self"]
    if len(params) == 0:
        return None
    if len(params) == 1:
        native = tango_native_type(params[0].annotation)
        if native is not None:
            return native
    return str


def command_uses_json_input(method: Any) -> bool:
    signature = inspect.signature(method)
    params = [p for p in signature.parameters.values() if p.name != "self"]
    if len(params) == 0:
        return False
    if len(params) == 1 and tango_native_type(params[0].annotation) is not None:
        return False
    return True


def command_output_type(method: Any) -> Any:
    return return_transport_type(inspect.signature(method).return_annotation)


def command_uses_json_output(method: Any) -> bool:
    annotation = inspect.signature(method).return_annotation
    if annotation in (None, type(None), inspect.Signature.empty):
        return False
    return tango_native_type(annotation) is None
