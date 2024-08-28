"""Sensor platform for owradar."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

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
from .coordinator import OwRadarDataUpdateCoordinator
from .models import OwRadarEntity


@dataclass
class OwRadarSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[OwRadarDevice], datetime | StateType]


@dataclass
class OwRadarSensorEntityDescription(
    SensorEntityDescription, OwRadarSensorEntityDescriptionMixin
):
    """Describes OwRadar sensor entity."""

    exists_fn: Callable[[OwRadarDevice], bool] = lambda _: True


SENSORS: tuple[OwRadarSensorEntityDescription, ...] = (
    OwRadarSensorEntityDescription(
        key="body_range",
        translation_key="body_range",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.body.range,
    ),
    OwRadarSensorEntityDescription(
        key="body_presence",
        translation_key="body_presence",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.body.presence,
        icon="mdi:location-enter",
    ),
    OwRadarSensorEntityDescription(
        key="body_movement",
        translation_key="body_movement",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.body.movement,
    ),
    OwRadarSensorEntityDescription(
        key="body_energy",
        translation_key="body_energy",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.body.energy,
    ),
    OwRadarSensorEntityDescription(
        key="body_distance",
        translation_key="body_distance",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.distance,
    ),
    OwRadarSensorEntityDescription(
        key="body_location_x",
        translation_key="body_location_x",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.x,
    ),
    OwRadarSensorEntityDescription(
        key="body_location_y",
        translation_key="body_location_y",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.y,
    ),
    OwRadarSensorEntityDescription(
        key="body_location_z",
        translation_key="body_location_z",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.z,
    ),
    OwRadarSensorEntityDescription(
        key="heart_rate",
        translation_key="heart_rate",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.rate,
        icon="mdi:heart",
    ),
    OwRadarSensorEntityDescription(
        key="heart_waves_w0",
        translation_key="heart_waves_w0",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w0,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="heart_waves_w1",
        translation_key="heart_waves_w1",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w1,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="heart_waves_w2",
        translation_key="heart_waves_w2",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w2,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="heart_waves_w3",
        translation_key="heart_waves_w3",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w3,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="heart_waves_w4",
        translation_key="heart_waves_w4",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w4,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="breath_info",
        translation_key="breath_info",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.breath.info,
    ),
    OwRadarSensorEntityDescription(
        key="breath_rate",
        translation_key="breath_rate",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.rate,
        icon="mdi:lungs",
    ),
    OwRadarSensorEntityDescription(
        key="breath_waves_w0",
        translation_key="breath_waves_w0",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w0,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="breath_waves_w1",
        translation_key="breath_waves_w1",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w1,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="breath_waves_w2",
        translation_key="breath_waves_w2",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w2,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="breath_waves_w3",
        translation_key="breath_waves_w3",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w3,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="breath_waves_w4",
        translation_key="breath_waves_w4",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w4,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_away",
        translation_key="sleep_away",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.away,
        icon="mdi:bed-outline",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_status",
        translation_key="sleep_status",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.status,
        icon="mdi:sleep",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_awake",
        translation_key="sleep_awake",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.awake,
    ),
    OwRadarSensorEntityDescription(
        key="sleep_light",
        translation_key="sleep_light",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.light,
    ),
    OwRadarSensorEntityDescription(
        key="sleep_deep",
        translation_key="sleep_deep",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.deep,
    ),
    OwRadarSensorEntityDescription(
        key="sleep_score",
        translation_key="sleep_score",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.score,
    ),
    OwRadarSensorEntityDescription(
        key="sleep_overview_presence",
        translation_key="sleep_overview_presence",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.overview.presence,
        icon="mdi:location-enter",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_overview_status",
        translation_key="sleep_overview_status",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.overview.status,
        icon="mdi:sleep",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_overview_breath",
        translation_key="sleep_overview_breath",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.breath,
        icon="mdi:lungs",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_overview_heart",
        translation_key="sleep_overview_heart",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.heart,
        icon="mdi:heart",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_overview_turn",
        translation_key="sleep_overview_turn",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.turn,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_overview_leratio",
        translation_key="sleep_overview_leratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.leratio,
        icon="mdi:percent",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_overview_seratio",
        translation_key="sleep_overview_seratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.seratio,
        icon="mdi:percent",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_overview_pause",
        translation_key="sleep_overview_pause",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.pause,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_quality_score",
        translation_key="sleep_quality_score",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.score,
    ),
    OwRadarSensorEntityDescription(
        key="sleep_quality_duration",
        translation_key="sleep_quality_duration",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.duration,
    ),
    OwRadarSensorEntityDescription(
        key="sleep_quality_awake",
        translation_key="sleep_quality_awake",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.awake,
        icon="mdi:percent",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_quality_light",
        translation_key="sleep_quality_light",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.light,
        icon="mdi:percent",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_quality_deep",
        translation_key="sleep_quality_deep",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.deep,
        icon="mdi:percent",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_quality_away",
        translation_key="sleep_quality_away",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.away,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_quality_turn",
        translation_key="sleep_quality_turn",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.turn,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_quality_breath",
        translation_key="sleep_quality_breath",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.breath,
        icon="mdi:lungs",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_quality_heart",
        translation_key="sleep_quality_heart",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.heart,
        icon="mdi:heart",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_quality_pause",
        translation_key="sleep_quality_pause",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.pause,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="sleep_exception",
        translation_key="sleep_exception",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.exception,
    ),
    OwRadarSensorEntityDescription(
        key="sleep_rating",
        translation_key="sleep_rating",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.rating,
    ),
    OwRadarSensorEntityDescription(
        key="sleep_struggle",
        translation_key="sleep_struggle",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.struggle,
    ),
    OwRadarSensorEntityDescription(
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
    """Set up OwRadar sensor based on a config entry."""
    coordinator: OwRadarDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        OwRadarSensorEntity(coordinator, description)
        for description in SENSORS
        if description.exists_fn(coordinator.data)
    )


class OwRadarSensorEntity(OwRadarEntity, SensorEntity):
    """Defines a OwRadar sensor entity."""

    entity_description: OwRadarSensorEntityDescription

    def __init__(
            self,
            coordinator: OwRadarDataUpdateCoordinator,
            description: OwRadarSensorEntityDescription,
    ) -> None:
        """Initialize a OwRadar sensor entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.info.mac_addr}_{description.key}"

    @property
    def native_value(self) -> datetime | StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)
