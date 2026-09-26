"""Declarative description of the iKuai CRUD resource groups.

More than 40 groups in the official API share the exact same shape:

    GET    /xxx            列表
    POST   /xxx            新建
    GET    /xxx/{id}       单条
    PATCH  /xxx/{id}       启用 / 停用
    PUT    /xxx/{id}       更新
    DELETE /xxx/{id}       删除

Instead of writing one entity class per group, every group is declared once
here and the switch platform renders it generically.

Two details were confirmed against real devices and are easy to get wrong:

* ``enabled`` is the **string** ``"yes"`` / ``"no"``, never 0/1.
* the list row key is not always ``data``; some groups use ``static_data``,
  ``iface_data`` or ``dir_data``.
* a handful of groups toggle on the *collection* path with a batch body
  ``{"id": "1,2,3", "enabled": "yes"}`` instead of ``PATCH /xxx/{id}``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

TOGGLE_SINGLE = "single"  # PATCH /path/{id}          {"enabled": "yes"|"no"}
TOGGLE_BATCH = "batch"    # PATCH /path               {"id": "1,2,3", "enabled": ...}


@dataclass(frozen=True)
class IkuaiResource:
    """One CRUD-capable resource group."""

    key: str
    """Stable identifier: used in the options flow and in entity unique ids."""

    path: str
    """Collection path relative to /api/v4.0/, e.g. ``security/acl-rules``."""

    name: str
    """Human readable group name."""

    id_field: str = "id"
    """Name of the primary key in a row (WireGuard uses ``wg_id``)."""

    enabled_field: str = "enabled"
    """Name of the enabled flag in a row."""

    list_keys: tuple[str, ...] = ("data",)
    """Candidate keys holding the row list, tried in order."""

    toggle: str = TOGGLE_SINGLE
    """How the enable/disable request is shaped."""

    label_fields: tuple[str, ...] = ("comment", "termname", "name", "tagname")
    """Fields tried in order to build a human readable entity name."""

    dangerous: bool = False
    """True when flipping a rule can cut someone off the network."""

    enterprise_only: bool = False
    """True when the group is not exposed by the free (软件版) firmware.

    Auto-detected by :func:`ikuai.helpers.detect_edition`; on a free edition such
    groups are hidden from the options picker and skipped during discovery so a
    user never enables a switch that would 404 on every refresh.
    """

    extra_attrs: tuple[str, ...] = field(default=())
    """Row fields copied into the entity attributes for context."""


RESOURCES: tuple[IkuaiResource, ...] = (
    # -- 行为管控 / 安全 -----------------------------------------------------
    IkuaiResource(
        key="acl_rules",
        path="security/acl-rules",
        name="ACL 策略",
        dangerous=True,
        extra_attrs=("src_addr", "dst_addr", "action", "prio"),
    ),
    IkuaiResource(
        key="mac_rules",
        path="security/mac-rules",
        name="MAC 黑白名单",
        toggle=TOGGLE_BATCH,
        dangerous=True,
        extra_attrs=("mac", "termname"),
    ),
    IkuaiResource(
        key="l7_rules",
        path="security/app-protocols/professional/rules",
        name="应用协议控制",
        dangerous=True,
    ),
    IkuaiResource(
        key="domain_blacklist",
        path="security/domain-blacklist/rules",
        name="域名黑名单",
        dangerous=True,
        extra_attrs=("domain_group",),
    ),
    IkuaiResource(
        key="conn_limit",
        path="security/peerconn/rules",
        name="连接数限制",
        dangerous=True,
    ),
    IkuaiResource(
        key="url_black",
        path="security/url-black/rules",
        name="URL 黑白名单",
        toggle=TOGGLE_BATCH,
        dangerous=True,
    ),
    IkuaiResource(
        key="url_keywords",
        path="security/url-keywords/rules",
        name="URL 关键字替换",
        toggle=TOGGLE_BATCH,
    ),
    IkuaiResource(
        key="url_redirect",
        path="security/url-redirect/rules",
        name="URL 跳转",
        toggle=TOGGLE_BATCH,
    ),
    IkuaiResource(
        key="url_replace",
        path="security/url-replace/rules",
        name="URL 参数替换",
        toggle=TOGGLE_BATCH,
    ),
    # -- 网络 / DHCP / 地址转换 ---------------------------------------------
    IkuaiResource(
        key="dhcp_access_control",
        path="network/dhcp/access-control/rules",
        name="DHCP 访问控制",
        dangerous=True,
        extra_attrs=("mac", "termname"),
    ),
    IkuaiResource(
        key="dhcp_services",
        path="network/dhcp/services",
        name="DHCP 服务",
        dangerous=True,
        extra_attrs=("interface", "addr_pool", "gateway"),
    ),
    IkuaiResource(
        key="dhcp_static",
        path="network/dhcp/static",
        name="DHCP 静态分配",
        list_keys=("static_data", "data"),
        extra_attrs=("mac", "ip_addr", "hostname", "termname"),
    ),
    IkuaiResource(
        key="dmz",
        path="network/dmz/rules",
        name="DMZ 主机",
        extra_attrs=("lan_addr", "interface"),
    ),
    IkuaiResource(
        key="dnat",
        path="network/dnat/rules",
        name="端口映射 (DNAT)",
        extra_attrs=("interface", "protocol", "wan_port", "lan_addr", "lan_port"),
    ),
    IkuaiResource(
        key="nat",
        path="network/nat/rules",
        name="NAT 规则",
        extra_attrs=("interface", "src_addr", "lan_addr"),
    ),
    IkuaiResource(
        key="dns_proxy",
        path="network/dns/proxy/rules",
        name="DNS 代理",
        dangerous=True,
    ),
    IkuaiResource(
        key="multi_dns",
        path="network/multi-dns/rules",
        name="多线 DNS",
        dangerous=True,
        extra_attrs=("interface", "dns1", "dns2"),
    ),
    IkuaiResource(
        key="vlan",
        path="network/vlan",
        name="VLAN 接口",
        dangerous=True,
    ),
    IkuaiResource(
        key="qos_ip",
        path="network/qos/ip",
        name="IP 限速",
        dangerous=True,
        extra_attrs=("ip_addr", "upload", "download"),
    ),
    IkuaiResource(
        key="qos_mac",
        path="network/qos/mac",
        name="MAC 限速",
        dangerous=True,
        extra_attrs=("mac_addr", "upload", "download"),
    ),
    IkuaiResource(
        key="custom_protocol",
        path="network/app-protocols/custom/rules",
        name="自定义协议",
    ),
    IkuaiResource(
        key="advanced_protocol",
        path="network/app-protocols/advanced/rules",
        name="高级自定义协议",
    ),
    # -- 路由 / 分流 ---------------------------------------------------------
    IkuaiResource(
        key="static_routes",
        path="routing/static-routes",
        name="静态路由",
        dangerous=True,
        extra_attrs=("dst_addr", "netmask", "gateway", "interface"),
    ),
    IkuaiResource(
        key="domain_routing",
        path="routing/domain-rules",
        name="域名分流",
        dangerous=True,
    ),
    IkuaiResource(
        key="five_tuple",
        path="routing/five-tuple-rules",
        name="端口分流",
        dangerous=True,
        extra_attrs=("src_addr", "dst_addr", "protocol", "interface"),
    ),
    IkuaiResource(
        key="load_balance",
        path="routing/load-balance-rules",
        name="多线负载分流",
        dangerous=True,
        extra_attrs=("interface", "mode", "weight"),
    ),
    IkuaiResource(
        key="protocol_routing",
        path="routing/app-protocols",
        name="协议分流",
        dangerous=True,
    ),
    IkuaiResource(
        key="updown",
        path="routing/updown",
        name="上下行分离",
        dangerous=True,
    ),
    # -- VPN -----------------------------------------------------------------
    IkuaiResource(
        key="wireguard",
        path="vpn/wireguard",
        name="WireGuard",
        id_field="wg_id",
        list_keys=("iface_data", "data"),
        dangerous=True,
    ),
    IkuaiResource(
        key="openvpn_clients",
        path="vpn/openvpn/clients",
        name="OpenVPN 客户端",
        extra_attrs=("remote_addr", "remote_port"),
    ),
    IkuaiResource(
        key="pptp_clients",
        path="vpn/pptp/clients",
        name="PPTP 客户端",
    ),
    IkuaiResource(
        key="l2tp_clients",
        path="vpn/l2tp/clients",
        name="L2TP 客户端",
    ),
    IkuaiResource(
        key="ikev2_clients",
        path="vpn/ikev2/clients",
        name="IKEv2 客户端",
        enterprise_only=True,
    ),
    IkuaiResource(
        key="ipsec_clients",
        path="vpn/ipsec/clients",
        name="IPsec 客户端",
    ),
    # -- 无线 -----------------------------------------------------------------
    IkuaiResource(
        key="wireless_acl",
        path="wireless/access-control/rules",
        name="无线黑白名单",
        dangerous=True,
    ),
    IkuaiResource(
        key="wireless_vlan",
        path="wireless/vlan/rules",
        name="无线终端 VLAN",
        dangerous=True,
    ),
    # -- 系统 / 服务 ---------------------------------------------------------
    IkuaiResource(
        key="reboot_schedules",
        path="system/reboot-schedules",
        name="定时重启计划",
        dangerous=True,
    ),
    IkuaiResource(
        key="ftp_users",
        path="advanced-service/ftp-users",
        name="FTP 用户",
    ),
    IkuaiResource(
        key="http_users",
        path="advanced-service/http-users",
        name="HTTP 服务",
    ),
    IkuaiResource(
        key="samba_users",
        path="advanced-service/samba-users",
        name="Samba 用户",
        list_keys=("dir_data", "data"),
    ),
    # -- 对象组（断网 / 家长控制等场景的前置素材，也可仅做启停开关） ----------
    IkuaiResource(
        key="object_ip",
        path="ip-objects",
        name="IP 对象",
        label_fields=("gp_name", "tagname", "comment"),
    ),
    IkuaiResource(
        key="object_ip6",
        path="ip6-objects",
        name="IPv6 对象",
        label_fields=("gp_name", "tagname", "comment"),
    ),
    IkuaiResource(
        key="object_mac",
        path="mac-objects",
        name="MAC 对象",
        label_fields=("gp_name", "tagname", "comment"),
    ),
    IkuaiResource(
        key="object_port",
        path="port-objects",
        name="端口对象",
        label_fields=("gp_name", "tagname", "comment"),
    ),
    IkuaiResource(
        key="object_proto",
        path="proto-objects",
        name="协议对象",
        label_fields=("gp_name", "tagname", "comment"),
    ),
    IkuaiResource(
        key="object_domain",
        path="domain-objects",
        name="域名对象",
        label_fields=("gp_name", "tagname", "comment"),
    ),
    IkuaiResource(
        key="object_time",
        path="time-objects",
        name="时间对象",
        label_fields=("gp_name", "tagname", "comment"),
    ),
    # -- Phase 4: DHCPv6 ------------------------------------------------------
    IkuaiResource(
        key="dhcp6_rules",
        path="network/dhcp6/access-control/rules",
        name="DHCPv6 访问控制",
        dangerous=True,
        extra_attrs=("mac", "tagname"),
    ),
)

RESOURCE_BY_KEY: dict[str, IkuaiResource] = {res.key: res for res in RESOURCES}


def resolve(keys: list[str] | tuple[str, ...] | None) -> list[IkuaiResource]:
    """Turn the stored option value into resource objects, skipping stale keys.

    Users can upgrade from a version whose table did not contain a key, so an
    unknown key is ignored instead of raising.
    """
    if not keys:
        return []
    return [RESOURCE_BY_KEY[key] for key in keys if key in RESOURCE_BY_KEY]


def filter_by_edition(
    resources: list[IkuaiResource], edition: str
) -> list[IkuaiResource]:
    """Drop enterprise-only groups when running on the free firmware.

    A user may still force ``edition="enterprise"`` via the options to expose
    them; on a real free box the per-group 404 handling then keeps discovery
    calm (no entities, just debug logs).
    """
    if edition != "free":
        return list(resources)
    return [res for res in resources if not res.enterprise_only]


# ---------------------------------------------------------------------------
# Phase 4: singleton configuration resources (GET/PUT pairs).
#
# Every one of these endpoints returns the *full* configuration object and
# expects the *full* object back on PUT (nearly all fields are required by the
# official schema), so writes must be read-modify-write. ``dangerous`` marks
# configs where a bad write can cut connectivity or lock the admin out; those
# demand an extra confirmation in the set_config service.
# ---------------------------------------------------------------------------

from .const import (  # noqa: E402  (deliberately late: keeps the tables together)
    API_AC_SERVICE,
    API_AC_START,
    API_AC_STOP,
    API_ALG,
    API_AP_CONFIG,
    API_AP_SSID_QUICK,
    API_AP_SSID_UNION,
    API_AUTH_ACCOUNTS,
    API_AUTH_PACKAGES,
    API_BACKUP_AUTO,
    API_CLIENTS_IP6_OFFLINE,
    API_CLIENTS_IP6_ONLINE,
    API_CLIENTS_OFFLINE,
    API_CLIENTS_TRAFFIC_LOAD,
    API_CLIENTS_TRAFFIC_SUMMARY,
    API_CPUFREQ,
    API_CPUFREQ_MODE,
    API_DHCP6_ACCESS_MODE,
    API_DHCP6_CLIENTS,
    API_DHCP6_RULES,
    API_DHCP_ACCESS_MODE,
    API_DHCP_RESTART,
    API_DNS_CONFIG,
    API_DNS_STATS,
    API_DOWNSTREAM,
    API_FLOW_SHUNTING,
    API_FTP,
    API_INTERFACES_CONFIG,
    API_INTERFACES_PHYSICAL_MON,
    API_INTERFACES_TRAFFIC,
    API_INTERFACES_TRAFFIC_V6,
    API_IKEV2_SERVER,
    API_KERNEL_PARAMS,
    API_L2TP_SERVER,
    API_MAC_MODE,
    API_MONITOR_CONNECTIONS,
    API_MONITOR_CPUTEMP,
    API_MONITOR_DISK,
    API_MONITOR_NETWORK,
    API_MONITOR_TERMINALS,
    API_OPENVPN_SERVER,
    API_PPPOE_SERVER,
    API_PPTP_SERVER,
    API_REMOTE_ACCESS,
    API_ROUTER_HEALTH,
    API_SAMBA,
    API_SECONDARY_ROUTE,
    API_SECURITY_ADVANCED,
    API_SNMP,
    API_SPEED_TEST,
    API_SYSTEM_BASIC,
    API_SYSTEM_DISKS,
    API_TERMINAL_NAMES,
    API_VRRP_CONFIG,
    API_VRRP_START,
    API_VRRP_STOP,
    API_WEB_AUTH_SERVICE,
    API_WIREGUARD,
    API_WIRELESS_TRAFFIC,
    API_APP_PROTOCOLS_LOAD,
    API_APP_PROTOCOLS_HISTORY,
    API_APP_PROTOCOLS_TERMINAL_LOAD,
    API_APP_TRAFFIC_SUMMARY,
    API_PROTOCOLS,
    API_PROTOCOLS_HISTORY,
    API_AUDIT_ACCOUNTS,
    API_AUDIT_ACCOUNT_APPS,
    API_AUDIT_ACCOUNT_TREND,
    API_AUDIT_TERMINAL_APPS,
    API_AUDIT_TERMINAL_TREND,
    API_POLICY_TRAFFIC,
    API_APS_CHANNEL_NOISE,
    API_CAMERAS,
    API_CLOUD_SWITCHES,
)


@dataclass(frozen=True)
class IkuaiConfigResource:
    """One singleton GET/PUT configuration endpoint."""

    key: str
    """Stable identifier used by the set_config service."""

    path: str
    """Collection path relative to /api/v4.0/, e.g. ``network/dns/config``."""

    name: str
    """Human readable name."""

    dangerous: bool = False
    """True when a bad write can cut connectivity or lock the admin out."""

    enterprise_only: bool = False


CONFIG_RESOURCES: tuple[IkuaiConfigResource, ...] = (
    IkuaiConfigResource("system_basic", API_SYSTEM_BASIC, "系统基础设置", dangerous=True),
    IkuaiConfigResource("dns_config", API_DNS_CONFIG, "DNS 代理配置"),
    IkuaiConfigResource("dhcp_access_mode", API_DHCP_ACCESS_MODE, "DHCP 访问控制模式"),
    IkuaiConfigResource("dhcp6_access_mode", API_DHCP6_ACCESS_MODE, "DHCPv6 访问控制模式"),
    IkuaiConfigResource("pppoe_server", API_PPPOE_SERVER, "PPPoE 服务端"),
    IkuaiConfigResource("pptp_server", API_PPTP_SERVER, "PPTP 服务端"),
    IkuaiConfigResource("l2tp_server", API_L2TP_SERVER, "L2TP 服务端"),
    IkuaiConfigResource("ikev2_server", API_IKEV2_SERVER, "IKEv2/IPSec 服务端"),
    IkuaiConfigResource("openvpn_server", API_OPENVPN_SERVER, "OpenVPN 服务端"),
    IkuaiConfigResource("web_auth", API_WEB_AUTH_SERVICE, "WEB 认证服务", dangerous=True),
    IkuaiConfigResource("alg", API_ALG, "ALG 配置"),
    IkuaiConfigResource("snmp", API_SNMP, "SNMP 服务"),
    IkuaiConfigResource("samba", API_SAMBA, "Samba 服务"),
    IkuaiConfigResource("ftp", API_FTP, "FTP 服务"),
    IkuaiConfigResource("security_advanced", API_SECURITY_ADVANCED, "安全中心高级设置"),
    IkuaiConfigResource("mac_mode", API_MAC_MODE, "MAC 黑白名单模式", dangerous=True),
    IkuaiConfigResource("remote_access", API_REMOTE_ACCESS, "远程访问", dangerous=True),
    IkuaiConfigResource("secondary_route", API_SECONDARY_ROUTE, "网络分享控制"),
    IkuaiConfigResource("kernel_params", API_KERNEL_PARAMS, "内核参数"),
    IkuaiConfigResource("cpufreq_mode", API_CPUFREQ_MODE, "CPU 工作模式"),
    IkuaiConfigResource("backup_auto", API_BACKUP_AUTO, "自动备份策略"),
    IkuaiConfigResource("vrrp", API_VRRP_CONFIG, "VRRP 热备"),
)

CONFIG_BY_KEY: dict[str, IkuaiConfigResource] = {
    res.key: res for res in CONFIG_RESOURCES
}


def filter_configs_by_edition(
    configs: list[IkuaiConfigResource], edition: str
) -> list[IkuaiConfigResource]:
    """Drop enterprise-only singleton configs on the free firmware."""
    if edition != "free":
        return list(configs)
    return [res for res in configs if not res.enterprise_only]


# Friendly key -> GET path, accepted by the `ikuai.query` service. Covers every
# Tier A read endpoint plus the singleton configs and the Phase 4 lists.
QUERY_PATHS: dict[str, str] = {
    # 负载监控历史（datetype/start_time/end_time/math 参数族）
    "connections": API_MONITOR_CONNECTIONS,
    "cputemp": API_MONITOR_CPUTEMP,
    "disk_usage": API_MONITOR_DISK,
    "network_load": API_MONITOR_NETWORK,
    "terminal_count": API_MONITOR_TERMINALS,
    # 接口
    "interfaces_config": API_INTERFACES_CONFIG,
    "interfaces_physical": API_INTERFACES_PHYSICAL_MON,
    "interfaces_traffic": API_INTERFACES_TRAFFIC,
    "interfaces_traffic_v6": API_INTERFACES_TRAFFIC_V6,
    # 终端
    "clients_offline": API_CLIENTS_OFFLINE,
    "clients_ip6_online": API_CLIENTS_IP6_ONLINE,
    "clients_ip6_offline": API_CLIENTS_IP6_OFFLINE,
    "clients_traffic_summary": API_CLIENTS_TRAFFIC_SUMMARY,
    "clients_traffic_load": API_CLIENTS_TRAFFIC_LOAD,
    "client_app_protocols": "monitoring/clients/app-protocols/load",
    "client_protocols": "monitoring/clients/protocols",
    "client_protocols_history": "monitoring/clients/protocols/history-load",
    # 应用/协议流量
    "app_protocols_load": API_APP_PROTOCOLS_LOAD,
    "app_protocols_history": API_APP_PROTOCOLS_HISTORY,
    "app_terminal_load": API_APP_PROTOCOLS_TERMINAL_LOAD,
    "app_traffic_summary": API_APP_TRAFFIC_SUMMARY,
    "protocols": API_PROTOCOLS,
    "protocols_history": API_PROTOCOLS_HISTORY,
    # 流量审计
    "audit_accounts": API_AUDIT_ACCOUNTS,
    "audit_account_apps": API_AUDIT_ACCOUNT_APPS,
    "audit_account_trend": API_AUDIT_ACCOUNT_TREND,
    "audit_terminal_apps": API_AUDIT_TERMINAL_APPS,
    "audit_terminal_trend": API_AUDIT_TERMINAL_TREND,
    # 其它监控
    "wireless_traffic": API_WIRELESS_TRAFFIC,
    "flow_shunting": API_FLOW_SHUNTING,
    "policy_traffic": API_POLICY_TRAFFIC,
    "aps_channel_noise": API_APS_CHANNEL_NOISE,
    "cameras": API_CAMERAS,
    "cloud_switches": API_CLOUD_SWITCHES,
    "downstream": API_DOWNSTREAM,
    "dns_stats": API_DNS_STATS,
    "cpu_freq": API_CPUFREQ,
    "system_disks": API_SYSTEM_DISKS,
    "speed_test": API_SPEED_TEST,
    "router_health": API_ROUTER_HEALTH,
    # 列表
    "dhcp6_clients": API_DHCP6_CLIENTS,
    "dhcp6_rules": API_DHCP6_RULES,
    "ac_service": API_AC_SERVICE,
    "ap_config": API_AP_CONFIG,
    "terminal_names": API_TERMINAL_NAMES,
    "auth_accounts": API_AUTH_ACCOUNTS,
    "auth_packages": API_AUTH_PACKAGES,
}
QUERY_PATHS.update({res.key: res.path for res in CONFIG_RESOURCES})

# Paths the `ikuai.api_request` service may touch. GET requests are limited to
# QUERY_PATHS; everything here (plus the {id} sub-paths) is writable when the
# entry has write support enabled. Tier D endpoints (backup restore, firmware
# upgrade, web-admin accounts, system files) are deliberately absent.
WRITE_PATHS: frozenset[str] = frozenset(
    {
        API_SPEED_TEST,   # POST 启动 / DELETE 停止
        API_ROUTER_HEALTH,  # POST / DELETE
        API_AC_START,
        API_AC_STOP,
        API_VRRP_START,
        API_VRRP_STOP,
        API_DHCP_RESTART,
        API_DHCP6_RULES,
        f"{API_DHCP6_RULES}/{{id}}",
        API_AUTH_ACCOUNTS,
        f"{API_AUTH_ACCOUNTS}/{{id}}",
        API_AUTH_PACKAGES,
        f"{API_AUTH_PACKAGES}/{{id}}",
        API_TERMINAL_NAMES,
        f"{API_TERMINAL_NAMES}/{{id}}",
        "interfaces/wan-config/{id}",
        "interfaces/lan-config/{id}",
        "interfaces/wan-lines",
        "interfaces/wan-lines/{id}",
        "interfaces/lan-lines",
        "interfaces/lan-lines/{id}",
        API_AP_CONFIG,
        f"{API_AP_CONFIG}/{{id}}",
        API_AP_SSID_QUICK,
        API_AP_SSID_UNION,
        f"{API_WIREGUARD}/{{wg_id}}/peers",
        f"{API_WIREGUARD}/{{wg_id}}/peers/{{peer_id}}",
    }
    | {res.path for res in CONFIG_RESOURCES}
)


def _path_matches(template: str, actual: str) -> bool:
    """True when `actual` equals `template` or fills its {id}-style slots."""
    t_segs = template.split("/")
    a_segs = actual.split("/")
    if len(t_segs) != len(a_segs):
        return False
    for t_seg, a_seg in zip(t_segs, a_segs):
        if t_seg.startswith("{") and t_seg.endswith("}"):
            if not a_seg:
                return False
        elif t_seg != a_seg:
            return False
    return True


def query_path_allowed(path: str) -> bool:
    """True when the GET path is in the query whitelist (exact or templated)."""
    return any(_path_matches(allowed, path) for allowed in QUERY_PATHS.values())


def write_path_allowed(path: str) -> bool:
    """True when the path may be written via the api_request service."""
    return any(_path_matches(allowed, path) for allowed in WRITE_PATHS)
