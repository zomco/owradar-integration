"""修复流程：用户确认后，删掉设备已不具备的那些实体。

删除**只在用户点了「修复」之后**发生。理由见 stale.py：
删注册表条目会连带删掉历史数据与自动化引用，而 `absent`
可能只是一次总线抖动。这个决定必须由人来做。

用 ConfirmRepairFlow 而不是自定义表单：这里没有要用户填的东西，
只有一个「你确定吗」。多做一个表单只是给人多一次点击。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .stale import find_stale

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult


class StaleEntitiesRepairFlow(ConfirmRepairFlow):
    """确认后删掉陈旧实体。"""

    def __init__(self, entry_id: str) -> None:
        super().__init__()
        self._entry_id = entry_id

    async def async_step_confirm(self, user_input: dict[str, str] | None = None) -> FlowResult:
        """用户点了确认才走到这里。"""
        if user_input is None:
            return await super().async_step_confirm(user_input)

        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        if entry is None or not hasattr(entry, "runtime_data"):
            # 用户在通知挂着的时候把设备删了 —— 没什么可修的，正常收尾
            return self.async_create_entry(data={})

        registry = er.async_get(self.hass)
        coordinator = entry.runtime_data.coordinator
        stale = find_stale(
            er.async_entries_for_config_entry(registry, self._entry_id),
            coordinator.capabilities,
            coordinator.device_id,
        )
        # 重新算一遍而不是用创建通知时的那份快照：
        # 用户可能是在把传感器插回去之后才点的，那时候不该再删。
        for item in stale:
            registry.async_remove(item.entity_id)

        return self.async_create_entry(data={})


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """HA 按 issue_id 找到这里。"""
    entry_id = str((data or {}).get("entry_id", ""))
    return StaleEntitiesRepairFlow(entry_id)
