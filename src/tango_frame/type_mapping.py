import inspect
from typing import Any, Dict, List, Optional, Tuple, Type, get_args, get_origin


def _list_element_type(annotation: Any) -> Optional[Type[Any]]:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in (list, List) and len(args) == 1:
        element = args[0]
        if element in (bool, int, float, str):
            return element
    return None


def tango_scalar_type(annotation: Any) -> Optional[Any]:
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
    element = _list_element_type(annotation)
    if element is None:
        return None
    return (element,)


def tango_value_type(annotation: Any) -> Optional[Any]:
    scalar = tango_scalar_type(annotation)
    if scalar is not None:
        return scalar
    return tango_array_type(annotation)


def is_void(annotation: Any) -> bool:
    return annotation is None or annotation is type(None)


def input_type(signature: inspect.Signature) -> Optional[Any]:
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
    annotation = signature.return_annotation
    if is_void(annotation):
        return None
    native = tango_value_type(annotation)
    if native is not None:
        return native
    return str


def uses_encoded_input(signature: inspect.Signature) -> bool:
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
    annotation = signature.return_annotation
    if is_void(annotation):
        return False
    return tango_value_type(annotation) is None

