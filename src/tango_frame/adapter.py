import base64
import json
from typing import Any, Dict


def _to_json_value(value: Any) -> Any:
    if isinstance(value, tuple):
        return {"__tango_frame_type__": "tuple", "items": [_to_json_value(v) for v in value]}
    if isinstance(value, bytes):
        return {
            "__tango_frame_type__": "bytes",
            "data": base64.b64encode(value).decode("ascii"),
        }
    if isinstance(value, list):
        return [_to_json_value(v) for v in value]
    if isinstance(value, dict):
        result = {}  # type: Dict[str, Any]
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("JSON transport requires string dictionary keys")
            result[key] = _to_json_value(item)
        return result
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError("Unsupported transport type: " + type(value).__name__)


def _from_json_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_from_json_value(v) for v in value]
    if isinstance(value, dict):
        tag = value.get("__tango_frame_type__")
        if tag == "tuple":
            return tuple(_from_json_value(v) for v in value["items"])
        if tag == "bytes":
            return base64.b64decode(value["data"].encode("ascii"))
        return {key: _from_json_value(item) for key, item in value.items()}
    return value


def dumps(value: Any) -> str:
    return json.dumps(_to_json_value(value), ensure_ascii=False, separators=(",", ":"))


def loads(text: str) -> Any:
    return _from_json_value(json.loads(text))


def pack_call(args: tuple, kwargs: Dict[str, Any]) -> str:
    return dumps({"args": args, "kwargs": kwargs})


def unpack_call(text: str) -> Any:
    request = loads(text)
    return request["args"], request["kwargs"]
