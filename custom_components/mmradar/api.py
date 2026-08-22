"""设备的局域网 HTTP + WebSocket 客户端。

对应数据模型 §9.1。本模块**只管收发与解析**，不碰 HA 的任何概念 ——
这样它可以脱离 HA 单独测试，而 HA 的测试夹具向来是个麻烦。

两条贯穿全文的原则（数据模型 §10 兼容性规则）：

1. **容忍未知字段。** 设备固件可能比集成新。多出来的字段安全忽略，
   绝不能因为固件升级就让集成崩掉。
2. **缺失即 None，不是 0。** `value: null` 表示传感器没数据；
   当成 0 会让 HA 记录一条「0 lx」的假历史，而假数据比没数据更糟。
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

import aiohttp

from .const import DEFAULT_TIMEOUT_S

_LOGGER = logging.getLogger(__name__)


class MmRadarError(Exception):
    """设备通信失败的基类。"""


class MmRadarAuthError(MmRadarError):
    """配对 Token 无效或已更换。

    与其他错误分开：这一类重试没有意义，必须让用户重新配对。
    """


class MmRadarConnectionError(MmRadarError):
    """连不上设备。通常是掉电、换 IP 或不在同一网段。"""


def _get(data: Any, *path: str) -> Any:
    """按路径安全取值。任意一层缺失或类型不对都返回 None。

    设备发来的是不可信输入 —— 用 `data["env"]["co2"]["value"]` 这种写法，
    固件少发一个字段就是一次 KeyError，整个集成随之崩掉。
    """
    cur = data
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


class MmRadarApi:
    """一台设备的客户端。

    HTTP 用于请求/响应，WebSocket 用于推送。两者共用同一个 aiohttp session
    （HA 提供的共享 session），不自己建连接池。
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        token: str,
        port: int = 80,
    ) -> None:
        self._session = session
        self._host = host
        self._port = port
        self._token = token

    @property
    def base_url(self) -> str:
        return f"http://{self._host}:{self._port}"

    @property
    def ws_url(self) -> str:
        return f"ws://{self._host}:{self._port}/api/v1/stream"

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token}"}

    # ── HTTP ──────────────────────────────────────────────

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        auth: bool = True,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            async with self._session.request(
                method,
                url,
                headers=self._headers if auth else None,
                json=json_body,
                timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT_S),
            ) as resp:
                if resp.status == 401:
                    raise MmRadarAuthError("配对 Token 无效")
                resp.raise_for_status()
                body = await resp.json(content_type=None)
        except MmRadarError:
            raise
        except TimeoutError as err:
            raise MmRadarConnectionError(f"{url} 超时") from err
        except aiohttp.ClientError as err:
            raise MmRadarConnectionError(f"{url} 连接失败: {err}") from err

        if not isinstance(body, dict):
            raise MmRadarError(f"{url} 返回的不是 JSON 对象")
        return body

    async def async_get_info(self) -> dict[str, Any]:
        """设备标识。**免鉴权** —— 配网流程要在拿到 Token 之前先确认这是台 mmRadar。"""
        return await self._request("GET", "/api/v1/info", auth=False)

    async def async_get_snapshot(self) -> dict[str, Any]:
        return await self._request("GET", "/api/v1/snapshot")

    async def async_get_config(self) -> dict[str, Any]:
        return await self._request("GET", "/api/v1/config")

    async def async_command(self, cmd: str, **params: Any) -> dict[str, Any]:
        """下发命令并等设备响应。

        设备拒绝命令时回的是 `{"ok": false, "error": {...}}` —— 那是**业务结果**，
        不是传输错误，因此原样返回而不抛异常。调用方自己判断 `ok`。
        """
        body: dict[str, Any] = {"cmd": cmd}
        if params:
            body["params"] = params
        return await self._request("POST", "/api/v1/command", json_body=body)

    async def async_verify(self) -> str:
        """校验 Token 是否有效，返回 device_id。配网流程用。"""
        info = await self.async_get_info()
        device_id = info.get("device_id")
        if not isinstance(device_id, str) or not device_id:
            raise MmRadarError("设备未返回 device_id")
        # info 是免鉴权的，所以还得再打一次带鉴权的接口才算验过 Token
        await self.async_get_snapshot()
        return device_id

    # ── WebSocket ─────────────────────────────────────────

    async def async_listen(
        self,
        on_snapshot: Callable[[dict[str, Any]], None],
        on_alert: Callable[[dict[str, Any]], None],
        *,
        on_connected: Callable[[], None] | None = None,
    ) -> None:
        """连上 WS 并持续接收，直到连接断开或被取消。

        本函数**不负责重连** —— 退避策略是 coordinator 的事。
        把两者混在一起会让「连不上」和「连上又断」的处理纠缠不清。
        """
        async with self._session.ws_connect(
            self.ws_url,
            headers=self._headers,
            heartbeat=20,
            timeout=aiohttp.ClientWSTimeout(ws_close=DEFAULT_TIMEOUT_S),
        ) as ws:
            if on_connected is not None:
                on_connected()

            async for msg in ws:
                if msg.type is aiohttp.WSMsgType.TEXT:
                    self._dispatch(msg.data, on_snapshot, on_alert)
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break

    @staticmethod
    def _dispatch(
        raw: str,
        on_snapshot: Callable[[dict[str, Any]], None],
        on_alert: Callable[[dict[str, Any]], None],
    ) -> None:
        """解析一帧信封并分派。

        坏帧只跳过这一帧，不中断连接 —— 一个畸形帧不该让整台设备掉线。
        """
        try:
            envelope = json.loads(raw)
        except json.JSONDecodeError:
            _LOGGER.debug("跳过非 JSON 帧")
            return

        if not isinstance(envelope, dict):
            return
        payload = envelope.get("payload")
        if not isinstance(payload, dict):
            return

        match envelope.get("type"):
            case "snapshot" | "delta":
                on_snapshot(payload)
            case "alert":
                on_alert(payload)
            case _:
                # 未知类型安全忽略：固件可能比集成新
                pass


def merge_delta(base: dict[str, Any], delta: dict[str, Any]) -> dict[str, Any]:
    """把 delta 合并进快照。

    只有 `env` 是逐指标合并的；其余顶层字段整体替换。
    设备的 delta 只带变化的指标，如果整体替换 `env`，
    没变化的指标会凭空消失，实体就会闪一下 unavailable。
    """
    merged = {**base, **delta}
    if isinstance(base.get("env"), dict) and isinstance(delta.get("env"), dict):
        merged["env"] = {**base["env"], **delta["env"]}
    return merged


def reading(data: dict[str, Any], metric: str) -> float | None:
    """取一个环境指标的值。

    `health` 不可用时返回 None —— 让实体变成 unavailable，
    而不是把上一个有效值继续显示下去。用户靠 unavailable 判断数据可不可信。
    """
    health = _get(data, "env", metric, "health")
    if health not in ("ok", "degraded"):
        return None
    value = _get(data, "env", metric, "value")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return None


def get_path(data: dict[str, Any], *path: str) -> Any:
    """导出给实体模块用的安全取值。"""
    return _get(data, *path)


async def async_probe(session: aiohttp.ClientSession, host: str, token: str, port: int = 80) -> str:
    """配网时用：确认能连上且 Token 有效，返回 device_id。"""
    api = MmRadarApi(session, host, token, port)
    return await api.async_verify()


__all__ = [
    "MmRadarApi",
    "MmRadarAuthError",
    "MmRadarConnectionError",
    "MmRadarError",
    "async_probe",
    "get_path",
    "merge_delta",
    "reading",
]
