"""能力探测。

这里守的是一条产品判断：**「这台没有」和「这台坏了」必须区别对待**。

- 没有（`health=absent`）-> 不建实体。建了就是一个永远 unavailable 的
  死实体，用户无从判断是坏了还是本来就没有，自动化引用它也永不触发。
- 坏了（`health=fault`）-> 建，并让它 unavailable。故障是临时状态，
  实体消失反而会让自动化在设备恢复后仍然是断的。

纯函数，不需要 Home Assistant 运行时。
"""

from __future__ import annotations

from typing import Any

import pytest

from custom_components.mmradar.capability import capabilities_from_snapshot
from custom_components.mmradar.const import ALL_ENTITY_KEYS


def _snapshot(**health: str) -> dict[str, Any]:
    """造一份快照，按需覆盖各传感器的 health。"""
    metrics = {"co2": 800, "temperature": 24.0, "humidity": 50.0, "noise": 45.0, "lux": 300}
    return {
        "schema_version": 1,
        "presence": {
            "state": "present_still",
            "distance_cm": 68,
            "in_zone": True,
            "seated_duration_s": 600,
            "health": health.get("presence", "ok"),
        },
        "env": {m: {"value": v, "health": health.get(m, "ok")} for m, v in metrics.items()},
        "risk": {"level": "good", "drivers": []},
        "device": {"fw_version": "1.0.0", "rssi_dbm": -50},
    }


class TestAbsentMeansNotInstalled:
    """absent = 这台机器上没有这个器件。"""

    def test_healthy_device_supports_all(self) -> None:
        """健全的设备支持契约里的全部实体。"""
        assert capabilities_from_snapshot(_snapshot()) == ALL_ENTITY_KEYS

    def test_absent_co2_drops_entity(self) -> None:
        """没有 CO2 传感器时不建 CO2 实体。"""
        caps = capabilities_from_snapshot(_snapshot(co2="absent"))
        assert "co2" not in caps

    def test_absent_co2_drops_calibrate_button(self) -> None:
        """没有 CO2 时连标定按钮一起不建 —— 按下去只会得到 unsupported。"""
        # 按下去只会得到 unsupported，而用户无从预知
        caps = capabilities_from_snapshot(_snapshot(co2="absent"))
        assert "calibrate_co2" not in caps

    def test_one_absent_sensor_does_not_affect_others(self) -> None:
        """缺一个传感器不影响其余实体。"""
        caps = capabilities_from_snapshot(_snapshot(co2="absent"))
        assert {"temperature", "humidity", "noise", "illuminance"} <= caps
        assert ALL_ENTITY_KEYS - caps == {"co2", "calibrate_co2"}

    def test_absent_radar_drops_presence_family(self) -> None:
        """没有雷达时，距离与区域相关的实体全不建。"""
        caps = capabilities_from_snapshot(_snapshot(presence="absent"))
        missing = ALL_ENTITY_KEYS - caps
        assert missing == {
            "presence",
            "in_zone",
            "distance",
            "seated_duration",
            "zone_min",
            "zone_max",
            "calibrate_zone",
        }


class TestFaultIsNotAbsent:
    """故障不等于不存在 —— 这是本模块最容易写错的地方。"""

    @pytest.mark.parametrize("state", ["fault", "warming_up", "degraded"])
    def test_transient_states_still_create_entities(self, state: str) -> None:
        """Fault / warming_up / degraded 都是临时状态，实体要在。"""
        # 传感器坏了、还在预热、读数有偏差 —— 都是临时的。
        # 实体要在，用 unavailable 或带偏差的数值如实反映。
        caps = capabilities_from_snapshot(_snapshot(co2=state))
        assert "co2" in caps
        assert "calibrate_co2" in caps

    def test_faulty_device_has_same_entity_set(self) -> None:
        """故障设备的实体集合与健全设备一致。"""
        assert capabilities_from_snapshot(_snapshot(co2="fault")) == ALL_ENTITY_KEYS


class TestOldFirmware:
    """字段整块缺失 = 老固件没有这个功能。"""

    def test_missing_env_field_drops_entity(self) -> None:
        """Env 里整块缺失的指标不建实体（老固件）。"""
        snap = _snapshot()
        del snap["env"]["lux"]
        caps = capabilities_from_snapshot(snap)
        assert "illuminance" not in caps
        assert "co2" in caps

    def test_missing_env_block_drops_all_env_entities(self) -> None:
        """整个 env 缺失时环境类实体全不建，但在场感知还在。"""
        snap = _snapshot()
        del snap["env"]
        caps = capabilities_from_snapshot(snap)
        assert not ({"co2", "temperature", "humidity", "noise", "illuminance"} & caps)
        # 但在场感知还在，设备仍然可用
        assert "presence" in caps


class TestDegradeSafely:
    """探测不到就多建，不要少建。"""

    def test_empty_snapshot_returns_all(self) -> None:
        """空快照返回全集 —— 探测不到就多建，不要少建。"""
        # 取快照失败时若返回空集，用户的自动化会在一次网络抖动后
        # 全部失效，而且不会自己恢复 —— 那比多几个 unavailable 实体糟得多。
        assert capabilities_from_snapshot({}) == ALL_ENTITY_KEYS

    def test_malformed_snapshot_does_not_raise(self) -> None:
        """畸形快照不抛异常。"""
        for bad in (
            {"env": None},
            {"env": "not a dict"},
            {"presence": []},
            {"env": {"co2": "not a dict"}},
            {"env": {"co2": {}}},
        ):
            caps = capabilities_from_snapshot(bad)
            assert isinstance(caps, frozenset)

    def test_non_string_health_treated_as_present(self) -> None:
        """Health 不是字符串时按「存在」处理，不能让实体凭空消失。"""
        snap = _snapshot()
        snap["env"]["co2"]["health"] = 42
        # 读不懂的 health 不该被当成 absent —— 那会让实体凭空消失
        assert "co2" in capabilities_from_snapshot(snap)


class TestCapabilitiesAreASubsetOfContract:
    """探测结果不能凭空造出契约里没有的键。"""

    @pytest.mark.parametrize(
        "health",
        [{}, {"co2": "absent"}, {"presence": "absent"}, {"noise": "absent", "lux": "absent"}],
    )
    def test_always_subset_of_contract(self, health: dict[str, str]) -> None:
        """探测结果始终是契约实体键的子集。"""
        # 多出来的键会被各平台的过滤悄悄丢掉，症状是「实体不见了」
        # 而日志里什么都没有 —— 所以在这里挡住。
        assert capabilities_from_snapshot(_snapshot(**health)) <= ALL_ENTITY_KEYS
