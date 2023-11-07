"""Asynchronous Python client for OWRCare."""
from __future__ import annotations

import asyncio
import json
import socket
from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout
import backoff
from awesomeversion import AwesomeVersion, AwesomeVersionException
from cachetools import TTLCache
from yarl import URL

from .exceptions import (
    OWRCareConnectionClosedError,
    OWRCareConnectionError,
    OWRCareConnectionTimeoutError,
    OWRCareEmptyResponseError,
    OWRCareError,
    OWRCareUpgradeError,
)
from .models import Report

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


VERSION_CACHE: TTLCache[str, str | None] = TTLCache(maxsize=16, ttl=7200)


@dataclass
class OWRCare:
    """Main class for handling connections with OWRCare."""

    host: str
    request_timeout: float = 8.0
    session: aiohttp.client.ClientSession | None = None

    _client: aiohttp.ClientWebSocketResponse | None = None
    _close_session: bool = False

    @property
    def connected(self) -> bool:
        """Return if we are connect to the WebSocket of a OWRCare device.

        Returns
        -------
            True if we are connected to the WebSocket of a OWRCare device,
            False otherwise.
        """
        return self._client is not None and not self._client.closed

    async def connect(self) -> None:
        """Connect to the WebSocket of a OWRCare device.

        Raises
        ------
            OWRCareError: The configured OWRCare device, does not support WebSocket
                communications.
            OWRCareConnectionError: Error occurred while communicating with
                the OWRCare device via the WebSocket.
        """
        if self.connected:
            return

        if not self.session is None:
            msg = "The OWRCare device at {self.host} does not support WebSockets"
            raise OWRCareError(msg)

        url = URL.build(scheme="ws", host=self.host, port=80, path="/ws")

        try:
            self._client = await self.session.ws_connect(url=url, heartbeat=30)
        except (
            aiohttp.WSServerHandshakeError,
            aiohttp.ClientConnectionError,
            socket.gaierror,
        ) as exception:
            msg = (
                "Error occurred while communicating with OWRCare device"
                f" on WebSocket at {self.host}"
            )
            raise OWRCareConnectionError(msg) from exception

    async def listen(self, callback: Callable[[Report], None]) -> None:
        """Listen for events on the OWRCare WebSocket.

        Args:
        ----
            callback: Method to call when a state update is received from
                the OWRCare device.

        Raises:
        ------
            OWRCareError: Not connected to a WebSocket.
            OWRCareConnectionError: An connection error occurred while connected
                to the OWRCare device.
            OWRCareConnectionClosedError: The WebSocket connection to the remote OWRCare
                has been closed.
        """
        if not self._client or not self.connected:
            msg = "Not connected to a OWRCare WebSocket"
            raise OWRCareError(msg)

        while not self._client.closed:
            message = await self._client.receive()

            if message.type == aiohttp.WSMsgType.ERROR:
                raise OWRCareConnectionError(self._client.exception())

            if message.type == aiohttp.WSMsgType.TEXT:
                message_data = message.json()
                callback(message_data)

            if message.type in (
                aiohttp.WSMsgType.CLOSE,
                aiohttp.WSMsgType.CLOSED,
                aiohttp.WSMsgType.CLOSING,
            ):
                msg = f"Connection to the OWRCare WebSocket on {self.host} has been closed"
                raise OWRCareConnectionClosedError(msg)

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket of a OWRCare device."""
        if not self._client or not self.connected:
            return

        await self._client.close()

    async def close(self) -> None:
        """Close open client (WebSocket) session."""
        await self.disconnect()
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> OWRCare:
        """Async enter.

        Returns
        -------
            The OWRCare object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.
        """
        await self.close()
