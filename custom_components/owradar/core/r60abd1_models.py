"""Models for OwRadar."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

from .common_models import (
    OwRadarCommonDevice,
    OwRadarCommonSetting,
    OwRadarCommonSettingSwitch,
    OwRadarCommonState,
)


@dataclass
class OwRadarR60abd1Event:
    """Object holding body location state in OwRadar."""

    status: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1Event:
        """
        Return Body Location object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Body Location object.

        """
        self.status = data.get("status", self.status)
        return self


@dataclass
class OwRadarR60abd1Snap:
    """Object holding body location state in OwRadar."""

    body_range: int = 0
    body_presence: int = 0
    body_energy: int = 0
    body_movement: int = 0
    body_distance: int = 0
    body_location_x: int = 0
    body_location_y: int = 0
    heart_rate: int = 0
    breath_rate: int = 0
    sleep_away: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1Snap:
        """
        Return Body Location object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Body Location object.

        """
        self.body_range = data.get("body_range", self.body_range)
        self.body_presence = data.get("body_presence", self.body_presence)
        self.body_energy = data.get("body_energy", self.body_energy)
        self.body_movement = data.get("body_movement", self.body_movement)
        self.body_distance = data.get("body_distance", self.body_distance)
        self.body_location_x = data.get("body_location_x", self.body_location_x)
        self.body_location_y = data.get("body_location_y", self.body_location_y)
        self.heart_rate = data.get("heart_rate", self.heart_rate)
        self.breath_rate = data.get("breath_rate", self.breath_rate)
        self.sleep_away = data.get("sleep_away", self.sleep_away)
        return self


@dataclass
class OwRadarR60abd1Stats:
    """Object holding body location state in OwRadar."""

    status: int = 0
    breath: int = 0
    heart: int = 0
    turn: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1Stats:
        """
        Return Body Location object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Body Location object.

        """
        self.status = data.get("status", self.status)
        self.breath = data.get("breath", self.breath)
        self.heart = data.get("heart", self.heart)
        self.turn = data.get("turn", self.turn)
        return self


class OwRadarR60abd1StateBodyRange(IntEnum):
    """Enumeration representing body range from OwRadar."""

    OUT = 0
    IN = 1


class OwRadarR60abd1StateBodyPresence(IntEnum):
    """Enumeration representing body presence from OwRadar."""

    NOBODY = 0
    SOMEBODY = 1


class OwRadarR60abd1StateBodyMovement(IntEnum):
    """Enumeration representing body movement from OwRadar."""

    NONE = 0
    STATIC = 1
    ACTIVE = 2


@dataclass
class OwRadarR60abd1StateBodyLocation:
    """Object holding body location state in OwRadar."""

    x: int = 0
    y: int = 0
    z: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1StateBodyLocation:
        """
        Return Body Location object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Body Location object.

        """
        self.x = data.get("x", self.x)
        self.y = data.get("y", self.y)
        self.z = data.get("z", self.z)
        return self


@dataclass
class OwRadarR60abd1StateBody:
    """Object holding body state in OwRadar."""

    range: OwRadarR60abd1StateBodyRange = OwRadarR60abd1StateBodyRange.OUT
    presence: OwRadarR60abd1StateBodyPresence = OwRadarR60abd1StateBodyPresence.NOBODY
    energy: int = 0
    movement: OwRadarR60abd1StateBodyMovement = OwRadarR60abd1StateBodyMovement.NONE
    distance: int = 0
    location: OwRadarR60abd1StateBodyLocation = field(
        default_factory=OwRadarR60abd1StateBodyLocation
    )

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1StateBody:
        """
        Update and Return Body object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Body object.

        """
        self.range = OwRadarR60abd1StateBodyRange(data.get("range", self.range.value))
        self.presence = OwRadarR60abd1StateBodyPresence(
            data.get("presence", self.presence.value)
        )
        self.energy = data.get("energy", self.energy)
        self.movement = OwRadarR60abd1StateBodyMovement(
            data.get("movement", self.movement.value)
        )
        self.distance = data.get("distance", self.distance)
        self.location = self.location.update_from_dict(
            data.get("location", self.location.__dict__)
        )

        return self


@dataclass
class OwRadarR60abd1StateWaves:
    """Object holding wave state in OwRadar."""

    w0: int = 0
    w1: int = 0
    w2: int = 0
    w3: int = 0
    w4: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1StateWaves:
        """
        Update and Return Heart object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Heart object.

        """
        self.w0 = data.get("w0", self.w0)
        self.w1 = data.get("w1", self.w1)
        self.w2 = data.get("w2", self.w2)
        self.w3 = data.get("w3", self.w3)
        self.w4 = data.get("w4", self.w4)

        return self


@dataclass
class OwRadarR60abd1StateHeart:
    """Object holding heart state in OwRadar."""

    rate: int = 0
    waves: OwRadarR60abd1StateWaves = field(default_factory=OwRadarR60abd1StateWaves)

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1StateHeart:
        """
        Update and Return Heart object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Heart object.

        """
        self.rate = data.get("rate", self.rate)
        self.waves = self.waves.update_from_dict(data.get("waves", self.waves.__dict__))

        return self


class OwRadarR60abd1StateBreathInfo(IntEnum):
    """Enumeration representing breath info from OwRadar."""

    UNSET = 0
    NORMAL = 1
    TOO_HIGH = 2
    TOO_LOW = 3
    NONE = 4


@dataclass
class OwRadarR60abd1StateBreath:
    """Object holding breath state in OwRadar."""

    info: OwRadarR60abd1StateBreathInfo = OwRadarR60abd1StateBreathInfo.UNSET
    rate: int = 0
    waves: OwRadarR60abd1StateWaves = field(default_factory=OwRadarR60abd1StateWaves)

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1StateBreath:
        """
        Update and Return Breath object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Breath object.

        """
        self.info = OwRadarR60abd1StateBreathInfo(data.get("info", self.info))
        self.rate = data.get("rate", self.rate)
        self.waves = self.waves.update_from_dict(data.get("waves", self.waves.__dict__))

        return self


class OwRadarR60abd1StateSleepAway(IntEnum):
    """Enumeration representing sleep away from OwRadar."""

    OUT = 0
    IN = 1
    ACTIVE = 2


class OwRadarR60abd1StateSleepStatus(IntEnum):
    """Enumeration representing sleep status from OwRadar."""

    DEEP = 0
    LIGHT = 1
    AWAKE = 2
    NONE = 3


class OwRadarR60abd1StateSleepException(IntEnum):
    """Enumeration representing sleep exception from OwRadar."""

    LESS_4HOUR = 0
    MORE_12HOUR = 1
    LONG_TIME = 2
    NONE = 3


class OwRadarR60abd1StateSleepRating(IntEnum):
    """Enumeration representing sleep rating from OwRadar."""

    NONE = 0
    GOOD = 1
    MEDIAN = 2
    BAD = 3


class OwRadarR60abd1StateSleepStruggle(IntEnum):
    """Enumeration representing sleep struggle from OwRadar."""

    NONE = 0
    NORMAL = 1
    ABNORMAL = 2


class OwRadarR60abd1StateSleepNobody(IntEnum):
    """Enumeration representing sleep nobody from OwRadar."""

    NONE = 0
    NORMAL = 1
    ABNORMAL = 2


@dataclass
class OwRadarR60abd1StateSleepOverview:
    """
    Object holding sleep overview state in OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A sleep overview object.

    """

    presence: OwRadarR60abd1StateBodyPresence = OwRadarR60abd1StateBodyPresence.NOBODY
    status: OwRadarR60abd1StateSleepStatus = OwRadarR60abd1StateSleepStatus.NONE
    breath: int = 0
    heart: int = 0
    turn: int = 0
    leratio: int = 0
    seratio: int = 0
    pause: int = 0

    def update_from_dict(
        self, data: dict[str, Any]
    ) -> OwRadarR60abd1StateSleepOverview:
        """
        Return SleepOverview object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An SleepOverview object.

        """
        self.presence = OwRadarR60abd1StateBodyPresence(
            data.get("presence", self.presence)
        )
        self.status = OwRadarR60abd1StateSleepStatus(data.get("status", self.status))
        self.heart = data.get("heart", self.heart)
        self.breath = data.get("breath", self.breath)
        self.turn = data.get("turn", self.turn)
        self.leratio = data.get("leratio", self.leratio)
        self.seratio = data.get("seratio", self.seratio)
        self.pause = data.get("pause", self.pause)

        return self


@dataclass
class OwRadarR60abd1StateSleepQuality:
    """
    Object holding sleep quality state in OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A sleep quality object.

    """

    score: int = 0
    duration: int = 0
    awake: int = 0
    light: int = 0
    deep: int = 0
    aduration: int = 0
    away: int = 0
    turn: int = 0
    breath: int = 0
    heart: int = 0
    pause: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1StateSleepQuality:
        """
        Return SleepQuality object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An SleepQuality object.

        """
        self.score = data.get("score", self.score)
        self.duration = data.get("duration", self.duration)
        self.awake = data.get("awake", self.awake)
        self.light = data.get("light", self.light)
        self.deep = data.get("deep", self.deep)
        self.aduration = data.get("aduration", self.aduration)
        self.away = data.get("away", self.away)
        self.turn = data.get("turn", self.turn)
        self.breath = data.get("breath", self.breath)
        self.heart = data.get("heart", self.heart)
        self.pause = data.get("pause", self.pause)

        return self


@dataclass
class OwRadarR60abd1StateSleep:
    """
    Object holding sleep state in OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A sleep object.

    """

    away: OwRadarR60abd1StateSleepAway = OwRadarR60abd1StateSleepAway.OUT
    status: OwRadarR60abd1StateSleepStatus = OwRadarR60abd1StateSleepStatus.NONE
    awake: int = 0
    light: int = 0
    deep: int = 0
    score: int = 0
    overview: OwRadarR60abd1StateSleepOverview = field(
        default_factory=OwRadarR60abd1StateSleepOverview
    )
    quality: OwRadarR60abd1StateSleepQuality = field(
        default_factory=OwRadarR60abd1StateSleepQuality
    )
    exception: OwRadarR60abd1StateSleepException = (
        OwRadarR60abd1StateSleepException.NONE
    )
    rating: OwRadarR60abd1StateSleepRating = OwRadarR60abd1StateSleepRating.NONE
    struggle: OwRadarR60abd1StateSleepStruggle = OwRadarR60abd1StateSleepStruggle.NONE
    nobody: OwRadarR60abd1StateSleepNobody = OwRadarR60abd1StateSleepNobody.NONE

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1StateSleep:
        """
        Update and Return Sleep object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Sleep object.

        """
        self.away = OwRadarR60abd1StateSleepAway(data.get("away", self.away))
        self.status = OwRadarR60abd1StateSleepStatus(data.get("status", self.status))
        self.awake = data.get("awake", self.awake)
        self.light = data.get("light", self.light)
        self.deep = data.get("deep", self.deep)
        self.score = data.get("score", self.score)
        self.overview = self.overview.update_from_dict(
            data.get("overview", self.overview.__dict__)
        )
        self.quality = self.quality.update_from_dict(
            data.get("quality", self.quality.__dict__)
        )
        self.exception = OwRadarR60abd1StateSleepException(
            data.get("exception", self.exception)
        )
        self.rating = OwRadarR60abd1StateSleepRating(data.get("rating", self.rating))
        self.struggle = OwRadarR60abd1StateSleepStruggle(
            data.get("struggle", self.struggle)
        )
        self.nobody = OwRadarR60abd1StateSleepNobody(data.get("nobody", self.nobody))

        return self


@dataclass
class OwRadarR60abd1State(OwRadarCommonState):
    """
    Object holding State Information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A State object.

    """

    body: OwRadarR60abd1StateBody = field(default_factory=OwRadarR60abd1StateBody)
    heart: OwRadarR60abd1StateHeart = field(default_factory=OwRadarR60abd1StateHeart)
    breath: OwRadarR60abd1StateBreath = field(default_factory=OwRadarR60abd1StateBreath)
    sleep: OwRadarR60abd1StateSleep = field(default_factory=OwRadarR60abd1StateSleep)

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1State:
        """
        Update Return State object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An State object.

        """
        super().update_from_dict(data)
        self.body.update_from_dict(data.get("body", self.body.__dict__))
        self.breath.update_from_dict(data.get("breath", self.breath.__dict__))
        self.heart.update_from_dict(data.get("heart", self.heart.__dict__))
        self.sleep.update_from_dict(data.get("sleep", self.sleep.__dict__))

        return self


@dataclass
class OwRadarR60abd1Setting(OwRadarCommonSetting):
    """
    Object holding R60ABD1 Setting information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A Setting object.

    """

    body: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    heart: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    breath: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    sleep: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    mode: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    nobody: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    nobody_duration: int = 0
    struggle: OwRadarCommonSettingSwitch = OwRadarCommonSettingSwitch.OFF
    stop_duration: int = 0

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1Setting:
        """
        Update and Return Device information object from OwRadar API response.

        Args:
        ----
            data: The data from the OwRadar device API.

        Returns:
        -------
            A Device information object.

        """
        super().update_from_dict(data)
        self.body = data.get("body", self.body)
        self.heart = data.get("heart", self.heart)
        self.breath = data.get("breath", self.breath)
        self.sleep = data.get("sleep", self.sleep)
        self.mode = data.get("mode", self.mode)
        self.nobody = data.get("nobody", self.nobody)
        self.nobody_duration = data.get("nobody_duration", self.nobody_duration)
        self.struggle = data.get("struggle", self.struggle)
        self.stop_duration = data.get("stop_duration", self.stop_duration)

        return self


@dataclass
class OwRadarR60abd1Device(OwRadarCommonDevice):
    """
    Object holding Device Information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A Device object.

    """

    setting: OwRadarR60abd1Setting = field(default_factory=OwRadarR60abd1Setting)
    state: OwRadarR60abd1State = field(default_factory=OwRadarR60abd1State)
    stats: OwRadarR60abd1Stats = field(default_factory=OwRadarR60abd1Stats)
    snap: OwRadarR60abd1Snap = field(default_factory=OwRadarR60abd1Snap)
    event: OwRadarR60abd1Event = field(default_factory=OwRadarR60abd1Event)

    def update_from_dict(self, data: dict[str, Any]) -> OwRadarR60abd1Device:
        """
        Update and Return Device object from OwRadar API response.

        Args:
        ----
            data: Update the device object with the data received from a
                OwRadar device API.

        Returns:
        -------
            The updated Device object.

        """
        super().update_from_dict(data)
        self.setting.update_from_dict(data.get("setting", self.setting.__dict__))
        return self
