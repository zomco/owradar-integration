"""设备不再具备的能力，对应的实体怎么办。

**背景**（工作区 OPEN-ISSUES S-17）：能力探测只在首次配置时起作用。
HA 的实体注册表是持久的 —— 实体注册过之后，即便平台下次不再添加它，
注册表条目照样留着、状态变 `unavailable`。

于是「装好之后拔掉 CO2 模块」会留下几个永远 unavailable 的实体，
正是能力探测想消灭的那种东西。

**为什么不直接删**：删注册表条目会连带删掉该实体的历史数据与
自动化引用，而 `absent` 也可能只是上电瞬间的一次 I2C 抖动。
「传感器接触不良一次，用户三个月的曲线没了」是不可接受的。

**做法**：发一条 HA 的 repairs 通知，把决定权交给用户 ——
他点了「修复」才删。既不悄悄毁数据，也不装作没这回事。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.helpers.entity_registry import RegistryEntry

#: repairs 通知的 id 前缀。每个配置项一条 —— 多台设备各报各的，
#: 共用一个 id 的话第二台会把第一台的通知顶掉。
ISSUE_PREFIX = "stale_entities"


def issue_id(entry_id: str) -> str:
    """一个配置项一条通知的 id。"""
    return f"{ISSUE_PREFIX}_{entry_id}"


def entity_key(unique_id: str, device_id: str) -> str | None:
    """从 `<device_id>_<key>` 里取出 key。

    对不上前缀就返回 None —— 那说明这条注册记录不是本集成按当前
    命名规则建的（换过 device_id、或很老的版本），不该拿它做判断。
    """
    prefix = f"{device_id}_"
    if not unique_id.startswith(prefix):
        return None
    key = unique_id[len(prefix) :]
    return key or None


def find_stale(
    entries: list[RegistryEntry],
    capabilities: frozenset[str],
    device_id: str,
) -> list[RegistryEntry]:
    """注册表里有、但设备已经不支持的实体。

    只看 unique_id 解析得出的 key。解析不出来的一律**不算陈旧** ——
    宁可漏报也不要误报：误报的下场是提示用户删掉一个其实好好的实体。
    """
    stale = []
    for entry in entries:
        key = entity_key(entry.unique_id, device_id)
        if key is None:
            continue
        if key not in capabilities:
            stale.append(entry)
    return stale
