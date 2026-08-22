"""自定义服务：Discovery 表达不了的设备专属能力。

按钮实体覆盖的是「用默认参数的常用场景」；这里覆盖的是需要传参的场景。
两者调的是同一条设备命令，行为完全一致。
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .const import (
    DOMAIN,
    SERVICE_CALIBRATE_CO2,
    SERVICE_CALIBRATE_ZONE,
    SERVICE_IDENTIFY,
    SERVICE_SET_RADAR,
    SERVICE_SET_ZONE,
)
from .coordinator import MmRadarCoordinator

ATTR_DEVICE_ID = "device_id"

# 显式标注：vol.Required 是个对象不是字符串，mypy 推不出这个字典的键类型。
_DEVICE_SCHEMA: dict[Any, Any] = {vol.Required(ATTR_DEVICE_ID): cv.string}

SCHEMAS = {
    SERVICE_CALIBRATE_CO2: vol.Schema(
        {
            **_DEVICE_SCHEMA,
            vol.Optional("reference_ppm", default=420): vol.All(
                vol.Coerce(int), vol.Range(min=400, max=2000)
            ),
        }
    ),
    SERVICE_CALIBRATE_ZONE: vol.Schema(_DEVICE_SCHEMA),
    SERVICE_IDENTIFY: vol.Schema(_DEVICE_SCHEMA),
    SERVICE_SET_ZONE: vol.Schema(
        {
            **_DEVICE_SCHEMA,
            vol.Optional("min_cm"): vol.All(vol.Coerce(int), vol.Range(min=30, max=600)),
            vol.Optional("max_cm"): vol.All(vol.Coerce(int), vol.Range(min=30, max=600)),
        }
    ),
    # 雷达内部参数。上限用的是厂商标称的**可信范围**（运动 600 / 微动 350），
    # 不是协议上限（717 / 425）—— 超出可信范围数据不准，
    # 让用户配一个不准的值没有意义。
    SERVICE_SET_RADAR: vol.Schema(
        {
            **_DEVICE_SCHEMA,
            vol.Optional("motion_max_cm"): vol.All(vol.Coerce(int), vol.Range(min=30, max=600)),
            vol.Optional("still_max_cm"): vol.All(vol.Coerce(int), vol.Range(min=30, max=350)),
            vol.Optional("absence_delay_s"): vol.All(vol.Coerce(int), vol.Range(min=0, max=6553)),
        }
    ),
}

#: 服务名 -> 设备命令名。两者刻意不完全同名 ——
#: 服务名是给 HA 用户看的，命令名是契约里的线格式。
_COMMANDS = {
    SERVICE_CALIBRATE_CO2: "calibrate_co2",
    SERVICE_CALIBRATE_ZONE: "calibrate_zone",
    SERVICE_IDENTIFY: "identify",
    SERVICE_SET_ZONE: "set_zone",
    SERVICE_SET_RADAR: "set_radar",
}


def _coordinator_for(hass: HomeAssistant, device_id: str) -> MmRadarCoordinator:
    """由 HA 的设备 ID 找到对应的 coordinator。

    用户在服务调用里选的是 HA 设备，不是我们的 device_id ——
    要经设备注册表反查回 config entry。
    """
    registry = dr.async_get(hass)
    device = registry.async_get(device_id)
    if device is None:
        raise HomeAssistantError(f"找不到设备 {device_id}")

    for entry_id in device.config_entries:
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry is not None and entry.domain == DOMAIN and entry.runtime_data is not None:
            coordinator = entry.runtime_data.coordinator
            if isinstance(coordinator, MmRadarCoordinator):
                return coordinator

    raise HomeAssistantError(f"设备 {device_id} 不属于 {DOMAIN}，或尚未就绪")


def async_register_services(hass: HomeAssistant) -> None:
    """注册全部服务。重复调用是安全的 —— 多台设备会各调一次。"""

    async def _handle(call: ServiceCall) -> None:
        coordinator = _coordinator_for(hass, call.data[ATTR_DEVICE_ID])
        params = {k: v for k, v in call.data.items() if k != ATTR_DEVICE_ID}
        await coordinator.async_send_command(_COMMANDS[call.service], **params)

    for service, schema in SCHEMAS.items():
        if not hass.services.has_service(DOMAIN, service):
            hass.services.async_register(DOMAIN, service, _handle, schema=schema)
