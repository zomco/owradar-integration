"""能力探测：这台设备到底有哪些实体值得建出来。

**问题**：不加区分地把 19 个实体全建出来，没有 CO2 模块的设备
会永远挂着四个 unavailable 的实体（co2、calibrate_co2 按钮……）。
用户没法判断那是「传感器坏了」还是「这台本来就没有」，
自动化里引用了它也永远不会触发，而 HA 不会给任何提示。

**信号来自契约本身，不用猜版本号**：`SensorHealth` 有一档 `absent`，
固件的定义是「总线上探测不到器件」（`mmr_core/types.hpp`）。
这正是「这台没有这个传感器」的权威表达。

按固件版本号做能力表是另一条路，但那要手工维护一张
版本 → 能力的对照表，每出一版固件就要改一次，漏改就是错的；
而且它表达不了同一版固件的不同硬件配置。快照自己说的话更可信。

本模块是**纯函数**，不依赖 Home Assistant，可以直接拿快照字典测。
"""

from __future__ import annotations

from typing import Any, Final

#: 传感器缺席。固件的含义是「总线上探测不到器件」。
#:
#: 与 `fault` 要分开看：`fault` 是器件在、但读不出数（接触不良、CRC 错），
#: 那种情况实体**要建**，用 unavailable 如实反映故障。
#: 只有 `absent` 才意味着这台机器上压根没有这个东西。
HEALTH_ABSENT: Final = "absent"

#: 环境指标 -> 它在 `env` 下的字段名。
_ENV_METRICS: Final[dict[str, str]] = {
    "co2": "co2",
    "temperature": "temperature",
    "humidity": "humidity",
    "noise": "noise",
    "illuminance": "lux",
}

#: 依赖某项能力才有意义的实体。
#:
#: 例如没有 CO2 传感器就不该有「CO2 标定」按钮 ——
#: 按下去只会得到一个 unsupported 错误，而用户无从预知。
_DEPENDS_ON: Final[dict[str, str]] = {
    "calibrate_co2": "co2",
    "zone_min": "presence",
    "zone_max": "presence",
    "calibrate_zone": "presence",
    "distance": "presence",
    "seated_duration": "presence",
    "in_zone": "presence",
}

#: 与传感器无关、任何固件都该有的实体。
#:
#: 探测不到就当它在 —— 宁可多建一个 unavailable 的实体，
#: 也不要因为一次异常的快照把设备的核心功能整个藏起来。
#:
#: `presence` **不在**这里：它由雷达提供，而雷达是可以缺席的
#: （无雷达的工程样机）。它单独按 health 判，见下面。
_ALWAYS: Final[frozenset[str]] = frozenset(
    {"alert_active", "risk_level", "rssi", "brightness", "identify", "reboot"}
)


def _health_of(snapshot: dict[str, Any], *path: str) -> str | None:
    """顺着路径取 `health`，取不到返回 None。"""
    node: Any = snapshot
    for key in path:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    if not isinstance(node, dict):
        return None
    health = node.get("health")
    return health if isinstance(health, str) else None


def capabilities_from_snapshot(snapshot: dict[str, Any]) -> frozenset[str]:
    """从一份全量快照推断这台设备支持哪些实体键。

    判定规则，按优先级：

    1. `health == "absent"` -> 没有这个传感器，相关实体一律不建。
    2. 快照里**整块缺失**（老固件没有这个字段）-> 同样不建。
    3. 其余一律建 —— 包括 `fault` 与 `warming_up`。
       故障和预热是**临时**状态，实体要在，用 unavailable 如实反映。

    传入空字典（连快照都没取到）时返回全集：宁可多建几个 unavailable 的
    实体，也不要因为一次取数失败让用户的自动化全部失效。
    """
    if not snapshot:
        return frozenset(_ALWAYS | set(_ENV_METRICS) | {"presence"} | set(_DEPENDS_ON))

    caps: set[str] = set(_ALWAYS)

    env = snapshot.get("env")
    for entity_key, field in _ENV_METRICS.items():
        if not isinstance(env, dict) or field not in env:
            continue  # 老固件没有这个字段
        if _health_of(snapshot, "env", field) == HEALTH_ABSENT:
            continue  # 这台没装这个传感器
        caps.add(entity_key)

    # 在场感知是雷达提供的，没有它这个产品就不成立；
    # 但仍然按同样的规则判，免得在无雷达的工程样机上建出一堆死实体。
    presence = snapshot.get("presence")
    if isinstance(presence, dict) and _health_of(snapshot, "presence") != HEALTH_ABSENT:
        caps.add("presence")

    for entity_key, needs in _DEPENDS_ON.items():
        if needs in caps:
            caps.add(entity_key)

    return frozenset(caps)


def missing_capabilities(all_keys: frozenset[str], caps: frozenset[str]) -> frozenset[str]:
    """契约里有、但这台设备没有的实体键。用于日志与诊断。"""
    return frozenset(all_keys - caps)
