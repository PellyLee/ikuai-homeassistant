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
