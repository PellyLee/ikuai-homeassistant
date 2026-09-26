# Phase 4 端点 schema 摘要

> 自动生成于 tools/extract_phase4_schemas.py；components 共 9 个。

## /monitoring/connections
### GET
parameters: datetype (query); start_time (query); end_time (query); math (query)
example keys: results


## /monitoring/cputemp
### GET
parameters: datetype (query); start_time (query); end_time (query); math (query)
example keys: results


## /monitoring/disk
### GET
parameters: datetype (query); start_time (query); end_time (query); math (query)
example keys: results


## /monitoring/network
### GET
parameters: datetype (query); start_time (query); end_time (query); math (query)
example keys: results


## /monitoring/terminals
### GET
parameters: datetype (query); start_time (query); end_time (query); math (query)
example keys: results


## /monitoring/interfaces-config
### GET
example keys: results


## /monitoring/interfaces-physical
### GET
example keys: results, ether_info, eth0, eth1, vnet


## /monitoring/interfaces-traffic
### GET
example keys: results


## /monitoring/interfaces-traffic-v6
### GET
example keys: results


## /monitoring/clients-offline
### GET
parameters: key (query); pattern (query); filter (query)
example keys: results


## /monitoring/clients-ip6-online
### GET
parameters: key (query); pattern (query); filter (query)
example keys: results


## /monitoring/clients-ip6-offline
### GET
parameters: key (query); pattern (query); filter (query)
example keys: results


## /monitoring/clients-traffic-summary
### GET
example keys: results


## /monitoring/clients-traffic-load
### GET
parameters: mac (query); ip (query)
example keys: results


## /monitoring/clients/app-protocols/load
### GET
parameters: mac (query); ip (query); limit (query)
example keys: results, rules, rules


## /monitoring/clients/protocols
### GET
parameters: mac (query); ip (query); starttime (query); stoptime (query)
example keys: results


## /monitoring/clients/protocols/history-load
### GET
parameters: mac (query); ip (query); starttime (query); stoptime (query)
example keys: results


## /monitoring/app-protocols/load
### GET
example keys: results


## /monitoring/app-protocols/history-load
### GET
parameters: starttime (query); stoptime (query); appids (query)
example keys: results


## /monitoring/app-protocols/terminal-load
### GET
parameters: appid (query)
example keys: results


## /monitoring/app-traffic-summary
### GET
example keys: results


## /monitoring/protocols
### GET
parameters: starttime (query); stoptime (query)
example keys: results


## /monitoring/protocols/history-load
### GET
parameters: starttime (query); stoptime (query)
example keys: results


## /monitoring/traffic-audit/accounts
### GET
example keys: results


## /monitoring/traffic-audit/accounts/applications
### GET
parameters: starttime (query); stoptime (query)
example keys: results, apps, apps


## /monitoring/traffic-audit/accounts/trend
### GET
example keys: results


## /monitoring/traffic-audit/terminals/applications
### GET
parameters: starttime (query); stoptime (query)
example keys: results, apps, apps


## /monitoring/traffic-audit/terminals/trend
### GET
example keys: results


## /monitoring/wireless-traffic
### GET


## /monitoring/flow-shunting
### GET
parameters: TYPE (query)


## /monitoring/policy-traffic
### GET
example keys: results, ipgroup, object, ipgroup, custom, ipgroup, object


## /monitoring/aps-channel-noise
### GET
example keys: results


## /monitoring/cameras
### GET
parameters: filter (query); key (query); pattern (query)


## /monitoring/switch
### GET
parameters: filter (query); key (query); pattern (query)


## /monitoring/downstream
### GET
parameters: filter (query); key (query); pattern (query)


## /network/dns/stats
### GET
example keys: results


## /system/cpufreq
### GET


## /system/disks
### GET
example keys: results, filesys, mounted, filesys, mounted, filesys, mounted, filesys, mounted, filesys, mounted, filesys


## /advanced-service/speed-test
### GET
example keys: results, data, wan1, recent_data

### POST
requestBody:
{$ref:"#/components/schemas/SpeedTestStartRequest"
example keys: 

### DELETE
example keys: 


## /monitoring/router-health
### GET
example keys: results

### POST
example keys: 

### DELETE
example keys: 


## /network/pppoe/services
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/PppoeServerConfigInput"
example keys: 


## /vpn/pptp/services
### GET

### PUT
requestBody:
{$ref:"#/components/schemas/PptpServerConfigInput"


## /vpn/l2tp/services
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/L2tpServerConfigInput"
example keys: 


## /vpn/ikev2/services
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/Ikev2ServerConfigInput"
example keys: 


## /vpn/openvpn/services
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/OpenVpnServerConfigInput"
example keys: 


## /interfaces/wan-config
### GET
example keys: results


## /interfaces/wan-config/{id}
### PUT
parameters: id (path)
requestBody:
{$ref:"#/components/schemas/WanConfigUpdateRequest"


## /interfaces/wan-lines
### POST
requestBody:
{$ref:"#/components/schemas/WanLineCreateRequest"
example keys: 


## /interfaces/wan-lines/{id}
### DELETE
parameters: id (path)


## /interfaces/wan-vlan-config
### GET
example keys: results


## /interfaces/lan-config
### GET
example keys: results


## /interfaces/lan-config/{id}
### PUT
parameters: id (path)
requestBody:
{$ref:"#/components/schemas/LanConfigUpdateRequest"
example keys: 


## /interfaces/lan-lines
### POST
requestBody:
{$ref:"#/components/schemas/LanLineCreateRequest"
example keys: 


## /interfaces/lan-lines/{id}
### DELETE
parameters: id (path)


## /interfaces/physical
### GET
example keys: results, ether_info, eth0, eth1, eth2, eth3, vnet


## /network/dns/config
### GET

### PUT
requestBody:
{$ref:"#/components/schemas/DnsConfigInput"
example keys: 


## /network/dhcp/access-control/mode
### GET
example keys: 

### PUT
requestBody:
{$ref:"#/components/schemas/DhcpAccessModeInput"
example keys: 


## /network/dhcp6/access-control/mode
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/Dhcp6AccessModeInput"
example keys: 


## /network/dhcp6/access-control/rules
### GET
parameters: filter (query)
example keys: results

### POST
requestBody:
{$ref:"#/components/schemas/Dhcp6AccessRuleInput"
example keys: 


## /network/dhcp6/access-control/rules/{id}
### GET

### PUT
requestBody:
{$ref:"#/components/schemas/Dhcp6AccessRuleInput"

### DELETE

### PATCH
requestBody:
required: enabled
  enabled* (string) — 规则启用状态
example keys: 


## /network/dhcp6/clients
### GET
parameters: filter (query)
example keys: results


## /auth/users
### GET
parameters: page (query); limit (query); filter (query); order (query); order_by (query)
example keys: results, src_addr, custom

### POST
requestBody:
{$ref:"#/components/schemas/UserInput"
example keys: src_addr


## /auth/users/{id}
### GET

### PUT
requestBody:
{$ref:"#/components/schemas/UserUpdateInput"
example keys: src_addr

### DELETE
example keys: 


## /auth/packages
### GET
parameters: page (query); limit (query); filter (query); order (query); order_by (query)
example keys: results

### POST
requestBody:
{$ref:"#/components/schemas/PackageInput"
example keys: 


## /auth/packages/{id}
### GET

### PUT
requestBody:
{$ref:"#/components/schemas/PackageInput"
example keys: 

### DELETE
example keys: 


## /auth/web/services
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/WebAuthServiceConfigInput"
example keys: 


## /system/alg
### GET
example keys: results

### PUT
requestBody:
required: support_ftp, support_tftp, support_sip, support_h323, ftp_ports, sip_ports, tftp_ports
  support_ftp* (integer) — FTP协议ALG开关（0关闭，1开启）
  support_tftp* (integer) — TFTP协议ALG开关（0关闭，1开启）
  support_sip* (integer) — SIP协议ALG开关（0关闭，1开启）
  support_h323* (integer) — H323协议ALG开关（0关闭，1开启）
  ftp_ports* (string) — FTP自定义端口，逗号分隔，最多7个，与SIP/TFTP端口不可重复，不含默认端口21
  sip_ports* (string) — SIP自定义端口，逗号分隔，最多7个，与FTP/TFTP端口不可重复，不含默认端口5060
  tftp_ports* (string) — TFTP自定义端口，逗号分隔，最多7个，与FTP/SIP端口不可重复，不含默认端口69
example keys: 


## /advanced-service/snmpd-config
### GET

### PUT
requestBody:
{$ref:"#/components/schemas/SnmpdConfigEditInput"


## /advanced-service/samba-config
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/SambaConfigEditInput"


## /advanced-service/ftp-config
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/FtpConfigEditInput"
example keys: 


## /security/advanced/config
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/SecurityAdvancedConfigInput"
example keys: 


## /security/mac-mode
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/MacAclModeInput"
example keys: 


## /system/remote-access
### GET

### PUT
requestBody:
{$ref:"#/components/schemas/RemoteAccessConfigInput"
example keys: 


## /security/secondary-route/config
### GET
example keys: results, nol2rt_ip

### PUT
requestBody:
{$ref:"#/components/schemas/SecondaryRouteConfigInput"
example keys: nol2rt_ip


## /system/kernel-params
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/KernelParamsEditInput"
example keys: 


## /system/cpufreq/mode
### GET

### PUT
requestBody:
{$ref:"#/components/schemas/CpuFrequencyModeEditInput"
example keys: 


## /system/backup-auto
### GET
example keys: results

### PUT
requestBody:
{$ref:"#/components/schemas/BackupSettingsRequest"


## /system/basic/config
### GET

### PUT
requestBody:
{$ref:"#/components/schemas/SystemBasicConfigInput"
example keys: 


## /system/vrrp/config
### GET

### PUT
requestBody:
{$ref:"#/components/schemas/VrrpConfigInput"
example keys: 


## /system/vrrp:start
### POST
example keys: 


## /system/vrrp:stop
### POST
example keys: 


## /network/ac/services
### GET
example keys: results


## /network/ac/services:start
### POST
example keys: 


## /network/ac/services:stop
### POST
example keys: 


## /network/ac/ap-config
### GET


## /network/ac/ap-config/{id}
### GET
parameters: id (path)

### PUT
parameters: id (path)
requestBody:
{$ref:"#/components/schemas/APConfigUpdate"


## /network/ac/ssid-quick
### PUT
requestBody:
{$ref:"#/components/schemas/APSSIDQuickUpdate"
example keys: 


## /network/ac/ssid-union
### PUT
requestBody:
{$ref:"#/components/schemas/APSSIDUnionUpdate"
example keys: 


## /network/dhcp/services:restart
### POST
example keys: 


## /security/terminals
### GET
parameters: page (query); limit (query); filter (query); order (query); order_by (query)

### POST
requestBody:
{$ref:"#/components/schemas/TerminalInput"
example keys: 


## /security/terminals/{id}
### GET
parameters: id (path)

### PUT
parameters: id (path)
requestBody:
{$ref:"#/components/schemas/TerminalInput"

### DELETE
parameters: id (path)
example keys: 


## /vpn/wireguard/{wg_id}/peers
### GET
parameters: key (query); pattern (query); filter (query)

### POST
requestBody:
{$ref:"#/components/schemas/WireguardTunnelInput"
example keys: 


## /vpn/wireguard/{wg_id}/peers/{peer_id}
### GET

### PUT
requestBody:
{$ref:"#/components/schemas/WireguardTunnelInput"

### DELETE

### PATCH
requestBody:
required: enabled
  enabled* (string) — 隧道启用状态
example keys: 

