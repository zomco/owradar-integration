"""Helpers for OWRCare."""
from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any, Concatenate, ParamSpec, TypeVar

from owrcare import OWRCareConnectionError, OWRCareError

from homeassistant.exceptions import HomeAssistantError

from .models import OWRCareEntity

_OWRCareEntityT = TypeVar("_OWRCareEntityT", bound=OWRCareEntity)
_P = ParamSpec("_P")


def owrcare_exception_handler(
    func: Callable[Concatenate[_OWRCareEntityT, _P], Coroutine[Any, Any, Any]]
) -> Callable[Concatenate[_OWRCareEntityT, _P], Coroutine[Any, Any, None]]:
    """Decorate OWRCare calls to handle OWRCare exceptions.

    A decorator that wraps the passed in function, catches OWRCare errors,
    and handles the availability of the device in the data coordinator.
    """

    async def handler(self: _OWRCareEntityT, *args: _P.args, **kwargs: _P.kwargs) -> None:
        try:
            await func(self, *args, **kwargs)
            self.coordinator.async_update_listeners()

        except OWRCareConnectionError as error:
            self.coordinator.last_update_success = False
            self.coordinator.async_update_listeners()
            raise HomeAssistantError("Error communicating with OWRCare API") from error

        except OWRCareError as error:
            raise HomeAssistantError("Invalid response from OWRCare API") from error

    return handler
