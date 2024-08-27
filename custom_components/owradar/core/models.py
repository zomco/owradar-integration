"""Models for OwRadar."""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class BodyRange(IntEnum):
    """Enumeration representing body range from OwRadar."""

    OUT = 0
    IN = 1


class BodyPresence(IntEnum):
    """Enumeration representing body presence from OwRadar."""

    NOBODY = 0
    SOMEBODY = 1


class BodyMovement(IntEnum):
    """Enumeration representing body movement from OwRadar."""

    NONE = 0
    STATIC = 1
    ACTIVE = 2


@dataclass
class BodyLocation:
    """Object holding body location state in OwRadar."""

    x: int
    y: int
    z: int

    @staticmethod
    def from_dict(data: dict[str, Any]) -> BodyLocation:
        """Return Body Location object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Body Location object.

        """
        return BodyLocation(
            x=data.get("x"),
            y=data.get("y"),
            z=data.get("z"),
        )


@dataclass
class Body:
    """Object holding body state in OwRadar."""

    range: BodyRange
    presence: BodyPresence
    energy: int
    movement: BodyMovement
    distance: int
    location: BodyLocation

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Body:
        """Return Body object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Body object.

        """
        return Body(
            range=BodyRange(data.get("range")),
            presence=BodyPresence(data.get("presence")),
            energy=data.get("energy"),
            movement=BodyMovement(data.get("movement")),
            distance=data.get("distance"),
            location=BodyLocation.from_dict(data.get("location")),
        )

    def update_from_dict(self, data: dict[str, Any]) -> Body:
        """Update and Return Body object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Body object.

        """
        if (_range := data.get("range")) is not None:
            self.range = BodyRange(_range)
        if (_presence := data.get("presence")) is not None:
            self.presence = BodyPresence(_presence)
        if (_energy := data.get("energy")) is not None:
            self.energy = _energy
        if (_movement := data.get("movement")) is not None:
            self.movement = BodyMovement(_movement)
        if (_distance := data.get("distance")) is not None:
            self.distance = _distance
        if (_location := data.get("location")) is not None:
            self.location = BodyLocation.from_dict(_location)

        return self


@dataclass
class Wave:
    """Object holding wave state in OwRadar."""

    w0: int
    w1: int
    w2: int
    w3: int
    w4: int

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Wave:
        """Return Wave object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Wave object.

        """
        return Wave(
            w0=data.get("w0"),
            w1=data.get("w1"),
            w2=data.get("w2"),
            w3=data.get("w3"),
            w4=data.get("w4"),
        )


@dataclass
class Heart:
    """Object holding heart state in OwRadar."""

    rate: int
    waves: Wave

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Heart:
        """Return Heart object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Heart object.

        """
        return Heart(
            rate=data.get("rate"),
            waves=Wave.from_dict(data.get("waves")),
        )

    def update_from_dict(self, data: dict[str, Any]) -> Heart:
        """Update and Return Heart object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Heart object.

        """
        if (_rate := data.get("rate")) is not None:
            self.rate = _rate
        if (_waves := data.get("waves")) is not None:
            self.waves = Wave.from_dict(_waves)

        return self


class BreathInfo(IntEnum):
    """Enumeration representing breath info from OwRadar."""

    UNSET = 0
    NORMAL = 1
    TOO_HIGH = 2
    TOO_LOW = 3
    NONE = 4


@dataclass
class Breath:
    """Object holding breath state in OwRadar."""

    info: BreathInfo
    rate: int
    waves: Wave

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Breath:
        """Return Breath object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Breath object.

        """
        return Breath(
            info=BreathInfo(data.get("info")),
            rate=data.get("rate"),
            waves=Wave.from_dict(data.get("waves")),
        )

    def update_from_dict(self, data: dict[str, Any]) -> Breath:
        """Update and Return Breath object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Breath object.

        """
        if (_info := data.get("info")) is not None:
            self.info = BreathInfo(_info)
        if (_rate := data.get("rate")) is not None:
            self.rate = _rate
        if (_waves := data.get("waves")) is not None:
            self.waves = Wave.from_dict(_waves)

        return self


class SleepAway(IntEnum):
    """Enumeration representing sleep away from OwRadar."""

    OUT = 0
    IN = 1
    ACTIVE = 2


class SleepStatus(IntEnum):
    """Enumeration representing sleep status from OwRadar."""

    DEEP = 0
    LIGHT = 1
    AWAKE = 2
    NONE = 3


class SleepException(IntEnum):
    """Enumeration representing sleep exception from OwRadar."""

    LESS_4HOUR = 0
    MORE_12HOUR = 1
    LONG_TIME = 2
    NONE = 3


class SleepRating(IntEnum):
    """Enumeration representing sleep rating from OwRadar."""

    NONE = 0
    GOOD = 1
    MEDIAN = 2
    BAD = 3


class SleepStruggle(IntEnum):
    """Enumeration representing sleep struggle from OwRadar."""

    NONE = 0
    NORMAL = 1
    ABNORMAL = 2


class SleepNobody(IntEnum):
    """Enumeration representing sleep nobody from OwRadar."""

    NONE = 0
    NORMAL = 1
    ABNORMAL = 2


@dataclass
class SleepOverview:
    """Object holding sleep overview state in OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

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
        """Return SleepOverview object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An SleepOverview object.

        """
        return SleepOverview(
            presence=BodyPresence(data.get("presence")),
            status=SleepStatus(data.get("status")),
            heart=data.get("heart"),
            breath=data.get("breath"),
            turn=data.get("turn"),
            leratio=data.get("leratio"),
            seratio=data.get("seratio"),
            pause=data.get("pause"),
        )


@dataclass
class SleepQuality:
    """Object holding sleep quality state in OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

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
        """Return SleepQuality object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An SleepQuality object.

        """
        return SleepQuality(
            score=data.get("score"),
            duration=data.get("duration"),
            awake=data.get("awake"),
            light=data.get("light"),
            deep=data.get("deep"),
            aduration=data.get("aduration"),
            away=data.get("away"),
            turn=data.get("turn"),
            breath=data.get("breath"),
            heart=data.get("heart"),
            pause=data.get("pause"),
        )


@dataclass
class Sleep:
    """Object holding sleep state in OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

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
        """Return Sleep object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Sleep object.

        """
        return Sleep(
            away=data.get("away"),
            status=data.get("status"),
            awake=data.get("awake"),
            light=data.get("light"),
            deep=data.get("deep"),
            score=data.get("score"),
            overview=SleepOverview.from_dict(data.get("overview")),
            quality=SleepQuality.from_dict(data.get("quality")),
            exception=SleepException(data.get("exception")),
            rating=SleepRating(data.get("rating")),
            struggle=SleepStruggle(data.get("struggle")),
            nobody=SleepNobody(data.get("nobody")),
        )

    def update_from_dict(self, data: dict[str, Any]) -> Sleep:
        """Update and Return Sleep object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Sleep object.

        """
        if (_away := data.get("away")) is not None:
            self.away = SleepAway(_away)
        if (_status := data.get("status")) is not None:
            self.status = _status
        if (_awake := data.get("awake")) is not None:
            self.awake = _awake
        if (_light := data.get("light")) is not None:
            self.light = _light
        if (_deep := data.get("deep")) is not None:
            self.deep = _deep
        if (_score := data.get("score")) is not None:
            self.score = _score
        if (_overview := data.get("overview")) is not None:
            self.overview = SleepOverview.from_dict(_overview)
        if (_quality := data.get("quality")) is not None:
            self.quality = SleepQuality.from_dict(_quality)
        if (_exception := data.get("exception")) is not None:
            self.exception = SleepException(_exception)
        if (_rating := data.get("rating")) is not None:
            self.rating = SleepRating(_rating)
        if (_struggle := data.get("struggle")) is not None:
            self.struggle = SleepStruggle(_struggle)
        if (_nobody := data.get("nobody")) is not None:
            self.nobody = SleepNobody(_nobody)

        return self


@dataclass
class Coord:
    """Object holding coordinate state in OwRadar."""

    x: float
    y: float
    z: float

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Coord:
        """Return Coordinate object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Coordinate object.

        """
        return Coord(
            x=data.get("x"),
            y=data.get("y"),
            z=data.get("z"),
        )


@dataclass
class MotionAngle:
    """Object holding Motion Angle state in OwRadar."""

    pitch: float
    roll: float

    @staticmethod
    def from_dict(data: dict[str, Any]) -> MotionAngle:
        """Return Motion Angle object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Motion Angle object.

        """
        return MotionAngle(
            pitch=data.get("pitch"),
            roll=data.get("roll"),
        )


@dataclass
class Motion:
    """Object holding motion state in OwRadar."""

    acce: Coord
    gyro: Coord
    angle: MotionAngle

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Motion:
        """Return Motion object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Motion object.

        """
        return Motion(
            acce=Coord.from_dict(data.get("acce")),
            gyro=Coord.from_dict(data.get("gyro")),
            angle=MotionAngle.from_dict(data.get("angle")),
        )

    def update_from_dict(self, data: dict[str, Any]) -> Motion:
        """Update and Return Motion object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Motion object.

        """
        if (_acce := data.get("acce")) is not None:
            self.acce = Coord.from_dict(_acce)
        if (_gyro := data.get("gyro")) is not None:
            self.gyro = Coord.from_dict(_gyro)
        if (_angle := data.get("angle")) is not None:
            self.angle = MotionAngle.from_dict(_angle)

        return self


@dataclass
class State:
    """Object holding State Infomation from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A State object.

    """

    timestamp: int
    body: Body
    heart: Heart
    breath: Breath
    sleep: Sleep
    motion: Motion

    @staticmethod
    def from_dict(data: dict[str, Any]) -> State:
        """Return State object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An State object.

        """
        return State(
            timestamp=data.get("timestamp", None),
            body=Body.from_dict(data.get("body")),
            heart=Heart.from_dict(data.get("heart")),
            breath=Breath.from_dict(data.get("breath")),
            sleep=Sleep.from_dict(data.get("sleep")),
            motion=Motion.from_dict(data.get("motion")),
        )

    def update_from_dict(self, data: dict[str, Any]) -> State:
        """Update Return State object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An State object.

        """
        if (_timestamp := data.get("timestamp")) is not None:
            self.timestamp = _timestamp
        if (_body := data.get("body")) is not None:
            self.body.update_from_dict(_body)
        if (_breath := data.get("breath")) is not None:
            self.breath.update_from_dict(_breath)
        if (_heart := data.get("heart")) is not None:
            self.heart.update_from_dict(_heart)
        if (_sleep := data.get("sleep")) is not None:
            self.sleep.update_from_dict(_sleep)
        if (_motion := data.get("motion")) is not None:
            self.motion.update_from_dict(_motion)

        return self


@dataclass
class Info:
    """Object holding device infomation from OwRadar."""

    radar_model: str
    radar_version: str
    mac_addr: str
    name: str
    ip: str
    free_heap: int
    version: str
    architecture: str
    brand: str
    product: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Info:
        """Return Device information object from OwRadar API response.

        Args:
        ----
            data: The data from the OwRadar device API.

        Returns:
        -------
            A Device information object.

        """
        return Info(
            radar_model=data.get("radar_model", None),
            radar_version=data.get("radar_version", None),
            mac_addr=data.get("mac_addr", None),
            name=data.get("name", None),
            ip=data.get("ip", None),
            free_heap=data.get("free_heap", None),
            version=data.get("version", None),
            architecture=data.get("architecture", None),
            brand=data.get("brand", None),
            product=data.get("product", None),
        )

    def update_from_dict(self, data: dict[str, Any]) -> Info:
        """Update and Return Device information object from OwRadar API response.

        Args:
        ----
            data: The data from the OwRadar device API.

        Returns:
        -------
            A Device information object.

        """
        if _radar_model := data.get("radar_model"):
            self.radar_model = _radar_model
        if _radar_version := data.get("radar_version"):
            self.radar_version = _radar_version
        if _mac := data.get("mac"):
            self.mac = _mac
        if _name := data.get("name"):
            self.name = _name
        if _ip := data.get("ip"):
            self.ip = _ip
        if _free_heap := data.get("free_heap"):
            self.free_heap = _free_heap
        if _version := data.get("version"):
            self.version = _version
        if _architecture := data.get("architecture"):
            self.architecture = _architecture
        if _brand := data.get("brand"):
            self.brand = _brand
        if _product := data.get("product"):
            self.product = _product

        return self


class SettingSwitch(IntEnum):
    """Enumeration representing body range from OwRadar."""

    OFF = 0
    ON = 1


@dataclass
class Setting:
    """Object holding Setting information from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A Setting object.

    """

    realtime_ws: SettingSwitch
    indicate: SettingSwitch
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
        """Return Setting object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Setting object.

        """
        return Setting(
            realtime_ws=data.get("realtime_ws", None),
            indicate=data.get("indicate", None),
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

    def update_from_dict(self, data: dict[str, Any]) -> Setting:
        """Update and Return Setting object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Setting object.

        """
        if (_realtime_ws := data.get("realtime_ws")) is not None:
            self.realtime_ws = _realtime_ws
        if (_indicate := data.get("indicate")) is not None:
            self.indicate = _indicate
        if (_body := data.get("body")) is not None:
            self.body = _body
        if (_heart := data.get("heart")) is not None:
            self.heart = _heart
        if (_breath := data.get("breath")) is not None:
            self.breath = _breath
        if (_sleep := data.get("sleep")) is not None:
            self.sleep = _sleep
        if (_mode := data.get("mode")) is not None:
            self.mode = _mode
        if (_nobody := data.get("nobody")) is not None:
            self.nobody = _nobody
        if (_nobody_duration := data.get("nobody_duration")) is not None:
            self.nobody_duration = _nobody_duration
        if (_struggle := data.get("struggle")) is not None:
            self.struggle = _struggle
        if (_stop_duration := data.get("stop_duration")) is not None:
            self.stop_duration = _stop_duration

        return self


@dataclass
class Device:
    """Object holding Device Infomation from OwRadar.

    Args:
    ----
        data: The data from the OwRadar device API.

    Returns:
    -------
        A Device object.

    """

    setting: Setting
    info: Info
    state: State

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Device:
        """Return Device object form OwRadar API response.

        Args:
        ----
            data: The response from the OwRadar API.

        Returns:
        -------
            An Device object.

        """
        return Device(
            setting=Setting.from_dict(data.get("setting")),
            info=Info.from_dict(data.get("info")),
            state=State.from_dict(data.get("state")),
        )

    # def __init__(self, data: dict[str, Any]) -> None:
    #     """Initialize an empty OwRadar device class.

    #     Args:
    #     ----
    #         data: The full API response from a OwRadar device.

    #     Raises:
    #     ------
    #         OwRadarError: In case the given API response is incomplete in a way
    #             that a Device object cannot be constructed from it.
    #     """
    #     # Check if all elements are in the passed dict, else raise an Error
    #     # if any(
    #     #     k not in data and data[k] is not None
    #     #     for k in ("setting","info", "state")
    #     # ):
    #     #     msg = "OwRadar data is incomplete, cannot construct device object"
    #     #     raise OwRadarError(msg)
    #     self.update_from_dict(data)

    def update_from_dict(self, data: dict[str, Any]) -> Device:
        """Update and Return Device object from OwRadar API response.

        Args:
        ----
            data: Update the device object with the data received from a
                OwRadar device API.

        Returns:
        -------
            The updated Device object.

        """
        if _setting := data.get("setting"):
            self.setting.update_from_dict(_setting)
        if _info := data.get("info"):
            self.info.update_from_dict(_info)
        if _state := data.get("state"):
            self.state.update_from_dict(_state)

        return self
