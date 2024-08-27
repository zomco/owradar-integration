"""Constants for owradar."""
from datetime import timedelta
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=10)

NAME = "OwRadar"
DOMAIN = "owradar"
VERSION = "0.0.231109"
