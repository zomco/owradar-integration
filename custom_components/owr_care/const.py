"""Constants for owr_care."""
from datetime import timedelta
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=10)

NAME = "owr care"
DOMAIN = "owr_care"
VERSION = "0.0.231107"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
