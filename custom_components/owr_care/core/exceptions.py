"""Exceptions for OWRCare."""


class OWRCareError(Exception):
    """Generic OWRCare exception."""


class OWRCareEmptyResponseError(Exception):
    """OWRCare empty API response exception."""


class OWRCareConnectionError(OWRCareError):
    """OWRCare connection exception."""


class OWRCareConnectionTimeoutError(OWRCareConnectionError):
    """OWRCare connection Timeout exception."""


class OWRCareConnectionClosedError(OWRCareConnectionError):
    """OWRCare WebSocket connection has been closed."""


class OWRCareUpgradeError(OWRCareError):
    """OWRCare upgrade exception."""
