"""Switch platform for owr_care."""
from __future__ import annotations

from functools import partial
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import OWRCareDataUpdateCoordinator
from .models import OWRCareEntity

PARALLEL_UPDATES = 1

@dataclass
class OWRCareSwitchEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[OWRCareDevice], bool | None]
    update_fn: Callable[[OWRCareDataUpdateCoordinator], None]


@dataclass
class OWRCareSwitchEntityDescription(
    SwitchEntityDescription, OWRCareSwitchEntityDescriptionMixin
):
    """Describes OWRCare switch entity."""

    exists_fn: Callable[[OWRCareDevice], bool] = lambda _: True


SWITCHES: tuple[OWRCareSwitchEntityDescription, ...] = [
    OWRCareSwitchEntityDescription(
        key="setting_binding",
        translation_key="setting_binding",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.state.setting.binding),
        update_fn=lambda coordinator, flag: coordinator.owrcare.setting(binding=flag),
    ),
    OWRCareSwitchEntityDescription(
        key="setting_realtime_ws",
        translation_key="setting_realtime_ws",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.state.setting.realtime_ws),
        update_fn=lambda coordinator, flag: coordinator.owrcare.setting(realtime_ws=flag),
    ),
    OWRCareSwitchEntityDescription(
        key="setting_realtime_mq",
        translation_key="setting_realtime_mq",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.state.setting.realtime_mq),
        update_fn=lambda coordinator, flag: coordinator.owrcare.setting(realtime_mq=flag),
    ),
    OWRCareSwitchEntityDescription(
        key="setting_body",
        translation_key="setting_body",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.state.setting.body),
        update_fn=lambda coordinator, flag: coordinator.owrcare.setting(body=flag),
    ),
    OWRCareSwitchEntityDescription(
        key="setting_heart",
        translation_key="setting_heart",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.state.setting.heart),
        update_fn=lambda coordinator, flag: coordinator.owrcare.setting(heart=flag),
    ),
    OWRCareSwitchEntityDescription(
        key="setting_breath",
        translation_key="setting_breath",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.state.setting.breath),
        update_fn=lambda coordinator, flag: coordinator.owrcare.setting(breath=flag),
    ),
    OWRCareSwitchEntityDescription(
        key="setting_sleep",
        translation_key="setting_sleep",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.state.setting.sleep),
        update_fn=lambda coordinator, flag: coordinator.owrcare.setting(sleep=flag),
    ),
    OWRCareSwitchEntityDescription(
        key="setting_mode",
        translation_key="setting_mode",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.state.setting.mode),
        update_fn=lambda coordinator, flag: coordinator.owrcare.setting(mode=flag),
    ),
    OWRCareSwitchEntityDescription(
        key="setting_nobody",
        translation_key="setting_nobody",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.state.setting.nobody),
        update_fn=lambda coordinator, flag: coordinator.owrcare.setting(nobody=flag),
    ),
    OWRCareSwitchEntityDescription(
        key="setting_struggle",
        translation_key="setting_struggle",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: bool(device.state.setting.struggle),
        update_fn=lambda coordinator, flag: coordinator.owrcare.setting(struggle=flag),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OWRCare switch based on a config entry."""
    coordinator: OWRCareDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        OWRCareSwitchEntity(coordinator, description)
        for description in SWITCHES
        if description.exists_fn(coordinator.data)
    )


class OWRCareSwitchEntify(OWRCareEntity, SwitchEntity):
    """Defines a OWRCare switch entity."""

    entity_description: OWRCareSwitchEntityDescription

    def __init__(
        self,
        coordinator: OWRCareDataUpdateCoordinator,
        description: OWRCareSwitchEntityDescription,
    ) -> None:
        """Initialize a OWRCare switch entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.info.mac_address}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self.entity_description.value_fn(self.coordinator.data)

    @owrcare_exception_handler
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the OWRCare setting switch."""
        await self.entity_description.update_fn(self.coordinator, False)

    @owrcare_exception_handler
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the OWRCare setting switch."""
        await self.entity_description.update_fn(self.coordinator, True)
