"""Support for LED numbers."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .core import Device as OwcareDevice

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import OwcareDataUpdateCoordinator
from .helpers import owcare_exception_handler
from .models import OwcareEntity

PARALLEL_UPDATES = 1


@dataclass
class OwcareNumberDescriptionMixin:
    """Mixin for Owcare number."""

    value_fn: Callable[[OwcareDevice], int | None]
    update_fn: Callable[[OwcareDataUpdateCoordinator], None]


@dataclass
class OwcareNumberEntityDescription(
    NumberEntityDescription, OwcareNumberDescriptionMixin
):
    """Describes Owcare number entity."""

    exists_fn: Callable[[OwcareDevice], bool] = lambda _: True


NUMBERS = [
    OwcareNumberEntityDescription(
        key="setting_nobody_duration",
        translation_key="setting_nobody_duration",
        name="Speed",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        native_min_value=30,
        native_max_value=180,
        native_unit_of_measurement="MIN",
        value_fn=lambda device: device.setting.nobody_duration,
        update_fn=lambda coordinator, value: coordinator.client.setting(
            nobody_duration=value
        ),
    ),
    OwcareNumberEntityDescription(
        key="setting_stop_duration",
        translation_key="setting_stop_duration",
        entity_category=EntityCategory.CONFIG,
        native_step=5,
        native_min_value=5,
        native_max_value=120,
        native_unit_of_measurement="MIN",
        value_fn=lambda device: device.setting.stop_duration,
        update_fn=lambda coordinator, value: coordinator.client.setting(
            stop_duration=value
        ),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Owcare number based on a config entry."""
    coordinator: OwcareDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        OwcareNumberEntity(coordinator, description)
        for description in NUMBERS
        if description.exists_fn(coordinator.data)
    )


class OwcareNumberEntity(OwcareEntity, NumberEntity):
    """Defines a Owcare number entity."""

    entity_description: OwcareNumberEntityDescription

    def __init__(
        self,
        coordinator: OwcareDataUpdateCoordinator,
        description: OwcareNumberEntityDescription,
    ) -> None:
        """Initialize a Owcare switch entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.info.mac_addr}_{description.key}"

    @property
    def native_value(self) -> int | None:
        """Return the current Owcare number value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @owcare_exception_handler
    async def async_set_native_value(self, value: int) -> None:
        """Set the Owcare number value."""
        await self.entity_description.update_fn(self.coordinator, value)
