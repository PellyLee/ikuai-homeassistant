# iKuai Router — Home Assistant 集成

基于爱快 **iKuaiOS 4.x 官方 OpenAPI** 的 Home Assistant 自定义集成，纯本地轮询，不经过任何云端。

## 你能得到什么

- **系统状态**：CPU 使用率、CPU 温度、内存使用率/占用、总连接数 / TCP / UDP、在线终端数、实时上下行速率、累计流量、运行时间、固件版本
- **WAN 线路**：每条线路的连通性二进制传感器 + 实时上下行速率与累计流量（多 WAN 自动发现）
- **设备追踪**：每个在线终端生成一个 tracker，附带厂商、型号、所属接口、VLAN、SSID 等属性，设备上下线动态增删

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

## 排错

| 现象 | 原因与处理 |
|---|---|
| 无法连接 | 确认地址可达并**使用 https**；HA 与路由器分网段时检查防火墙 |
| 401/403 令牌被拒 | 令牌过期或被重新生成，或后台 API 开关未开启；无令牌请求会返回 401 |
| CPU 温度不可用 | 该机型无温控芯片（`cputemp` 返回空数组），属正常现象 |
| TLS 报错 | 关闭「校验 TLS 证书」选项（自签证书默认不校验） |

日志排查：设置 → 系统 → 日志，关键词 `ikuai`。

## 目录结构

```
custom_components/ikuai/
├── manifest.json      集成元数据
├── const.py           常量与接口路径
├── helpers.py         地址归一化（兼容各种填法）
├── api.py             v4.0 REST 客户端
├── coordinator.py     轮询协调器
├── config_flow.py     配置 / 选项 / 重新认证流程
├── sensor.py          系统传感器 + WAN 流量传感器
├── binary_sensor.py   WAN 线路连通性
├── device_tracker.py  在线终端追踪
└── translations/      zh-Hans / en
tools/dump_api.py      零凭据依赖的诊断脚本
```

## 路线图

- [ ] 重启 / 控制类接口（按钮、开关）
- [ ] CPU、内存历史曲线传感器
- [ ] 更多实体：VLAN、DHCP 客户端、VPN 状态
- [ ] 提交 HA 官方仓库

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
