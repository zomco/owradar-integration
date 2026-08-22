"""可调数值：目标区域距离门、屏幕亮度。

距离门是本产品的核心参数 —— 它决定「多远算我在工位」。
把它做成 number 实体是为了让用户能在 HA 里边看 `in_zone` 边调，
比在 App 里盲调直观。

注意区分两组「距离」：
- 这里调的是**固件侧的距离门**，决定算不算在座
- `mmradar.set_radar` 服务调的是**雷达内部**探测范围，决定模组上不上报
前者才是产品语义。
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MmRadarConfigEntry
from .coordinator import MmRadarCoordinator
from .entity import MmRadarEntity


@dataclass(frozen=True, kw_only=True)
class MmRadarNumberDescription(NumberEntityDescription):
    """可调数值的描述：读一个、写一个。"""

    value_fn: Callable[[dict[str, Any]], float | None]
    set_fn: Callable[[MmRadarCoordinator, float], Awaitable[Any]]


def _zone(field: str) -> Callable[[dict[str, Any]], float | None]:
    def _get(data: dict[str, Any]) -> float | None:
        zone = data.get("zone")
        if not isinstance(zone, dict):
            return None
        value = zone.get(field)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        return None

    return _get


def _brightness(data: dict[str, Any]) -> float | None:
    display = data.get("display")
    if not isinstance(display, dict):
        return None
    value = display.get("brightness_pct")
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


NUMBERS: tuple[MmRadarNumberDescription, ...] = (
    MmRadarNumberDescription(
        key="zone_min",
        translation_key="zone_min",
        device_class=NumberDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        native_min_value=30,
        native_max_value=600,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        value_fn=_zone("min_cm"),
        set_fn=lambda c, v: c.async_send_command("set_zone", min_cm=int(v)),
    ),
    MmRadarNumberDescription(
        key="zone_max",
        translation_key="zone_max",
        device_class=NumberDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        native_min_value=30,
        native_max_value=600,
        native_step=5,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        value_fn=_zone("max_cm"),
        set_fn=lambda c, v: c.async_send_command("set_zone", max_cm=int(v)),
    ),
    MmRadarNumberDescription(
        key="brightness",
        translation_key="brightness",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=5,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        value_fn=_brightness,
        set_fn=lambda c, v: c.async_send_command("set_display", brightness_pct=int(v)),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MmRadarConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """建立本平台的实体。"""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(MmRadarNumber(coordinator, d) for d in NUMBERS)


class MmRadarNumber(MmRadarEntity, NumberEntity):
    """一个可调数值实体。"""

    entity_description: MmRadarNumberDescription

    def __init__(self, coordinator: Any, description: MmRadarNumberDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        return self.entity_description.value_fn(self._snapshot())

    async def async_set_native_value(self, value: float) -> None:
        await self.entity_description.set_fn(self.coordinator, value)
        # 设备接受后会在下一拍推新快照，但等一拍会让滑块弹回旧值，
        # 看起来像没生效。主动拉一次让界面立刻对齐。
        await self.coordinator.async_request_refresh()
