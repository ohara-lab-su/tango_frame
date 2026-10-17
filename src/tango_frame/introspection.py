import inspect
from typing import Any, List, NamedTuple, Type


class MethodSpec(NamedTuple):
    name: str
    signature: inspect.Signature


class PropertySpec(NamedTuple):
    name: str
    descriptor: property
    annotation: Any
    writable: bool


def public_methods(device_class: Type[Any]) -> List[MethodSpec]:
    result = []
    for name in dir(device_class):
        if name.startswith("_"):
            continue
        raw = getattr(device_class, name)
        if not callable(raw):
            continue
        signature = inspect.signature(raw)
        parameters = list(signature.parameters.values())
        if parameters and parameters[0].name == "self":
            signature = signature.replace(parameters=parameters[1:])
        result.append(MethodSpec(name=name, signature=signature))
    return result


def public_properties(device_class: Type[Any]) -> List[PropertySpec]:
    result = []
    for name in dir(device_class):
        if name.startswith("_"):
            continue
        descriptor = getattr(device_class, name)
        if not isinstance(descriptor, property):
            continue
        annotation = inspect.signature(descriptor.fget).return_annotation
        result.append(
            PropertySpec(
                name=name,
                descriptor=descriptor,
                annotation=annotation,
                writable=descriptor.fset is not None,
            )
        )
    return result
