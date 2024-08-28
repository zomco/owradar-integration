"""Models for OwRadar."""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any


@dataclass
class CommonEvent:
    """Object holding State Information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A State object.

    """

    timestamp: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> CommonEvent:
        """Update Return State object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An State object.

        """
        self.timestamp = data.get("timestamp", self.timestamp)

        return self


@dataclass
class CommonSnap:
    """Object holding State Information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A State object.

    """

    timestamp: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> CommonSnap:
        """Update Return State object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An State object.

        """
        self.timestamp = data.get("timestamp", self.timestamp)

        return self


@dataclass
class CommonStats:
    """Object holding State Information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A State object.

    """

    timestamp: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> CommonStats:
        """Update Return State object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An State object.

        """
        self.timestamp = data.get("timestamp", self.timestamp)

        return self


@dataclass
class CommonStateMotionAngle:
    """Object holding Motion Angle state in OwRadar."""

    pitch: float = 0
    roll: float = 0

    def update_from_dict(self, data: dict[str, Any]) -> CommonStateMotionAngle:
        """Return Motion Angle object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Motion Angle object.

        """
        self.pitch = data.get("pitch", self.pitch)
        self.roll = data.get("roll", self.roll)

        return self


@dataclass
class CommonStateMotion:
    """Object holding motion state in OwRadar."""

    angle: CommonStateMotionAngle = CommonStateMotionAngle()

    def update_from_dict(self, data: dict[str, Any]) -> CommonStateMotion:
        """Update and Return Motion object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Motion object.

        """
        self.angle = self.angle.update_from_dict(data.get("angle", self.angle.__dict__))

        return self


@dataclass
class CommonState:
    """Object holding State Information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A State object.

    """

    timestamp: int = 0
    motion: CommonStateMotion = CommonStateMotion()

    def update_from_dict(self, data: dict[str, Any]) -> CommonState:
        """Update Return State object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An State object.

        """
        self.timestamp = data.get("timestamp", self.timestamp)
        self.motion = self.motion.update_from_dict(data.get("motion", self.motion.__dict__))

        return self


@dataclass
class CommonInfo:
    """Object holding device information from OwRadar."""

    radar_model: str = ""
    radar_version: str = ""
    mac_addr: str = ""
    name: str = ""
    ip: str = ""
    free_heap: int = ""
    version: str = ""
    architecture: str = ""
    brand: str = ""
    product: str = ""
    board: str = ""

    def update_from_dict(self, data: dict[str, Any]) -> CommonInfo:
        """Update and Return Device information object from OwRadar API response.

        Args:
        ----
            data: The data from the OwRadar device API.

        Returns:
        -------
            A Device information object.

        """
        self.radar_model = data.get("radar_model", self.radar_model)
        self.radar_version = data.get("radar_version", self.radar_version)
        self.mac_addr = data.get("mac", self.mac_addr)
        self.name = data.get("name", self.name)
        self.ip = data.get("ip", self.ip)
        self.free_heap = data.get("free_heap", self.free_heap)
        self.version = data.get("version", self.version)
        self.architecture = data.get("architecture", self.architecture)
        self.brand = data.get("brand", self.brand)
        self.product = data.get("product", self.product)
        self.board = data.get("board", self.board)

        return self


class CommonSettingSwitch(IntEnum):
    """Enumeration representing switch state from OwRadar."""

    OFF = 0
    ON = 1


@dataclass
class CommonSetting:
    """Object holding Common Setting information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A Setting object.

    """

    broker: str = ""
    gatt_state: CommonSettingSwitch = CommonSettingSwitch.OFF
    mqtt_state: CommonSettingSwitch = CommonSettingSwitch.OFF
    websocket_state: CommonSettingSwitch = CommonSettingSwitch.OFF
    gatt_stats: CommonSettingSwitch = CommonSettingSwitch.OFF
    mqtt_stats: CommonSettingSwitch = CommonSettingSwitch.OFF
    websocket_stats: CommonSettingSwitch = CommonSettingSwitch.OFF
    gatt_event: CommonSettingSwitch = CommonSettingSwitch.OFF
    mqtt_event: CommonSettingSwitch = CommonSettingSwitch.OFF
    websocket_event: CommonSettingSwitch = CommonSettingSwitch.OFF
    gatt_snap: CommonSettingSwitch = CommonSettingSwitch.OFF
    mqtt_snap: CommonSettingSwitch = CommonSettingSwitch.OFF
    websocket_snap: CommonSettingSwitch = CommonSettingSwitch.OFF
    indicate: CommonSettingSwitch = CommonSettingSwitch.OFF
    interval: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> CommonSetting:
        """Update and Return Setting object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Setting object.

        """
        self.broker = data.get("broker", self.broker)
        self.gatt_state = data.get("gatt_state", self.gatt_state)
        self.mqtt_state = data.get("mqtt_state", self.mqtt_state)
        self.websocket_state = data.get("websocket_state", self.websocket_state)
        self.gatt_stats = data.get("gatt_stats", self.gatt_stats)
        self.mqtt_stats = data.get("mqtt_stats", self.mqtt_stats)
        self.websocket_stats = data.get("websocket_stats", self.websocket_stats)
        self.gatt_event = data.get("gatt_event", self.gatt_event)
        self.mqtt_event = data.get("mqtt_event", self.mqtt_event)
        self.websocket_event = data.get("websocket_event", self.websocket_event)
        self.gatt_snap = data.get("gatt_snap", self.gatt_snap)
        self.mqtt_snap = data.get("mqtt_snap", self.mqtt_snap)
        self.websocket_snap = data.get("websocket_snap", self.websocket_snap)
        self.indicate = data.get("indicate", self.indicate)
        self.interval = data.get("interval", self.interval)

        return self


@dataclass
class CommonDevice:
    """Object holding device information from OwRadar."""

    info: CommonInfo = CommonInfo()

    def update_from_dict(self, data: dict[str, Any]) -> CommonDevice:
        """Update and Return Device information object from OwRadar API response.

        Args:
        ----
            data: The data from the OwRadar device API.

        Returns:
        -------
            A Device information object.

        """
        self.info.update_from_dict(data.get("info", self.info.__dict__))

        return self
