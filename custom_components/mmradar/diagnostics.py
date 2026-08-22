"""诊断信息导出。

用户在 HA 的设备页点「下载诊断」时调用，导出的内容会被贴进 issue。
**因此它的第一要务是不泄露凭证**，第二才是有用。

会泄露的东西只有两类，都必须打码：
- 配对 Token（`pairing_token`）—— 拿到它就能读走这台设备的全部数据
- Wi-Fi SSID —— 不是凭证，但足以定位到具体某个家庭/办公室

`host` 不打码：它是内网地址（192.168.x.x），排障时几乎总要用到，
而它对屋外的人没有意义。
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import MmRadarConfigEntry
from .const import ALL_ENTITY_KEYS, CONF_TOKEN

#: 配置项里要打码的键。
TO_REDACT_CONFIG = {CONF_TOKEN}

#: 快照里要打码的键。`async_redact_data` 会递归匹配。
TO_REDACT_DATA = {"wifi_ssid"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: MmRadarConfigEntry,
) -> dict[str, Any]:
    """导出一台设备的诊断信息。"""
    coordinator = entry.runtime_data.coordinator
    snapshot = coordinator.data if isinstance(coordinator.data, dict) else {}

    missing = sorted(ALL_ENTITY_KEYS - coordinator.capabilities)

    return {
        "config": async_redact_data(dict(entry.data), TO_REDACT_CONFIG),
        "device": {
            "device_id": coordinator.device_id,
            "fw_version": coordinator.fw_version,
            # 快照里的 schema_version 与集成编译期的预期不一致时，
            # 大多数「字段读不到」的报障都能在这里一眼看出来。
            "schema_version": snapshot.get("schema_version"),
        },
        "connection": {
            "available": coordinator.last_update_success,
            # 实体全 unavailable 时，这两个字段能区分
            # 「连不上」和「连上了但设备不推数据」—— 两者的排查方向完全不同。
            "seconds_since_last_frame": coordinator.seconds_since_last_frame(),
            "links": snapshot.get("links"),
        },
        "capabilities": {
            "supported": sorted(coordinator.capabilities),
            "missing": missing,
            # 把「为什么没有这个实体」直接写进诊断，
            # 免得用户和维护者各猜一遍
            "note": (
                "missing 里的实体是按快照探测出这台设备不具备的（health=absent 或字段缺失），"
                "不是故障。传感器故障的表达是 health=fault，实体仍会建出来并显示 unavailable。"
            )
            if missing
            else "这台设备支持契约里的全部实体。",
        },
        "snapshot": async_redact_data(snapshot, TO_REDACT_DATA),
    }
