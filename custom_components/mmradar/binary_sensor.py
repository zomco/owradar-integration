"""布尔传感器：在场、在目标区域、有活跃告警。

这三个是本产品与普通空气检测仪的分野 ——
「有人」和「**我本人在工位上**」不是一回事，后者才是规则触发的前提。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MmRadarConfigEntry
from .const import PRESENCE_ABSENT
from .entity import MmRadarEntity


@dataclass(frozen=True, kw_only=True)
class MmRadarBinaryDescription(BinarySensorEntityDescription):
    """布尔实体的描述：多一个取值函数。"""

    value_fn: Callable[[dict[str, Any]], bool | None]


def _presence(data: dict[str, Any]) -> bool | None:
    """有没有人。

    注意用的是**去抖后的 `state`**，不是瞬时的 `in_zone` ——
    雷达抖一下就翻转的实体没法用来做自动化，
    灯会跟着一闪一闪。
    """
    presence = data.get("presence")
    if not isinstance(presence, dict):
        return None
    state = presence.get("state")
    if not isinstance(state, str):
        return None
    if presence.get("health") not in ("ok", "degraded"):
        return None
    return state != PRESENCE_ABSENT


def _in_zone(data: dict[str, Any]) -> bool | None:
    """是否在目标区域内。

    这是**瞬时**值，与 presence 的语义不同：
    presence 回答「我在不在工位」，in_zone 回答「此刻雷达看到的目标在不在距离门内」。
    调距离门时用它做可视化反馈，不建议直接拿去做自动化。
    """
    presence = data.get("presence")
    if not isinstance(presence, dict):
        return None
    value = presence.get("in_zone")
    return value if isinstance(value, bool) else None


def _alert_active(data: dict[str, Any]) -> bool | None:
    risk = data.get("risk")
    if not isinstance(risk, dict):
        return None
    ids = risk.get("active_alert_ids")
    if not isinstance(ids, list):
        return None
    return len(ids) > 0


BINARY_SENSORS: tuple[MmRadarBinaryDescription, ...] = (
    MmRadarBinaryDescription(
        key="presence",
        translation_key="presence",
        device_class=BinarySensorDeviceClass.OCCUPANCY,
        value_fn=_presence,
    ),
    MmRadarBinaryDescription(
        key="in_zone",
        translation_key="in_zone",
        device_class=BinarySensorDeviceClass.PRESENCE,
        value_fn=_in_zone,
    ),
    MmRadarBinaryDescription(
        key="alert_active",
        translation_key="alert_active",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=_alert_active,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MmRadarConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """建立本平台的实体。"""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(MmRadarBinarySensor(coordinator, d) for d in BINARY_SENSORS)


class MmRadarBinarySensor(MmRadarEntity, BinarySensorEntity):
    """一个布尔实体。"""

    entity_description: MmRadarBinaryDescription

    def __init__(self, coordinator: Any, description: MmRadarBinaryDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self._snapshot())
