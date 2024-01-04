"""Exceptions for Owcare."""


class OwcareError(Exception):
    """Generic Owcare exception."""


class OwcareEmptyResponseError(Exception):
    """Owcare empty API response exception."""


class OwcareConnectionError(OwcareError):
    """Owcare connection exception."""


class OwcareConnectionTimeoutError(OwcareConnectionError):
    """Owcare connection Timeout exception."""


class OwcareConnectionClosedError(OwcareConnectionError):
    """Owcare WebSocket connection has been closed."""


class OwcareUpgradeError(OwcareError):
    """Owcare upgrade exception."""
