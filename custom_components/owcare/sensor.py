"""Sensor platform for owcare."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from .core import Device as OwcareDevice

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .coordinator import OwcareDataUpdateCoordinator
from .models import OwcareEntity


@dataclass
class OwcareSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[OwcareDevice], datetime | StateType]


@dataclass
class OwcareSensorEntityDescription(
    SensorEntityDescription, OwcareSensorEntityDescriptionMixin
):
    """Describes Owcare sensor entity."""

    exists_fn: Callable[[OwcareDevice], bool] = lambda _: True


SENSORS: tuple[OwcareSensorEntityDescription, ...] = (
    OwcareSensorEntityDescription(
        key="body_range",
        translation_key="body_range",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.body.range,
    ),
    OwcareSensorEntityDescription(
        key="body_presence",
        translation_key="body_presence",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.body.presence,
        icon="mdi:location-enter",
    ),
    OwcareSensorEntityDescription(
        key="body_movement",
        translation_key="body_movement",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.body.movement,
    ),
    OwcareSensorEntityDescription(
        key="body_energy",
        translation_key="body_energy",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.body.energy,
    ),
    OwcareSensorEntityDescription(
        key="body_distance",
        translation_key="body_distance",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.distance,
    ),
    OwcareSensorEntityDescription(
        key="body_location_x",
        translation_key="body_location_x",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.x,
    ),
    OwcareSensorEntityDescription(
        key="body_location_y",
        translation_key="body_location_y",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.y,
    ),
    OwcareSensorEntityDescription(
        key="body_location_z",
        translation_key="body_location_z",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.z,
    ),
    OwcareSensorEntityDescription(
        key="heart_rate",
        translation_key="heart_rate",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.rate,
        icon="mdi:heart",
    ),
    OwcareSensorEntityDescription(
        key="heart_waves_w0",
        translation_key="heart_waves_w0",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w0,
        icon="mdi:sine-wave",
    ),
    OwcareSensorEntityDescription(
        key="heart_waves_w1",
        translation_key="heart_waves_w1",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w1,
        icon="mdi:sine-wave",
    ),
    OwcareSensorEntityDescription(
        key="heart_waves_w2",
        translation_key="heart_waves_w2",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w2,
        icon="mdi:sine-wave",
    ),
    OwcareSensorEntityDescription(
        key="heart_waves_w3",
        translation_key="heart_waves_w3",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w3,
        icon="mdi:sine-wave",
    ),
    OwcareSensorEntityDescription(
        key="heart_waves_w4",
        translation_key="heart_waves_w4",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w4,
        icon="mdi:sine-wave",
    ),
    OwcareSensorEntityDescription(
        key="breath_info",
        translation_key="breath_info",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.breath.info,
    ),
    OwcareSensorEntityDescription(
        key="breath_rate",
        translation_key="breath_rate",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.rate,
        icon="mdi:lungs",
    ),
    OwcareSensorEntityDescription(
        key="breath_waves_w0",
        translation_key="breath_waves_w0",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w0,
        icon="mdi:sine-wave",
    ),
    OwcareSensorEntityDescription(
        key="breath_waves_w1",
        translation_key="breath_waves_w1",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w1,
        icon="mdi:sine-wave",
    ),
    OwcareSensorEntityDescription(
        key="breath_waves_w2",
        translation_key="breath_waves_w2",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w2,
        icon="mdi:sine-wave",
    ),
    OwcareSensorEntityDescription(
        key="breath_waves_w3",
        translation_key="breath_waves_w3",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w3,
        icon="mdi:sine-wave",
    ),
    OwcareSensorEntityDescription(
        key="breath_waves_w4",
        translation_key="breath_waves_w4",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w4,
        icon="mdi:sine-wave",
    ),
    OwcareSensorEntityDescription(
        key="sleep_away",
        translation_key="sleep_away",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.away,
        icon="mdi:bed-outline",
    ),
    OwcareSensorEntityDescription(
        key="sleep_status",
        translation_key="sleep_status",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.status,
        icon="mdi:sleep",
    ),
    OwcareSensorEntityDescription(
        key="sleep_awake",
        translation_key="sleep_awake",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.awake,
    ),
    OwcareSensorEntityDescription(
        key="sleep_light",
        translation_key="sleep_light",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.light,
    ),
    OwcareSensorEntityDescription(
        key="sleep_deep",
        translation_key="sleep_deep",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.deep,
    ),
    OwcareSensorEntityDescription(
        key="sleep_score",
        translation_key="sleep_score",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.score,
    ),
    OwcareSensorEntityDescription(
        key="sleep_overview_presence",
        translation_key="sleep_overview_presence",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.overview.presence,
        icon="mdi:location-enter",
    ),
    OwcareSensorEntityDescription(
        key="sleep_overview_status",
        translation_key="sleep_overview_status",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.overview.status,
        icon="mdi:sleep",
    ),
    OwcareSensorEntityDescription(
        key="sleep_overview_breath",
        translation_key="sleep_overview_breath",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.breath,
        icon="mdi:lungs",
    ),
    OwcareSensorEntityDescription(
        key="sleep_overview_heart",
        translation_key="sleep_overview_heart",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.heart,
        icon="mdi:heart",
    ),
    OwcareSensorEntityDescription(
        key="sleep_overview_turn",
        translation_key="sleep_overview_turn",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.turn,
        icon="mdi:counter",
    ),
    OwcareSensorEntityDescription(
        key="sleep_overview_leratio",
        translation_key="sleep_overview_leratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.leratio,
        icon="mdi:percent",
    ),
    OwcareSensorEntityDescription(
        key="sleep_overview_seratio",
        translation_key="sleep_overview_seratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.seratio,
        icon="mdi:percent",
    ),
    OwcareSensorEntityDescription(
        key="sleep_overview_pause",
        translation_key="sleep_overview_pause",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.pause,
        icon="mdi:counter",
    ),
    OwcareSensorEntityDescription(
        key="sleep_quality_score",
        translation_key="sleep_quality_score",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.score,
    ),
    OwcareSensorEntityDescription(
        key="sleep_quality_duration",
        translation_key="sleep_quality_duration",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.duration,
    ),
    OwcareSensorEntityDescription(
        key="sleep_quality_awake",
        translation_key="sleep_quality_awake",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.awake,
        icon="mdi:percent",
    ),
    OwcareSensorEntityDescription(
        key="sleep_quality_light",
        translation_key="sleep_quality_light",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.light,
        icon="mdi:percent",
    ),
    OwcareSensorEntityDescription(
        key="sleep_quality_deep",
        translation_key="sleep_quality_deep",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.deep,
        icon="mdi:percent",
    ),
    OwcareSensorEntityDescription(
        key="sleep_quality_away",
        translation_key="sleep_quality_away",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.away,
        icon="mdi:counter",
    ),
    OwcareSensorEntityDescription(
        key="sleep_quality_turn",
        translation_key="sleep_quality_turn",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.turn,
        icon="mdi:counter",
    ),
    OwcareSensorEntityDescription(
        key="sleep_quality_breath",
        translation_key="sleep_quality_breath",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.breath,
        icon="mdi:lungs",
    ),
    OwcareSensorEntityDescription(
        key="sleep_quality_heart",
        translation_key="sleep_quality_heart",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.heart,
        icon="mdi:heart",
    ),
    OwcareSensorEntityDescription(
        key="sleep_quality_pause",
        translation_key="sleep_quality_pause",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.pause,
        icon="mdi:counter",
    ),
    OwcareSensorEntityDescription(
        key="sleep_exception",
        translation_key="sleep_exception",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.exception,
    ),
    OwcareSensorEntityDescription(
        key="sleep_rating",
        translation_key="sleep_rating",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.rating,
    ),
    OwcareSensorEntityDescription(
        key="sleep_struggle",
        translation_key="sleep_struggle",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.struggle,
    ),
    OwcareSensorEntityDescription(
        key="sleep_nobody",
        translation_key="sleep_nobody",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.nobody,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Owcare sensor based on a config entry."""
    coordinator: OwcareDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        OwcareSensorEntity(coordinator, description)
        for description in SENSORS
        if description.exists_fn(coordinator.data)
    )


class OwcareSensorEntity(OwcareEntity, SensorEntity):
    """Defines a Owcare sensor entity."""

    entity_description: OwcareSensorEntityDescription

    def __init__(
        self,
        coordinator: OwcareDataUpdateCoordinator,
        description: OwcareSensorEntityDescription,
    ) -> None:
        """Initialize a Owcare sensor entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.info.mac_addr}_{description.key}"

    @property
    def native_value(self) -> datetime | StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
