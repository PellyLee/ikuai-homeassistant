# 落地路线图

接口全貌见 [api-inventory.md](./api-inventory.md)（235 路径 / 476 操作，自动从官方
文档生成）。本文档定义分阶段落地计划与验收标准。

## 一个关键发现：官方 API 是高度规律的 CRUD

绝大多数资源组都遵循同一套模式：

```
GET    /xxx            列表
POST   /xxx            新建
GET    /xxx/{id}       单条
PATCH  /xxx/{id}       启用 / 停用      ← 开关原语
PUT    /xxx/{id}       更新
DELETE /xxx/{id}       删除
```

适用该模式的分组超过 40 个：ACL 规则、MAC ACL、L7 ACL、流控分流
（ipport / domain / proto / updown）、QoS（IP / MAC）、URL 黑白名单与关键字、
域名黑名单、端口映射 DNAT、NAT 规则、DMZ、静态路由、VLAN、DHCP 静态分配、
连接数限制、自定义协议、时间对象 / IP / MAC / 端口 / 协议 / 域名对象组、
无线 ACL、无线 MVLAN、VPN 客户端（WireGuard / OpenVPN / PPTP / L2TP / IKEv2）等。

**结论：不应为每个分组各写一套代码**，而应实现「通用资源引擎」——配置驱动地
声明资源，自动生成开关（PATCH）与读实体（GET）。这是 Phase 2 的核心。

## 阶段划分

### Phase 0 — 只读监控（已完成，v0.1.0）
`/monitoring/system`、`/monitoring/interfaces-status`、`/monitoring/clients-online`
→ 系统传感器、线路连通与流量、设备追踪。

### Phase 1 — 只读面扩展（已完成）
双机验证结果：

| 项 | 设备 A（4.0.311） | 设备 B（4.0.303） |
|---|---|---|
| DHCP 租约 / 静态绑定 | 8 / 7 | 61 / 48 |
| 固件 | 已是最新（4.0.311） | **有更新**（4.0.303 → 4.0.311） |
| 流量审计 | 404，优雅降级为不可用 | 最高终端「海康威视监控」 |
| CPU / 内存小时均值 | 4.3% / 43.0% | 8.6% / 76.3% |
| 无线 | 均为 0（无 AC 纳管 AP） | 均为 0 |

新增接口：
| 目标 | 接口 |
|---|---|
| DHCP 客户端与静态绑定 | `/network/dhcp/clients`、`/network/dhcp/static` |
| 无线监控（SSID / 信道 / 评分 / 流量） | `/monitoring/ssid-clients`、`channel-clients`、`wireless-score`、`wireless-statistics`、`wireless-traffic` |
| 认证用户在线 | `/auth/online-users` |
| 升级状态 | `/system/upgrade`、`/system/upgrade:status` |
| 流量审计 Top N | `/monitoring/traffic-audit/*` |
| 历史曲线（CPU / 内存） | `/monitoring/cpu`、`/monitoring/memory`（datetype 参数） |

架构：新增 `IkuaiExtendedCoordinator`（300 秒轮询），每个接口独立容错——
某功能在设备上不存在（404）时只影响对应实体，写 `IkuaiExtendedData` 的
对应字段为 `None`，实体自动变为不可用。后续阶段沿用此模式。

风险：低。验收（已通过）：两台真机均可用，无新增写操作。

### Phase 2 — 通用资源引擎 + 策略开关（核心价值）

**版本识别（免费版 / 企业版）**
iKuai 有「免费版」（装在 x86 上的软件）与「企业版」（IK-M200 等硬件设备）之分，
暴露的接口不同。固件字段 `verinfo.is_enterprise` 在两台真机上均为 `0`，不可用；
可靠的判据是 `verinfo.modelname` / `verinfo.sn` —— 免费版两者均为空，企业版硬件设备
带型号与序列号。因此：

- `helpers.detect_edition(verinfo)` 自动判定：`is_enterprise` 为真、或 `modelname`/`sn`
  非空 → 企业版，否则免费版。
- 集成选项新增「版本类型」下拉：**自动检测 / 免费版 / 企业版**，允许用户纠偏。
- `resources.py` 中标记为 `enterprise_only=True` 的分组，在免费版上**自动不暴露**
  （不生成开关、选项里打「仅企业版」标签）。
- 真机实测：免费版 `10.10.10.1` 在 40 个资源分组中**只有 `ikev2_clients` 返回 404**，
  企业版 `10.10.5.1` 该分组正常 → 目前唯一确认的企业版独占分组是 IKEv2 客户端。
- 即便判错，分组级 404 也会优雅降级（无实体、仅 debug 日志），不会崩溃。

其余 Phase 2 内容：
1. `api.py`：`async_request`（校验业务 `code`，非仅 HTTP 状态）+ `async_list_resource`
   + `async_set_resource_enabled`（PATCH `{"enabled":"yes"|"no"}`）
2. `resources.py`：40 个资源描述（路径、id 字段、list keys、toggle 方式、label 字段、dangerous）
3. 平台落地：
   - **switch**：对支持 PATCH 的资源按行自动生成「启用/停用」开关，`dangerous` 组
     默认 `entity_registry_enabled_default=False`
   - **button**：立即重启 `/system/reboot-tasks`、手动备份 `/system/backup`、NTP 同步、
     版本检测 `/system/upgrade:check`（重启按钮默认禁用，需显式开启）
   - **sensor / binary_sensor**：资源计数（ACL 规则数、黑名单条数等）
4. **默认关闭写能力**：`enable_write` + `resource_groups` 双重确认，关闭时零额外请求
5. `diagnostics.py`：暴露检测到的版本、版本纠偏值、原始 `verinfo`（便于用户确认）

状态：**代码完成，只读路径双机验证通过**。写通道（创建→启停→删除）依用户要求
**不在远程企业版 10.10.5.1 上实测**（配置无法远程修复）；免费版 10.10.10.1 可做写
实测，但需事后还原——本轮未做写实测，仅做静态/逻辑校验与集成代码路径的只读验证。
后续在用户本地 HA 开启写权限后实测。

风险：中。写操作必须可回滚、可关闭、有确认语义。验收：开关状态与实际路由配置双向一致，断电重启 HA 后状态不漂移。

### Phase 3 — 场景化控制（代码完成，待 HA 内实测）

已落地（v0.3.0）：

1. **终端断网 / 放行**：`ikuai.block_terminal` / `ikuai.allow_terminal` 服务，
   POST/DELETE `security/mac-rules`。`expires_hours` 支持到期自动恢复。
2. **家长控制**：`ikuai.parental_control`（周计划 + 时间模板内联，无需先建时间对象）
   + `ikuai.clear_parental_control`（按「HA集成家长控制」备注标记撤销）。
   关键发现：`acl-rules` 的 `src_addr.custom` 直接接受 MAC/IP 字符串，
   `time.custom` 接受内联周计划 → 对象组不再是前置条件。
3. **VPN 客户端启停**：Phase 2 的资源引擎已覆盖（选项流中 VPN 组打 `[VPN]` 标签）。
4. **无线只读统计**：无线评分 / SSID 终端统计 / 信道终端统计三个传感器
   （`monitoring/wireless-score`、`ssid-clients`、`channel-clients`），
   无 AP 设备上优雅降级为不可用。
5. 资源表扩充对象组（ip/ip6/mac/port/proto/domain/time-objects，共 47 组），
   `api.py` 新增 `async_create_resource` / `async_delete_resource` 原语。

安全设计：服务创建的规则备注固定带「HA集成」前缀标记，撤销服务只删带标记的规则；
服务不依赖 `resource_groups` 勾选，但必须打开 `enable_write`。

风险：中高（会真实改变网络行为）。验收（待做）：用户在 HA 上开启写权限后，
对免费版 10.10.10.1 做创建→启停→删除全链路实测并确认还原；文档已明确副作用。

### Phase 4 — 工程化与发布
- `diagnostics.py`（脱敏诊断下载）、单元测试（脱敏 payload 样本）、quality scale bronze
- 英文本地化补全、README 实体清单自动化生成
- 提交 HACS 默认仓库收录

## 排期建议

| 阶段 | 相对工作量 | 依赖 |
|---|---|---|
| Phase 1 | 小 | 无 |
| Phase 2 | 中 | Phase 1 |
| Phase 3 | 中 | Phase 2 的写通道 |
| Phase 4 | 小 | 前三个阶段稳定后 |

每阶段产出：代码 + 真机验证（至少两台）+ README 更新 + 独立版本号。

## 不做的事

- 不实现账号/管理员管理（`web-admin-accounts`）、备份恢复下发等破坏性高危操作
  ，或仅在显式确认后提供
- 不实现固件升级触发（`/system/upgrade:start`）——风险过高，仅提供状态与检测
