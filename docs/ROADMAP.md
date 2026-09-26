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
1. `api.py` 增加 `async_request(method, path, json)`，统一 PATCH/PUT/POST/DELETE
2. `resources.py`：资源描述表（路径、id 字段、名称字段、是否支持开关）
3. 平台落地：
   - **switch**：对支持 PATCH 的资源自动生成「启用/停用」开关
   - **button**：立即重启 `/system/reboot-tasks`、手动备份 `/system/backup`、NTP 同步、版本检测 `/system/upgrade:check`、断开认证用户 `DELETE /auth/online-users/{id}`
   - **sensor / binary_sensor**：资源计数（ACL 规则数、黑名单条数等）
4. **默认关闭写能力**，由用户在集成选项中显式开启，开关默认 `entity_registry_enabled_default=False`

风险：中。写操作必须可回滚、可关闭、有确认语义。验收：开关状态与实际路由配置双向一致，断电重启 HA 后状态不漂移。

### Phase 3 — 场景化控制
| 场景 | 接口 |
|---|---|
| 终端断网 / 放行 | `/security/acl-mac`、`/object-mac` |
| 家长控制（时间对象 + ACL） | `/object-time` + `/security/acl-rules` |
| VPN 客户端启停 | WireGuard / OpenVPN / PPTP / L2TP / IKEv2 客户端组 |
| 无线 SSID 与 AP 管理 | `/wireless/*`、`/ap-config`、`/ap-detail` |

风险：中高（会真实改变网络行为）。验收：提供「恢复默认」路径，文档中明确副作用。

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
