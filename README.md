# iKuai Router — Home Assistant 集成

基于爱快 **iKuaiOS 4.x 官方 OpenAPI** 的 Home Assistant 自定义集成，纯本地轮询，不经过任何云端。

## 你能得到什么

- **系统状态**：CPU 使用率、CPU 温度、内存使用率/占用、总连接数 / TCP / UDP、在线终端数、实时上下行速率、累计流量、运行时间、固件版本
- **WAN 线路**：每条线路的连通性二进制传感器 + 实时上下行速率与累计流量（多 WAN 自动发现）
- **设备追踪**：每个在线终端生成一个 tracker，附带厂商、型号、所属接口、VLAN、SSID 等属性，设备上下线动态增删
- **DHCP**：租约数、静态绑定数
- **无线**：AP 总数 / 在线数、无线终端数
- **固件**：有新版本时给出「固件更新」传感器（带当前版本、最新版本、更新日志属性）
- **流量审计**：流量最高的终端（设备未开启审计功能时该实体自动不可用）
- **历史均值**：CPU、内存近 1 小时平均值
- **扩展监控（v0.4.0 新增，29 个传感器）**：连接数 / 磁盘 / 网络负载历史曲线、离线终端、IPv6 在线/离线终端、应用协议流量排行与汇总、协议明细与历史、无线流量、分流统计、策略流量、AP 信道底噪、摄像头列表、云管交换机、周边设备、DNS 统计、CPU 实时频率、系统磁盘、接口流量 / 配置 / 物理状态、终端备注、认证账号与套餐、DHCPv6 客户端、AC 服务状态、AP 列表、WireGuard 隧道 peers——重负载列表每 3 个轮询周期才刷新一次，失败保留上次数据，不闪烁

## 快速开始

1. 路由器固件为 iKuaiOS 4.x
2. 在路由器 Web 后台开启 API 对接并生成令牌（4.x 通常在「系统设置」下的第三方对接 / API 相关页面；不同固件版本菜单位置略有差异）
3. Home Assistant 能访问路由器管理地址（**必须用 `https`**：明文的 http 在不同固件上表现不一致，有的返回 302 跳转，有的直接 403 拒绝 API 请求）

**HACS 安装**：HACS → 右上角 ⋮ → 自定义存储库 → 填入本仓库地址 → 类别选「集成」→ 下载 → 重启 HA。

**手动安装**：复制 `custom_components/ikuai/` 到 HA 配置目录的 `custom_components/` 下，重启 HA。

然后：设置 → 设备与服务 → 添加集成 → 搜索 **iKuai Router**。

| 字段 | 说明 | 示例 |
|---|---|---|
| 路由器地址 | 支持 `10.10.10.1`、`https://10.10.10.1`、`https://router:8443`；不写协议时默认 https | `10.10.10.1` |
| API 令牌 | 路由器后台生成的令牌 | `xxxxxxxx-...` |
| 校验 TLS 证书 | 爱快使用自签证书，**默认关闭**；装了可信证书可打开 | 关闭 |
| 轮询间隔 | 10–3600 秒 | `30` |

之后可在集成的「配置」里随时修改地址、令牌、证书校验和轮询间隔。令牌失效时 HA 会提示重新输入，不会丢已有实体。

## 写操作（策略开关）与版本识别

默认**只读**。如需把 iKuai 的策略规则（ACL、MAC 黑白名单、端口映射、限速、分流、
VPN 客户端等）暴露成 HA 开关/按钮，需在集成选项里**两步确认**后才会生效：

1. 打开「允许写操作」
2. 勾选要暴露的具体规则分组

两者都满足前，集成不发出任何写请求。写操作通过 `PATCH` 切换 `enabled` 字段，并严格
校验业务返回 `code==0`；切换失败不会影响 UI 状态，下一个刷新周期会回显真实值。重启
路由器按钮默认**禁用**，需显式开启才能按。

**免费版 / 企业版自动识别**：iKuai 有免费版（装在 x86 的软件）和企业版（IK-M200 等
硬件）之分，接口暴露不同。集成从 `verinfo` 自动判定——免费版 `modelname`/`sn` 为空，
企业版带型号与序列号；企业版独占的分组（如 IKEv2 客户端）在免费版上**自动不暴露**，
选项里会标注「仅企业版」。若自动判定与实际不符，可在选项里手动选「免费版 / 企业版」
纠偏。

## 场景服务与诊断服务

在开关之外，集成注册了 13 个服务（开发者工具 → 动作里搜 `ikuai`）。
前四个是场景控制，需要打开「允许写操作」，但**不要求**勾选任何规则分组：

| 服务 | 作用 |
|---|---|
| `ikuai.block_terminal` | 把终端加入 MAC 黑名单（禁止上网），支持 `expires_hours` 到期自动恢复 |
| `ikuai.allow_terminal` | 移除该终端在黑名单里的全部规则 |
| `ikuai.parental_control` | 按每周时间表禁止终端上网（如工作日 22:00–07:00） |
| `ikuai.clear_parental_control` | 删除由本集成创建的家长控制规则 |

后九个是 v0.4.0 新增的诊断 / 配置服务（只读服务无需写权限；标 ✍ 的需写权限）：

| 服务 | 作用 |
|---|---|
| `ikuai.query` | 只读查询 60+ 白名单端点（监控历史、终端列表、单例配置等），支持自定义参数 |
| `ikuai.set_config` ✍ | 以读-改-写方式修改 22 项单例配置（DNS、VPN 服务端、ALG、SNMP…），高风险项需 `confirm: true` |
| `ikuai.speed_test` | 一键测速：启动 / 停止 / 查询结果 |
| `ikuai.router_health` | 路由体检：启动 / 停止 / 查询（外网、DHCP、云连接等自检） |
| `ikuai.ac_service` ✍ | AC 无线服务启停与状态 |
| `ikuai.restart_dhcp` ✍ | 重启 DHCP 服务 |
| `ikuai.set_terminal_name` ✍ | 给终端设备起备注名（按 MAC 自动增改） |
| `ikuai.set_ssid` ✍ | 修改 AP 的 Wi-Fi 名称 / 密码（指定 AP、频段、SSID 序号） |
| `ikuai.api_request` ✍ | 高级：白名单内任意路径的 GET（只读）/ POST / PUT / DELETE，兜底官方 API 全量能力 |

示例（自动化里调用）：

```yaml
action: ikuai.parental_control
data:
  target: "08:9B:4B:00:10:2E"   # MAC 或 IPv4 均可
  weekdays: "12345"             # 1=周一 … 7=周日
  start_time: "22:00"
  end_time: "07:00"
  name: "孩子工作日禁网"
```

查询某终端的实时流量明细（参数要求写在服务描述里）：

```yaml
action: ikuai.query
data:
  resource: clients_traffic_load
  params:
    ip: "192.168.1.100"
    mac: "AA:BB:CC:DD:EE:FF"
```

安全说明：本集成创建的规则备注带「HA集成」标记，撤销类服务只删带标记的规则，
不会碰你手工建的配置；`tagname` 受路由器 15 字符限制，超长会自动截断。
`query` / `api_request` 均有路径白名单，备份恢复、固件升级、管理员账号等
高危端点**永远不在白名单内**。

## 令牌与隐私

- **令牌不会离开你的局域网**，本集成只和你的路由器通信，没有任何遥测或外部请求
- **不要提交令牌**：仓库里的工具通过环境变量读取凭据（`IKUAI_HOST` / `IKUAI_TOKEN`），`.env` 已被 git 忽略
- 上报 issue 前请对输出脱敏（诊断输出含 MAC、内网 IP、主机名）
- 怀疑令牌泄露时，在路由器后台重新生成一条，再到 HA 集成选项里更新即可

## 自查工具

无需安装 Home Assistant 即可验证连通性和字段：

```bash
cp .env.example .env      # 填入你自己的地址和令牌
python tools/dump_api.py          # 解析后的摘要
python tools/dump_api.py --raw    # 原始 JSON
```

也支持直接传环境变量：

```bash
IKUAI_HOST=10.10.10.1 IKUAI_TOKEN=xxxx python tools/dump_api.py
```

装集成前，还可以对路由器做一次**资源组全量自查**（只发 GET，绝不写配置）：

```bash
IKUAI_HOST=10.10.10.1 IKUAI_TOKEN=xxxx python tools/live_check_free.py
```

它会逐个探测全部 48 个 CRUD 资源组、47 个扩展监控端点与 22 个单例配置（哪组正常、哪组 404、哪组权限受限），验证免费版/企业版识别与企业版独占组的自动隐藏。v0.4.0 起还覆盖详情类端点的参数要求（终端详情需 ip+mac、应用详情需 appid）。

装完集成后，再从任意能连通 HA 的机器上**自查 HA 端**：

```bash
export HA_URL="http://<你的HA地址>:80"
export HA_TOKEN="eyJ...（Long-Lived Access Token）"
python tools/verify_ha.py
```

它会依次检查：令牌有效性 → `ikuai` 是否已加载（components）→ `ikuai.*` 实体清单 → 错误日志里的 ikuai 相关行。两个脚本均为纯标准库实现，令牌只从环境变量读取、不落盘。

## 排错

| 现象 | 原因与处理 |
|---|---|
| 无法连接 | 确认地址可达并**使用 https**；HA 与路由器分网段时检查防火墙 |
| 401/403 令牌被拒 | 令牌过期或被重新生成，或后台 API 开关未开启；无令牌请求会返回 401 |
| CPU 温度不可用 | 该机型无温控芯片（`cputemp` 返回空数组），属正常现象 |
| 某些实体显示「不可用」 | 该功能在当前设备/授权下不存在（如流量审计返回 404），不影响其他实体 |
| TLS 报错 | 关闭「校验 TLS 证书」选项（自签证书默认不校验） |

日志排查：设置 → 系统 → 日志，关键词 `ikuai`。

## 目录结构

```
custom_components/ikuai/
├── manifest.json      集成元数据
├── const.py           常量、接口路径、服务名
├── helpers.py         地址归一化、UTF-8 容错解码、版本识别、MAC/时间归一化
├── api.py             v4.0 REST 客户端（读 + 写通道 + 监控/配置/动作封装）
├── coordinator.py     轮询协调器（主 / 扩展两级缓存：轻量项每周期，重列表每 3 周期）
├── resources.py       48 个 CRUD 资源 + 22 个单例配置 + 查询/写入白名单 + 版本过滤
├── config_flow.py     配置 / 选项 / 重新认证流程
├── sensor.py          系统传感器 + WAN 流量 + 扩展监控（29 个 v0.4.0 传感器）
├── binary_sensor.py   固件更新 / WAN 线路连通性
├── switch.py          通用资源引擎开关（按行生成）
├── button.py          动作按钮（重启 / 备份 / NTP / 版本检测）
├── device_tracker.py  在线终端追踪
├── services.py        13 个服务（场景控制 4 + 诊断/配置 9）
├── services.yaml      服务与字段定义
├── diagnostics.py     脱敏诊断输出（含版本识别）
└── translations/      zh-Hans / en
tools/dump_api.py      零凭据依赖的诊断脚本
tools/live_check_free.py  真机只读全量自查（资源组 + 监控端点 + 单例配置）
docs/coverage-gap.md   官方 API 覆盖差距五档分析与集成状态
```

## 路线图

- [x] 通用资源引擎：48 组规则的读取 + 启停开关（含对象组、企业版独占过滤）
- [x] 动作按钮：重启 / 备份 / NTP / 版本检测
- [x] CPU、内存历史曲线、流量审计等扩展传感器
- [x] 场景服务：终端断网 / 放行、家长控制（周计划）
- [x] API 全量扩展（v0.4.0）：44 个监控端点传感器化 + 22 项配置读写 + 9 个诊断/配置服务 + AP SSID 下发
- [ ] 规则创建 / 编辑 / 删除的表单化封装（当前可通过 `ikuai.api_request` 或资源引擎覆盖）
- [ ] 提交 HACS 默认仓库

## 已在真机交叉验证

| 设备 | 固件 | 场景 |
|---|---|---|
| x64 软路由 | 4.0.311 | 单 WAN、6–7 个终端、无温控芯片 |
| IK-M200（arm） | 4.0.303 | 5 条 WAN + 1 条 OVPN 线路、74 个终端、无温控芯片 |

两台串行实机验证后，以下现实差异已被处理（也是这类设备接入最容易踩的坑）：

- **明文 http 行为不一致**：一台 302 跳 https，另一台直接 403 → 统一按 https 处理
- **自签证书**：默认不校验
- **`cputemp` 可能为空数组**：无温控机型不产生该传感器的数据（显示不可用而非报错）
- **`connect_num` 可能是 `"--"`、`uprate`/`signal` 可能为空字符串**：统一做清洗
- **`iface_stream` 含非物理接口**（如 `doc_app_default`）、`iface_check` 含 VPN 线路：线路传感器以 `iface_check` 为准，流量仅取有统计数据的接口
- **终端名不可靠**：有的设备把 MAC 的原始二进制字节当 hostname 上报，有的是 URL 编码串（`HUAWEI%20PixLab%20X1_0257`），有的无任何名称 → 依次降级到备注/终端名/厂商，最后兜底 MAC，并自动解码 `%xx` 转义

欢迎提交你的机型验证结果到 issue（附 `tools/dump_api.py` 输出，注意脱敏）。

## 参考

- 官方 OpenAPI 文档：<https://rapi-docs.ikuai8.com/>
- 接口基址：`https://<路由器>/api/v4.0/`，认证方式 `Authorization: Bearer <token>`

## 许可

MIT License。详见 [LICENSE](./LICENSE)。本项目非爱快官方产品。
