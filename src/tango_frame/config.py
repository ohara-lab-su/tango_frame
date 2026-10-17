"""Configuration objects for TANGO client connections."""

from typing import Optional


class Config(object):
    """Store the connection settings for a TANGO device.

    Normal operation uses the TANGO database namespace.  A database-less
    connection is supported only for local tests and requires ``tango_host``.

    Args:
        device_name: TANGO device name in ``domain/family/member`` form, or a
            device alias when a database is used.
        tango_host: TANGO database endpoint in ``host:port`` form.  If omitted
            for a database connection, PyTango resolves the device using the
            process TANGO_HOST configuration.
        database: Whether the normal TANGO database namespace is used.
    """

    def __init__(
        self,
        device_name: str,
        tango_host: Optional[str] = None,
        database: bool = True,
    ) -> None:
        """Initialize TANGO connection settings.

        Args:
            device_name: TANGO device name or database alias.
            tango_host: TANGO database endpoint in ``host:port`` form.
            database: Whether to resolve the device through the TANGO database.

        Raises:
            ValueError: If required configuration is missing or inconsistent.
        """
        if not device_name:
            raise ValueError("device_name must not be empty")
        if not database and not tango_host:
            raise ValueError("tango_host is required when database is False")

        self.device_name = device_name
        self.tango_host = tango_host
        self.database = database

    def device_url(self) -> str:
        """Return the device identifier passed to native ``tango.DeviceProxy``.

        Returns:
            Device name, alias, or a fully qualified TANGO URL.
        """
        # With no explicit host, leave namespace resolution to the normal
        # PyTango/TANGO_HOST configuration.
        if self.database and self.tango_host is None:
            return self.device_name

        if self.database:
            return "tango://{0}/{1}".format(
                self.tango_host,
                self.device_name,
            )

        # Database-less addressing is intentionally isolated to local tests.
        return "tango://{0}/{1}#dbase=no".format(
            self.tango_host,
            self.device_name,
        )
