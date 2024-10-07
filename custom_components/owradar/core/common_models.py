"""Models for OwRadar."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


@dataclass
class OwRadarCommonEvent:
    """
    Object holding State Information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A State object.

    """

    timestamp: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarCommonEvent:
        """
        Update Return State object form OwRadar API response.

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
class OwRadarCommonSnap:
    """
    Object holding State Information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A State object.

    """

    timestamp: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarCommonSnap:
        """
        Update Return State object form OwRadar API response.

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
class OwRadarCommonStats:
    """
    Object holding State Information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A State object.

    """

    timestamp: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarCommonStats:
        """
        Update Return State object form OwRadar API response.

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
class OwRadarCommonStateMotionAngle:
    """Object holding Motion Angle state in OwRadar."""

    pitch: float = 0
    roll: float = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarCommonStateMotionAngle:
        """
        Return Motion Angle object form OwRadar API response.

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
class OwRadarCommonStateMotion:
    """Object holding motion state in OwRadar."""

    angle: OwRadarCommonStateMotionAngle = field(
        default_factory=OwRadarCommonStateMotionAngle
    )

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarCommonStateMotion:
        """
        Update and Return Motion object form OwRadar API response.

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
class OwRadarCommonState:
    """
    Object holding State Information from device.

    Args:
    ----
        data: The data from the device API.

    Returns:
    -------
        A State object.

    """

    timestamp: int = 0
    motion: OwRadarCommonStateMotion = field(default_factory=OwRadarCommonStateMotion)

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarCommonState:
        """
        Update Return State object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An State object.

        """
        self.timestamp = data.get("timestamp", self.timestamp)
        self.motion = self.motion.update_from_dict(
            data.get("motion", self.motion.__dict__)
        )

        return self


@dataclass
class OwRadarCommonInfo:
    """Object holding device information from OwRadar."""

    radar_model: str = ""
    radar_version: str = ""
    mac_addr: str = ""
    name: str = ""
    ip: str = ""
    free_heap: int = 0
    version: str = ""
    architecture: str = ""
    brand: str = ""
    product: str = ""
    board: str = ""

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarCommonInfo:
        """
        Update and Return Device information object from OwRadar API response.

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


class OwRadarCommonSettingSwitch(IntEnum):
    """Enumeration representing switch state from OwRadar."""

    OFF = 0
    ON = 1


@dataclass
class OwRadarCommonSetting:
    """
    Object holding Common Setting information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A Setting object.

    """

    broker: str = ""
    gatt_state: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    mqtt_state: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    websocket_state: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    gatt_stats: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    mqtt_stats: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    websocket_stats: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    gatt_event: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    mqtt_event: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    websocket_event: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    gatt_snap: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    mqtt_snap: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    websocket_snap: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    indicate: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    interval: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarCommonSetting:
        """
        Update and Return Setting object form OwRadar API response.

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
class OwRadarCommonDevice:
    """Object holding device information from OwRadar."""

    info: OwRadarCommonInfo = field(default_factory=OwRadarCommonInfo)

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarCommonDevice:
        """
        Update and Return Device information object from OwRadar API response.

        Args:
        ----
            data: The data from the OwRadar device API.

        Returns:
        -------
            A Device information object.

        """
        self.info.update_from_dict(data.get("info", self.info.__dict__))

        return self
