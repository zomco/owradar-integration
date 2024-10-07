"""Switch platform for owradar."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
    SwitchDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import OwRadarDataUpdateCoordinator
from .entities import OwRadarEntity
from .helpers import owradar_exception_handler

PARALLEL_UPDATES = 1


@dataclass
class OwRadarSwitchEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[Any], bool | None]
    update_fn: Callable[[OwRadarDataUpdateCoordinator], Any]


@dataclass
class OwRadarSwitchEntityDescription(
    SwitchEntityDescription, OwRadarSwitchEntityDescriptionMixin
):
    """Describes OwRadar switch entity."""

    exists_fn: Callable[[Any], bool] = lambda _: True


COMMON_SETTING_SWITCHES: tuple[OwRadarSwitchEntityDescription, ...] = (
    OwRadarSwitchEntityDescription(
        key="setting_gatt_state",
        translation_key="setting_gatt_state",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.gatt_state),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"gatt_state": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_mqtt_state",
        translation_key="setting_mqtt_state",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.mqtt_state),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"mqtt_state": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_websocket_state",
        translation_key="setting_websocket_state",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.websocket_state),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"websocket_state": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_gatt_stats",
        translation_key="setting_gatt_stats",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.gatt_stats),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"gatt_stats": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_mqtt_stats",
        translation_key="setting_mqtt_stats",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.mqtt_stats),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"mqtt_stats": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_websocket_stats",
        translation_key="setting_websocket_stats",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.websocket_stats),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"websocket_stats": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_gatt_snap",
        translation_key="setting_gatt_snap",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.gatt_snap),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"gatt_snap": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_mqtt_snap",
        translation_key="setting_mqtt_snap",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.mqtt_snap),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"mqtt_snap": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_websocket_snap",
        translation_key="setting_websocket_snap",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.websocket_snap),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"websocket_snap": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_gatt_event",
        translation_key="setting_gatt_event",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.gatt_event),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"gatt_event": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_mqtt_event",
        translation_key="setting_mqtt_event",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.mqtt_event),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"mqtt_event": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_websocket_event",
        translation_key="setting_websocket_event",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.websocket_event),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"websocket_event": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_indicate",
        translation_key="setting_indicate",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.indicate),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"indicate": flag}),
    ),
)

R60ABD1_SETTING_SWITCHES: tuple[OwRadarSwitchEntityDescription, ...] = (
    OwRadarSwitchEntityDescription(
        key="setting_body",
        translation_key="setting_body",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.body),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"body": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_heart",
        translation_key="setting_heart",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.heart),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"heart": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_breath",
        translation_key="setting_breath",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.breath),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"breath": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_sleep",
        translation_key="setting_sleep",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.sleep),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"sleep": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_mode",
        translation_key="setting_mode",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.mode),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"mode": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_nobody",
        translation_key="setting_nobody",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.nobody),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"nobody": flag}),
    ),
    OwRadarSwitchEntityDescription(
        key="setting_struggle",
        translation_key="setting_struggle",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.setting.struggle),
        update_fn=lambda coordinator, flag: coordinator.client.setting(data={"struggle": flag}),
    ),
)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OwRadar switch based on a config entry."""
    coordinator: OwRadarDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    switches = COMMON_SETTING_SWITCHES + R60ABD1_SETTING_SWITCHES
    async_add_entities(
        OwRadarSwitchEntity(coordinator, description)
        for description in switches
        if description.exists_fn(coordinator.data)
    )


class OwRadarSwitchEntity(OwRadarEntity, SwitchEntity):
    """Defines a OwRadar switch entity."""

    entity_description: OwRadarSwitchEntityDescription

    def __init__(
            self,
            coordinator: OwRadarDataUpdateCoordinator,
            description: OwRadarSwitchEntityDescription,
    ) -> None:
        """Initialize a OwRadar switch entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.info.mac_addr}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self.entity_description.value_fn(self.coordinator.data)

    @owradar_exception_handler
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the OwRadar setting switch."""
        device = await self.entity_description.update_fn(self.coordinator, False)
        self.coordinator.async_set_updated_data(device)

    @owradar_exception_handler
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the OwRadar setting switch."""
        device = await self.entity_description.update_fn(self.coordinator, True)
        self.coordinator.async_set_updated_data(device)
