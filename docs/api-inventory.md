# 官方 API 接口清单

> 由 `tools/gen_api_inventory.py` 从 <https://rapi-docs.ikuai8.com/> 自动生成，请勿手工编辑。

共 **235** 个路径 / **476** 个操作，基址 `https://<路由器>/api/v4.0/`。

其中读取 213 个、写入类 263 个。
图例：🔵 GET（读取） / 🟠 POST 新建 / 🔴 DELETE 删除 / 🟣 PUT 更新 / ⚪ PATCH 启用停用

## IPSEC VPN客户端（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/vpn/ipsec/clients` | 获取IPSEC客户端列表 |
| 🟠 POST | `/vpn/ipsec/clients` | 创建IPSEC客户端 |
| 🔴 DELETE | `/vpn/ipsec/clients/{id}` | 删除IPSEC客户端 |
| 🔵 GET | `/vpn/ipsec/clients/{id}` | 获取指定IPSEC客户端 |
| ⚪ PATCH | `/vpn/ipsec/clients/{id}` | 启用/停用IPSEC客户端 |
| 🟣 PUT | `/vpn/ipsec/clients/{id}` | 更新IPSEC客户端 |

## OpenVPN客户端（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/vpn/openvpn/clients` | 获取OpenVPN客户端列表 |
| 🟠 POST | `/vpn/openvpn/clients` | 创建OpenVPN客户端 |
| 🔴 DELETE | `/vpn/openvpn/clients/{id}` | 删除OpenVPN客户端 |
| 🔵 GET | `/vpn/openvpn/clients/{id}` | 获取指定OpenVPN客户端 |
| ⚪ PATCH | `/vpn/openvpn/clients/{id}` | 启用/停用OpenVPN客户端 |
| 🟣 PUT | `/vpn/openvpn/clients/{id}` | 更新OpenVPN客户端 |

## ac-service（3）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/ac/services` | 获取AC服务状态 |
| 🟠 POST | `/network/ac/services:start` | 开启AC服务 |
| 🟠 POST | `/network/ac/services:stop` | 关闭AC服务 |

## acl-l7（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/app-protocols/professional/rules` | 获取应用协议控制策略列表 |
| 🟠 POST | `/security/app-protocols/professional/rules` | 创建应用协议控制策略 |
| 🔴 DELETE | `/security/app-protocols/professional/rules/{id}` | 删除应用协议控制策略 |
| 🔵 GET | `/security/app-protocols/professional/rules/{id}` | 获取单个应用协议控制策略 |
| ⚪ PATCH | `/security/app-protocols/professional/rules/{id}` | 启用/停用应用协议控制策略 |
| 🟣 PUT | `/security/app-protocols/professional/rules/{id}` | 更新应用协议控制策略 |

## acl-mac（8）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/mac-mode` | 获取MAC黑白名单模式 |
| 🟣 PUT | `/security/mac-mode` | 设置MAC黑白名单模式 |
| 🔵 GET | `/security/mac-rules` | 获取MAC黑白名单策略列表 |
| ⚪ PATCH | `/security/mac-rules` | 批量启用/停用MAC策略 |
| 🟠 POST | `/security/mac-rules` | 创建MAC黑白名单策略 |
| 🔴 DELETE | `/security/mac-rules/{id}` | 删除MAC策略 |
| 🔵 GET | `/security/mac-rules/{id}` | 获取单个MAC策略 |
| 🟣 PUT | `/security/mac-rules/{id}` | 更新MAC策略 |

## acl-rules（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/acl-rules` | 获取ACL策略列表 |
| 🟠 POST | `/security/acl-rules` | 创建ACL策略 |
| 🔴 DELETE | `/security/acl-rules/{id}` | 删除ACL策略 |
| 🔵 GET | `/security/acl-rules/{id}` | 获取单个ACL策略 |
| ⚪ PATCH | `/security/acl-rules/{id}` | 启用/停用ACL策略 |
| 🟣 PUT | `/security/acl-rules/{id}` | 更新ACL策略 |

## advanced-protocols（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/app-protocols/advanced/rules` | 获取高级自定义协议列表 |
| 🟠 POST | `/network/app-protocols/advanced/rules` | 创建高级自定义协议 |
| 🔴 DELETE | `/network/app-protocols/advanced/rules/{id}` | 删除高级自定义协议 |
| 🔵 GET | `/network/app-protocols/advanced/rules/{id}` | 获取指定高级自定义协议详情 |
| ⚪ PATCH | `/network/app-protocols/advanced/rules/{id}` | 启用/停用高级自定义协议 |
| 🟣 PUT | `/network/app-protocols/advanced/rules/{id}` | 更新高级自定义协议 |

## advanced-router-health（3）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/monitoring/router-health` | 停止路由体检 |
| 🔵 GET | `/monitoring/router-health` | 查询路由体检结果 |
| 🟠 POST | `/monitoring/router-health` | 启动路由体检 |

## advanced-speed-test（3）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/advanced-service/speed-test` | 停止一键测速 |
| 🔵 GET | `/advanced-service/speed-test` | 查询测速状态、结果和可测速线路 |
| 🟠 POST | `/advanced-service/speed-test` | 启动一键测速 |

## alg（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/alg` | 获取ALG配置 |
| 🟣 PUT | `/system/alg` | 更新ALG配置 |

## ap-config（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/ac/ap-config` | 获取所有AP配置列表 |
| 🔵 GET | `/network/ac/ap-config/{id}` | 获取指定AP配置 |
| 🟣 PUT | `/network/ac/ap-config/{id}` | 更新AP完整配置 |
| 🟣 PUT | `/network/ac/ssid-quick` | 设置AP指定SSID配置 |
| 🟣 PUT | `/network/ac/ssid-union` | 设置AP双频合一Wi-Fi配置 |

## ap-detail（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/aps-channel-noise` | 获取AP信道和底噪信息 |

## auth-users（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/auth/users` | 获取用户账号列表 |
| 🟠 POST | `/auth/users` | 添加用户账号 |
| 🔴 DELETE | `/auth/users/{id}` | 删除用户账号 |
| 🔵 GET | `/auth/users/{id}` | 获取指定用户账号 |
| 🟣 PUT | `/auth/users/{id}` | 修改用户账号 |

## backup（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/system/backup` | 删除备份文件 |
| 🔵 GET | `/system/backup` | 获取备份信息 |
| 🟠 POST | `/system/backup` | 手动备份配置 |
| 🔵 GET | `/system/backup-auto` | 获取自动备份策略 |
| 🟣 PUT | `/system/backup-auto` | 保存自动备份策略 |
| 🟠 POST | `/system/backup:restore` | 恢复备份 |

## cloud-switch（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/switch` | 查询云管交换机设备列表 |

## conn-limit（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/peerconn/rules` | 获取连接数限制策略列表 |
| 🟠 POST | `/security/peerconn/rules` | 创建连接数限制策略 |
| 🔴 DELETE | `/security/peerconn/rules/{id}` | 删除连接数限制策略 |
| 🔵 GET | `/security/peerconn/rules/{id}` | 获取单个连接数限制策略 |
| ⚪ PATCH | `/security/peerconn/rules/{id}` | 启用/停用连接数限制策略 |
| 🟣 PUT | `/security/peerconn/rules/{id}` | 更新连接数限制策略 |

## cpu-freq（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/cpufreq/mode` | 获取CPU工作模式 |
| 🟣 PUT | `/system/cpufreq/mode` | 配置CPU工作模式 |

## cpu-freq-monitor（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/cpufreq` | 获取CPU实时频率 |

## custom-proto（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/app-protocols/custom/rules` | 获取自定义协议策略列表 |
| 🟠 POST | `/network/app-protocols/custom/rules` | 创建自定义协议策略 |
| 🔴 DELETE | `/network/app-protocols/custom/rules/{id}` | 删除自定义协议策略 |
| 🔵 GET | `/network/app-protocols/custom/rules/{id}` | 获取指定自定义协议策略详情 |
| ⚪ PATCH | `/network/app-protocols/custom/rules/{id}` | 启用/停用自定义协议策略 |
| 🟣 PUT | `/network/app-protocols/custom/rules/{id}` | 更新自定义协议策略 |

## dhcp-access-mode（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dhcp/access-control/mode` | 获取访问控制模式 |
| 🟣 PUT | `/network/dhcp/access-control/mode` | 设置访问控制模式 |

## dhcp-access-rules（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dhcp/access-control/rules` | 获取访问控制规则列表 |
| 🟠 POST | `/network/dhcp/access-control/rules` | 创建访问控制规则 |
| 🔴 DELETE | `/network/dhcp/access-control/rules/{id}` | 删除访问控制规则 |
| 🔵 GET | `/network/dhcp/access-control/rules/{id}` | 获取指定访问控制规则 |
| ⚪ PATCH | `/network/dhcp/access-control/rules/{id}` | 启用/停用访问控制规则 |
| 🟣 PUT | `/network/dhcp/access-control/rules/{id}` | 更新访问控制规则 |

## dhcp-clients（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dhcp/clients` | 获取DHCP客户端列表 |

## dhcp-service（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dhcp/services` | 获取所有DHCP策略 |
| 🟠 POST | `/network/dhcp/services` | 创建DHCP策略 |
| 🔴 DELETE | `/network/dhcp/services/{id}` | 删除DHCP策略 |
| 🔵 GET | `/network/dhcp/services/{id}` | 获取指定DHCP策略 |
| ⚪ PATCH | `/network/dhcp/services/{id}` | 启用/停用DHCP策略 |
| 🟣 PUT | `/network/dhcp/services/{id}` | 更新DHCP策略 |

## dhcp-service-control（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🟠 POST | `/network/dhcp/services:restart` | 重启DHCP服务 |

## dhcp-static（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dhcp/static` | 获取静态分配列表 |
| 🟠 POST | `/network/dhcp/static` | 创建静态分配规则 |
| 🔴 DELETE | `/network/dhcp/static/{id}` | 删除静态分配规则 |
| 🔵 GET | `/network/dhcp/static/{id}` | 获取指定静态分配规则 |
| ⚪ PATCH | `/network/dhcp/static/{id}` | 启用/停用静态分配规则 |
| 🟣 PUT | `/network/dhcp/static/{id}` | 更新静态分配规则 |

## dhcpv6-access-mode（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dhcp6/access-control/mode` | 获取DHCPv6访问控制模式 |
| 🟣 PUT | `/network/dhcp6/access-control/mode` | 设置DHCPv6访问控制模式 |

## dhcpv6-access-rules（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dhcp6/access-control/rules` | 获取DHCPv6访问控制规则列表 |
| 🟠 POST | `/network/dhcp6/access-control/rules` | 创建DHCPv6访问控制规则 |
| 🔴 DELETE | `/network/dhcp6/access-control/rules/{id}` | 删除DHCPv6访问控制规则 |
| 🔵 GET | `/network/dhcp6/access-control/rules/{id}` | 获取指定DHCPv6访问控制规则 |
| ⚪ PATCH | `/network/dhcp6/access-control/rules/{id}` | 启用/停用DHCPv6访问控制规则 |
| 🟣 PUT | `/network/dhcp6/access-control/rules/{id}` | 更新DHCPv6访问控制规则 |

## dhcpv6-clients（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dhcp6/clients` | 获取DHCPv6客户端列表 |

## dmz（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dmz/rules` | 获取DMZ策略列表 |
| 🟠 POST | `/network/dmz/rules` | 添加DMZ策略 |
| 🔴 DELETE | `/network/dmz/rules/{id}` | 删除DMZ策略 |
| 🔵 GET | `/network/dmz/rules/{id}` | 获取指定DMZ策略详情 |
| ⚪ PATCH | `/network/dmz/rules/{id}` | 启用/停用DMZ策略 |
| 🟣 PUT | `/network/dmz/rules/{id}` | 更新DMZ策略 |

## dnat（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dnat/rules` | 获取所有DNAT规则 |
| 🟠 POST | `/network/dnat/rules` | 添加DNAT规则 |
| 🔴 DELETE | `/network/dnat/rules/{id}` | 删除DNAT规则 |
| 🔵 GET | `/network/dnat/rules/{id}` | 获取指定DNAT规则详情 |
| ⚪ PATCH | `/network/dnat/rules/{id}` | 启用/停用DNAT规则 |
| 🟣 PUT | `/network/dnat/rules/{id}` | 更新DNAT规则 |

## dns-cache（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dns/stats` | 获取DNS缓存状态 |

## dns-config（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dns/config` | 获取DNS配置 |
| 🟣 PUT | `/network/dns/config` | 更新DNS配置 |

## dns-proxy（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/dns/proxy/rules` | 获取DNS代理规则列表 |
| 🟠 POST | `/network/dns/proxy/rules` | 添加DNS代理规则 |
| 🔴 DELETE | `/network/dns/proxy/rules/{id}` | 删除DNS代理规则 |
| 🔵 GET | `/network/dns/proxy/rules/{id}` | 获取指定DNS代理规则 |
| ⚪ PATCH | `/network/dns/proxy/rules/{id}` | 启用/停用DNS代理规则 |
| 🟣 PUT | `/network/dns/proxy/rules/{id}` | 更新DNS代理规则 |

## domain-blacklist（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/domain-blacklist/rules` | 获取域名黑名单策略列表 |
| 🟠 POST | `/security/domain-blacklist/rules` | 创建域名黑名单策略 |
| 🔴 DELETE | `/security/domain-blacklist/rules/{id}` | 删除域名黑名单策略 |
| 🔵 GET | `/security/domain-blacklist/rules/{id}` | 获取单个域名黑名单策略 |
| ⚪ PATCH | `/security/domain-blacklist/rules/{id}` | 启用/停用域名黑名单策略 |
| 🟣 PUT | `/security/domain-blacklist/rules/{id}` | 更新域名黑名单策略 |

## ftp-config（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/advanced-service/ftp-config` | 获取FTP服务配置 |
| 🟣 PUT | `/advanced-service/ftp-config` | 更新FTP服务配置 |

## ftp-users（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/advanced-service/ftp-users` | 获取FTP用户列表 |
| 🟠 POST | `/advanced-service/ftp-users` | 新增FTP用户 |
| 🔴 DELETE | `/advanced-service/ftp-users/{id}` | 删除FTP用户 |
| ⚪ PATCH | `/advanced-service/ftp-users/{id}` | 启用/停用FTP用户 |
| 🟣 PUT | `/advanced-service/ftp-users/{id}` | 更新FTP用户 |

## http-server（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/advanced-service/http-users` | 获取HTTP服务器列表 |
| 🟠 POST | `/advanced-service/http-users` | 创建HTTP服务器 |
| 🔴 DELETE | `/advanced-service/http-users/{id}` | 删除HTTP服务器 |
| ⚪ PATCH | `/advanced-service/http-users/{id}` | 启用/停用HTTP服务器 |
| 🟣 PUT | `/advanced-service/http-users/{id}` | 更新HTTP服务器 |

## ikev2-clients（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/vpn/ikev2/clients` | 获取IKEv2客户端列表 |
| 🟠 POST | `/vpn/ikev2/clients` | 创建IKEv2客户端 |
| 🔴 DELETE | `/vpn/ikev2/clients/{id}` | 删除IKEv2客户端 |
| 🔵 GET | `/vpn/ikev2/clients/{id}` | 获取指定IKEv2客户端 |
| ⚪ PATCH | `/vpn/ikev2/clients/{id}` | 启用/停用IKEv2客户端 |
| 🟣 PUT | `/vpn/ikev2/clients/{id}` | 更新IKEv2客户端 |

## ikev2-server（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/vpn/ikev2/services` | 获取IKEv2/IPSec服务器配置 |
| 🟣 PUT | `/vpn/ikev2/services` | 更新IKEv2/IPSec服务器配置 |

## kernel-params（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/kernel-params` | 获取内核参数配置 |
| 🟣 PUT | `/system/kernel-params` | 更新内核参数配置 |

## l2tp-clients（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/vpn/l2tp/clients` | 获取L2TP客户端列表 |
| 🟠 POST | `/vpn/l2tp/clients` | 创建L2TP客户端 |
| 🔴 DELETE | `/vpn/l2tp/clients/{id}` | 删除L2TP客户端 |
| 🔵 GET | `/vpn/l2tp/clients/{id}` | 获取指定L2TP客户端 |
| ⚪ PATCH | `/vpn/l2tp/clients/{id}` | 启用/停用L2TP客户端 |
| 🟣 PUT | `/vpn/l2tp/clients/{id}` | 更新L2TP客户端 |

## l2tp-server（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/vpn/l2tp/services` | 获取L2TP服务器配置 |
| 🟣 PUT | `/vpn/l2tp/services` | 更新L2TP服务器配置 |

## lan-interfaces（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/interfaces/lan-config` | 获取LAN接口配置 |
| 🟣 PUT | `/interfaces/lan-config/{id}` | 更新LAN接口配置 |
| 🟠 POST | `/interfaces/lan-lines` | 新建LAN线路 |
| 🔴 DELETE | `/interfaces/lan-lines/{id}` | 删除LAN线路 |
| 🔵 GET | `/interfaces/physical` | 获取物理网卡列表 |

## log-arp（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/log/arp` | 删除ARP日志 |
| 🔵 GET | `/log/arp` | 获取ARP日志列表 |

## log-auth（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/log/auth` | 清空认证日志 |
| 🔵 GET | `/log/auth` | 获取认证日志列表 |

## log-ddns（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/log/ddns` | 清空动态域名日志 |
| 🔵 GET | `/log/ddns` | 获取动态域名日志列表 |

## log-dhcp（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/log/dhcp` | 清空DHCP日志 |
| 🔵 GET | `/log/dhcp` | 获取DHCP日志列表 |

## log-message-center（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/log/message-center` | 获取消息中心列表 |

## log-notice（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/log/notice` | 清空推送通知日志 |
| 🔵 GET | `/log/notice` | 获取推送通知日志列表 |

## log-pppoe（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/log/pppoe` | 清空外网拨号日志 |
| 🔵 GET | `/log/pppoe` | 获取外网拨号日志列表 |

## log-system（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/log/system` | 清空系统日志 |
| 🔵 GET | `/log/system` | 获取系统日志列表 |

## log-terminal-presence（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/log/terminal-presence` | 获取终端上下线日志列表 |

## log-url-visits（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/log/url-visits` | 清空网址浏览记录 |
| 🔵 GET | `/log/url-visits` | 获取网址浏览记录列表 |

## log-warnings（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/log/warnings` | 获取告警信息列表 |

## log-web-activity（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/log/web_activity` | 清空WEB操作日志 |
| 🔵 GET | `/log/web_activity` | 获取WEB操作日志列表 |

## log-wireless-client（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔴 DELETE | `/log/wireless` | 清空无线终端日志 |
| 🔵 GET | `/log/wireless` | 获取无线终端日志列表 |

## mac-comment（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/terminals` | 获取终端设备列表 |
| 🟠 POST | `/security/terminals` | 创建终端设备名称 |
| 🔴 DELETE | `/security/terminals/{id}` | 删除终端设备名称 |
| 🔵 GET | `/security/terminals/{id}` | 获取单个终端设备名称 |
| 🟣 PUT | `/security/terminals/{id}` | 更新终端设备名称 |

## monitor-app-traffic（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/app-protocols/history-load` | 获取应用协议历史速率使用详情 |
| 🔵 GET | `/monitoring/app-protocols/load` | 获取当前应用协议速率使用详情 |
| 🔵 GET | `/monitoring/app-protocols/terminal-load` | 获取访问指定应用协议的终端列表 |
| 🔵 GET | `/monitoring/app-traffic-summary` | 获取最近24小时应用协议流量统计 |
| 🔵 GET | `/monitoring/protocols` | 获取最近24小时协议分类流量汇总 |
| 🔵 GET | `/monitoring/protocols/history-load` | 获取协议分类历史速率 |

## monitor-cameras（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/cameras` | 查询摄像头设备列表 |

## monitor-clients（9）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/clients-ip6-offline` | 获取IPv6终端离线统计 |
| 🔵 GET | `/monitoring/clients-ip6-online` | 获取IPv6终端在线统计 |
| 🔵 GET | `/monitoring/clients-offline` | 获取IPv4终端离线统计 |
| 🔵 GET | `/monitoring/clients-online` | 获取IPv4终端在线统计 |
| 🔵 GET | `/monitoring/clients-traffic-load` | 获取指定终端的5分钟流量负载 |
| 🔵 GET | `/monitoring/clients-traffic-summary` | 获取终端当日流量统计 |
| 🔵 GET | `/monitoring/clients/app-protocols/load` | 获取指定终端当前应用协议速率统计 |
| 🔵 GET | `/monitoring/clients/protocols` | 获取指定终端的协议分类流量统计 |
| 🔵 GET | `/monitoring/clients/protocols/history-load` | 获取指定终端的协议分类历史速率 |

## monitor-flow-shunting（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/flow-shunting` | 查询分流统计数据 |

## monitor-interfaces（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/interfaces-config` | 获取内外网接口配置监控 |
| 🔵 GET | `/monitoring/interfaces-physical` | 获取物理网卡列表 |
| 🔵 GET | `/monitoring/interfaces-status` | 获取线路状态监控 |
| 🔵 GET | `/monitoring/interfaces-traffic` | 获取线路最近24小时流量负载监控 |
| 🔵 GET | `/monitoring/interfaces-traffic-v6` | 获取IPv6线路详情 |

## monitor-load（8）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/connections` | 获取连接数监控数据 |
| 🔵 GET | `/monitoring/cpu` | 获取CPU负载监控数据 |
| 🔵 GET | `/monitoring/cputemp` | 获取系统温度监控数据 |
| 🔵 GET | `/monitoring/disk` | 获取磁盘空间使用监控数据 |
| 🔵 GET | `/monitoring/memory` | 获取内存使用监控数据 |
| 🔵 GET | `/monitoring/network` | 获取网络负载监控数据 |
| 🔵 GET | `/monitoring/system` | 获取系统实时状态信息 |
| 🔵 GET | `/monitoring/terminals` | 获取在线终端数监控数据 |

## monitor-peripheral（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/downstream` | 查询周边设备列表 |

## monitor-policy-traffic（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/policy-traffic` | 获取策略监控数据 |

## monitor-traffic-audit（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/traffic-audit/accounts` | 查询账号流量审计列表 |
| 🔵 GET | `/monitoring/traffic-audit/accounts/applications` | 查询指定账号应用流量详情 |
| 🔵 GET | `/monitoring/traffic-audit/accounts/trend` | 查询指定账号流量趋势详情 |
| 🔵 GET | `/monitoring/traffic-audit/terminals` | 查询 MAC 流量审计列表 |
| 🔵 GET | `/monitoring/traffic-audit/terminals/applications` | 查询指定 MAC 应用流量详情 |
| 🔵 GET | `/monitoring/traffic-audit/terminals/trend` | 查询指定 MAC 流量趋势详情 |

## monitor-wireless（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/monitoring/channel-clients` | 获取信道终端统计 |
| 🔵 GET | `/monitoring/ssid-clients` | 获取SSID终端统计 |
| 🔵 GET | `/monitoring/wireless-score` | 获取无线网络评分 |
| 🔵 GET | `/monitoring/wireless-statistics` | 获取无线监控统计信息 |
| 🔵 GET | `/monitoring/wireless-traffic` | 获取无线流量统计 |

## multi-dns（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/multi-dns/rules` | 获取多线DNS策略列表 |
| 🟠 POST | `/network/multi-dns/rules` | 添加多线DNS策略 |
| 🔴 DELETE | `/network/multi-dns/rules/{id}` | 删除多线DNS策略 |
| 🔵 GET | `/network/multi-dns/rules/{id}` | 获取指定多线DNS策略 |
| ⚪ PATCH | `/network/multi-dns/rules/{id}` | 启用/停用多线DNS策略 |
| 🟣 PUT | `/network/multi-dns/rules/{id}` | 更新多线DNS策略 |

## nat-rules（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/nat/rules` | 获取NAT规则列表 |
| 🟠 POST | `/network/nat/rules` | 创建NAT规则 |
| 🔴 DELETE | `/network/nat/rules/{id}` | 删除NAT规则 |
| 🔵 GET | `/network/nat/rules/{id}` | 获取指定NAT规则详情 |
| ⚪ PATCH | `/network/nat/rules/{id}` | 启用/停用NAT规则 |
| 🟣 PUT | `/network/nat/rules/{id}` | 更新NAT规则 |

## object-domain（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/domain-objects` | 获取域名对象列表 |
| 🟠 POST | `/domain-objects` | 创建域名对象 |
| 🔵 GET | `/domain-objects/ref` | 查询域名对象引用关系 |
| 🔴 DELETE | `/domain-objects/{id}` | 删除域名对象 |
| 🔵 GET | `/domain-objects/{id}` | 获取指定域名对象 |
| 🟣 PUT | `/domain-objects/{id}` | 更新域名对象 |

## object-ip（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/ip-objects` | 获取IP对象列表 |
| 🟠 POST | `/ip-objects` | 创建IP对象 |
| 🔵 GET | `/ip-objects/ref` | 查询IP对象引用 |
| 🔴 DELETE | `/ip-objects/{id}` | 删除IP对象 |
| 🔵 GET | `/ip-objects/{id}` | 获取指定IP对象 |
| 🟣 PUT | `/ip-objects/{id}` | 更新IP对象 |

## object-ipv6（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/ip6-objects` | 获取IPv6对象列表 |
| 🟠 POST | `/ip6-objects` | 创建IPv6对象 |
| 🔵 GET | `/ip6-objects/ref` | 查询IPv6对象引用关系 |
| 🔴 DELETE | `/ip6-objects/{id}` | 删除IPv6对象 |
| 🔵 GET | `/ip6-objects/{id}` | 获取指定IPv6对象 |
| 🟣 PUT | `/ip6-objects/{id}` | 更新IPv6对象 |

## object-mac（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/mac-objects` | 获取MAC对象列表 |
| 🟠 POST | `/mac-objects` | 创建MAC对象 |
| 🔵 GET | `/mac-objects/ref` | 查询MAC对象引用 |
| 🔴 DELETE | `/mac-objects/{id}` | 删除MAC对象 |
| 🔵 GET | `/mac-objects/{id}` | 获取指定MAC对象 |
| 🟣 PUT | `/mac-objects/{id}` | 更新MAC对象 |

## object-port（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/port-objects` | 获取端口对象列表 |
| 🟠 POST | `/port-objects` | 创建端口对象 |
| 🔵 GET | `/port-objects/ref` | 查询端口对象引用关系 |
| 🔴 DELETE | `/port-objects/{id}` | 删除端口对象 |
| 🔵 GET | `/port-objects/{id}` | 获取指定端口对象 |
| 🟣 PUT | `/port-objects/{id}` | 更新端口对象 |

## object-proto（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/proto-objects` | 获取协议对象列表 |
| 🟠 POST | `/proto-objects` | 创建协议对象 |
| 🔵 GET | `/proto-objects/ref` | 查询协议对象引用关系 |
| 🔴 DELETE | `/proto-objects/{id}` | 删除协议对象 |
| 🔵 GET | `/proto-objects/{id}` | 获取指定协议对象 |
| 🟣 PUT | `/proto-objects/{id}` | 更新协议对象 |

## object-time（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/time-objects` | 获取时间对象列表 |
| 🟠 POST | `/time-objects` | 创建时间对象 |
| 🔵 GET | `/time-objects/ref` | 查询时间对象引用 |
| 🔴 DELETE | `/time-objects/{id}` | 删除时间对象 |
| 🔵 GET | `/time-objects/{id}` | 获取指定时间对象 |
| 🟣 PUT | `/time-objects/{id}` | 更新时间对象 |

## online-users（3）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/auth/online-users` | 获取认证用户列表 |
| 🔴 DELETE | `/auth/online-users/{id}` | 断开认证用户 |
| 🔵 GET | `/auth/online-users/{id}` | 获取指定认证用户 |

## openvpn-server（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/vpn/openvpn/services` | 获取OpenVPN服务器配置 |
| 🟣 PUT | `/vpn/openvpn/services` | 更新OpenVPN服务器配置 |

## packages（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/auth/packages` | 获取套餐列表 |
| 🟠 POST | `/auth/packages` | 添加套餐 |
| 🔴 DELETE | `/auth/packages/{id}` | 删除套餐 |
| 🔵 GET | `/auth/packages/{id}` | 获取指定套餐 |
| 🟣 PUT | `/auth/packages/{id}` | 修改套餐 |

## peerconn（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/secondary-route/config` | 获取网络分享控制策略 |
| 🟣 PUT | `/security/secondary-route/config` | 更新网络分享控制策略 |

## pppoe-server（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/pppoe/services` | 获取PPPoE服务器配置 |
| 🟣 PUT | `/network/pppoe/services` | 更新PPPoE服务器配置 |

## pptp-clients（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/vpn/pptp/clients` | 获取PPTP客户端列表 |
| 🟠 POST | `/vpn/pptp/clients` | 创建PPTP客户端 |
| 🔴 DELETE | `/vpn/pptp/clients/{id}` | 删除PPTP客户端 |
| 🔵 GET | `/vpn/pptp/clients/{id}` | 获取指定PPTP客户端 |
| ⚪ PATCH | `/vpn/pptp/clients/{id}` | 启用/停用PPTP客户端 |
| 🟣 PUT | `/vpn/pptp/clients/{id}` | 更新PPTP客户端 |

## pptp-server（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/vpn/pptp/services` | 获取PPTP服务器配置 |
| 🟣 PUT | `/vpn/pptp/services` | 更新PPTP服务器配置 |

## qos-ip（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/qos/ip` | 获取IP限速列表 |
| 🟠 POST | `/network/qos/ip` | 创建IP限速规则 |
| 🔴 DELETE | `/network/qos/ip/{id}` | 删除IP限速规则 |
| 🔵 GET | `/network/qos/ip/{id}` | 获取指定IP限速规则 |
| ⚪ PATCH | `/network/qos/ip/{id}` | 启用/停用IP限速规则 |
| 🟣 PUT | `/network/qos/ip/{id}` | 更新IP限速规则 |

## qos-mac（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/qos/mac` | 获取MAC限速列表 |
| 🟠 POST | `/network/qos/mac` | 创建MAC限速规则 |
| 🔴 DELETE | `/network/qos/mac/{id}` | 删除MAC限速规则 |
| 🔵 GET | `/network/qos/mac/{id}` | 获取指定MAC限速规则 |
| ⚪ PATCH | `/network/qos/mac/{id}` | 启用/停用MAC限速规则 |
| 🟣 PUT | `/network/qos/mac/{id}` | 更新MAC限速规则 |

## reboots（7）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/reboot-schedules` | 获取重启计划列表 |
| 🟠 POST | `/system/reboot-schedules` | 添加重启计划 |
| 🔴 DELETE | `/system/reboot-schedules/{id}` | 删除重启计划 |
| 🔵 GET | `/system/reboot-schedules/{id}` | 获取指定重启计划 |
| ⚪ PATCH | `/system/reboot-schedules/{id}` | 启用/停用重启计划 |
| 🟣 PUT | `/system/reboot-schedules/{id}` | 更新重启计划 |
| 🟠 POST | `/system/reboot-tasks` | 立即重启 |

## remote-access（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/remote-access` | 获取远程访问配置 |
| 🟣 PUT | `/system/remote-access` | 更新远程访问配置 |

## samba-service（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/advanced-service/samba-config` | 获取Samba服务基础配置 |
| 🟣 PUT | `/advanced-service/samba-config` | 更新Samba服务基础配置 |

## samba-users（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/advanced-service/samba-users` | 获取Samba用户列表 |
| 🟠 POST | `/advanced-service/samba-users` | 创建Samba用户 |
| 🔴 DELETE | `/advanced-service/samba-users/{id}` | 删除Samba用户 |
| ⚪ PATCH | `/advanced-service/samba-users/{id}` | 启用/停用Samba用户 |
| 🟣 PUT | `/advanced-service/samba-users/{id}` | 更新Samba用户 |

## security-advanced（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/advanced/config` | 获取安全中心高级设置 |
| 🟣 PUT | `/security/advanced/config` | 更新安全中心高级设置 |

## snmp-service（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/advanced-service/snmpd-config` | 获取SNMP服务配置 |
| 🟣 PUT | `/advanced-service/snmpd-config` | 更新SNMP服务配置 |

## static-routes（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/routing/static-routes` | 获取所有静态路由策略 |
| 🟠 POST | `/routing/static-routes` | 添加静态路由策略 |
| 🔴 DELETE | `/routing/static-routes/{id}` | 删除静态路由策略 |
| 🔵 GET | `/routing/static-routes/{id}` | 获取指定静态路由策略 |
| ⚪ PATCH | `/routing/static-routes/{id}` | 启用/停用静态路由策略 |
| 🟣 PUT | `/routing/static-routes/{id}` | 更新静态路由策略 |

## stream-domain（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/routing/domain-rules` | 获取所有域名分流策略 |
| 🟠 POST | `/routing/domain-rules` | 添加域名分流策略 |
| 🔴 DELETE | `/routing/domain-rules/{id}` | 删除域名分流策略 |
| 🔵 GET | `/routing/domain-rules/{id}` | 获取指定域名分流策略 |
| ⚪ PATCH | `/routing/domain-rules/{id}` | 启用/停用域名分流策略 |
| 🟣 PUT | `/routing/domain-rules/{id}` | 更新域名分流策略 |

## stream-ipport（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/routing/five-tuple-rules` | 获取所有端口分流策略 |
| 🟠 POST | `/routing/five-tuple-rules` | 添加端口分流策略 |
| 🔴 DELETE | `/routing/five-tuple-rules/{id}` | 删除端口分流策略 |
| 🔵 GET | `/routing/five-tuple-rules/{id}` | 获取指定端口分流策略 |
| ⚪ PATCH | `/routing/five-tuple-rules/{id}` | 启用/停用端口分流策略 |
| 🟣 PUT | `/routing/five-tuple-rules/{id}` | 更新端口分流策略 |

## stream-load（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/routing/load-balance-rules` | 获取所有多线负载分流策略 |
| 🟠 POST | `/routing/load-balance-rules` | 添加多线负载分流策略 |
| 🔴 DELETE | `/routing/load-balance-rules/{id}` | 删除多线负载分流策略 |
| 🔵 GET | `/routing/load-balance-rules/{id}` | 获取指定多线负载分流策略 |
| ⚪ PATCH | `/routing/load-balance-rules/{id}` | 启用/停用多线负载分流策略 |
| 🟣 PUT | `/routing/load-balance-rules/{id}` | 更新多线负载分流策略 |

## stream-proto（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/routing/app-protocols` | 获取所有协议分流策略 |
| 🟠 POST | `/routing/app-protocols` | 添加协议分流策略 |
| 🔴 DELETE | `/routing/app-protocols/{id}` | 删除协议分流策略 |
| 🔵 GET | `/routing/app-protocols/{id}` | 获取指定协议分流策略 |
| ⚪ PATCH | `/routing/app-protocols/{id}` | 启用/停用协议分流策略 |
| 🟣 PUT | `/routing/app-protocols/{id}` | 更新协议分流策略 |

## stream-updown（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/routing/updown` | 获取所有上下行分离策略 |
| 🟠 POST | `/routing/updown` | 添加上下行分离策略 |
| 🔴 DELETE | `/routing/updown/{id}` | 删除上下行分离策略 |
| 🔵 GET | `/routing/updown/{id}` | 获取指定上下行分离策略 |
| ⚪ PATCH | `/routing/updown/{id}` | 启用/停用上下行分离策略 |
| 🟣 PUT | `/routing/updown/{id}` | 更新上下行分离策略 |

## system-basic（3）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/basic/config` | 获取系统基础设置 |
| 🟣 PUT | `/system/basic/config` | 更新系统基础设置 |
| 🟠 POST | `/system/basic/ntp:sync` | 立即进行NTP同步 |

## system-disks（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/disks` | 获取系统磁盘信息 |

## system-files（1）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/files` | 获取文件列表 |

## upgrade（4）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/upgrade` | 获取版本信息 |
| 🟠 POST | `/system/upgrade:check` | 版本检测 |
| 🟠 POST | `/system/upgrade:start` | 立即升级 |
| 🔵 GET | `/system/upgrade:status` | 获取升级状态 |

## url-blacklist（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/url-black/rules` | 获取URL黑白名单策略列表 |
| ⚪ PATCH | `/security/url-black/rules` | 批量启用/停用URL黑白名单策略 |
| 🟠 POST | `/security/url-black/rules` | 创建URL黑白名单策略 |
| 🔴 DELETE | `/security/url-black/rules/{id}` | 删除URL黑白名单策略 |
| 🔵 GET | `/security/url-black/rules/{id}` | 获取单个URL黑白名单策略 |
| 🟣 PUT | `/security/url-black/rules/{id}` | 更新URL黑白名单策略 |

## url-keywords（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/url-keywords/rules` | 获取URL关键字替换策略列表 |
| ⚪ PATCH | `/security/url-keywords/rules` | 批量启用/停用URL关键字替换策略 |
| 🟠 POST | `/security/url-keywords/rules` | 创建URL关键字替换策略 |
| 🔴 DELETE | `/security/url-keywords/rules/{id}` | 删除URL关键字替换策略 |
| 🔵 GET | `/security/url-keywords/rules/{id}` | 获取单个URL关键字替换策略 |
| 🟣 PUT | `/security/url-keywords/rules/{id}` | 更新URL关键字替换策略 |

## url-redirect（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/url-redirect/rules` | 获取URL跳转策略列表 |
| ⚪ PATCH | `/security/url-redirect/rules` | 批量启用/停用URL跳转策略 |
| 🟠 POST | `/security/url-redirect/rules` | 创建URL跳转策略 |
| 🔴 DELETE | `/security/url-redirect/rules/{id}` | 删除URL跳转策略 |
| 🔵 GET | `/security/url-redirect/rules/{id}` | 获取单个URL跳转策略 |
| 🟣 PUT | `/security/url-redirect/rules/{id}` | 更新URL跳转策略 |

## url-replace（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/security/url-replace/rules` | 获取URL参数替换策略列表 |
| ⚪ PATCH | `/security/url-replace/rules` | 批量启用/停用URL参数替换策略 |
| 🟠 POST | `/security/url-replace/rules` | 创建URL参数替换策略 |
| 🔴 DELETE | `/security/url-replace/rules/{id}` | 删除URL参数替换策略 |
| 🔵 GET | `/security/url-replace/rules/{id}` | 获取单个URL参数替换策略 |
| 🟣 PUT | `/security/url-replace/rules/{id}` | 更新URL参数替换策略 |

## vlan（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/network/vlan` | 获取VLAN接口配置列表 |
| 🟠 POST | `/network/vlan` | 新建VLAN接口 |
| 🔴 DELETE | `/network/vlan/{id}` | 删除VLAN接口 |
| 🔵 GET | `/network/vlan/{id}` | 获取单个VLAN接口配置 |
| ⚪ PATCH | `/network/vlan/{id}` | 启用/停用VLAN接口 |
| 🟣 PUT | `/network/vlan/{id}` | 更新VLAN接口配置 |

## vrrp-config（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/vrrp/config` | 获取热备配置 |
| 🟣 PUT | `/system/vrrp/config` | 设置热备配置 |

## vrrp-control（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🟠 POST | `/system/vrrp:start` | 开启热备配置 |
| 🟠 POST | `/system/vrrp:stop` | 关闭热备配置 |

## wan-interfaces（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/interfaces/wan-config` | 获取WAN接口配置 |
| 🟣 PUT | `/interfaces/wan-config/{id}` | 更新WAN接口配置 |
| 🟠 POST | `/interfaces/wan-lines` | 新建WAN线路 |
| 🔴 DELETE | `/interfaces/wan-lines/{id}` | 删除WAN线路 |
| 🔵 GET | `/interfaces/wan-vlan-config` | 获取WAN混合模式配置 |

## web-admin-accounts（7）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/web-admin/accounts` | 获取WEB登录账号列表 |
| 🟠 POST | `/system/web-admin/accounts` | 新增WEB登录账号 |
| 🔴 DELETE | `/system/web-admin/accounts/{id}` | 删除WEB登录账号 |
| 🔵 GET | `/system/web-admin/accounts/{id}` | 获取单个WEB登录账号详情 |
| 🟣 PUT | `/system/web-admin/accounts/{id}` | 全量修改WEB登录账号 |
| 🟣 PUT | `/system/web-admin/password` | 修改WEB登录账号密码 |
| 🔵 GET | `/system/web-admin/password-status` | 查询账号是否需要修改密码 |

## web-admin-groups（5）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/system/web-admin/groups` | 获取WEB登录用户组列表 |
| 🟠 POST | `/system/web-admin/groups` | 新增WEB登录用户组 |
| 🔴 DELETE | `/system/web-admin/groups/{id}` | 删除WEB登录用户组 |
| 🔵 GET | `/system/web-admin/groups/{id}` | 获取单个WEB登录用户组详情 |
| 🟣 PUT | `/system/web-admin/groups/{id}` | 全量修改WEB登录用户组 |

## web-auth（2）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/auth/web/services` | 获取WEB认证服务配置 |
| 🟣 PUT | `/auth/web/services` | 更新WEB认证服务配置 |

## wireguard-interfaces（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/vpn/wireguard` | 获取WireGuard接口列表 |
| 🟠 POST | `/vpn/wireguard` | 创建WireGuard接口 |
| 🔴 DELETE | `/vpn/wireguard/{wg_id}` | 删除WireGuard接口 |
| 🔵 GET | `/vpn/wireguard/{wg_id}` | 获取指定WireGuard接口 |
| ⚪ PATCH | `/vpn/wireguard/{wg_id}` | 启用/停用WireGuard接口 |
| 🟣 PUT | `/vpn/wireguard/{wg_id}` | 更新WireGuard接口 |

## wireguard-tunnels（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/vpn/wireguard/{wg_id}/peers` | 获取WireGuard隧道列表 |
| 🟠 POST | `/vpn/wireguard/{wg_id}/peers` | 创建WireGuard隧道 |
| 🔴 DELETE | `/vpn/wireguard/{wg_id}/peers/{peer_id}` | 删除WireGuard隧道 |
| 🔵 GET | `/vpn/wireguard/{wg_id}/peers/{peer_id}` | 获取指定WireGuard隧道 |
| ⚪ PATCH | `/vpn/wireguard/{wg_id}/peers/{peer_id}` | 启用/停用WireGuard隧道 |
| 🟣 PUT | `/vpn/wireguard/{wg_id}/peers/{peer_id}` | 更新WireGuard隧道 |

## wireless-acl（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/wireless/access-control/rules` | 获取无线黑白名单列表 |
| 🟠 POST | `/wireless/access-control/rules` | 添加无线黑白名单配置 |
| 🔴 DELETE | `/wireless/access-control/rules/{id}` | 删除无线黑白名单 |
| 🔵 GET | `/wireless/access-control/rules/{id}` | 获取指定无线黑白名单 |
| ⚪ PATCH | `/wireless/access-control/rules/{id}` | 启用/停用无线黑白名单 |
| 🟣 PUT | `/wireless/access-control/rules/{id}` | 更新无线黑白名单的配置 |

## wireless-mvlan（6）

| 方法 | 路径 | 说明 |
|---|---|---|
| 🔵 GET | `/wireless/vlan/rules` | 获取无线终端VLAN列表 |
| 🟠 POST | `/wireless/vlan/rules` | 添加无线终端VLAN配置 |
| 🔴 DELETE | `/wireless/vlan/rules/{id}` | 删除无线终端VLAN |
| 🔵 GET | `/wireless/vlan/rules/{id}` | 获取指定无线终端VLAN |
| ⚪ PATCH | `/wireless/vlan/rules/{id}` | 启用/停用无线终端VLAN |
| 🟣 PUT | `/wireless/vlan/rules/{id}` | 更新无线终端VLAN的配置 |

