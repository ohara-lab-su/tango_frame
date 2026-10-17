"""JSON codec used when a Python call cannot use a native TANGO type."""

import base64
import json
from typing import Any, Dict, Tuple


_TYPE_KEY = "__tango_frame_type__"


def _encode(value: Any) -> Any:
    """Convert Python values into JSON-serializable values.

    Args:
        value: Python value to encode.

    Returns:
        JSON-serializable representation.
    """
    if isinstance(value, bytes):
        return {
            _TYPE_KEY: "bytes",
            "data": base64.b64encode(value).decode("ascii"),
        }
    if isinstance(value, tuple):
        return {
            _TYPE_KEY: "tuple",
            "items": [_encode(item) for item in value],
        }
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _encode(item) for key, item in value.items()}
    return value


def _decode(value: Any) -> Any:
    """Restore a Python value from its JSON-compatible representation.

    Args:
        value: Decoded JSON value.

    Returns:
        Restored Python value.
    """
    if isinstance(value, list):
        return [_decode(item) for item in value]
    if isinstance(value, dict):
        value_type = value.get(_TYPE_KEY)
        if value_type == "bytes":
            return base64.b64decode(value["data"].encode("ascii"))
        if value_type == "tuple":
            return tuple(_decode(item) for item in value["items"])
        return {key: _decode(item) for key, item in value.items()}
    return value


def pack_call(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:
    """Serialize positional and keyword arguments into one TANGO string.

    Args:
        args: Positional call arguments.
        kwargs: Keyword call arguments.

    Returns:
        Compact JSON payload.
    """
    return json.dumps(
        {"args": _encode(args), "kwargs": _encode(kwargs)},
        ensure_ascii=False,
        separators=(",", ":"),
    )


def unpack_call(payload: str) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
    """Deserialize a call payload.

    Args:
        payload: JSON call payload.

    Returns:
        Tuple containing positional arguments and keyword arguments.
    """
    data = json.loads(payload)
    args = _decode(data["args"])
    kwargs = _decode(data["kwargs"])
    return tuple(args), dict(kwargs)


def pack_value(value: Any) -> str:
    """Serialize a non-native Python value.

    Args:
        value: Python value to serialize.

    Returns:
        Compact JSON payload.
    """
    return json.dumps(_encode(value), ensure_ascii=False, separators=(",", ":"))


def unpack_value(payload: str) -> Any:
    """Deserialize a non-native Python value.

    Args:
        payload: JSON payload.

    Returns:
        Restored Python value.
    """
    return _decode(json.loads(payload))
