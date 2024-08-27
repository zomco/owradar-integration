"""Exceptions for OwRadar."""


class OwRadarError(Exception):
    """Generic OwRadar exception."""


class OwRadarEmptyResponseError(Exception):
    """OwRadar empty API response exception."""


class OwRadarConnectionError(OwRadarError):
    """OwRadar connection exception."""


class OwRadarConnectionTimeoutError(OwRadarConnectionError):
    """OwRadar connection Timeout exception."""


class OwRadarConnectionClosedError(OwRadarConnectionError):
    """OwRadar WebSocket connection has been closed."""


class OwRadarUpgradeError(OwRadarError):
    """OwRadar upgrade exception."""
