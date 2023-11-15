"""Support for LED numbers."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .core import Device as OWRCareDevice

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import OWRCareDataUpdateCoordinator
from .helpers import owrcare_exception_handler
from .models import OWRCareEntity

PARALLEL_UPDATES = 1


@dataclass
class OWRCareNumberDescriptionMixin:
    """Mixin for OWRCare number."""

    value_fn: Callable[[OWRCareDevice], int | None]
    update_fn: Callable[[OWRCareDataUpdateCoordinator], None]


@dataclass
class OWRCareNumberEntityDescription(
    NumberEntityDescription, OWRCareNumberDescriptionMixin
):
    """Describes OWRCare number entity."""

    exists_fn: Callable[[OWRCareDevice], bool] = lambda _: True


NUMBERS = [
    OWRCareNumberEntityDescription(
        key="setting_nobody_duration",
        translation_key="setting_nobody_duration",
        name="Speed",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        native_min_value=30,
        native_max_value=180,
        value_fn=lambda device: device.setting.nobody_duration,
        update_fn=lambda coordinator, value: coordinator.owrcare.setting(
            nobody_duration=value
        ),
    ),
    OWRCareNumberEntityDescription(
        key="setting_stop_duration",
        translation_key="setting_stop_duration",
        entity_category=EntityCategory.CONFIG,
        native_step=5,
        native_min_value=5,
        native_max_value=120,
        value_fn=lambda device: device.setting.stop_duration,
        update_fn=lambda coordinator, value: coordinator.owrcare.setting(
            stop_duration=value
        ),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OWRCare number based on a config entry."""
    coordinator: OWRCareDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        OWRCareNumberEntity(coordinator, description)
        for description in NUMBERS
        if description.exists_fn(coordinator.data)
    )


class OWRCareNumberEntity(OWRCareEntity, NumberEntity):
    """Defines a OWRCare number entity."""

    entity_description: OWRCareNumberEntityDescription

    def __init__(
        self,
        coordinator: OWRCareDataUpdateCoordinator,
        description: OWRCareNumberEntityDescription,
    ) -> None:
        """Initialize a OWRCare switch entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.info.mac_addr}_{description.key}"

    @property
    def native_value(self) -> int | None:
        """Return the current OWRCare number value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @owrcare_exception_handler
    async def async_set_native_value(self, value: int) -> None:
        """Set the OWRCare number value."""
        await self.entity_description.update_fn(self.coordinator, value)
