"""Sensor platform for owradar."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

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
from .core.common_models import OwRadarCommonSettingSwitch
from .entities import OwRadarEntity


@dataclass
class OwRadarSensorEntityDescriptionMixin:
    """Mixin for required keys."""

    value_fn: Callable[[Any], datetime | StateType]


@dataclass
class OwRadarSensorEntityDescription(
    SensorEntityDescription, OwRadarSensorEntityDescriptionMixin
):
    """Describes OwRadar sensor entity."""

    exists_fn: Callable[[Any], bool] = lambda _: True


R60ABD1_STATE_SENSORS: tuple[OwRadarSensorEntityDescription, ...] = (
    OwRadarSensorEntityDescription(
        key="state_body_range",
        translation_key="state_body_range",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.body.range,
        exists_fn=lambda device: device.setting.websocket_state == OwRadarCommonSettingSwitch.ON,
    ),
    OwRadarSensorEntityDescription(
        key="state_body_presence",
        translation_key="state_body_presence",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.body.presence,
        exists_fn=lambda device: device.setting.websocket_state == OwRadarCommonSettingSwitch.ON,
        icon="mdi:location-enter",
    ),
    OwRadarSensorEntityDescription(
        key="state_body_movement",
        translation_key="state_body_movement",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.body.movement,
        exists_fn=lambda device: device.setting.websocket_state == OwRadarCommonSettingSwitch.ON,
    ),
    OwRadarSensorEntityDescription(
        key="state_body_energy",
        translation_key="state_body_energy",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.body.energy,
        exists_fn=lambda device: device.setting.websocket_state == OwRadarCommonSettingSwitch.ON,
    ),
    OwRadarSensorEntityDescription(
        key="state_body_distance",
        translation_key="state_body_distance",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.distance,
        exists_fn=lambda device: device.setting.websocket_state == OwRadarCommonSettingSwitch.ON,
    ),
    OwRadarSensorEntityDescription(
        key="state_body_location_x",
        translation_key="state_body_location_x",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.x,
        exists_fn=lambda device: device.setting.websocket_state == OwRadarCommonSettingSwitch.ON,
    ),
    OwRadarSensorEntityDescription(
        key="state_body_location_y",
        translation_key="state_body_location_y",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.y,
    ),
    OwRadarSensorEntityDescription(
        key="state_body_location_z",
        translation_key="state_body_location_z",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        value_fn=lambda device: device.state.body.location.z,
    ),
    OwRadarSensorEntityDescription(
        key="state_heart_rate",
        translation_key="state_heart_rate",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.rate,
        icon="mdi:heart",
    ),
    OwRadarSensorEntityDescription(
        key="state_heart_waves_w0",
        translation_key="state_heart_waves_w0",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w0,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="state_heart_waves_w1",
        translation_key="state_heart_waves_w1",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w1,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="state_heart_waves_w2",
        translation_key="state_heart_waves_w2",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w2,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="state_heart_waves_w3",
        translation_key="state_heart_waves_w3",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w3,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="state_heart_waves_w4",
        translation_key="state_heart_waves_w4",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.heart.waves.w4,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="state_breath_info",
        translation_key="state_breath_info",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.breath.info,
    ),
    OwRadarSensorEntityDescription(
        key="state_breath_rate",
        translation_key="state_breath_rate",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.rate,
        icon="mdi:lungs",
    ),
    OwRadarSensorEntityDescription(
        key="state_breath_waves_w0",
        translation_key="state_breath_waves_w0",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w0,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="state_breath_waves_w1",
        translation_key="state_breath_waves_w1",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w1,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="state_breath_waves_w2",
        translation_key="state_breath_waves_w2",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w2,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="state_breath_waves_w3",
        translation_key="state_breath_waves_w3",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w3,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="state_breath_waves_w4",
        translation_key="state_breath_waves_w4",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.breath.waves.w4,
        icon="mdi:sine-wave",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_away",
        translation_key="state_sleep_away",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.away,
        icon="mdi:bed-outline",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_status",
        translation_key="state_sleep_status",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.status,
        icon="mdi:sleep",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_awake",
        translation_key="state_sleep_awake",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.awake,
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_light",
        translation_key="state_sleep_light",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.light,
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_deep",
        translation_key="state_sleep_deep",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.deep,
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_score",
        translation_key="state_sleep_score",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.score,
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_overview_presence",
        translation_key="state_sleep_overview_presence",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.overview.presence,
        icon="mdi:location-enter",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_overview_status",
        translation_key="state_sleep_overview_status",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.overview.status,
        icon="mdi:sleep",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_overview_breath",
        translation_key="state_sleep_overview_breath",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.breath,
        icon="mdi:lungs",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_overview_heart",
        translation_key="state_sleep_overview_heart",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.heart,
        icon="mdi:heart",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_overview_turn",
        translation_key="state_sleep_overview_turn",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.turn,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_overview_leratio",
        translation_key="state_sleep_overview_leratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.leratio,
        icon="mdi:percent",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_overview_seratio",
        translation_key="state_sleep_overview_seratio",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.seratio,
        icon="mdi:percent",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_overview_pause",
        translation_key="state_sleep_overview_pause",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.overview.pause,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_quality_score",
        translation_key="state_sleep_quality_score",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.score,
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_quality_duration",
        translation_key="state_sleep_quality_duration",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.duration,
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_quality_awake",
        translation_key="state_sleep_quality_awake",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.awake,
        icon="mdi:percent",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_quality_light",
        translation_key="state_sleep_quality_light",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.light,
        icon="mdi:percent",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_quality_deep",
        translation_key="state_sleep_quality_deep",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.deep,
        icon="mdi:percent",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_quality_away",
        translation_key="state_sleep_quality_away",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.away,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_quality_turn",
        translation_key="state_sleep_quality_turn",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.turn,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_quality_breath",
        translation_key="state_sleep_quality_breath",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.breath,
        icon="mdi:lungs",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_quality_heart",
        translation_key="state_sleep_quality_heart",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.heart,
        icon="mdi:heart",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_quality_pause",
        translation_key="state_sleep_quality_pause",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.sleep.quality.pause,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_exception",
        translation_key="state_sleep_exception",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.exception,
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_rating",
        translation_key="state_sleep_rating",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.rating,
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_struggle",
        translation_key="state_sleep_struggle",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.struggle,
    ),
    OwRadarSensorEntityDescription(
        key="state_sleep_nobody",
        translation_key="state_sleep_nobody",
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.state.sleep.nobody,
    ),
)

R60ABD1_STATS_SENSORS: tuple[OwRadarSensorEntityDescription, ...] = (
    OwRadarSensorEntityDescription(
        key="stats_status",
        translation_key="stats_status",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.stats.status,
        icon="mdi:sleep",
    ),
    OwRadarSensorEntityDescription(
        key="stats_breath",
        translation_key="stats_breath",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.stats.breath,
        icon="mdi:lungs",
    ),
    OwRadarSensorEntityDescription(
        key="stats_heart",
        translation_key="stats_heart",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.stats.heart,
        icon="mdi:heart",
    ),
    OwRadarSensorEntityDescription(
        key="stats_turn",
        translation_key="stats_turn",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.stats.turn,
        icon="mdi:counter",
    ),
)

R60ABD1_SNAP_SENSORS: tuple[OwRadarSensorEntityDescription, ...] = (
    OwRadarSensorEntityDescription(
        key="snap_body_range",
        translation_key="snap_body_range",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.snap.body_range,
        icon="mdi:sleep",
    ),
    OwRadarSensorEntityDescription(
        key="snap_body_presence",
        translation_key="snap_body_presence",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.snap.body_presence,
        icon="mdi:lungs",
    ),
    OwRadarSensorEntityDescription(
        key="snap_body_energy",
        translation_key="snap_body_energy",
        native_unit_of_measurement="BPM",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.snap.body_energy,
        icon="mdi:heart",
    ),
    OwRadarSensorEntityDescription(
        key="snap_body_movement",
        translation_key="snap_body_movement",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.snap.body_movement,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="snap_body_distance",
        translation_key="snap_body_distance",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.snap.body_distance,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="snap_body_location_x",
        translation_key="snap_body_location_x",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.snap.body_location_x,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="snap_body_location_y",
        translation_key="snap_body_location_y",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.snap.body_location_y,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="snap_heart_rate",
        translation_key="snap_heart_rate",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.snap.heart_rate,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="snap_breath_rate",
        translation_key="snap_breath_rate",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.snap.breath_rate,
        icon="mdi:counter",
    ),
    OwRadarSensorEntityDescription(
        key="snap_sleep_away",
        translation_key="snap_sleep_away",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.snap.sleep_away,
        icon="mdi:counter",
    ),
)

R60ABD1_EVENT_SENSORS: tuple[OwRadarSensorEntityDescription, ...] = (
    OwRadarSensorEntityDescription(
        key="event_status",
        translation_key="event_status",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.ENUM,
        value_fn=lambda device: device.event.status,
        icon="mdi:sleep",
    ),
)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OwRadar sensor based on a config entry."""
    coordinator: OwRadarDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = R60ABD1_STATS_SENSORS + R60ABD1_STATE_SENSORS + R60ABD1_SNAP_SENSORS + R60ABD1_EVENT_SENSORS
    async_add_entities(
        OwSensorEntity(coordinator, description)
        for description in sensors
        if description.exists_fn(coordinator.data)
    )


class OwSensorEntity(OwRadarEntity, SensorEntity):
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
