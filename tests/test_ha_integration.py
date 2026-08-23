"""把集成真的装进一个 Home Assistant 实例里跑。

其余测试覆盖的都是纯函数。**这个文件覆盖的是接线** ——
manifest 认不认、平台模块导不导得进、config flow 走不走得通、
实体建不建得出、卸载干不干净。这些只有 HA 真的加载它才会暴露。

写这个文件的当天它就抓到一件纯函数测试抓不到的事，见
`test_existing_entity_survives_as_unavailable` 的注释。

跑法：先起模拟器
    node scripts/device-sim/index.mjs --port 8199 --token e2e-token

模拟器不在就整体跳过 —— 与 test_contract_parity.py 同样的做法，
单独克隆本仓库的人不该被一个跑不起来的测试挡住。

Windows 上起不了完整的 `hass`（runner 依赖 POSIX 的 fcntl），
所以在进程内跑 core —— HA 自己的测试就是这么做的。
"""

from __future__ import annotations

import asyncio
import shutil
import socket
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parent.parent
SIM_HOST = "127.0.0.1"
SIM_PORT = 8199
SIM_TOKEN = "e2e-token"


def _simulator_up() -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((SIM_HOST, SIM_PORT)) == 0


pytestmark = pytest.mark.skipif(
    not _simulator_up(),
    reason=(
        f"设备模拟器不在 {SIM_HOST}:{SIM_PORT} —— "
        "先跑 node scripts/device-sim/index.mjs --port 8199 --token e2e-token"
    ),
)


async def _sim_health(metric: str, value: str) -> None:
    """强制某个传感器的 health。模拟器专有的控制面。"""
    import aiohttp

    async with aiohttp.ClientSession() as s:
        await s.post(f"http://{SIM_HOST}:{SIM_PORT}/sim/set", json={"health": {metric: value}})


def _mmradar_issues(hass: Any) -> dict[str, Any]:
    """当前挂着的 mmradar repairs 通知。"""
    from homeassistant.helpers import issue_registry as ir

    registry = ir.async_get(hass)
    return {
        key[1]: {
            "severity": str(issue.severity),
            "is_fixable": issue.is_fixable,
            "translation_key": issue.translation_key,
            "placeholders": issue.translation_placeholders,
        }
        for key, issue in registry.issues.items()
        if key[0] == "mmradar"
    }


async def _boot(config_dir: Path) -> Any:
    """在进程内起一个 HA core。

    下面这几步平时由 bootstrap 完成，顺序不能换：
    loader 缓存不建好，async_get_integration 直接 KeyError；
    config_entries 不建好，setup_component 里拿它当 None 用；
    network 不装，第一次发 HTTP 请求会 KeyError（aiohttp 的 resolver 要它）。
    """
    from homeassistant import config_entries, loader
    from homeassistant.bootstrap import async_load_base_functionality
    from homeassistant.core import HomeAssistant
    from homeassistant.setup import async_setup_component

    hass = HomeAssistant(str(config_dir))
    loader.async_setup(hass)
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await loader.async_get_custom_components(hass)
    await async_load_base_functionality(hass)
    await async_setup_component(hass, "homeassistant", {})
    await async_setup_component(hass, "network", {})
    # repairs：陈旧实体的提示走它。不装的话通知发出去没人接。
    await async_setup_component(hass, "repairs", {})
    await hass.config_entries.async_initialize()
    await hass.async_start()
    return hass


async def _collect() -> dict[str, Any]:
    """跑一遍完整场景，把观察到的都收进一个字典。

    HA 启一次要好几秒，所以只启一次、把结果分给下面各条断言，
    而不是每条断言都启一遍。
    """
    from homeassistant.const import CONF_HOST, CONF_PORT
    from homeassistant.helpers import entity_registry as er

    config_dir = Path(tempfile.mkdtemp(prefix="mmr-ha-"))
    shutil.copytree(
        REPO / "custom_components" / "mmradar",
        config_dir / "custom_components" / "mmradar",
    )
    out: dict[str, Any] = {}

    from homeassistant import loader
    from homeassistant.setup import async_setup_component

    await _sim_health("lux", "ok")
    hass = await _boot(config_dir)

    try:
        integration = await loader.async_get_integration(hass, "mmradar")
        out["config_flow_declared"] = integration.config_flow
        out["version"] = str(integration.version)
        out["platforms"] = {}
        for platform in ("sensor", "binary_sensor", "number", "button", "diagnostics"):
            try:
                await integration.async_get_platform(platform)
                out["platforms"][platform] = None
            except Exception as err:
                out["platforms"][platform] = f"{type(err).__name__}: {err}"

        await async_setup_component(hass, "mmradar", {})

        flow = await hass.config_entries.flow.async_init("mmradar", context={"source": "user"})
        out["flow_type"] = flow["type"]

        bad = await hass.config_entries.flow.async_configure(
            flow["flow_id"],
            {CONF_HOST: SIM_HOST, CONF_PORT: SIM_PORT, "pairing_token": "wrong"},
        )
        out["bad_token_errors"] = bad.get("errors")

        created = await hass.config_entries.flow.async_configure(
            bad["flow_id"],
            {CONF_HOST: SIM_HOST, CONF_PORT: SIM_PORT, "pairing_token": SIM_TOKEN},
        )
        out["created_type"] = created["type"]
        await hass.async_block_till_done()

        entry = hass.config_entries.async_entries("mmradar")[0]
        out["entry_state"] = str(entry.state)

        registry = er.async_get(hass)
        registered = [e for e in registry.entities.values() if e.config_entry_id == entry.entry_id]
        out["registered"] = len(registered)
        out["disabled"] = [e.unique_id for e in registered if e.disabled]
        out["states"] = {
            s.entity_id: s.state
            for s in hass.states.async_all()
            if s.entity_id.split(".")[1].startswith("mmr")
        }

        diag_platform = await integration.async_get_platform("diagnostics")
        diag = await diag_platform.async_get_config_entry_diagnostics(hass, entry)
        out["diag_has_token"] = SIM_TOKEN in repr(diag)
        out["diag_keys"] = sorted(diag)

        # 传感器变 absent 之后重载：注册表里的那条会怎样
        await _sim_health("lux", "absent")
        await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        out["after_absent_states"] = {
            s.entity_id: s.state for s in hass.states.async_all() if "illuminance" in s.entity_id
        }
        out["issues_after_absent"] = _mmradar_issues(hass)

        # 传感器插回去 -> 通知该自己消失，否则用户点进去发现无事可修
        await _sim_health("lux", "ok")
        await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        out["issues_after_restore"] = _mmradar_issues(hass)

        out["unloaded"] = await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
    finally:
        await hass.async_stop()
        await _sim_health("lux", "ok")
        shutil.rmtree(config_dir, ignore_errors=True)

    return out


@lru_cache(maxsize=1)
def _result() -> dict[str, Any]:
    return asyncio.run(_collect())


class TestLoads:
    """HA 能不能认出并加载这个集成。"""

    def test_manifest_declares_config_flow(self) -> None:
        """Manifest 声明了 config_flow —— 不声明的话 UI 里根本加不了。"""
        assert _result()["config_flow_declared"] is True

    def test_manifest_has_version(self) -> None:
        """Manifest 有 version。HA 与 HACS 对自定义集成都强制要求。"""
        assert _result()["version"] not in (None, "None", "")

    def test_all_platforms_import(self) -> None:
        """五个平台模块都能被 HA 导入。"""
        # 语法错、导入环、写错的类型注解都会在这里炸，
        # 而 pytest 直接 import 时不一定 —— HA 走的是自己的加载器。
        assert _result()["platforms"] == {
            "sensor": None,
            "binary_sensor": None,
            "number": None,
            "button": None,
            "diagnostics": None,
        }


class TestConfigFlow:
    """配置流程。用户加设备走的就是这条路。"""

    def test_flow_opens(self) -> None:
        """配置流程能起来并给出表单。"""
        assert _result()["flow_type"] == "form"

    def test_wrong_token_rejected_at_config_time(self) -> None:
        """错误的配对 Token 在配置阶段就被挡住。"""
        # 配错了当场知道，好过建完实体全是 unavailable 再去猜
        assert _result()["bad_token_errors"] == {"base": "invalid_auth"}

    def test_correct_token_creates_entry(self) -> None:
        """正确凭证建出配置项并加载成功。"""
        assert _result()["created_type"] == "create_entry"
        assert _result()["entry_state"] == "ConfigEntryState.LOADED"


class TestEntities:
    """实体建得对不对。"""

    def test_all_contract_entities_registered(self) -> None:
        """契约里的 19 个实体都注册了。"""
        assert _result()["registered"] == 19

    def test_only_rssi_disabled_by_default(self) -> None:
        """只有 rssi 默认不启用 —— 它是诊断类，多数人不需要。"""
        # 注意实体 id 由 translation_key 生成（wi_fi_signal），
        # 认 unique_id 才靠谱
        disabled = _result()["disabled"]
        assert len(disabled) == 1
        assert disabled[0].endswith("_rssi")

    def test_every_platform_has_entities(self) -> None:
        """四个平台都建出了实体。"""
        ids = _result()["states"]
        for platform in ("sensor", "binary_sensor", "number", "button"):
            assert any(e.startswith(f"{platform}.") for e in ids), platform

    def test_sensors_carry_real_readings(self) -> None:
        """传感器读到的是模拟器的真实数值，不是一片 unknown。"""
        # 实体建出来了但全是 unknown，说明 coordinator 没接上 ——
        # 这种「看起来成功」的失败最值得单独断言
        live = [
            v
            for k, v in _result()["states"].items()
            if k.startswith("sensor.") and v not in ("unknown", "unavailable")
        ]
        assert len(live) >= 5, _result()["states"]


class TestDiagnostics:
    """诊断导出会被贴进 issue。"""

    def test_exports_without_token(self) -> None:
        """诊断导出里不含配对 Token。"""
        assert _result()["diag_has_token"] is False

    def test_has_expected_sections(self) -> None:
        """诊断带齐排障要看的几段。"""
        assert set(_result()["diag_keys"]) >= {
            "config",
            "device",
            "connection",
            "capabilities",
            "snapshot",
        }


class TestStaleEntities:
    """传感器事后没了，怎么办（工作区 OPEN-ISSUES S-17）。"""

    def test_existing_entity_survives_as_unavailable(self) -> None:
        """已注册的实体不会自己消失，只会变 unavailable。

        这是 HA 的既定行为，不是缺陷：实体注册表是持久的，
        平台不再添加它，条目照样留着。

        能力探测因此只在**首次配置**时起作用 —— 这条钉住它，
        免得以后有人以为「不建实体」也覆盖了事后拔传感器的情况。
        """
        after = _result()["after_absent_states"]
        assert len(after) == 1
        assert list(after.values()) == ["unavailable"]

    def test_notifies_user_instead_of_deleting(self) -> None:
        """留下 unavailable 实体时发一条 repairs 通知，而不是闷声删掉。

        不直接删是因为删注册表条目会连带删掉历史数据与自动化引用，
        而 absent 也可能只是上电瞬间的一次总线抖动。
        """
        issues = _result()["issues_after_absent"]
        assert len(issues) == 1, issues
        issue = next(iter(issues.values()))
        assert issue["translation_key"] == "stale_entities"
        # IssueSeverity 是 StrEnum，str() 出来就是 "warning"
        assert issue["severity"] == "warning"

    def test_notification_is_actionable(self) -> None:
        """通知可一键修复，且写清了要删哪些、代价是什么。"""
        # 只提示不给出路的话，用户得自己去实体列表里一个个找
        issue = next(iter(_result()["issues_after_absent"].values()))
        assert issue["is_fixable"] is True
        placeholders = issue["placeholders"] or {}
        assert "illuminance" in placeholders.get("entities", "")
        assert placeholders.get("count") == "1"

    def test_notification_clears_when_sensor_returns(self) -> None:
        """传感器插回去之后通知自己消失。"""
        # 不撤的话它会一直挂着，用户点进去发现无事可修 ——
        # 那种通知第二次出现时就没人看了
        assert _result()["issues_after_restore"] == {}


class TestUnload:
    """卸载要干净，否则重载会留下两个 coordinator。"""

    def test_unloads_cleanly(self) -> None:
        """配置项能干净卸载。"""
        assert _result()["unloaded"] is True
