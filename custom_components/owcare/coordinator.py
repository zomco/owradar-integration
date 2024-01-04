"""DataUpdateCoordinator for owcare."""
from __future__ import annotations

from .core import (
    Client,
    Device as OwcareDevice,
    OwcareConnectionClosedError,
    OwcareError,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, SCAN_INTERVAL


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class OwcareDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Owcare data from single endpoint."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        self.client = Client(
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
                await self.client.connect()
            except OwcareError as err:
                self.logger.info(err)
                if self.unsub:
                    self.unsub()
                    self.unsub = None
                return

            try:
                await self.client.listen(callback=self.async_set_updated_data)
            except OwcareConnectionClosedError as err:
                self.last_update_success = False
                self.logger.info(err)
            except OwcareError as err:
                self.last_update_success = False
                self.async_update_listeners()
                self.logger.error(err)

            # Ensure we are disconnected
            await self.client.disconnect()
            if self.unsub:
                self.unsub()
                self.unsub = None

        async def close_websocket(_: Event) -> None:
            """Close WebSocket connection."""
            self.unsub = None
            await self.client.disconnect()

        # Clean disconnect WebSocket on Home Assistant shutdown
        self.unsub = self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STOP, close_websocket
        )

        # Start listening
        self.config_entry.async_create_background_task(
            self.hass, listen(), "owcare-listen"
        )

    async def _async_update_data(self) -> OwcareDevice:
        """Fetch data from Owcare."""
        # If the device supports a WebSocket, try activating it.
        try:
            device = await self.client.update(full_update=not self.last_update_success)
        except OwcareError as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error

        # If the device supports a WebSocket, try activating it.
        if not self.client.connected and not self.unsub:
            self._use_websocket()

        return device
