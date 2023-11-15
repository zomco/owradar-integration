"""DataUpdateCoordinator for owr_care."""
from __future__ import annotations

from .core import (
    OWRCare,
    Device as OWRCareDevice,
    OWRCareConnectionClosedError,
    OWRCareError,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, SCAN_INTERVAL


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class OWRCareDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching OWRCare data from single endpoint."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        self.owrcare = OWRCare(
            entry.data[CONF_HOST], session=async_get_clientsession(hass)
        )
        self.unsub: CALLBACK_TYPE | None = None

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    @callback
    def _use_websocket(self) -> None:
        """Use WebSocket for updates, instead of polling."""

        async def listen() -> None:
            """Listen for state changes via WebSocket."""
            try:
                await self.owrcare.connect()
            except OWRCareError as err:
                self.logger.info(err)
                if self.unsub:
                    self.unsub()
                    self.unsub = None
                return

            try:
                await self.owrcare.listen(callback=self.async_set_updated_data)
            except OWRCareConnectionClosedError as err:
                self.last_update_success = False
                self.logger.info(err)
            except OWRCareError as err:
                self.last_update_success = False
                self.async_update_listeners()
                self.logger.error(err)

            # Ensure we are disconnected
            await self.owrcare.disconnect()
            if self.unsub:
                self.unsub()
                self.unsub = None

        async def close_websocket(_: Event) -> None:
            """Close WebSocket connection."""
            self.unsub = None
            await self.owrcare.disconnect()

        # Clean disconnect WebSocket on Home Assistant shutdown
        self.unsub = self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STOP, close_websocket
        )

        # Start listening
        self.config_entry.async_create_background_task(
            self.hass, listen(), "owrcare-listen"
        )

    async def _async_update_data(self) -> OWRCareDevice:
        """Fetch data from OWRCare."""
        # If the device supports a WebSocket, try activating it.
        try:
            device = await self.owrcare.update(full_update=not self.last_update_success)
        except OWRCareError as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error

        # If the device supports a WebSocket, try activating it.
        if not self.owrcare.connected and not self.unsub:
            self._use_websocket()

        return device
