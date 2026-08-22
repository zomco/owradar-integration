"""诊断导出。

诊断文件会被用户直接贴进 GitHub issue，所以这里的第一条断言不是
「内容对不对」，而是**凭证有没有被打码**。配对 Token 一旦泄露，
拿到的人就能读走这台设备的全部数据 —— 包括主人什么时候在工位。

不用 HA 的完整测试夹具：被测函数只碰 entry.data / entry.runtime_data，
拿两个轻量替身就够，跑得也快。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from custom_components.mmradar.capability import capabilities_from_snapshot
from custom_components.mmradar.const import ALL_ENTITY_KEYS
from custom_components.mmradar.diagnostics import async_get_config_entry_diagnostics

TOKEN = "super-secret-pairing-token"
SSID = "zomco-home-5g"


def _snapshot(co2_health: str = "ok") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "presence": {"state": "present_still", "distance_cm": 68, "health": "ok"},
        "env": {
            "co2": {"value": 800, "health": co2_health},
            "temperature": {"value": 24.0, "health": "ok"},
            "humidity": {"value": 50.0, "health": "ok"},
            "noise": {"value": 45.0, "health": "ok"},
            "lux": {"value": 300, "health": "ok"},
        },
        "device": {"fw_version": "1.0.0", "rssi_dbm": -50, "wifi_ssid": SSID},
        "links": {"local": "connected", "cloud": "disabled", "mqtt": "disabled"},
    }


@dataclass
class _FakeCoordinator:
    data: dict[str, Any]
    capabilities: frozenset[str]
    device_id: str = "mmr-a1b2c3d4e5f6"
    fw_version: str | None = "1.0.0"
    last_update_success: bool = True

    def seconds_since_last_frame(self) -> float | None:
        return 1.5


@dataclass
class _FakeRuntime:
    coordinator: _FakeCoordinator


@dataclass
class _FakeEntry:
    data: dict[str, Any]
    runtime_data: _FakeRuntime = field(init=False)

    def attach(self, coordinator: _FakeCoordinator) -> _FakeEntry:
        self.runtime_data = _FakeRuntime(coordinator)
        return self


def _entry(snapshot: dict[str, Any]) -> _FakeEntry:
    coordinator = _FakeCoordinator(
        data=snapshot,
        capabilities=capabilities_from_snapshot(snapshot),
    )
    return _FakeEntry(
        data={"host": "192.168.1.50", "port": 80, "pairing_token": TOKEN},
    ).attach(coordinator)


def _diag(snapshot: dict[str, Any]) -> dict[str, Any]:
    """跑一次诊断导出。

    用 asyncio.run 而不是引入 pytest-asyncio：被测函数里没有真正的 await，
    为一个文件多加一个测试依赖不划算，其余测试也都是同步的。
    """
    return asyncio.run(
        async_get_config_entry_diagnostics(None, _entry(snapshot))  # type: ignore[arg-type]
    )


class TestSecrets:
    """会被贴进 issue 的东西，一个凭证都不能带。"""

    def test_pairing_token_is_redacted(self) -> None:
        """配对 Token 被打码。"""
        diag = _diag(_snapshot())
        assert diag["config"]["pairing_token"] != TOKEN

    def test_token_absent_from_entire_payload(self) -> None:
        """整份诊断的任何角落都不含 Token。"""
        # 逐个字段断言会漏 —— 将来往诊断里加字段时很容易忘。
        # 直接对整份序列化结果做子串检查，加什么字段都跑不掉。
        diag = _diag(_snapshot())
        assert TOKEN not in repr(diag)

    def test_wifi_ssid_is_redacted(self) -> None:
        """Wi-Fi SSID 被打码 —— 不是凭证，但足以定位到具体某处。"""
        # 不是凭证，但足以定位到具体某个家庭或办公室
        diag = _diag(_snapshot())
        assert SSID not in repr(diag)

    def test_lan_host_is_kept(self) -> None:
        """内网地址保留 —— 对屋外的人没有意义，排障时几乎总要用到。"""
        # host 对屋外的人没有意义，而排障时几乎总要用到
        diag = _diag(_snapshot())
        assert diag["config"]["host"] == "192.168.1.50"


class TestUsefulness:
    """排障时真正要看的几项。"""

    def test_includes_versions(self) -> None:
        """带上固件版本与契约版本。"""
        # 「字段读不到」的报障多数能在这两个数上一眼看出来
        diag = _diag(_snapshot())
        assert diag["device"]["fw_version"] == "1.0.0"
        assert diag["device"]["schema_version"] == 1

    def test_includes_seconds_since_last_frame(self) -> None:
        """带上距上一帧的秒数。"""
        # 区分「连不上设备」与「连上了但设备不推数据」，两者排查方向不同
        diag = _diag(_snapshot())
        assert diag["connection"]["seconds_since_last_frame"] == 1.5

    def test_lists_missing_entities_with_reason(self) -> None:
        """列出缺失的实体并说明原因。"""
        snap = _snapshot()
        del snap["env"]["co2"]
        diag = _diag(snap)

        assert "co2" in diag["capabilities"]["missing"]
        assert "co2" not in diag["capabilities"]["supported"]
        # 「为什么没有这个实体」直接写进诊断，免得双方各猜一遍
        assert "absent" in diag["capabilities"]["note"]

    def test_no_misleading_note_when_complete(self) -> None:
        """设备健全时不留误导性的缺失说明。"""
        diag = _diag(_snapshot())
        assert diag["capabilities"]["missing"] == []
        assert sorted(ALL_ENTITY_KEYS) == diag["capabilities"]["supported"]

    def test_faulty_sensor_still_supported(self) -> None:
        """故障传感器仍算支持 —— fault 是临时状态。"""
        # fault 是临时状态，不是「这台没有」
        diag = _diag(_snapshot(co2_health="fault"))
        assert "co2" in diag["capabilities"]["supported"]
