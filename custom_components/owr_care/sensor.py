"""Sensor platform for owr_care."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from .owrcare import Device as OWRCareDevice

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfInformation,
    UnitOfLength
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util.dt import utcnow

from .const import DOMAIN
from .coordinator import OWRCareDataUpdateCoordinator
from .models import OWRCareEntity


@dataclass
class OWRCareSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[OWRCareDevice], datetime | StateType]


@dataclass
class OWRCareSensorEntityDescription(
    SensorEntityDescription, OWRCareSensorEntityDescriptionMixin
):
    """Describes OWRCare sensor entity."""

    exists_fn: Callable[[OWRCareDevice], bool] = lambda _: True


SENSORS: tuple[OWRCareSensorEntityDescription, ...] = (
    OWRCareSensorEntityDescription(
        key="body_range",
        translation_key="body_range",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.body.range,
    ),
    OWRCareSensorEntityDescription(
        key="body_info",
        translation_key="body_info",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.body.info,
    ),
    OWRCareSensorEntityDescription(
        key="body_movement",
        translation_key="body_movement",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.body.movement,
    ),
    OWRCareSensorEntityDescription(
        key="body_energy",
        translation_key="body_energy",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.body.energy,
    ),
    OWRCareSensorEntityDescription(
        key="body_distance",
        translation_key="body_distance",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.distance,
    ),
    OWRCareSensorEntityDescription(
        key="body_location_x",
        translation_key="body_location_x",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.x,
    ),
    OWRCareSensorEntityDescription(
        key="body_location_y",
        translation_key="body_location_y",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.y,
    ),
    OWRCareSensorEntityDescription(
        key="body_location_z",
        translation_key="body_location_z",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.z,
    ),
    OWRCareSensorEntityDescription(
        key="heart_rate",
        translation_key="heart_rate",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.rate,
    ),
    OWRCareSensorEntityDescription(
        key="heart_waves_w0",
        translation_key="heart_waves_w0",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w0,
    ),
    OWRCareSensorEntityDescription(
        key="heart_waves_w1",
        translation_key="heart_waves_w1",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w1,
    ),
    OWRCareSensorEntityDescription(
        key="heart_waves_w2",
        translation_key="heart_waves_w2",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w2,
    ),
    OWRCareSensorEntityDescription(
        key="heart_waves_w3",
        translation_key="heart_waves_w3",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w3,
    ),
    OWRCareSensorEntityDescription(
        key="heart_waves_w4",
        translation_key="heart_waves_w4",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w4,
    ),
    OWRCareSensorEntityDescription(
        key="breath_info",
        translation_key="breath_info",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.info,
    ),
    OWRCareSensorEntityDescription(
        key="breath_rate",
        translation_key="breath_rate",
        icon="mdi:wifi",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.rate,
    ),
    OWRCareSensorEntityDescription(
        key="breath_waves_w0",
        translation_key="breath_waves_w0",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w0,
    ),
    OWRCareSensorEntityDescription(
        key="breath_waves_w1",
        translation_key="breath_waves_w1",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w1,
    ),
    OWRCareSensorEntityDescription(
        key="breath_waves_w2",
        translation_key="breath_waves_w2",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w2,
    ),
    OWRCareSensorEntityDescription(
        key="breath_waves_w3",
        translation_key="breath_waves_w3",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w3,
    ),
    OWRCareSensorEntityDescription(
        key="breath_waves_w4",
        translation_key="breath_waves_w4",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w4,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_away",
        translation_key="sleep_away",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.away,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_status",
        translation_key="sleep_status",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.status,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_awake",
        translation_key="sleep_awake",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.awake,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_light",
        translation_key="sleep_light",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.light,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_deep",
        translation_key="sleep_deep",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.deep,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_score",
        translation_key="sleep_score",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.score,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_overview_presence",
        translation_key="sleep_overview_presence",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.presence,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_overview_status",
        translation_key="sleep_overview_status",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.status,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_overview_breath",
        translation_key="sleep_overview_breath",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.breath,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_overview_heart",
        translation_key="sleep_overview_heart",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.heart,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_overview_turn",
        translation_key="sleep_overview_turn",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.turn,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_overview_leratio",
        translation_key="sleep_overview_leratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.leratio,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_overview_seratio",
        translation_key="sleep_overview_seratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.seratio,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_overview_pause",
        translation_key="sleep_overview_pause",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.pause,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_quality_score",
        translation_key="sleep_quality_score",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.score,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_quality_duration",
        translation_key="sleep_quality_duration",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.duration,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_quality_awake",
        translation_key="sleep_quality_awake",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.awake,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_quality_light",
        translation_key="sleep_quality_light",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.light,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_quality_deep",
        translation_key="sleep_quality_deep",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.deep,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_quality_away",
        translation_key="sleep_quality_away",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.away,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_quality_turn",
        translation_key="sleep_quality_turn",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.turn,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_quality_breath",
        translation_key="sleep_quality_breath",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.breath,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_quality_heart",
        translation_key="sleep_quality_heart",
        native_unit_of_measurement="bpm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.heart,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_quality_pause",
        translation_key="sleep_quality_pause",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.pause,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_exception",
        translation_key="sleep_exception",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.exception,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_rating",
        translation_key="sleep_rating",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.rating,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_struggle",
        translation_key="sleep_struggle",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.struggle,
    ),
    OWRCareSensorEntityDescription(
        key="sleep_nobody",
        translation_key="sleep_nobody",
        device_class=SensorDeviceClass.ENUM,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.nobody,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OWRCare sensor based on a config entry."""
    coordinator: OWRCareDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        OWRCareSensorEntity(coordinator, description)
        for description in SENSORS
        if description.exists_fn(coordinator.data)
    )


class OWRCareSensorEntity(OWRCareEntity, SensorEntity):
    """Defines a OWRCare sensor entity."""

    entity_description: OWRCareSensorEntityDescription

    def __init__(
        self,
        coordinator: OWRCareDataUpdateCoordinator,
        description: OWRCareSensorEntityDescription,
    ) -> None:
        """Initialize a OWRCare sensor entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.info.mac_addr}_{description.key}"

    @property
    def native_value(self) -> datetime | StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

