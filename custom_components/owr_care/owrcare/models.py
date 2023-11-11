"""Models for OWRCare."""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, IntFlag
from typing import Any

from awesomeversion import AwesomeVersion

from .exceptions import OWRCareError
import json


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

    x: int = None
    y: int = None
    z: int = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> BodyLocation:
        if data is None:
            return None
        if _x := data.get("x"):
            self.x = _x
        if _y := data.get("y"):
            self.y = _y
        if _z := data.get("z"):
            self.z = _z
        return self


@dataclass
class Body:
    """Object holding body state in OWRCare."""

    range: BodyRange = None
    presence: BodyPresence = None
    energy: int = None
    movement: BodyMovement = None
    distance: int = None
    location: BodyLocation = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> Body:
        if data is None:
            return None
        if _range := data.get("range"):
            self.range = BodyRange(_range)
        if _presence := data.get("presence"):
            self.presence = BodyPresence(_presence)
        if _energy := data.get("energy"):
            self.energy = _energy
        if _movement := data.get("movement"):
            self.movement = BodyMovement(_movement)
        if _distance := data.get("distance"):
            self.distance = _distance
        if _location := data.get("location"):
            self.location = BodyLocation(_location)

        return self


@dataclass
class Wave:
    """Object holding wave state in OWRCare."""

    w0: int = None
    w1: int = None
    w2: int = None
    w3: int = None
    w4: int = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> Wave:
        if data is None:
            return None
        if _w0 := data.get("w0"):
            self.w0 = _w0
        if _w1 := data.get("w1"):
            self.w1 = _w1
        if _w2 := data.get("w2"):
            self.w2 = _w2
        if _w3 := data.get("w3"):
            self.w3 = _w3
        if _w4 := data.get("w4"):
            self.w4 = _w4

        return self

@dataclass
class Heart:
    """Object holding heart state in OWRCare."""

    rate: int = None
    waves: Wave = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> Heart:
        if data is None:
            return None
        if _rate := data.get("rate"):
            self.rate = _rate
        if _waves := data.get("waves"):
            self.waves = Wave(_waves)

        return self


class BreathInfo(IntEnum):
    """Enumeration representing breath info from OWRCare."""

    NORMAL = 1
    TOO_HIGH = 2
    TOO_LOW = 3
    NONE = 4

@dataclass
class Breath:
    """Object holding breath state in OWRCare."""

    info: BreathInfo = None
    rate: int = None
    waves: Wave = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> Breath:
        if data is None:
            return None
        if _info := data.get("info"):
            self.info = BreathInfo(_info)
        if _rate := data.get("rate"):
            self.rate = _rate
        if _waves := data.get("waves"):
            self.waves = Wave(_waves)

        return self


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

    presence: BodyPresence = None
    status: SleepStatus = None
    breath: int = None
    heart: int = None
    turn: int = None
    leratio: int = None
    seratio: int = None
    pause: int = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> SleepOverview:
        if data is None:
            return None
        if _presence := data.get("presence"):
            self.presence = _presence
        if _status := data.get("status"):
            self.status = _status
        if _breath := data.get("breath"):
            self.breath = _breath
        if _heart := data.get("heart"):
            self.heart = _heart
        if _turn := data.get("turn"):
            self.turn = _turn
        if _leratio := data.get("leratio"):
            self.leratio = _leratio
        if _seratio := data.get("seratio"):
            self.seratio = _seratio
        if _pause := data.get("pause"):
            self.pause = _pause

        return self

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

    score: int = None
    duration: int = None
    awake: int = None
    light: int = None
    deep: int = None
    aduration: int = None
    away: int = None
    turn: int = None
    breath: int = None
    heart: int = None
    pause: int = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> SleepQuality:
        if data is None:
            return None
        if _score := data.get("score"):
            self.score = _score
        if _duration := data.get("duration"):
            self.duration= _duration
        if _awake := data.get("awake"):
            self.awake = _awake
        if _light := data.get("light"):
            self.light = _light
        if _deep := data.get("deep"):
            self.deep = _deep
        if _aduration := data.get("aduration"):
            self.aduration = _aduration
        if _away := data.get("away"):
            self.away = _away
        if _turn := data.get("turn"):
            self.turn = _turn
        if _breath := data.get("breath"):
            self.breath = _breath
        if _heart := data.get("heart"):
            self.heart = _heart
        if _pause := data.get("pause"):
            self.pause = _pause

        return self

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

    away: SleepAway = None
    status: SleepStatus = None
    awake: int = None
    light: int = None
    deep: int = None
    score: int = None
    overview: SleepOverview = None
    quality: SleepQuality = None
    exception: SleepException = None
    rating: SleepRating = None
    struggle: SleepStruggle = None
    nobody: SleepNobody = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> Sleep:
        if data is None:
            return None
        if _away := data.get("away"):
            self.away = _away
        if _status := data.get("status"):
            self.status = _status
        if _awake := data.get("awake"):
            self.awake = _awake
        if _light := data.get("light"):
            self.light = _light
        if _deep := data.get("deep"):
            self.deep = _deep
        if _score := data.get("score"):
            self.score = _score
        if _overview := data.get("overview"):
            self.overview = SleepOverview(_overview)
        if _quality := data.get("quality"):
            self.quality = SleepQuality(_quality)
        if _exception := data.get("exception"):
            self.exception = _exception
        if _rating := data.get("rating"):
            self.rating = _rating
        if _struggle := data.get("struggle"):
            self.struggle = _struggle
        if _nobody := data.get("nobody"):
            self.nobody = _nobody

        return self

@dataclass
class State:
    """Object holding State Infomation from OWRCare.

    Args:
    ----
        data: The data from the OWRCare device API.

    Returns:
    -------
        A State object.
    """

    timestamp: int = None
    body: Body = None
    heart: Heart = None
    breath: Breath = None
    sleep: Sleep = None


    def __init__(self, data: dict[str, Any]) -> None:
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> State:
        if data is None:
            return None
        timestamp = data.get("timestamp")
        if timestamp is None:
            return None
        if _body := data.get("body"):
            self.body = Body(_body)
        if _breath := data.get("breath"):
            self.breath = Breath(_breath)
        if _heart := data.get("heart"):
            self.heart = Heart(_heart)
        if _sleep := data.get("sleep"):
            self.sleep = Sleep(_sleep)

        return self



@dataclass
class Info:
    """Object holding device infomation from OWRCare."""

    model: str
    id: str
    hardware: str
    firmware: str
    version: str
    free_heap: int
    ip: str
    mac_addr: str
    name: str

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
        if data is None:
            return None

        return Info(
            model=data.get("model", None),
            id=data.get("id", None),
            hardware=data.get("hardware", None),
            firmware=data.get("firmware", None),
            version=data.get("version", None),
            free_heap=data.get("free_heap", None),
            ip=data.get("ip", None),
            mac_addr=data.get("mac_addr", None),
            name=data.get("name", None),
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

    binding_count: int = None
    binding: SettingSwitch = None
    realtime_ws: SettingSwitch = None
    realtime_mq: SettingSwitch = None
    body: SettingSwitch = None
    heart: SettingSwitch = None
    breath: SettingSwitch = None
    sleep: SettingSwitch = None
    mode: SettingSwitch = None
    nobody: SettingSwitch = None
    nobody_duration: int = None
    struggle: SettingSwitch = None
    stop_duration: int = None

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
        if data is None:
            return None

        return Setting(
            binding_count=data.get("binding_count", None),
            binding=data.get("binding", None),
            realtime_ws=data.get("realtime_ws", None),
            realtime_mq=data.get("realtime_mq", None),
            body=data.get("body", None),
            heart=data.get("heart", None),
            breath=data.get("breath", None),
            sleep=data.get("sleep", None),
            mode=data.get("mode", None),
            nobody=data.get("nobody", None),
            nobody_duration=data.get("nobody_duration", None),
            struggle=data.get("struggle", None),
            stop_duration=data.get("stop_duration", None),
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

    setting: Setting = None
    info: Info = None
    state: State = None


    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize an empty OWRCare device class.

        Args:
        ----
            data: The full API response from a OWRCare device.

        Raises:
        ------
            OWRCareError: In case the given API response is incomplete in a way
                that a Device object cannot be constructed from it.
        """
        # Check if all elements are in the passed dict, else raise an Error
        # if any(
        #     k not in data and data[k] is not None
        #     for k in ("setting","info", "state")
        # ):
        #     msg = "OWRCare data is incomplete, cannot construct device object"
        #     raise OWRCareError(msg)
        self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> Device:
        """Return Device object from OWRCare API response.

        Args:
        ----
            data: Update the device object with the data received from a
                OWRCare device API.

        Returns:
        -------
            The updated Device object.
        """
        if _setting := data.get("setting"):
            self.setting = Setting.from_dict(_setting)

        if _info := data.get("info"):
            self.info = Info.from_dict(_info)

        if _states := data.get("state"):
            self.state = State(_states)

        return self
