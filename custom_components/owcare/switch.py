"""Switch platform for owcare."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .core import Device as OwcareDevice

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
    SwitchDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import OwcareDataUpdateCoordinator
from .helpers import owcare_exception_handler
from .models import OwcareEntity

PARALLEL_UPDATES = 1


@dataclass
class OwcareSwitchEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[OwcareDevice], bool | None]
    update_fn: Callable[[OwcareDataUpdateCoordinator], OwcareDevice]


@dataclass
class OwcareSwitchEntityDescription(
    SwitchEntityDescription, OwcareSwitchEntityDescriptionMixin
):
    """Describes Owcare switch entity."""

    exists_fn: Callable[[OwcareDevice], bool] = lambda _: True


SWITCHES: tuple[OwcareSwitchEntityDescription, ...] = [
    OwcareSwitchEntityDescription(
        key="setting_realtime_ws",
        translation_key="setting_realtime_ws",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.realtime_ws),
        update_fn=lambda coordinator, flag: coordinator.client.setting(
            realtime_ws=flag
        ),
    ),
    OwcareSwitchEntityDescription(
        key="setting_body",
        translation_key="setting_body",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.body),
        update_fn=lambda coordinator, flag: coordinator.client.setting(body=flag),
    ),
    OwcareSwitchEntityDescription(
        key="setting_heart",
        translation_key="setting_heart",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.heart),
        update_fn=lambda coordinator, flag: coordinator.client.setting(heart=flag),
    ),
    OwcareSwitchEntityDescription(
        key="setting_breath",
        translation_key="setting_breath",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.breath),
        update_fn=lambda coordinator, flag: coordinator.client.setting(breath=flag),
    ),
    OwcareSwitchEntityDescription(
        key="setting_sleep",
        translation_key="setting_sleep",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.sleep),
        update_fn=lambda coordinator, flag: coordinator.client.setting(sleep=flag),
    ),
    OwcareSwitchEntityDescription(
        key="setting_mode",
        translation_key="setting_mode",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.mode),
        update_fn=lambda coordinator, flag: coordinator.client.setting(mode=flag),
    ),
    OwcareSwitchEntityDescription(
        key="setting_nobody",
        translation_key="setting_nobody",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.nobody),
        update_fn=lambda coordinator, flag: coordinator.client.setting(nobody=flag),
    ),
    OwcareSwitchEntityDescription(
        key="setting_struggle",
        translation_key="setting_struggle",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.struggle),
        update_fn=lambda coordinator, flag: coordinator.client.setting(struggle=flag),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Owcare switch based on a config entry."""
    coordinator: OwcareDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        OwcareSwitchEntity(coordinator, description)
        for description in SWITCHES
        if description.exists_fn(coordinator.data)
    )


class OwcareSwitchEntity(OwcareEntity, SwitchEntity):
    """Defines a Owcare switch entity."""

    entity_description: OwcareSwitchEntityDescription

    def __init__(
        self,
        coordinator: OwcareDataUpdateCoordinator,
        description: OwcareSwitchEntityDescription,
    ) -> None:
        """Initialize a Owcare switch entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.info.mac_addr}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self.entity_description.value_fn(self.coordinator.data)

    @owcare_exception_handler
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the Owcare setting switch."""
        device = await self.entity_description.update_fn(self.coordinator, False)
        self.coordinator.async_set_updated_data(device)

    @owcare_exception_handler
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the Owcare setting switch."""
        device = await self.entity_description.update_fn(self.coordinator, True)
        self.coordinator.async_set_updated_data(device)
