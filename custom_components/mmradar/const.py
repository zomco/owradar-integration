"""常量与实体键。

实体键（`object_id`）必须与固件 MQTT Discovery 发出的**完全一致** ——
同一台设备经 MQTT 直连和经本集成接入时，实体 ID 与显示名一模一样，
否则用户换接入方式会丢掉全部历史数据与自动化配置。

唯一事实来源是工作区的 `contracts/ha-discovery.json`；
`tests/test_contract_parity.py` 会逐条比对，漂移即测试失败。
"""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "mmradar"
MANUFACTURER: Final = "mmRadar"
MODEL: Final = "MMR-1"

# ── 连接 ──────────────────────────────────────────────────

CONF_TOKEN: Final = "pairing_token"

DEFAULT_PORT: Final = 80
DEFAULT_TIMEOUT_S: Final = 10

#: WebSocket 断开后的重连退避（秒）。上限 60s ——
#: 设备可能只是在重启，也可能被拔了电源好几天，
#: 后一种情况下每秒重试只是白白耗掉 HA 主机的资源。
RECONNECT_BACKOFF_S: Final[tuple[int, ...]] = (1, 2, 5, 10, 30, 60)

#: WS 不可用时的降级轮询间隔。
#: 只是兜底 —— 正常路径是推送，见架构文档 §4。
FALLBACK_POLL_INTERVAL_S: Final = 30

#: 多久收不到任何帧就认为设备失联。
#: 固件每秒推一拍，30s 静默足以判定异常而不会误杀网络抖动。
STALE_AFTER_S: Final = 30

# ── 实体键 ────────────────────────────────────────────────
# 顺序与 contracts/ha-discovery.json 一致，方便逐条对照。

SENSOR_KEYS: Final[tuple[str, ...]] = (
    "co2",
    "temperature",
    "humidity",
    "noise",
    "illuminance",
    "distance",
    "seated_duration",
    "risk_level",
    "rssi",
)

BINARY_SENSOR_KEYS: Final[tuple[str, ...]] = (
    "presence",
    "in_zone",
    "alert_active",
)

NUMBER_KEYS: Final[tuple[str, ...]] = (
    "zone_min",
    "zone_max",
    "brightness",
)

BUTTON_KEYS: Final[tuple[str, ...]] = (
    "identify",
    "calibrate_co2",
    "calibrate_zone",
    "reboot",
)

#: 全部实体键。契约比对测试用它做集合运算。
ALL_ENTITY_KEYS: Final[frozenset[str]] = frozenset(
    SENSOR_KEYS + BINARY_SENSOR_KEYS + NUMBER_KEYS + BUTTON_KEYS
)

# ── 契约取值 ──────────────────────────────────────────────

#: 传感器健康状态。**只有 `ok` 与 `degraded` 的读数可用** ——
#: 其余状态下实体必须是 unavailable 而不是显示上一个有效值。
#: 用户靠 unavailable 判断数据可不可信，显示陈旧值是最危险的做法。
HEALTH_USABLE: Final[frozenset[str]] = frozenset({"ok", "degraded"})

#: 在场状态。`absent` 之外都算有人。
PRESENCE_ABSENT: Final = "absent"

#: 服务名
SERVICE_CALIBRATE_CO2: Final = "calibrate_co2"
SERVICE_CALIBRATE_ZONE: Final = "calibrate_zone"
SERVICE_SET_ZONE: Final = "set_zone"
SERVICE_SET_RADAR: Final = "set_radar"
SERVICE_IDENTIFY: Final = "identify"
