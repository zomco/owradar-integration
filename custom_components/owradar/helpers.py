"""Helpers for OwRadar."""
from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any, Concatenate, ParamSpec, TypeVar

from .core import OwRadarConnectionError, OwRadarError

from homeassistant.exceptions import HomeAssistantError

from .models import OwRadarEntity

_OwRadarEntityT = TypeVar("_OwRadarEntityT", bound=OwRadarEntity)
_P = ParamSpec("_P")


def owradar_exception_handler(
    func: Callable[Concatenate[_OwRadarEntityT, _P], Coroutine[Any, Any, Any]]
) -> Callable[Concatenate[_OwRadarEntityT, _P], Coroutine[Any, Any, None]]:
    """Decorate OwRadar calls to handle OwRadar exceptions.

    A decorator that wraps the passed in function, catches OwRadar errors,
    and handles the availability of the device in the data coordinator.
    """

    async def handler(
        self: _OwRadarEntityT, *args: _P.args, **kwargs: _P.kwargs
    ) -> None:
        try:
            await func(self, *args, **kwargs)
            self.coordinator.async_update_listeners()

        except OwRadarConnectionError as error:
            self.coordinator.last_update_success = False
            self.coordinator.async_update_listeners()
            raise HomeAssistantError("Error communicating with OwRadar API") from error

        except OwRadarError as error:
            raise HomeAssistantError("Invalid response from OwRadar API") from error

    return handler
