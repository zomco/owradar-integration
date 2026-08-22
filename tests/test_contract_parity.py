"""实体清单必须与固件的 MQTT Discovery 完全一致。

这是本仓库最重要的一条测试。

理由：同一台设备有两条接入路径 —— 固件直接发 MQTT Discovery，
或者用户装本集成走局域网直连。两条路径产生的实体 ID 与显示名
**必须一模一样**，否则用户从一条切到另一条时，
HA 会认为那是一批全新的实体：历史数据断掉，自动化和仪表盘全部失效。

而这个后果要到用户真的切换那天才暴露 —— 没有测试守着的话，
漂移会在代码里躺很久。

本测试不依赖 Home Assistant，纯读文件比对，因此在任何环境都能跑。
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
COMPONENT = REPO / "custom_components" / "mmradar"

#: 契约在工作区里。单独检出本仓库时它不在旁边 —— 那种情况下跳过，
#: 而不是让测试失败：贡献者克隆单个仓库跑测试是很正常的。
CONTRACT = REPO.parent.parent / "contracts" / "ha-discovery.json"

pytestmark = pytest.mark.skipif(
    not CONTRACT.exists(),
    reason=f"契约不在旁边（{CONTRACT}）—— 需在工作区内运行",
)


def _contract_entities() -> dict[str, str]:
    """契约里的 object_id -> platform。"""
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    return {e["object_id"]: e["platform"] for e in data["entities"]}


def _literal(module: str, name: str) -> object:
    """从模块里取一个字面量常量，不 import。

    不 import 是因为这些模块依赖 homeassistant 包，
    而本测试要能在没装 HA 的环境里跑。
    """
    tree = ast.parse((COMPONENT / module).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return ast.literal_eval(node.value)  # type: ignore[arg-type]
    raise AssertionError(f"{module} 里找不到 {name}")


def _keys_from_descriptions(module: str, container: str) -> set[str]:
    """从实体描述元组里抽出所有 key=... 的值。

    同样走 AST：描述对象里有 device_class 之类的 HA 枚举，literal_eval 吃不下。
    """
    tree = ast.parse((COMPONENT / module).read_text(encoding="utf-8"))
    keys: set[str] = set()
    for node in ast.walk(tree):
        # 带类型标注的赋值是 AnnAssign 而不是 Assign。
        # 这些容器都写成 `SENSORS: tuple[...] = (...)`，漏掉 AnnAssign
        # 会让本测试永远扫不到东西 —— 它第一次跑就是这么失败的。
        if isinstance(node, ast.Assign):
            targets: list[ast.expr] = list(node.targets)
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
            value = node.value
        else:
            continue

        if not any(isinstance(t, ast.Name) and t.id == container for t in targets):
            continue
        for call in ast.walk(value):
            if not isinstance(call, ast.Call):
                continue
            for kw in call.keywords:
                if kw.arg == "key" and isinstance(kw.value, ast.Constant):
                    keys.add(str(kw.value.value))
    assert keys, f"{module} 的 {container} 里没找到任何 key"
    return keys


def test_const_matches_contract() -> None:
    """const.py 里登记的键与契约完全相同。"""
    contract = _contract_entities()

    declared: set[str] = set()
    for name in ("SENSOR_KEYS", "BINARY_SENSOR_KEYS", "NUMBER_KEYS", "BUTTON_KEYS"):
        declared |= set(_literal("const.py", name))  # type: ignore[arg-type]

    missing = set(contract) - declared
    extra = declared - set(contract)

    assert not missing, f"契约里有但集成没实现的实体: {sorted(missing)}"
    assert not extra, f"集成里有但契约没定义的实体: {sorted(extra)}"


@pytest.mark.parametrize(
    ("module", "container", "const_name", "platform"),
    [
        ("sensor.py", "SENSORS", "SENSOR_KEYS", "sensor"),
        ("binary_sensor.py", "BINARY_SENSORS", "BINARY_SENSOR_KEYS", "binary_sensor"),
        ("number.py", "NUMBERS", "NUMBER_KEYS", "number"),
        ("button.py", "BUTTONS", "BUTTON_KEYS", "button"),
    ],
)
def test_platform_keys_match(module: str, container: str, const_name: str, platform: str) -> None:
    """每个平台实际创建的实体，与 const.py 和契约三方一致。"""
    contract = _contract_entities()
    expected = {k for k, p in contract.items() if p == platform}

    declared = set(_literal("const.py", const_name))  # type: ignore[arg-type]
    actual = _keys_from_descriptions(module, container)

    assert declared == expected, (
        f"const.py 的 {const_name} 与契约里的 {platform} 不一致\n"
        f"  缺: {sorted(expected - declared)}\n"
        f"  多: {sorted(declared - expected)}"
    )
    assert actual == expected, (
        f"{module} 实际创建的实体与契约不一致\n"
        f"  缺: {sorted(expected - actual)}\n"
        f"  多: {sorted(actual - expected)}"
    )


def test_unique_id_format_matches_firmware() -> None:
    """unique_id 的拼法必须与固件的 discovery 载荷一致。

    固件发的是 `<device_id>_<object_id>`；集成也必须这么拼，
    否则同一台设备在两条路径下会得到两套不同的实体。
    """
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    # 契约本身不带 unique_id（那是固件生成时拼的），
    # 这里锁的是集成侧的实现，防止有人改成别的格式
    source = (COMPONENT / "entity.py").read_text(encoding="utf-8")
    assert 'f"{coordinator.device_id}_{key}"' in source, (
        "entity.py 的 unique_id 拼法变了 —— "
        "它必须与固件 ha_discovery_gen.c 里的 <device_id>_<object_id> 保持一致"
    )
    assert data["entities"], "契约里没有实体"
