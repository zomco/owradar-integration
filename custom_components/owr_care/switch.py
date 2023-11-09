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

    value_fn: Callable[[OWRCareDevice], datetime | StateType]


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
        value_fn=lambda device: device.state.setting.binding,
    ),
    OWRCareSwitchEntityDescription(
        key="setting_realtime_ws",
        translation_key="setting_realtime_ws",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: device.state.setting.realtime_ws,
    ),
    OWRCareSwitchEntityDescription(
        key="setting_realtime_mq",
        translation_key="setting_realtime_mq",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: device.state.setting.realtime_mq,
    ),
    OWRCareSwitchEntityDescription(
        key="setting_body",
        translation_key="setting_body",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: device.state.setting.body,
    ),
    OWRCareSwitchEntityDescription(
        key="setting_heart",
        translation_key="setting_heart",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: device.state.setting.heart,
    ),
    OWRCareSwitchEntityDescription(
        key="setting_body",
        translation_key="setting_body",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: device.state.setting.body,
    ),
    OWRCareSwitchEntityDescription(
        key="setting_breath",
        translation_key="setting_breath",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: device.state.setting.breath,
    ),
    OWRCareSwitchEntityDescription(
        key="setting_sleep",
        translation_key="setting_sleep",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: device.state.setting.sleep,
    ),
    OWRCareSwitchEntityDescription(
        key="setting_mode",
        translation_key="setting_mode",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: device.state.setting.mode,
    ),
    OWRCareSwitchEntityDescription(
        key="setting_nobody",
        translation_key="setting_nobody",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: device.state.setting.nobody,
    ),
    OWRCareSwitchEntityDescription(
        key="setting_struggle",
        translation_key="setting_struggle",
        device_class=SwitchDeviceClass.SWITCH,
        value_fn=lambda device: device.state.setting.struggle,
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
        return bool(self.entity_description.value_fn(self.coordinator.data))

    @owrcare_exception_handler
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the OWRCare setting switch."""
        await self.coordinator.owrcare.setting(on=False)

    @owrcare_exception_handler
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the OWRCare setting switch."""
        await self.coordinator.owrcare.setting(on=True)
