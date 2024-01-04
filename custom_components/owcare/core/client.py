"""Asynchronous Python client for owcare."""
from __future__ import annotations

import asyncio
import json
import socket
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout
import backoff
from cachetools import TTLCache
from yarl import URL

from .exceptions import (
    OwcareConnectionClosedError,
    OwcareConnectionError,
    OwcareConnectionTimeoutError,
    OwcareEmptyResponseError,
    OwcareError,
)
from .models import Device

if TYPE_CHECKING:
    from collections.abc import Callable


VERSION_CACHE: TTLCache[str, str | None] = TTLCache(maxsize=16, ttl=7200)


@dataclass
class Client:
    """Main class for handling connections with owcare."""

    host: str
    request_timeout: float = 8.0
    session: aiohttp.client.ClientSession | None = None

    _client: aiohttp.ClientWebSocketResponse | None = None
    _close_session: bool = False
    _device: Device | None = None

    @property
    def connected(self) -> bool:
        """Return if we are connect to the WebSocket of a owcare device.

        Returns
        -------
            True if we are connected to the WebSocket of a owcare device,
            False otherwise.
        """
        return self._client is not None and not self._client.closed

    async def connect(self) -> None:
        """Connect to the WebSocket of a owcare device.

        Raises
        ------
            OwcareError: The configured owcare device, does not support WebSocket
                communications.
            OwcareConnectionError: Error occurred while communicating with
                the owcare device via the WebSocket.
        """
        if self.connected:
            return

        if not self._device:
            await self.update()

        if not self.session or not self._device:
            msg = "The owcare device at {self.host} does not support WebSockets"
            raise OwcareError(msg)

        url = URL.build(scheme="ws", host=self.host, port=80, path="/ws")

        try:
            self._client = await self.session.ws_connect(url=url, heartbeat=30)
        except (
            aiohttp.WSServerHandshakeError,
            aiohttp.ClientConnectionError,
            socket.gaierror,
        ) as exception:
            msg = (
                "Error occurred while communicating with owcare device"
                f" on WebSocket at {self.host}"
            )
            raise OwcareConnectionError(msg) from exception

    async def listen(self, callback: Callable[[Device], None]) -> None:
        """Listen for events on the owcare WebSocket.

        Args:
        ----
            callback: Method to call when a state update is received from
                the owcare device.

        Raises:
        ------
            OwcareError: Not connected to a WebSocket.
            OwcareConnectionError: An connection error occurred while connected
                to the owcare device.
            OwcareConnectionClosedError: The WebSocket connection to the remote owcare
                has been closed.
        """
        if not self._client or not self.connected or not self._device:
            msg = "Not connected to a owcare WebSocket"
            raise OwcareError(msg)

        while not self._client.closed:
            message = await self._client.receive()

            if message.type == aiohttp.WSMsgType.ERROR:
                raise OwcareConnectionError(self._client.exception())

            if message.type == aiohttp.WSMsgType.TEXT:
                message_data = message.json()
                # construct states list to update device
                msg = {"state": message_data}
                device = self._device.update_from_dict(msg)
                callback(device)

            if message.type in (
                aiohttp.WSMsgType.CLOSE,
                aiohttp.WSMsgType.CLOSED,
                aiohttp.WSMsgType.CLOSING,
            ):
                msg = f"Connection to the owcare WebSocket on {self.host} has been closed"
                raise OwcareConnectionClosedError(msg)

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket of a owcare device."""
        if not self._client or not self.connected:
            return

        await self._client.close()

    @backoff.on_exception(
        backoff.expo, OwcareConnectionError, max_tries=3, logger=None
    )
    async def request(
        self,
        uri: str = "",
        method: str = "GET",
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to a owcare device.

        A generic method for sending/handling HTTP requests done gainst
        the owcare device.

        Args:
        ----
            uri: Request URI, for example `/api/device`.
            method: HTTP method to use for the request.E.g., "GET" or "POST".
            data: Dictionary of data to send to the owcare device.

        Returns:
        -------
            A Python dictionary (JSON decoded) with the response from the
            owcare device.

        Raises:
        ------
            OwcareConnectionError: An error occurred while communication with
                the owcare device.
            OwcareConnectionTimeoutError: A timeout occurred while communicating
                with the owcare device.
            OwcareError: Received an unexpected response from the owcare device.
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
                    raise OwcareError(  # noqa: TRY301
                        response.status,
                        json.loads(contents.decode("utf8")),
                    )
                raise OwcareError(  # noqa: TRY301
                    response.status,
                    {"message": contents.decode("utf8")},
                )

            if "application/json" in content_type:
                response_data = await response.json()
            else:
                response_data = await response.text()

        except asyncio.TimeoutError as exception:
            msg = f"Timeout occurred while connecting to owcare device at {self.host}"
            raise OwcareConnectionTimeoutError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = (
                f"Error occurred while communicating with owcare device at {self.host}"
            )
            raise OwcareConnectionError(msg) from exception

        return response_data

    @backoff.on_exception(
        backoff.expo,
        OwcareEmptyResponseError,
        max_tries=3,
        logger=None,
    )
    async def update(self, *, full_update: bool = False) -> Device:  # noqa: PLR0912
        """Get all information about the device in a single call.

        This method updates all owcare information available with a single API
        call.

        Args:
        ----
            full_update: Force a full update from the owcare Device.

        Returns:
        -------
            owcare Device data.

        Raises:
        ------
            OwcareEmptyResponseError: The owcare device returned an empty response.
        """
        if self._device is None or full_update:
            if not (data := await self.request("/api/device")):
                msg = (
                    f"owcare device at {self.host} returned an empty API"
                    " response on full update",
                )
                raise OwcareEmptyResponseError(msg)
            self._device = Device.from_dict(data)
            return self._device

        return self._device

    async def setting(
        self,
        *,
        realtime_ws: int | None = None,
        body: int | None = None,
        heart: int | None = None,
        breath: int | None = None,
        sleep: int | None = None,
        mode: int | None = None,
        nobody: int | None = None,
        nobody_duration: int | None = None,
        struggle: int | None = None,
        stop_duration: int | None = None,
    ) -> Device:
        """Set the setting of the owcare device.

        Args:
        ----
            realtime_ws: Websocket publishing mode.
            body: Body monioring switch.
            heart: Heart monioring switch.
            breath: Breath monioring switch.
            sleep: Sleep monioring switch.
            mode: Mode monioring switch.
            nobody: Nobody monioring switch.
            nobody_duration: Nobody duration setting.
            struggle: Struggle monioring switch.
            stop_duration: Sleep stop duration setting.
        """
        setting = {
            "realtime_ws": realtime_ws,
            "body": body,
            "heart": heart,
            "breath": breath,
            "sleep": sleep,
            "mode": mode,
            "nobody": nobody,
            "nobody_duration": nobody_duration,
            "struggle": struggle,
            "stop_duration": stop_duration,
        }
        setting = {k: int(v) for k, v in setting.items() if v is not None}
        message_data = await self.request(
            "/api/device", method="POST", data={"setting": setting}
        )
        return self._device.update_from_dict(message_data)

    async def close(self) -> None:
        """Close open client (WebSocket) session."""
        await self.disconnect()
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Client:
        """Async enter.

        Returns
        -------
            The owcare object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.
        """
        await self.close()
