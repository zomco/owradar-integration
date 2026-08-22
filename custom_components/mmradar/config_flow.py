"""配置流程：zeroconf 自动发现 + 手动填 IP。

设备在局域网广播 `_mmradar._tcp.local`，TXT 里带 `id` / `fw` / `model`。
用户在 HA 里会直接看到「发现了一台 mmRadar」，只需填配对 Token。

手动入口保留给跨 VLAN 等 mDNS 不通的网络。
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .api import MmRadarAuthError, MmRadarConnectionError, MmRadarError, async_probe
from .const import CONF_TOKEN, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MmRadarConfigFlow(ConfigFlow, domain=DOMAIN):
    """引导用户接入一台设备。"""

    VERSION = 1

    def __init__(self) -> None:
        self._host: str | None = None
        self._port: int = DEFAULT_PORT
        self._device_id: str | None = None

    # ── 自动发现 ──────────────────────────────────────────

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> ConfigFlowResult:
        """处理 mDNS 发现到的设备。"""
        device_id = discovery_info.properties.get("id")
        if not device_id:
            return self.async_abort(reason="no_device_id")

        # unique_id 用 device_id 而不是 IP —— IP 会变，设备不会。
        # 这样设备换了 IP 之后 HA 会自动更新而不是当成一台新设备。
        await self.async_set_unique_id(device_id)
        self._abort_if_unique_id_configured(
            updates={CONF_HOST: discovery_info.host, CONF_PORT: discovery_info.port or DEFAULT_PORT}
        )

        self._host = discovery_info.host
        self._port = discovery_info.port or DEFAULT_PORT
        self._device_id = device_id

        # 让发现卡片上显示设备标识，用户有多台时能分清
        self.context["title_placeholders"] = {"name": device_id}
        return await self.async_step_pair()

    async def async_step_pair(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """自动发现之后只差一个配对 Token。"""
        errors: dict[str, str] = {}

        if user_input is not None and self._host is not None:
            token = user_input[CONF_TOKEN]
            error = await self._async_try(self._host, self._port, token)
            if error is None:
                return self.async_create_entry(
                    title=self._device_id or self._host,
                    data={CONF_HOST: self._host, CONF_PORT: self._port, CONF_TOKEN: token},
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="pair",
            data_schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
            description_placeholders={"device_id": self._device_id or ""},
            errors=errors,
        )

    # ── 手动添加 ──────────────────────────────────────────

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """手动填 IP 与 Token。mDNS 不通时走这条。"""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            token = user_input[CONF_TOKEN]

            error = await self._async_try(host, port, token)
            if error is None and self._device_id is not None:
                await self.async_set_unique_id(self._device_id)
                # 同一台设备已经加过就不重复添加，但顺手更新 IP ——
                # 用户手动重加的常见原因正是设备换了地址
                self._abort_if_unique_id_configured(updates={CONF_HOST: host, CONF_PORT: port})
                return self.async_create_entry(
                    title=self._device_id,
                    data={CONF_HOST: host, CONF_PORT: port, CONF_TOKEN: token},
                )
            errors["base"] = error or "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(CONF_TOKEN): str,
                }
            ),
            errors=errors,
        )

    # ── 重新认证 ──────────────────────────────────────────

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Token 失效时由 coordinator 触发。"""
        self._host = entry_data.get(CONF_HOST)
        self._port = entry_data.get(CONF_PORT, DEFAULT_PORT)
        self._device_id = self.context.get("unique_id")
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None and self._host is not None:
            token = user_input[CONF_TOKEN]
            error = await self._async_try(self._host, self._port, token)
            if error is None:
                entry = self._get_reauth_entry()
                return self.async_update_reload_and_abort(entry, data_updates={CONF_TOKEN: token})
            errors["base"] = error

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
            errors=errors,
        )

    # ── 探测 ──────────────────────────────────────────────

    async def _async_try(self, host: str, port: int, token: str) -> str | None:
        """试连一次。成功返回 None，失败返回错误码（对应 strings.json）。"""
        session = async_get_clientsession(self.hass)
        try:
            self._device_id = await async_probe(session, host, token, port)
        except MmRadarAuthError:
            return "invalid_auth"
        except MmRadarConnectionError:
            return "cannot_connect"
        except MmRadarError as err:
            _LOGGER.debug("探测 %s 失败: %s", host, err)
            return "unknown"
        return None
