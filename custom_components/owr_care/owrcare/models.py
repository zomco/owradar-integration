"""Models for OWRCare."""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, IntFlag
from typing import Any

from awesomeversion import AwesomeVersion

from .exceptions import OWRCareError


class BodyRange(IntEnum):
    """Enumeration representing body range from OWRCare."""

    OUT = 0
    IN = 1

class BodyPresence(IntEnum):
    """Enumeration representing body presence from OWRCare."""

    NOBODY = 0
    SOMEBODY = 1

class BodyMovement(IntEnum):
    """Enumeration representing body movement from OWRCare."""

    NONE = 0
    STATIC = 1
    ACTIVE = 2

@dataclass
class BodyLocation:
    """Object holding body location state in OWRCare."""

    x: int
    y: int
    z: int

    @staticmethod
    def from_dict(data: dict[str, Any]) -> BodyLocation:
        """Return Body Location object from OWRCare API response.

        Args:
        ----
            data: The data from the OWRCare device API.

        Returns:
        -------
            A Body Location object.
        """
        location = data.get("location")
        if location is None:
            return None

        return BodyLocation(
            x=location.get("x", 0),
            y=location.get("y", 0),
            z=location.get("z", 0),
        )

@dataclass
class Body:
    """Object holding body state in OWRCare."""

    range: BodyRange
    presence: BodyPresence
    energy: int
    movement: BodyMovement
    distance: int
    location: BodyLocation

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Body:
        """Return Body object from OWRCare API response.

        Args:
        ----
            data: The data from the OWRCare device API.

        Returns:
        -------
            A Body object.
        """
        body = data.get("body", {})

        return Body(
            range=body.get("range", None),
            presence=body.get("presence", None),
            energy=body.get("energy", None),
            movement=body.get("movement", None),
            distance=body.get("distance", None),
            location=BodyLocation(body),
        )


@dataclass
class Wave:
    """Object holding wave state in OWRCare."""

    w0: int
    w1: int
    w2: int
    w3: int
    w4: int

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Wave:
        """Return Wave object from OWRCare API response.

        Args:
        ----
            data: The data from the OWRCare device API.

        Returns:
        -------
            A Wave object.
        """
        waves = data.get("waves")
        if waves is None:
            return None

        return Wave(
            w0=waves.get("w0", 0),
            w1=waves.get("w1", 0),
            w2=waves.get("w2", 0),
            w3=waves.get("w3", 0),
            w4=waves.get("w4", 0),
        )

@dataclass
class Heart:
    """Object holding heart state in OWRCare."""

    rate: int
    waves: Wave

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Heart:
        """Return Heart object from OWRCare API response.

        Args:
        ----
            data: The data from the OWRCare device API.

        Returns:
        -------
            A heart object.
        """
        heart = data.get("heart", {})
        return Heart(
            rate=heart.get("rate", None),
            waves=Wave(heart)
        )


class BreathInfo(IntEnum):
    """Enumeration representing breath info from OWRCare."""

    NORMAL = 1
    TOO_HIGH = 2
    TOO_LOW = 3
    NONE = 4

@dataclass
class Breath:
    """Object holding breath state in OWRCare."""

    info: BreathInfo
    rate: int
    waves: Wave

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Breath:
        """Return Breath object from OWRCare API response.

        Args:
        ----
            data: The data from the OWRCare device API.

        Returns:
        -------
            A breath object.
        """
        breath = data.get("breath", {})
        return Heart(
            info=breath.get("info", None),
            rate=breath.get("breath", None),
            waves=Wave(breath)
        )


class SleepAway(IntEnum):
    """Enumeration representing sleep away from OWRCare."""

    OUT = 0
    IN = 1
    ACTIVE = 2

class SleepStatus(IntEnum):
    """Enumeration representing sleep status from OWRCare."""

    DEEP = 0
    LIGHT = 1
    AWAKE = 2
    NONE = 3

class SleepException(IntEnum):
    """Enumeration representing sleep exception from OWRCare."""

    LESS_4HOUR = 0
    MORE_12HOUR = 1
    LONG_TIME = 2
    NONE = 3

class SleepRating(IntEnum):
    """Enumeration representing sleep rating from OWRCare."""

    NONE = 0
    GOOD = 1
    MEDIAN = 2
    BAD = 3

class SleepStruggle(IntEnum):
    """Enumeration representing sleep struggle from OWRCare."""

    NONE = 0
    NORMAL = 1
    ABNORMAL = 2

class SleepNobody(IntEnum):
    """Enumeration representing sleep nobody from OWRCare."""

    NONE = 0
    NORMAL = 1
    ABNORMAL = 2

@dataclass
class SleepOverview:
    """Object holding sleep overview state in OWRCare.

    Args:
    ----
        data: The data from the OWRCare device API.

    Returns:
    -------
        A sleep overview object.
    """

    presence: BodyPresence
    status: SleepStatus
    breath: int
    heart: int
    turn: int
    leratio: int
    seratio: int
    pause: int

    @staticmethod
    def from_dict(data: dict[str, Any]) -> SleepOverview:
        """Return Sleep overview object from OWRCare API response.

        Args:
        ----
            data: The data from the OWRCare device API.

        Returns:
        -------
            A sleep overview object.
        """
        overview = data.get("overview")
        if overview is None:
            return None

        return SleepOverview(
            presence=overview.get("presence", None),
            status=overview.get("status", None),
            breath=overview.get("breath", None),
            heart=overview.get("heart", None),
            turn=overview.get("turn", None),
            leratio=overview.get("leratio", None),
            seratio=overview.get("seratio", None),
            pause=overview.get("pause", None)
        )

@dataclass
class SleepQuality:
    """Object holding sleep quality state in OWRCare.

    Args:
    ----
        data: The data from the OWRCare device API.

    Returns:
    -------
        A sleep quality object.
    """

    score: int
    duration: int
    awake: int
    light: int
    deep: int
    aduration: int
    away: int
    turn: int
    breath: int
    heart: int
    pause: int

    @staticmethod
    def from_dict(data: dict[str, Any]) -> SleepQuality:
        """Return Sleep quality object from OWRCare API response.

        Args:
        ----
            data: The data from the OWRCare device API.

        Returns:
        -------
            A sleep quality object.
        """
        overview = data.get("overview")
        if overview is None:
            return None

        return SleepOverview(
            score=overview.get("score", None),
            duration=overview.get("duration", None),
            awake=overview.get("awake", None),
            light=overview.get("light", None),
            deep=overview.get("deep", None),
            aduration=overview.get("aduration", None),
            away=overview.get("away", None),
            turn=overview.get("turn", None),
            breath=overview.get("breath", None),
            heart=overview.get("heart", None),
            pause=overview.get("pause", None)
        )

@dataclass
class Sleep:
    """Object holding sleep state in OWRCare.

    Args:
    ----
        data: The data from the OWRCare device API.

    Returns:
    -------
        A sleep object.
    """

    away: SleepAway
    status: SleepStatus
    awake: int
    light: int
    deep: int
    score: int
    overview: SleepOverview
    quality: SleepQuality
    exception: SleepException
    rating: SleepRating
    struggle: SleepStruggle
    nobody: SleepNobody

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Sleep:
        """Return Sleep object from OWRCare API response.

        Args:
        ----
            data: The data from the OWRCare device API.

        Returns:
        -------
            A sleep object.
        """
        sleep = data.get("sleep")
        if sleep is None:
            return None

        return SleepOverview(
            away=sleep.get("away", None),
            status=sleep.get("status", None),
            awake=sleep.get("awake", None),
            light=sleep.get("light", None),
            deep=sleep.get("deep", None),
            score=sleep.get("score", None),
            overview=SleepOverview(sleep),
            quality=SleepQuality(sleep),
            exception=sleep.get("exception", None),
            rating=sleep.get("rating", None),
            struggle=sleep.get("struggle", None),
            nobody=sleep.get("nobody", None)
        )


@dataclass
class Report:
    """Object holding Report Infomation from OWRCare.

    Args:
    ----
        data: The data from the OWRCare device API.

    Returns:
    -------
        A Report object.
    """

    timestamp: int
    body: Body
    heart: Heart
    breath: Breath
    sleep: Sleep


    @staticmethod
    def from_dict(data: dict[str, Any]) -> Report:
        """Return Status object form OWRCare API response.

        Args:
        ----
            data: The response from the OWRCare API.

        Returns:
        -------
            An Status object.
        """
        timestamp = data.get("timestamp")
        if timestamp is None:
            return None

        return Report(
            timestamp=timestamp,
            body=Body(data.get("body")),
            breath=Breath(data.get("breath")),
            heart=Heart(data.get("heart")),
            sleep=Sleep(data.get("sleep")),
        )



@dataclass
class Info:
    """Object holding device infomation from OWRCare."""

    model: str
    id: str
    hardware: str
    firmware: str
    version: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Info:
        """Return Device information object from OWRCare API response.

        Args:
        ----
            data: The data from the OWRCare device API.

        Returns:
        -------
            A Device information object.
        """
        product = data.get("info")
        if product is None:
            return None

        return Info(
            model=product.get("model", None),
            id=product.get("id", None),
            hardware=product.get("hardware", None),
            firmware=product.get("firmware", None),
            version=product.get("version", None),
        )

class SettingSwitch(IntEnum):
    """Enumeration representing body range from OWRCare."""

    OFF = 0
    ON = 1

@dataclass
class Setting:
    """Object holding Setting information from OWRCare.

    Args:
    ----
        data: The data from the OWRCare device API.

    Returns:
    -------
        A Setting object.
    """

    bingding_count: int
    bingding: SettingSwitch
    realtime_ws: SettingSwitch
    realtime_mq: SettingSwitch
    body: SettingSwitch
    heart: SettingSwitch
    breath: SettingSwitch
    sleep: SettingSwitch
    mode: SettingSwitch
    nobody: SettingSwitch
    nobody_duration: int
    struggle: SettingSwitch
    stop_duration: int

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Setting:
        """Return Setting object form OWRCare API response.

        Args:
        ----
            data: The response from the OWRCare API.

        Returns:
        -------
            An Setting object.
        """
        setting = data.get("setting")
        if setting is None:
            return None
        return Setting(
            binding_count=setting.get("binding_count", None),
            binding=setting.get("binding", None),
            realtime_ws=setting.get("realtime_ws", None),
            realtime_mq=setting.get("realtime_mq", None),
            body=setting.get("body", None),
            heart=setting.get("heart", None),
            breath=setting.get("breath", None),
            sleep=setting.get("sleep", None),
            mode=setting.get("mode", None),
            nobody=setting.get("nobody", None),
            nobody_duration=setting.get("nobody_duration", None),
            struggle=setting.get("struggle", None),
            stop_duration=setting.get("stop_duration", None),
        )

@dataclass
class Device:
    """Object holding Device Infomation from OWRCare.

    Args:
    ----
        data: The data from the OWRCare device API.

    Returns:
    -------
        A Device object.
    """

    setting: Setting
    info: Info


    @staticmethod
    def from_dict(data: dict[str, Any]) -> Device:
        """Return Device object form OWRCare API response.

        Args:
        ----
            data: The response from the OWRCare API.

        Returns:
        -------
            An Device object.
        """

        return Device(
            setting=Setting(data.get("setting")),
            info=Info(data.get("info")),
        )
