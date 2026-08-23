# mmRadar Desk Sentinel — Home Assistant 集成

把 [mmRadar 桌面助理](https://github.com/zomco/mmradar-firmware) 接进 Home Assistant，
**不需要 MQTT broker**。

> 架构说明在工作区：[集成架构](../../docs/architecture/06-integration-architecture.md) ·
> [数据模型契约](../../docs/architecture/02-data-model.md)
>
> 本文件只讲怎么用和怎么开发。

---

## 1. 这个集成解决什么

固件自己就会发 MQTT Discovery —— 有 broker 的用户什么都不用装，实体自动出现。
那本集成的价值在哪？

| 场景 | MQTT 路径 | 本集成 |
|---|---|---|
| 没装 / 不想装 MQTT broker | ❌ | ✅ 直连设备局域网 API |
| 图形化添加设备 | ❌ 要手工配 broker | ✅ mDNS 自动发现 |
| CO₂ 强制校准、区域标定 | ❌ Discovery 表达不了 | ✅ 注册成 HA service |

## 2. 两条路径的实体是同一套

**这是本仓库最重要的约束。**

同一台设备，经 MQTT 直连和经本集成接入，产生的实体 ID 与显示名**必须完全一致**。
否则用户从一条路径切到另一条时，HA 会认为那是一批全新的实体：
历史数据断掉，自动化和仪表盘全部失效。

唯一事实来源是工作区的 [`contracts/ha-discovery.json`](../../contracts/ha-discovery.json)：

- 固件由 `scripts/gen_ha_discovery.mjs` 从它生成 discovery 载荷
- 本集成由 `tests/test_contract_parity.py` 对着它逐条比对

漂移即测试失败。而没有这条测试的话，漂移要到用户真的换接入方式那天才暴露。

## 3. 安装

### HACS（推荐）

自定义仓库添加 `zomco/mmradar-integration`，类别选 Integration，然后安装并重启 HA。

### 手动

把 `custom_components/mmradar` 拷进 HA 的 `config/custom_components/`，重启。

## 4. 添加设备

设备在局域网广播 `_mmradar._tcp.local`，HA 会自动发现它。
你只需要填**配对 Token** —— 在设备屏幕上，或 mmRadar App 的设置里。

mDNS 不通（跨 VLAN 之类）时走「手动添加」，填 IP 和 Token。

`unique_id` 用的是设备的 `device_id` 而不是 IP —— 设备换了地址会自动更新，
不会变成一台新设备。

## 5. 实体

19 个，与固件的 MQTT Discovery 一一对应。

| 平台 | 实体 |
|---|---|
| sensor | 二氧化碳 · 温度 · 湿度 · 噪音 · 光照 · 目标距离 · 在座时长 · 风险等级 · Wi-Fi 信号 |
| binary_sensor | 在场 · 在目标区域 · 有活跃告警 |
| number | 区域近端 · 区域远端 · 屏幕亮度 |
| button | 识别本机 · 校准 CO₂ · 标定目标区域 · 重启 |

### 两个容易混淆的地方

**「在场」与「在目标区域」不是一回事。**
前者是**去抖后**的判定，是规则触发的依据，适合做自动化；
后者是**瞬时**的距离门判定，雷达抖一下就翻转 —— 拿它开灯会一闪一闪。
它存在的意义是让你调距离门时有可视化反馈。

**「区域近端/远端」与 `set_radar` 服务调的不是同一组距离。**
前者是固件侧的距离门，决定「算不算我在工位」；
后者是雷达模组内部的探测范围，决定「模组上不上报」。前者才是产品语义。

### 传感器坏了会怎样

`health` 不是 `ok`/`degraded` 时，实体是 **unavailable**，
不会继续显示上一次的有效值。

这是刻意的：用户看到一个数值就会当它是当前的。
「传感器坏了但还显示 24.5°C」比「显示不可用」危险得多。

## 6. 服务

`calibrate_co2` · `calibrate_zone` · `set_zone` · `set_radar` · `identify`

按钮实体覆盖的是默认参数的常用场景，服务覆盖的是要传参的场景，
两者调的是同一条设备命令。

## 7. 推送，不是轮询

设备每秒推一拍，所以 coordinator 的 `update_interval` 是 `None`。
HTTP 拉取只在两种情况下发生：启动时打底、以及写完值后主动对齐。

连接断开或**超过 30 秒没收到任何帧**，实体全部 unavailable。
后一条是必要的：连接还在不等于数据还在，设备可能已经死在那里而 TCP 没断。

重连用指数退避，上限 60 秒。配对 Token 失效时**不重连** ——
重试一个永远不会成功的连接只会刷满日志、掩盖真正的原因，
正确的做法是让 HA 弹出重新配对的流程。

## 8. 开发

```bash
python -m pip install homeassistant ruff mypy pytest
python -m ruff check . && python -m ruff format --check .
python -m mypy custom_components/mmradar
python -m pytest
```

**需要 Python ≥ 3.14.2** —— HA 2026.8 的 `Requires-Python` 就是这么写的，
它自己的源码用了 PEP 758 语法。工作区文档里一度写的 3.13 是错的，
按 3.13 建环境会装不上 HA。

契约一致性测试在工作区外会自动跳过（契约文件不在旁边），
所以单独克隆本仓库也能跑测试。

## 9. 能力探测

不是每台设备都有全部传感器。**「这台没有」和「这台坏了」必须区别对待**：

| 快照里的 `health` | 含义 | 做法 |
|---|---|---|
| `absent` | 总线上探测不到器件 —— 这台机器上没有 | **不建实体** |
| `fault` | 器件在，但读不出数 | 建，显示 unavailable |
| `warming_up` / `degraded` | 临时状态 | 建，如实反映 |
| 字段整块缺失 | 老固件没有这个功能 | 不建实体 |

不建的理由：一个永远 unavailable 的实体，用户无从判断是坏了还是本来就没有，
自动化引用它也永远不会触发，而 HA 不给任何提示。

判据取自快照而不是固件版本号：按版本号做能力表要手工维护一张对照表，
每出一版固件改一次、漏改就是错的，而且表达不了同一版固件的不同硬件配置。

传感器后来接上了会自动重载集成把实体补出来（只在能力**变多**时重载 ——
按变少重载会在接触不良时把实体历史打得七零八落）。

### 它做不到什么

**能力探测只在首次配置时起作用。**

HA 的实体注册表是持久的：一个实体注册过之后，即便平台下次不再添加它，
注册表条目照样留着，状态变成 `unavailable`。所以「装好之后传感器坏了
或被拔了」这种情况仍然会留下一个 unavailable 的实体 ——
正是这个功能想消灭的那种。

| 情形 | 结果 |
|---|---|
| 首次配置时传感器就 absent | ✅ 不建实体 |
| 配好之后传感器变 absent | ⚠️ 实体留在注册表，显示 unavailable |

没有顺手加自动删除：删注册表条目会**连带删掉用户的历史数据与自动化引用**，
而 `absent` 也可能只是上电瞬间的一次总线抖动。取舍见工作区 OPEN-ISSUES S-17。

这条限制是 `tests/test_ha_integration.py` 在真 HA 里跑出来的 ——
纯函数测试全绿的时候它才浮出来。那条测试现在把这个行为钉住了，
免得以后有人以为它已经被解决了。

逻辑在 `capability.py`，是纯函数，`tests/test_capability.py` 直接拿快照字典测。

## 9.5 在真 HA 里跑一遍

`tests/test_ha_integration.py` 会在**进程内起一个真的 Home Assistant core**，
把集成装进去：manifest 认不认、五个平台模块导不导得进、config flow
走不走得通、19 个实体建不建得出、诊断有没有漏 Token、卸载干不干净。

其余测试覆盖的是纯函数；这个文件覆盖的是**接线**，而接线的错
纯函数测试一条都抓不住。

```bash
node scripts/device-sim/index.mjs --port 8199 --token e2e-token   # 另开一个终端
python -m pytest tests/test_ha_integration.py
```

模拟器不在就整体跳过，单独克隆本仓库的人不会被它挡住。

> Windows 上起不了完整的 `hass`（runner 依赖 POSIX 的 `fcntl`），
> 所以在进程内跑 core —— HA 自己的测试就是这么做的。

## 10. 尚未实现

- 自定义 Lovelace 卡片（在场距离可视化）
- 品牌图标（需向 `home-assistant/brands` 提 PR）

## License

MIT
