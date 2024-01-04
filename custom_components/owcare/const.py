"""Constants for owcare."""
from datetime import timedelta
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=10)

NAME = "Oware"
DOMAIN = "owcare"
VERSION = "0.0.231109"
