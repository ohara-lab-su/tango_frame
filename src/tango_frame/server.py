"""Helpers for starting TANGO device servers."""

from typing import Any, List, Optional, Sequence, Type

from tango.server import run


def run_device_server(
    device_class: Type[Any],
    args: Optional[Sequence[str]] = None,
) -> None:
    """Run a PyTango device server class.

    The helper does not force database-less operation.  Normal TANGO database
    startup arguments can therefore be supplied by the application.  ``-nodb``
    remains an application-level option for local tests only.

    Args:
        device_class: PyTango ``Device`` subclass to run.
        args: Optional argument sequence passed to ``tango.server.run``.
    """
    run_args = None  # type: Optional[List[str]]
    if args is not None:
        run_args = list(args)

    run((device_class,), args=run_args)
