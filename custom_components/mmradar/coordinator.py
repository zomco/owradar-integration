"""数据协调器：WebSocket 推送驱动，不轮询。

设备每秒推一拍，轮询只会白白浪费两端资源（架构文档 §4）。
轮询仅作为 WS 建不起来时的降级路径。

三条状态规则：

- WS 断开 → 实体全部 unavailable。**不保留最后一次读数** ——
  用户看到一个数值就会以为它是当前的。
- 收帧超过 STALE_AFTER_S → 同样判为失联。连接还在不等于数据还在，
  设备可能已经死在那里但 TCP 连接没断。
- 重连用指数退避，上限 60s。设备可能只是重启，也可能被拔了好几天。
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import (
    MmRadarApi,
    MmRadarAuthError,
    MmRadarConnectionError,
    merge_delta,
)
from .capability import capabilities_from_snapshot
from .const import ALL_ENTITY_KEYS, DOMAIN, RECONNECT_BACKOFF_S, STALE_AFTER_S

_LOGGER = logging.getLogger(__name__)


class MmRadarCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """维护一台设备的实时快照。"""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: MmRadarApi,
        device_id: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {device_id}",
            # update_interval=None：不轮询。数据由 WS 推上来。
            update_interval=None,
            config_entry=entry,
        )
        self.api = api
        self.entry = entry
        self.device_id = device_id
        self.fw_version: str | None = None

        #: 这台设备实际支持的实体键。首次全量快照到手后才准。
        #: 空集之前不要建实体 —— 见 async_start 里的顺序。
        self.capabilities: frozenset[str] = ALL_ENTITY_KEYS

        self._task: asyncio.Task[None] | None = None
        self._connected = False
        self._last_frame: float | None = None
        self._attempt = 0

    # ── 生命周期 ──────────────────────────────────────────

    async def async_start(self) -> None:
        """取一次全量快照打底，然后起后台的 WS 循环。

        先取快照是为了让实体在 WS 握手完成之前就有值 ——
        否则用户添加集成后会先看到一屏 unavailable，像是坏了。
        """
        try:
            snapshot = await self.api.async_get_snapshot()
        except MmRadarAuthError as err:
            raise UpdateFailed(f"配对 Token 无效: {err}") from err
        except MmRadarConnectionError as err:
            raise UpdateFailed(f"连不上设备: {err}") from err

        self._mark_frame()

        # 能力必须在 async_forward_entry_setups 之前算好 ——
        # 各平台的 async_setup_entry 会读 self.capabilities 来决定建哪些实体。
        self.capabilities = capabilities_from_snapshot(snapshot)
        missing = ALL_ENTITY_KEYS - self.capabilities
        if missing:
            # 用 info 而不是 debug：用户找不到某个实体时，
            # 第一件事就是翻日志，这条要能被翻到。
            _LOGGER.info(
                "%s: 这台设备没有以下实体，已跳过不建：%s（若之后接上了对应传感器，"
                "重载本集成即可出现）",
                self.device_id,
                ", ".join(sorted(missing)),
            )

        self.async_set_updated_data(snapshot)

        self._task = self.entry.async_create_background_task(
            self.hass, self._run(), name=f"{DOMAIN}-ws-{self.device_id}"
        )

    async def async_shutdown(self) -> None:
        if self._task is not None:
            self._task.cancel()
            # 等它真的退出。不等的话 HA 重载集成时会有两个循环并存，
            # 表现为实体状态在新旧连接之间来回跳。
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None
        await super().async_shutdown()

    async def _async_update_data(self) -> dict[str, Any]:
        """按需拉一次全量快照。

        两个用途：
        1. 实体写完值后主动对齐 —— 等设备下一拍推送会让滑块弹回旧值，
           看起来像没生效
        2. WS 建不起来时的降级路径（架构文档 §4）

        正常路径是 WS 推送，这个函数**不会被周期性调用**
        （update_interval 是 None）。
        """
        try:
            return await self.api.async_get_snapshot()
        except MmRadarAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except MmRadarConnectionError as err:
            raise UpdateFailed(f"取快照失败: {err}") from err

    # ── WS 循环 ───────────────────────────────────────────

    async def _run(self) -> None:
        while True:
            try:
                await self.api.async_listen(
                    self._on_snapshot,
                    self._on_alert,
                    on_connected=self._on_connected,
                )
                # 正常返回意味着对端关了连接
                _LOGGER.debug("%s: WS 已关闭", self.device_id)
            except asyncio.CancelledError:
                raise
            except MmRadarAuthError:
                # Token 失效重试没有意义 —— 退出循环，让用户去重新配对。
                # 一直重试只会把日志刷满，且掩盖真正的原因。
                _LOGGER.error("%s: 配对 Token 已失效，停止重连", self.device_id)
                self._set_unavailable("配对 Token 已失效，请重新配置")
                return
            except Exception as err:
                _LOGGER.debug("%s: WS 异常: %s", self.device_id, err)

            self._set_unavailable("与设备的连接已断开")
            await asyncio.sleep(self._next_backoff())

    def _next_backoff(self) -> int:
        delay = RECONNECT_BACKOFF_S[min(self._attempt, len(RECONNECT_BACKOFF_S) - 1)]
        self._attempt += 1
        return delay

    def _on_connected(self) -> None:
        self._connected = True
        self._attempt = 0
        _LOGGER.debug("%s: WS 已连接", self.device_id)

    def _mark_frame(self) -> None:
        self._last_frame = dt_util.utcnow().timestamp()

    def seconds_since_last_frame(self) -> float | None:
        """距上一帧过去了多久。从未收到过任何帧时为 None。

        诊断用。实体全 unavailable 时，它能区分「连不上设备」和
        「连上了但设备不推数据」—— 两者的排查方向完全不同。
        """
        if self._last_frame is None:
            return None
        return round(dt_util.utcnow().timestamp() - self._last_frame, 1)

    def _on_snapshot(self, payload: dict[str, Any]) -> None:
        self._mark_frame()
        # delta 只带变化的字段，必须合并进现有快照。
        # 直接替换的话没变化的指标会凭空消失，实体闪一下 unavailable。
        base = self.data if isinstance(self.data, dict) else {}
        merged = merge_delta(base, payload)
        self.async_set_updated_data(merged)
        self._maybe_reload_for_new_capabilities(merged)

    def _maybe_reload_for_new_capabilities(self, snapshot: dict[str, Any]) -> None:
        """传感器后来接上了就重载，把之前没建的实体补出来。

        只在能力**变多**时重载，绝不因变少而重载：
        - 变多是一次性的（用户插上了 CO2 模块），重载次数有上限；
        - 变少往往是临时故障，按它重载会在传感器接触不良时
          把集成反复重载，把实体历史打得七零八落。

        传感器坏掉的表达方式是 `fault` + unavailable，不是删实体。
        """
        gained = capabilities_from_snapshot(snapshot) - self.capabilities
        if not gained:
            return
        _LOGGER.info(
            "%s: 检测到新增能力 %s，重载集成以建立对应实体",
            self.device_id,
            ", ".join(sorted(gained)),
        )
        self.capabilities |= gained
        self.hass.config_entries.async_schedule_reload(self.entry.entry_id)

    def _on_alert(self, payload: dict[str, Any]) -> None:
        self._mark_frame()
        # 告警本身由 risk.active_alert_ids 反映在快照里，
        # 这里只广播事件，方便用户写自动化。
        self.hass.bus.async_fire(f"{DOMAIN}_alert", {"device_id": self.device_id, **payload})

    def _set_unavailable(self, reason: str) -> None:
        self._connected = False
        # 让实体变 unavailable 而不是继续显示旧值。
        # UpdateFailed 是 coordinator 表达「数据不可信」的标准方式。
        self.async_set_update_error(UpdateFailed(reason))

    # ── 供实体查询 ────────────────────────────────────────

    @property
    def available(self) -> bool:
        """连接活着，且最近确实收到过帧。

        只看连接状态是不够的：设备可能已经死在那里而 TCP 连接没断，
        那样实体会一直显示一份永不更新的旧数据。
        """
        if not self._connected or self._last_frame is None:
            return False
        return (dt_util.utcnow().timestamp() - self._last_frame) < STALE_AFTER_S

    async def async_send_command(self, cmd: str, **params: Any) -> dict[str, Any]:
        """下发命令。失败时抛 HomeAssistantError，让 HA 前端显示原因。"""
        try:
            resp = await self.api.async_command(cmd, **params)
        except MmRadarConnectionError as err:
            raise HomeAssistantError(f"设备无响应: {err}") from err

        if not resp.get("ok", False):
            error = resp.get("error")
            message = ""
            if isinstance(error, dict):
                message = str(error.get("message") or error.get("code") or "")
            raise HomeAssistantError(message or f"设备拒绝了 {cmd}")
        return resp
