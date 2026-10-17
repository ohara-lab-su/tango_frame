"""Map Python 3.7 type annotations onto PyTango value types."""

import inspect
from typing import Any, List, Optional, Type


def _list_element_type(annotation: Any) -> Optional[Type[Any]]:
    """Return the supported element type of a homogeneous list annotation.

    Python 3.7 does not provide ``typing.get_origin`` or ``typing.get_args``.
    The compatibility path therefore uses the ``__origin__`` and ``__args__``
    attributes exposed by ``typing.List``.

    Args:
        annotation: Python type annotation.

    Returns:
        Supported list element type, or ``None`` when unsupported.
    """
    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", ())
    if origin in (list, List) and len(args) == 1:
        element = args[0]
        if element in (bool, int, float, str):
            return element
    return None


def tango_scalar_type(annotation: Any) -> Optional[Any]:
    """Map a scalar Python annotation to a PyTango high-level type.

    Args:
        annotation: Python type annotation.

    Returns:
        PyTango-compatible scalar type, or ``None`` when unsupported.
    """
    if annotation is bool:
        return bool
    if annotation is int:
        return int
    if annotation is float:
        return float
    if annotation is str:
        return str
    return None


def tango_array_type(annotation: Any) -> Optional[Any]:
    """Map a homogeneous list annotation to a PyTango spectrum type.

    Args:
        annotation: Python type annotation.

    Returns:
        PyTango high-level spectrum type, or ``None`` when unsupported.
    """
    element = _list_element_type(annotation)
    if element is None:
        return None
    return (element,)


def tango_value_type(annotation: Any) -> Optional[Any]:
    """Map a supported Python annotation to a PyTango value type.

    Args:
        annotation: Python type annotation.

    Returns:
        PyTango-compatible type, or ``None`` when JSON fallback is required.
    """
    scalar = tango_scalar_type(annotation)
    if scalar is not None:
        return scalar
    return tango_array_type(annotation)


def is_void(annotation: Any) -> bool:
    """Return whether an annotation represents no return value.

    Args:
        annotation: Python return annotation.

    Returns:
        ``True`` for ``None`` or ``NoneType``.
    """
    return annotation is None or annotation is type(None)


def input_type(signature: inspect.Signature) -> Optional[Any]:
    """Determine the TANGO command input type for a Python signature.

    Args:
        signature: Python method signature without ``self``.

    Returns:
        Native PyTango type, ``str`` for encoded input, or ``None`` for void.
    """
    parameters = list(signature.parameters.values())
    if len(parameters) == 0:
        return None
    if len(parameters) == 1:
        parameter = parameters[0]
        if parameter.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            native = tango_value_type(parameter.annotation)
            if native is not None:
                return native
    return str


def output_type(signature: inspect.Signature) -> Optional[Any]:
    """Determine the TANGO command output type for a Python signature.

    Args:
        signature: Python method signature without ``self``.

    Returns:
        Native PyTango type, ``str`` for encoded output, or ``None`` for void.
    """
    annotation = signature.return_annotation
    if is_void(annotation):
        return None

    native = tango_value_type(annotation)
    if native is not None:
        return native
    return str


def uses_encoded_input(signature: inspect.Signature) -> bool:
    """Return whether a call requires the JSON input envelope.

    Args:
        signature: Python method signature without ``self``.

    Returns:
        ``True`` when the input cannot be represented by one native TANGO value.
    """
    parameters = list(signature.parameters.values())
    if len(parameters) == 0:
        return False
    if len(parameters) == 1:
        parameter = parameters[0]
        native = tango_value_type(parameter.annotation)
        if native is not None:
            return False
    return True


def uses_encoded_output(signature: inspect.Signature) -> bool:
    """Return whether a return value requires JSON encoding.

    Args:
        signature: Python method signature without ``self``.

    Returns:
        ``True`` when the return type has no native TANGO representation.
    """
    annotation = signature.return_annotation
    if is_void(annotation):
        return False
    return tango_value_type(annotation) is None
