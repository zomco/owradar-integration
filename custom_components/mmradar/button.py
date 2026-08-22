"""按钮：识别、标定、重启。

这几件事 Discovery 表达不了 —— 它们是动作不是状态。
同样的能力另有 service 形式（带参数），按钮只是把默认参数的常用场景
放到卡片上，让用户不必去写 service 调用。
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MmRadarConfigEntry
from .coordinator import MmRadarCoordinator
from .entity import MmRadarEntity


@dataclass(frozen=True, kw_only=True)
class MmRadarButtonDescription(ButtonEntityDescription):
    """按钮描述：多一个按下时执行的协程。"""

    press_fn: Callable[[MmRadarCoordinator], Awaitable[Any]]


BUTTONS: tuple[MmRadarButtonDescription, ...] = (
    MmRadarButtonDescription(
        key="identify",
        translation_key="identify",
        entity_category=EntityCategory.CONFIG,
        press_fn=lambda c: c.async_send_command("identify"),
    ),
    MmRadarButtonDescription(
        key="calibrate_co2",
        translation_key="calibrate_co2",
        entity_category=EntityCategory.CONFIG,
        # 420ppm = 户外新鲜空气。按钮用默认值，
        # 要自定义参考值的话走 mmradar.calibrate_co2 服务。
        press_fn=lambda c: c.async_send_command("calibrate_co2", reference_ppm=420),
    ),
    MmRadarButtonDescription(
        key="calibrate_zone",
        translation_key="calibrate_zone",
        entity_category=EntityCategory.CONFIG,
        press_fn=lambda c: c.async_send_command("calibrate_zone"),
    ),
    MmRadarButtonDescription(
        key="reboot",
        translation_key="reboot",
        entity_category=EntityCategory.CONFIG,
        press_fn=lambda c: c.async_send_command("reboot"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MmRadarConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """建立本平台的实体。"""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(MmRadarButton(coordinator, d) for d in BUTTONS)


class MmRadarButton(MmRadarEntity, ButtonEntity):
    """一个按钮实体。"""

    entity_description: MmRadarButtonDescription

    def __init__(self, coordinator: Any, description: MmRadarButtonDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        await self.entity_description.press_fn(self.coordinator)
