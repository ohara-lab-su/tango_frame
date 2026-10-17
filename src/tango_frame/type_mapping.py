import inspect
from typing import Any, List, Tuple, Type, get_args, get_origin


_JSON = str


def tango_native_type(annotation: Any) -> Any:
    if annotation in (bool, int, float, str):
        return annotation
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin in (list, List, tuple, Tuple) and len(args) > 0:
        element = args[0]
        if element in (bool, int, float, str):
            if origin in (tuple, Tuple) and len(args) > 1 and args[1] is not Ellipsis:
                for item in args:
                    if item is not element:
                        return None
            return (element,)
    return None


def return_transport_type(annotation: Any) -> Any:
    if annotation in (None, type(None), inspect.Signature.empty):
        return None
    native = tango_native_type(annotation)
    if native is not None:
        return native
    return _JSON
