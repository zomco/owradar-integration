"""数值传感器。

字段直接来自 Telemetry，**不做任何重命名或单位换算**（架构文档 §3）——
换算是 bug 的温床，而且设备、App、屏幕、HA 四端必须显示同一个数。

`health` 不是 `ok`/`degraded` 时返回 None，实体随之 unavailable。
不显示上一次的有效值：用户看到数值就会当它是当前的，
而「传感器坏了但还在显示 24.5°C」比「显示不可用」危险得多。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    LIGHT_LUX,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfLength,
    UnitOfSoundPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MmRadarConfigEntry
from .api import reading
from .entity import MmRadarEntity


@dataclass(frozen=True, kw_only=True)
class MmRadarSensorDescription(SensorEntityDescription):
    """多一个取值函数 —— 各指标在 Telemetry 里的位置不统一。"""

    value_fn: Callable[[dict[str, Any]], float | str | None]


def _env(metric: str) -> Callable[[dict[str, Any]], float | None]:
    return lambda data: reading(data, metric)


def _presence_distance(data: dict[str, Any]) -> float | None:
    """目标距离。

    无人时固件上报 -1 表示「无有效距离」。**必须转成 None** ——
    直接给 HA 一个 -1 会让历史曲线上出现一条负距离，
    统计和自动化都会被它带偏。
    """
    presence = data.get("presence")
    if not isinstance(presence, dict):
        return None
    value = presence.get("distance_cm")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    return None if value < 0 else float(value)


def _seated(data: dict[str, Any]) -> float | None:
    presence = data.get("presence")
    if not isinstance(presence, dict):
        return None
    value = presence.get("seated_duration_s")
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _risk(data: dict[str, Any]) -> str | None:
    risk = data.get("risk")
    if not isinstance(risk, dict):
        return None
    level = risk.get("level")
    return level if isinstance(level, str) else None


def _rssi(data: dict[str, Any]) -> float | None:
    device = data.get("device")
    if not isinstance(device, dict):
        return None
    value = device.get("rssi_dbm")
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


SENSORS: tuple[MmRadarSensorDescription, ...] = (
    MmRadarSensorDescription(
        key="co2",
        translation_key="co2",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_env("co2"),
    ),
    MmRadarSensorDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=_env("temperature"),
    ),
    MmRadarSensorDescription(
        key="humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_env("humidity"),
    ),
    MmRadarSensorDescription(
        key="noise",
        translation_key="noise",
        device_class=SensorDeviceClass.SOUND_PRESSURE,
        native_unit_of_measurement=UnitOfSoundPressure.WEIGHTED_DECIBEL_A,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_env("noise"),
    ),
    MmRadarSensorDescription(
        key="illuminance",
        translation_key="illuminance",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_env("lux"),
    ),
    MmRadarSensorDescription(
        key="distance",
        translation_key="distance",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_presence_distance,
    ),
    MmRadarSensorDescription(
        key="seated_duration",
        translation_key="seated_duration",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_seated,
    ),
    MmRadarSensorDescription(
        key="risk_level",
        translation_key="risk_level",
        device_class=SensorDeviceClass.ENUM,
        options=["good", "fair", "poor", "bad"],
        value_fn=_risk,
    ),
    MmRadarSensorDescription(
        key="rssi",
        translation_key="rssi",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=_rssi,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MmRadarConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """建立本平台的实体。"""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        MmRadarSensor(coordinator, d) for d in SENSORS if d.key in coordinator.capabilities
    )


class MmRadarSensor(MmRadarEntity, SensorEntity):
    """一个数值实体。"""

    entity_description: MmRadarSensorDescription

    def __init__(self, coordinator: Any, description: MmRadarSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | str | None:
        return self.entity_description.value_fn(self._snapshot())
