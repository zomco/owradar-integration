"""mmRadar 桌面助理的 Home Assistant 集成。

直连设备的局域网 API，不需要 MQTT broker。
与固件的 MQTT Discovery 路径产生**完全一致**的实体，
用户在两条路径之间切换不会丢历史数据。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MmRadarApi, MmRadarAuthError, MmRadarConnectionError
from .const import CONF_TOKEN, DEFAULT_PORT
from .coordinator import MmRadarCoordinator
from .services import async_register_services

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SENSOR,
]


@dataclass
class MmRadarData:
    """存进 `entry.runtime_data` 的运行时对象。

    用 runtime_data 而不是 `hass.data[DOMAIN][entry_id]`：
    前者由 HA 管理生命周期，卸载时自动清掉，不会留下悬挂引用。
    """

    api: MmRadarApi
    coordinator: MmRadarCoordinator


type MmRadarConfigEntry = ConfigEntry[MmRadarData]


async def async_setup_entry(hass: HomeAssistant, entry: MmRadarConfigEntry) -> bool:
    """建立与一台设备的连接。"""
    session = async_get_clientsession(hass)
    api = MmRadarApi(
        session,
        host=entry.data[CONF_HOST],
        token=entry.data[CONF_TOKEN],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
    )

    # 先探一次 info：拿固件版本，也顺便确认设备真的在。
    # 免鉴权接口，所以 Token 有问题的话会在下一步才暴露 —— 这是有意的，
    # 能区分「设备不在」和「Token 不对」，前者要重试，后者要重新配对。
    try:
        info = await api.async_get_info()
    except MmRadarConnectionError as err:
        raise ConfigEntryNotReady(f"连不上设备: {err}") from err

    device_id = str(info.get("device_id") or entry.unique_id or "")
    coordinator = MmRadarCoordinator(hass, entry, api, device_id)
    fw = info.get("fw_version")
    coordinator.fw_version = str(fw) if isinstance(fw, str) else None

    try:
        await coordinator.async_start()
    except MmRadarAuthError as err:
        # ConfigEntryAuthFailed 会让 HA 弹出重新认证的流程，
        # 而不是无限重试一个永远不会成功的连接
        raise ConfigEntryAuthFailed(str(err)) from err
    except Exception as err:
        await coordinator.async_shutdown()
        raise ConfigEntryNotReady(str(err)) from err

    entry.runtime_data = MmRadarData(api=api, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    async_register_services(hass)

    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: MmRadarConfigEntry) -> bool:
    """卸载一台设备，关掉它的 WS 循环。"""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.coordinator.async_shutdown()
    return unloaded


async def _async_reload(hass: HomeAssistant, entry: MmRadarConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
