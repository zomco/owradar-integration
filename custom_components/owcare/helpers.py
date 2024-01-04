"""Helpers for Owcare."""
from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any, Concatenate, ParamSpec, TypeVar

from .core import OwcareConnectionError, OwcareError

from homeassistant.exceptions import HomeAssistantError

from .models import OwcareEntity

_OwcareEntityT = TypeVar("_OwcareEntityT", bound=OwcareEntity)
_P = ParamSpec("_P")


def owcare_exception_handler(
    func: Callable[Concatenate[_OwcareEntityT, _P], Coroutine[Any, Any, Any]]
) -> Callable[Concatenate[_OwcareEntityT, _P], Coroutine[Any, Any, None]]:
    """Decorate Owcare calls to handle Owcare exceptions.

    A decorator that wraps the passed in function, catches Owcare errors,
    and handles the availability of the device in the data coordinator.
    """

    async def handler(
        self: _OwcareEntityT, *args: _P.args, **kwargs: _P.kwargs
    ) -> None:
        try:
            await func(self, *args, **kwargs)
            self.coordinator.async_update_listeners()

        except OwcareConnectionError as error:
            self.coordinator.last_update_success = False
            self.coordinator.async_update_listeners()
            raise HomeAssistantError("Error communicating with Owcare API") from error

        except OwcareError as error:
            raise HomeAssistantError("Invalid response from Owcare API") from error

    return handler
