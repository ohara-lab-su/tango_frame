from typing import Any, List, Optional, Sequence, Type

from tango.server import run


def run_device_server(
    device_class: Type[Any],
    args: Optional[Sequence[str]] = None,
) -> None:
    run((device_class,), args=list(args) if args is not None else None)
