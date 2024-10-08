"""Support for LED numbers."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import OwRadarDataUpdateCoordinator
from .entities import OwRadarEntity
from .helpers import owradar_exception_handler

PARALLEL_UPDATES = 1


@dataclass
class OwRadarNumberDescriptionMixin:
    """Mixin for OwRadar number."""

    value_fn: Callable[[Any], int | None]
    update_fn: Callable[[OwRadarDataUpdateCoordinator], None]


@dataclass
class OwRadarNumberEntityDescription(
    NumberEntityDescription, OwRadarNumberDescriptionMixin
):
    """Describes OwRadar number entity."""

    exists_fn: Callable[[Any], bool] = lambda _: True


COMMON_SETTING_NUMBERS: tuple[OwRadarNumberEntityDescription, ...] = (
    OwRadarNumberEntityDescription(
        key="setting_interval",
        translation_key="setting_interval",
        name="Speed",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        native_min_value=3,
        native_max_value=60,
        native_unit_of_measurement="MIN",
        value_fn=lambda device: device.setting.nobody_duration,
        update_fn=lambda coordinator, value: coordinator.client.setting(data={"interval": value}),
    ),
)

R60ABD1_SETTING_NUMBERS: tuple[OwRadarNumberEntityDescription, ...] = (
    OwRadarNumberEntityDescription(
        key="setting_nobody_duration",
        translation_key="setting_nobody_duration",
        name="Speed",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        native_min_value=30,
        native_max_value=180,
        native_unit_of_measurement="MIN",
        value_fn=lambda device: device.setting.nobody_duration,
        update_fn=lambda coordinator, value: coordinator.client.setting(data={"nobody_duration": value}),
    ),
    OwRadarNumberEntityDescription(
        key="setting_stop_duration",
        translation_key="setting_stop_duration",
        entity_category=EntityCategory.CONFIG,
        native_step=5,
        native_min_value=5,
        native_max_value=120,
        native_unit_of_measurement="MIN",
        value_fn=lambda device: device.setting.stop_duration,
        update_fn=lambda coordinator, value: coordinator.client.setting(data={"stop_duration": value}),
    ),
)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OwRadar number based on a config entry."""
    coordinator: OwRadarDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    numbers = COMMON_SETTING_NUMBERS + R60ABD1_SETTING_NUMBERS
    async_add_entities(
        OwRadarNumberEntity(coordinator, description)
        for description in numbers
        if description.exists_fn(coordinator.data)
    )


class OwRadarNumberEntity(OwRadarEntity, NumberEntity):
    """Defines a OwRadar number entity."""

    entity_description: OwRadarNumberEntityDescription

    def __init__(
            self,
            coordinator: OwRadarDataUpdateCoordinator,
            description: OwRadarNumberEntityDescription,
    ) -> None:
        """Initialize a OwRadar switch entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.info.mac_addr}_{description.key}"

    @property
    def native_value(self) -> int | None:
        """Return the current OwRadar number value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @owradar_exception_handler
    async def async_set_native_value(self, value: int) -> None:
        """Set the OwRadar number value."""
        await self.entity_description.update_fn(self.coordinator, value)
