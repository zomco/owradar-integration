"""实体基类。

所有实体共用同一份 `device_info`，这样它们在 HA 里归到同一台设备下。

`unique_id` 形如 `<device_id>_<key>`，**与固件的 MQTT Discovery 完全一致** ——
用户从 MQTT 切到本集成（或反过来）时，实体 ID 不变，
历史数据与自动化配置都能延续。这不是巧合，是 `tests/test_contract_parity.py`
在守着的约束。
"""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import get_path
from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import MmRadarCoordinator


class MmRadarEntity(CoordinatorEntity[MmRadarCoordinator]):
    """带设备归属与可用性判定的实体基类。"""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MmRadarCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{coordinator.device_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.device_id)},
            name="mmRadar Desk Sentinel",
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=self.coordinator.fw_version,
        )

    @property
    def available(self) -> bool:
        """连接活着且数据新鲜。

        注意这里没有「保留最后一次读数」的降级 —— 那是刻意的。
        用户看到一个数值就会当它是当前的，显示陈旧值比显示 unavailable 危险。
        """
        return super().available and self.coordinator.available

    # ── 取值helper ────────────────────────────────────────

    def _snapshot(self) -> dict[str, Any]:
        return self.coordinator.data if isinstance(self.coordinator.data, dict) else {}

    def _path(self, *path: str) -> Any:
        return get_path(self._snapshot(), *path)
