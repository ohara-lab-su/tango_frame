"""Introspection helpers for ordinary Python device classes."""

import inspect
from typing import Any, List, NamedTuple, Type


class MethodSpec(NamedTuple):
    """Describe one public Python method.

    Attributes:
        name: Public method name.
        signature: Method signature without the instance ``self`` parameter.
    """

    name: str
    signature: inspect.Signature


class PropertySpec(NamedTuple):
    """Describe one public Python property.

    Attributes:
        name: Public property name.
        descriptor: Original Python property descriptor.
        annotation: Getter return annotation used for TANGO type mapping.
        writable: Whether the property has a setter.
    """

    name: str
    descriptor: property
    annotation: Any
    writable: bool


def public_methods(device_class: Type[Any]) -> List[MethodSpec]:
    """Return public callable methods declared by a device class.

    Args:
        device_class: Ordinary Python device class to inspect.

    Returns:
        Public method specifications.
    """
    result = []  # type: List[MethodSpec]
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
    """Return public properties declared by a device class.

    Args:
        device_class: Ordinary Python device class to inspect.

    Returns:
        Public property specifications.
    """
    result = []  # type: List[PropertySpec]
    for name in dir(device_class):
        if name.startswith("_"):
            continue

        descriptor = getattr(device_class, name)
        if not isinstance(descriptor, property):
            continue

        # A property getter is required by Python's property protocol for a
        # readable property.  Its return annotation defines the TANGO type.
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
