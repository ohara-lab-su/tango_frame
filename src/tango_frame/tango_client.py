from types import MethodType
from typing import Any, Callable, Dict, Set

from tango import AttrWriteType, CmdArgType, DeviceProxy

from .adapter import dumps, loads, pack_call
from .dispatch_core import JSON_ARGS_MARKER, JSON_ATTRIBUTE_MARKER, JSON_RESULT_MARKER

_BUILTIN_COMMANDS = {"Init", "State", "Status"}


class TangoClient:
    def __init__(self, device_name: str) -> None:
        object.__setattr__(self, "_proxy", DeviceProxy(device_name))
        object.__setattr__(self, "_attribute_names", set())
        object.__setattr__(self, "_writable_attributes", set())
        object.__setattr__(self, "_json_attributes", set())
        self._build_interface()

    def _build_interface(self) -> None:
        attribute_names = set()  # type: Set[str]
        writable = set()  # type: Set[str]
        json_attributes = set()  # type: Set[str]
        for info in self._proxy.attribute_list_query_ex():
            if info.name in ("State", "Status"):
                continue
            attribute_names.add(info.name)
            if info.writable != AttrWriteType.READ:
                writable.add(info.name)
            if JSON_ATTRIBUTE_MARKER in (getattr(info, "description", "") or ""):
                json_attributes.add(info.name)

        object.__setattr__(self, "_attribute_names", attribute_names)
        object.__setattr__(self, "_writable_attributes", writable)
        object.__setattr__(self, "_json_attributes", json_attributes)

        for info in self._proxy.command_list_query():
            if info.cmd_name in _BUILTIN_COMMANDS:
                continue
            dispatcher = self._make_command_dispatcher(info)
            object.__setattr__(self, info.cmd_name, MethodType(dispatcher, self))

    @staticmethod
    def _make_command_dispatcher(info: Any) -> Callable[..., Any]:
        command_name = info.cmd_name
        json_input = JSON_ARGS_MARKER in (getattr(info, "in_type_desc", "") or "")
        json_output = JSON_RESULT_MARKER in (getattr(info, "out_type_desc", "") or "")
        no_input = info.in_type == CmdArgType.DevVoid
        no_output = info.out_type == CmdArgType.DevVoid

        def invoke(client_self: "TangoClient", *args: Any, **kwargs: Any) -> Any:
            if no_input:
                if args or kwargs:
                    raise TypeError(command_name + " takes no arguments")
                result = client_self._proxy.command_inout(command_name)
            elif json_input:
                result = client_self._proxy.command_inout(command_name, pack_call(args, kwargs))
            else:
                if kwargs or len(args) != 1:
                    raise TypeError(command_name + " requires exactly one positional argument")
                result = client_self._proxy.command_inout(command_name, args[0])

            if no_output:
                return None
            if json_output:
                return loads(result)
            return result

        invoke.__name__ = command_name
        return invoke

    def __getattr__(self, name: str) -> Any:
        if name in self._attribute_names:
            value = self._proxy.read_attribute(name).value
            if name in self._json_attributes:
                return loads(value)
            return value
        raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        if name in self._writable_attributes:
            actual = dumps(value) if name in self._json_attributes else value
            self._proxy.write_attribute(name, actual)
            return
        object.__setattr__(self, name, value)

    def is_connected(self) -> bool:
        try:
            self._proxy.ping()
            return True
        except Exception:
            return False

    @property
    def raw_proxy(self) -> DeviceProxy:
        return self._proxy
