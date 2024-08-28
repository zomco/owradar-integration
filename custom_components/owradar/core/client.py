"""Asynchronous Python client for owradar."""
from __future__ import annotations

import asyncio
import json
import socket
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import aiohttp
import asyncio
import async_timeout
import backoff
from cachetools import TTLCache
from yarl import URL

from .common_models import CommonDevice
from .exceptions import (
    OwRadarConnectionClosedError,
    OwRadarConnectionError,
    OwRadarConnectionTimeoutError,
    OwRadarEmptyResponseError,
    OwRadarError,
)
from .r60abd1_models import R60abd1Device, R60abd1Setting

if TYPE_CHECKING:
    from collections.abc import Callable

VERSION_CACHE: TTLCache[str, str | None] = TTLCache(maxsize=16, ttl=7200)


@dataclass
class Client:
    """Main class for handling connections with owradar."""

    host: str
    request_timeout: float = 8.0
    session: aiohttp.client.ClientSession | None = None

    _state_client: aiohttp.ClientWebSocketResponse | None = None
    _stats_client: aiohttp.ClientWebSocketResponse | None = None
    _snap_client: aiohttp.ClientWebSocketResponse | None = None
    _event_client: aiohttp.ClientWebSocketResponse | None = None
    _state_data: any = None
    _stats_data: any = None
    _snap_data: any = None
    _event_data: any = None
    _close_session: bool = False
    _device: Any = None

    @property
    def state_connected(self) -> bool:
        """Return if we are connect to the WebSocket of device.

        Returns
        -------
            True if we are connected to the WebSocket of device,
            False otherwise.

        """
        return self._state_client is not None and not self._state_client.closed

    @property
    def stats_connected(self) -> bool:
        """Return if we are connect to the WebSocket of device.

        Returns
        -------
            True if we are connected to the WebSocket of device,
            False otherwise.

        """
        return self._stats_client is not None and not self._stats_client.closed

    @property
    def snap_connected(self) -> bool:
        """Return if we are connect to the WebSocket of device.

        Returns
        -------
            True if we are connected to the WebSocket of device,
            False otherwise.

        """
        return self._snap_client is not None and not self._snap_client.closed

    @property
    def event_connected(self) -> bool:
        """Return if we are connect to the WebSocket of device.

        Returns
        -------
            True if we are connected to the WebSocket of device,
            False otherwise.

        """
        return self._event_client is not None and not self._event_client.closed

    async def state_connect(self) -> None:
        """Connect to the WebSocket of device.

        Raises
        ------
            OwRadarError: The configured device, does not support WebSocket
                communications.
            OwRadarConnectionError: Error occurred while communicating with
                the device via the WebSocket.

        """
        if self.state_connected:
            return
        url = URL.build(scheme="ws", host=self.host, port=80, path="/ws/state")
        try:
            self._state_client = await self.session.ws_connect(url=url, heartbeat=30)
        except (
                aiohttp.WSServerHandshakeError,
                aiohttp.ClientConnectionError,
                socket.gaierror,
        ) as exception:
            msg = (
                "Error occurred while communicating with device"
                f" on WebSocket at {self.host}"
            )
            raise OwRadarConnectionError(msg) from exception

    async def stats_connect(self) -> None:
        """Connect to the WebSocket of device.

        Raises
        ------
            OwRadarError: The configured device, does not support WebSocket
                communications.
            OwRadarConnectionError: Error occurred while communicating with
                the device via the WebSocket.

        """
        if self.stats_connected:
            return
        url = URL.build(scheme="ws", host=self.host, port=80, path="/ws/stats")
        try:
            self._stats_client = await self.session.ws_connect(url=url, heartbeat=30)
        except (
                aiohttp.WSServerHandshakeError,
                aiohttp.ClientConnectionError,
                socket.gaierror,
        ) as exception:
            msg = (
                "Error occurred while communicating with device"
                f" on WebSocket at {self.host}"
            )
            raise OwRadarConnectionError(msg) from exception

    async def snap_connect(self) -> None:
        """Connect to the WebSocket of device.

        Raises
        ------
            OwRadarError: The configured device, does not support WebSocket
                communications.
            OwRadarConnectionError: Error occurred while communicating with
                the device via the WebSocket.

        """
        if self.snap_connected:
            return
        url = URL.build(scheme="ws", host=self.host, port=80, path="/ws/snap")
        try:
            self._snap_client = await self.session.ws_connect(url=url, heartbeat=30)
        except (
                aiohttp.WSServerHandshakeError,
                aiohttp.ClientConnectionError,
                socket.gaierror,
        ) as exception:
            msg = (
                "Error occurred while communicating with device"
                f" on WebSocket at {self.host}"
            )
            raise OwRadarConnectionError(msg) from exception

    async def event_connect(self) -> None:
        """Connect to the WebSocket of device.

        Raises
        ------
            OwRadarError: The configured device, does not support WebSocket
                communications.
            OwRadarConnectionError: Error occurred while communicating with
                the device via the WebSocket.

        """
        if self.event_connected:
            return
        url = URL.build(scheme="ws", host=self.host, port=80, path="/ws/event")
        try:
            self._state_client = await self.session.ws_connect(url=url, heartbeat=30)
        except (
                aiohttp.WSServerHandshakeError,
                aiohttp.ClientConnectionError,
                socket.gaierror,
        ) as exception:
            msg = (
                "Error occurred while communicating with device"
                f" on WebSocket at {self.host}"
            )
            raise OwRadarConnectionError(msg) from exception

    async def state_listen(self, callback: Callable[[Any], None]) -> None:
        """Listen for events on the WebSocket.

        Args:
        ----
            callback: Method to call when a state update is received from
                the device.

        Raises:
        ------
            OwRadarError: Not connected to a WebSocket.
            OwRadarConnectionError: An connection error occurred while connected
                to the device.
            OwRadarConnectionClosedError: The WebSocket connection to the remote device
                has been closed.

        """
        if not self._state_client or not self.state_connected or not self._device:
            msg = "Not connected to a WebSocket"
            raise OwRadarError(msg)

        while not self._state_client.closed:
            message = await self._state_client.receive()

            if message.type == aiohttp.WSMsgType.ERROR:
                raise OwRadarConnectionError(self._state_client.exception())

            if message.type == aiohttp.WSMsgType.TEXT:
                state_data = self._state_data.update_from_dict(message.json())
                callback(state_data)

            if message.type in (
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSING,
            ):
                msg = f"Connection to the WebSocket on {self.host} has been closed"
                raise OwRadarConnectionClosedError(msg)

    async def stats_listen(self, callback: Callable[[Any], None]) -> None:
        """Listen for events on the WebSocket.

        Args:
        ----
            callback: Method to call when a state update is received from
                the device.

        Raises:
        ------
            OwRadarError: Not connected to a WebSocket.
            OwRadarConnectionError: An connection error occurred while connected
                to the device.
            OwRadarConnectionClosedError: The WebSocket connection to the remote device
                has been closed.

        """
        if not self._stats_client or not self.stats_connected or not self._device:
            msg = "Not connected to a WebSocket"
            raise OwRadarError(msg)

        while not self._stats_client.closed:
            message = await self._stats_client.receive()

            if message.type == aiohttp.WSMsgType.ERROR:
                raise OwRadarConnectionError(self._stats_client.exception())

            if message.type == aiohttp.WSMsgType.TEXT:
                stats_data = self._stats_data.update_from_dict(message.json())
                callback(stats_data)

            if message.type in (
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSING,
            ):
                msg = f"Connection to the WebSocket on {self.host} has been closed"
                raise OwRadarConnectionClosedError(msg)

    async def snap_listen(self, callback: Callable[[Any], None]) -> None:
        """Listen for events on the WebSocket.

        Args:
        ----
            callback: Method to call when a state update is received from
                the device.

        Raises:
        ------
            OwRadarError: Not connected to a WebSocket.
            OwRadarConnectionError: An connection error occurred while connected
                to the device.
            OwRadarConnectionClosedError: The WebSocket connection to the remote device
                has been closed.

        """
        if not self._stats_client or not self.stats_connected or not self._device:
            msg = "Not connected to a WebSocket"
            raise OwRadarError(msg)

        while not self._stats_client.closed:
            message = await self._stats_client.receive()

            if message.type == aiohttp.WSMsgType.ERROR:
                raise OwRadarConnectionError(self._stats_client.exception())

            if message.type == aiohttp.WSMsgType.TEXT:
                snap_data = self._snap_data.update_from_dict(message.json())
                callback(snap_data)

            if message.type in (
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSING,
            ):
                msg = f"Connection to the WebSocket on {self.host} has been closed"
                raise OwRadarConnectionClosedError(msg)

    async def event_listen(self, callback: Callable[[Any], None]) -> None:
        """Listen for events on the WebSocket.

        Args:
        ----
            callback: Method to call when a state update is received from
                the device.

        Raises:
        ------
            OwRadarError: Not connected to a WebSocket.
            OwRadarConnectionError: An connection error occurred while connected
                to the device.
            OwRadarConnectionClosedError: The WebSocket connection to the remote device
                has been closed.

        """
        if not self._stats_client or not self.stats_connected or not self._device:
            msg = "Not connected to a WebSocket"
            raise OwRadarError(msg)

        while not self._stats_client.closed:
            message = await self._stats_client.receive()

            if message.type == aiohttp.WSMsgType.ERROR:
                raise OwRadarConnectionError(self._stats_client.exception())

            if message.type == aiohttp.WSMsgType.TEXT:
                event_data = self._event_data.update_from_dict(message.json())
                callback(event_data)

            if message.type in (
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSING,
            ):
                msg = f"Connection to the WebSocket on {self.host} has been closed"
                raise OwRadarConnectionClosedError(msg)

    async def state_disconnect(self) -> None:
        """Disconnect from the WebSocket of device."""
        if not self._state_client or not self.state_connected:
            return

        await self._state_client.close()

    async def stats_disconnect(self) -> None:
        """Disconnect from the WebSocket of device."""
        if not self._stats_client or not self.stats_connected:
            return

        await self._stats_client.close()

    async def snap_disconnect(self) -> None:
        """Disconnect from the WebSocket of device."""
        if not self._snap_client or not self.snap_connected:
            return

        await self._snap_client.close()

    async def event_disconnect(self) -> None:
        """Disconnect from the WebSocket of device."""
        if not self._event_client or not self.event_connected:
            return

        await self._event_client.close()

    @backoff.on_exception(
        backoff.expo, OwRadarConnectionError, max_tries=3, logger=None
    )
    async def request(
            self,
            uri: str = "",
            method: str = "GET",
            data: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to device.

        A generic method for sending/handling HTTP requests done against
        the device.

        Args:
        ----
            uri: Request URI, for example `/api/device`.
            method: HTTP method to use for the request.E.g., "GET" or "POST".
            data: Dictionary of data to send to the device.

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from the
            device.

        Raises:
        ------
            OwRadarConnectionError: An error occurred while communication with
                the device.
            OwRadarConnectionTimeoutError: A timeout occurred while communicating
                with the device.
            OwRadarError: Received an unexpected response from the device.

        """
        url = URL.build(scheme="http", host=self.host, port=80, path=uri)

        headers = {
            "Accept": "application/json, text/plain, */*",
        }

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    json=data,
                    headers=headers,
                )

            content_type = response.headers.get("Content-Type", "")
            if response.status // 100 in [4, 5]:
                contents = await response.read()
                response.close()

                if content_type == "application/json":
                    raise OwRadarError(  # noqa: TRY301
                        response.status,
                        json.loads(contents.decode("utf8")),
                    )
                raise OwRadarError(  # noqa: TRY301
                    response.status,
                    {"message": contents.decode("utf8")},
                )

            if "application/json" in content_type:
                response_data = await response.json()
            else:
                response_data = await response.text()

        except asyncio.TimeoutError as exception:
            msg = f"Timeout occurred while connecting to device at {self.host}"
            raise OwRadarConnectionTimeoutError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = (
                f"Error occurred while communicating with device at {self.host}"
            )
            raise OwRadarConnectionError(msg) from exception

        return response_data

    @backoff.on_exception(
        backoff.expo,
        OwRadarEmptyResponseError,
        max_tries=3,
        logger=None,
    )
    async def update(self, *, full_update: bool = False) -> Any:  # noqa: PLR0912
        """Get all information about the device in a single call.

        This method updates all information available with a single API
        call.

        Args:
        ----
            full_update: Force a full update from the device.

        Returns:
        -------
            device data.

        Raises:
        ------
            OwRadarEmptyResponseError: The device returned an empty response.

        """
        if self._device is None or full_update:
            if not (data := await self.request("/api/device")):
                msg = (
                    f"device at {self.host} returned an empty API response on full update",
                )
                raise OwRadarEmptyResponseError(msg)
            info = data.get("info")
            if info is None:
                msg = (
                    f"device at {self.host} returned an invalid response missing field `info` on full update",
                )
                raise OwRadarEmptyResponseError(msg)
            radar_model = data.get("radar_model")
            if radar_model is None:
                msg = (
                    f"device at {self.host} returned an invalid response missing field `info.radar_model` on full update",
                )
                raise OwRadarEmptyResponseError(msg)
            self._device = {}
            if radar_model == "r60abd1":
                self._device = R60abd1Device()
            self._device.update_from_dict(data)
            return self._device

        return self._device

    async def setting(
            self,
            *,
            data: dict[str, Any]
    ) -> Any:
        """Set the setting of the device.

        Args:
        ----
            data: setting data.
        """
        setting = {}
        if self._device.get("info").get("radar_model") == "r60abd1":
            setting = R60abd1Setting()
            setting.update_from_dict(data)
        setting = {k: int(v) for k, v in setting.items() if v is not None}
        message_data = await self.request(
            "/api/device", method="POST", data={"setting": setting}
        )
        return self._device.update_from_dict(message_data)

    @property
    def connected(self) -> bool:
        """Return if we are connect to the WebSocket of device.

        Returns
        -------
            True if we are connected to the WebSocket of device,
            False otherwise.

        """
        return ((self._state_client is not None and not self._state_client.closed)
                and (self._stats_client is not None and not self._stats_client.closed)
                and (self._snap_client is not None and not self._snap_client.closed)
                and (self._event_client is not None and not self._event_client.closed))

    async def listen(self, callback: Callable[[Any], None]) -> None:
        """Listen for events."""
        await asyncio.gather(
            self.state_listen(callback),
            self.stats_listen(callback),
            self.snap_listen(callback),
            self.event_listen(callback)
        )

    async def open(self) -> None:
        """Open client (WebSocket) session."""
        if not self._device:
            await self.update()
        if not self.session or not self._device:
            msg = "The device at {self.host} does not support WebSockets"
            raise OwRadarError(msg)
        await self.state_connect()
        await self.stats_connect()
        await self.snap_connect()
        await self.event_connect()

    async def close(self) -> None:
        """Close opened client (WebSocket) session."""
        await self.state_disconnect()
        await self.stats_disconnect()
        await self.snap_disconnect()
        await self.event_disconnect()
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Client:
        """Async enter.

        Returns
        -------
            The object.

        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
