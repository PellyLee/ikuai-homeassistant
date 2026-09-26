"""Sensors for the iKuai Router integration.

Static sensors come from GET /api/v4.0/monitoring/system (one call returns CPU,
temperature, memory, connections, uptime, version, online clients and traffic
totals). Per-WAN traffic sensors are added dynamically from
GET /api/v4.0/monitoring/interfaces-status -> results.iface_stream.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    STATE_UNKNOWN,
    UnitOfDataRate,
    UnitOfInformation,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .. import IkuaiRuntimeData
from .const import DOMAIN, MANUFACTURER
from .coordinator import (
    IkuaiDataUpdateCoordinator,
    IkuaiExtendedCoordinator,
    IkuaiExtendedData,
)
from .helpers import client_name


def _sysinfo(coordinator: IkuaiDataUpdateCoordinator) -> dict[str, Any]:
    return (coordinator.data.system or {}).get("sysinfo", {})


@dataclass(frozen=True, kw_only=True)
class IkuaiSensorDescription(SensorEntityDescription):
    """Describes an iKuai system sensor."""

    value_fn: Callable[[dict[str, Any]], Any] = lambda _s: None


SENSORS: tuple[IkuaiSensorDescription, ...] = (
    IkuaiSensorDescription(
        key="cpu_usage",
        translation_key="cpu_usage",
        name="CPU 使用率",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _to_float(_first(s.get("cpu"))),
    ),
    IkuaiSensorDescription(
        key="cpu_temp",
        translation_key="cpu_temp",
        name="CPU 温度",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        # devices without a thermal probe return an empty list -> unavailable
        entity_registry_enabled_default=True,
        value_fn=lambda s: _to_float(_first(s.get("cputemp"))),
    ),
    IkuaiSensorDescription(
        key="mem_usage",
        translation_key="mem_usage",
        name="内存使用率",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _to_float(str(_memory(s).get("used", "")).rstrip("%")),
    ),
    IkuaiSensorDescription(
        key="mem_used",
        translation_key="mem_used",
        name="内存已用",
        native_unit_of_measurement=UnitOfInformation.MEBIBYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _kb_to_mb(
            (_memory(s).get("total") or 0) - (_memory(s).get("available") or 0)
        ),
    ),
    IkuaiSensorDescription(
        key="connections",
        translation_key="connections",
        name="连接数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _int(_stream(s).get("connect_num")),
    ),
    IkuaiSensorDescription(
        key="tcp_connections",
        translation_key="tcp_connections",
        name="TCP 连接数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _int(_stream(s).get("tcp_connect_num")),
    ),
    IkuaiSensorDescription(
        key="udp_connections",
        translation_key="udp_connections",
        name="UDP 连接数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _int(_stream(s).get("udp_connect_num")),
    ),
    IkuaiSensorDescription(
        key="online_clients",
        translation_key="online_clients",
        name="在线终端数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _int((_online(s) or {}).get("count")),
    ),
    IkuaiSensorDescription(
        key="upload_rate",
        translation_key="upload_rate",
        name="上传速率",
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _to_float(_stream(s).get("upload")),
    ),
    IkuaiSensorDescription(
        key="download_rate",
        translation_key="download_rate",
        name="下载速率",
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: _to_float(_stream(s).get("download")),
    ),
    IkuaiSensorDescription(
        key="total_up",
        translation_key="total_up",
        name="累计上传",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda s: _to_float(_stream(s).get("total_up")),
    ),
    IkuaiSensorDescription(
        key="total_down",
        translation_key="total_down",
        name="累计下载",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda s: _to_float(_stream(s).get("total_down")),
    ),
    IkuaiSensorDescription(
        key="uptime",
        translation_key="uptime",
        name="运行时间",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda s: _uptime_ts(s),
    ),
    IkuaiSensorDescription(
        key="version",
        translation_key="version",
        name="固件版本",
        value_fn=lambda s: (_verinfo(s) or {}).get("version") or None,
    ),
)


@dataclass(frozen=True, kw_only=True)
class WanSensorDescription(SensorEntityDescription):
    """Describes a per-WAN traffic sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


WAN_SENSORS: tuple[WanSensorDescription, ...] = (
    WanSensorDescription(
        key="wan_upload",
        translation_key="wan_upload",
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda i: _to_float(i.get("upload")),
    ),
    WanSensorDescription(
        key="wan_download",
        translation_key="wan_download",
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda i: _to_float(i.get("download")),
    ),
    WanSensorDescription(
        key="wan_total_up",
        translation_key="wan_total_up",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda i: _to_float(i.get("total_up")),
    ),
    WanSensorDescription(
        key="wan_total_down",
        translation_key="wan_total_down",
        native_unit_of_measurement=UnitOfInformation.BYTES,
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda i: _to_float(i.get("total_down")),
    ),
)


@dataclass(frozen=True, kw_only=True)
class ExtendedSensorDescription(SensorEntityDescription):
    """Describes a sensor fed by the slow-polling coordinator."""

    value_fn: Callable[[IkuaiExtendedData], Any]
    attrs_fn: Callable[[IkuaiExtendedData], dict[str, Any] | None] | None = None


def _wireless(data: IkuaiExtendedData) -> dict[str, Any]:
    return data.wireless or {}


def _wireless_clients(data: IkuaiExtendedData) -> dict[str, Any]:
    return (_wireless(data).get("clt_status")) or {}


def _ap_status(data: IkuaiExtendedData) -> dict[str, Any]:
    return (_wireless(data).get("ap_status")) or {}


def _count(value: list | None) -> int | None:
    return len(value) if value is not None else None


def _top_terminal_name(data: IkuaiExtendedData) -> Any:
    terminal = data.top_terminal
    if not terminal:
        return None
    return client_name(terminal, str(terminal.get("mac") or "unknown"))


_SCORE_KEYS = ("score", "total_score", "total", "value")


def _wireless_score_value(data: IkuaiExtendedData) -> Any:
    """Overall score field, tolerating unknown response shapes."""
    score = data.wireless_score
    if not isinstance(score, dict):
        return None
    for key in _SCORE_KEYS:
        value = _to_float(score.get(key))
        if value is not None:
            return value
    return None


def _hourly_rows(rows: list[dict[str, Any]], label_keys: tuple[str, ...]) -> dict[str, Any]:
    """Latest client count per SSID/channel row, tolerating unknown shapes."""
    attrs: dict[str, Any] = {}
    for row in rows:
        label = next(
            (str(row.get(key)) for key in label_keys if row.get(key)), "unknown"
        )
        series = row.get("data") if isinstance(row.get("data"), list) else []
        if series and isinstance(series[-1], dict):
            last = series[-1]
            count = _to_float(
                last.get("count") or last.get("clt_count") or last.get("clients")
            )
            if count is not None:
                attrs[label] = count
                continue
        for key in ("count", "clt_count", "clients"):
            count = _to_float(row.get(key))
            if count is not None:
                attrs[label] = count
                break
    return attrs or None


def _ssid_clients_attrs(data: IkuaiExtendedData) -> dict[str, Any] | None:
    if data.ssid_clients is None:
        return None
    return _hourly_rows(data.ssid_clients, ("ssid", "name", "tagname"))


def _channel_clients_attrs(data: IkuaiExtendedData) -> dict[str, Any] | None:
    if data.channel_clients is None:
        return None
    return _hourly_rows(data.channel_clients, ("channel", "name", "ssid"))


# -- Phase 4: tolerant extractors for the extended monitor endpoints --------
# The official docs only pin down a handful of response shapes; everything the
# Phase 4 coordinators fetch is probed field-by-field so an unexpected shape
# degrades to "unknown" instead of crashing the platform.

_SERIES_VALUE_KEYS = (
    "value", "total", "count", "connect_num", "percent", "usage", "rate",
)
_SERIES_TIME_KEYS = ("time", "date", "hour", "day", "index")


def _series_last(
    series: list[dict[str, Any]] | None,
    value_keys: tuple[str, ...] = _SERIES_VALUE_KEYS,
) -> float | None:
    """Last numeric value of a history series."""
    if not isinstance(series, list) or not series:
        return None
    last = series[-1]
    if not isinstance(last, dict):
        return _to_float(last)
    for key in value_keys:
        value = _to_float(last.get(key))
        if value is not None:
            return value
    return None


def _series_attrs(
    series: list[dict[str, Any]] | None,
    value_keys: tuple[str, ...] = _SERIES_VALUE_KEYS,
    max_points: int = 24,
) -> dict[str, Any] | None:
    """History series as {time: value} attributes (bounded)."""
    if not isinstance(series, list):
        return None
    attrs: dict[str, Any] = {}
    for point in series[-max_points:]:
        if not isinstance(point, dict):
            continue
        when = next(
            (str(point.get(k)) for k in _SERIES_TIME_KEYS if point.get(k) is not None),
            str(len(attrs)),
        )
        value = next(
            (
                _to_float(point.get(k))
                for k in value_keys
                if _to_float(point.get(k)) is not None
            ),
            None,
        )
        if value is not None:
            attrs[when] = value
    return attrs or None


def _rows_attrs(
    rows: list[dict[str, Any]] | None,
    label_keys: tuple[str, ...],
    value_keys: tuple[str, ...] = (),
    max_rows: int = 30,
) -> dict[str, Any] | None:
    """List rows as {label: value-or-summary} attributes (bounded)."""
    if not isinstance(rows, list):
        return None
    attrs: dict[str, Any] = {}
    for row in rows[:max_rows]:
        if not isinstance(row, dict):
            continue
        label = (
            next((str(row.get(k)) for k in label_keys if row.get(k)), None)
            or f"row{len(attrs) + 1}"
        )
        value = next(
            (
                _to_float(row.get(k))
                for k in value_keys
                if _to_float(row.get(k)) is not None
            ),
            None,
        )
        attrs[label[:60]] = value if value is not None else _trim_value(row, 1)
    return attrs or None


def _trim_value(value: Any, depth: int = 2) -> Any:
    """JSON-safe bounded copy of one attribute value."""
    if isinstance(value, dict):
        if depth <= 0:
            return f"<{len(value)} keys>"
        return {
            str(k)[:40]: _trim_value(v, depth - 1)
            for k, v in list(value.items())[:20]
        }
    if isinstance(value, (list, tuple)):
        if not value:
            return []
        if depth <= 0:
            return f"<{len(value)} items>"
        return [_trim_value(v, depth - 1) for v in value[:20]]
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return str(value)[:200]


def _trim_attrs(raw: Any, max_items: int = 40) -> dict[str, Any] | None:
    """Bounded attribute view of an arbitrary response payload."""
    if not isinstance(raw, dict):
        return None
    attrs = {
        str(k)[:40]: _trim_value(v)
        for k, v in list(raw.items())[:max_items]
        if k != "code"
    }
    return attrs or None


def _dict_metric(raw: dict[str, Any] | None) -> float | None:
    """Best-effort single number from an arbitrary payload."""
    if not isinstance(raw, dict):
        return None
    for key in ("freq", "frequency", "total", "count", "sum", "value", "rate"):
        number = _to_float(raw.get(key))
        if number is not None:
            return number
    for value in raw.values():
        if isinstance(value, list):
            return len(value)
    for value in raw.values():
        number = _to_float(value)
        if number is not None:
            return number
    return None


_ON_TEXTS = ("1", "yes", "on", "true", "running", "start", "open", "opened")
_OFF_TEXTS = ("0", "no", "off", "false", "stopped", "stop", "close", "closed")


def _on_off(raw: dict[str, Any] | None) -> str | None:
    """on/off state from an arbitrary status payload."""
    if not isinstance(raw, dict):
        return None
    for key in ("enabled", "run", "running", "status", "switch"):
        value = raw.get(key)
        if value is None:
            continue
        text = str(value).strip().lower()
        if text in _ON_TEXTS:
            return "on"
        if text in _OFF_TEXTS:
            return "off"
    return None


def _terminal_name_attrs(data: IkuaiExtendedData) -> dict[str, Any] | None:
    if data.terminal_names is None:
        return None
    return _rows_attrs(data.terminal_names, ("mac", "tagname"), max_rows=60)


def _wireguard_attrs(
    data: IkuaiExtendedData,
) -> dict[str, Any] | None:
    if data.wireguard_peers is None:
        return None
    attrs: dict[str, Any] = {}
    for wg_id, peers in data.wireguard_peers.items():
        names = [
            str(
                peer.get("comment")
                or str(peer.get("peer_publickey") or "")[:12]
                or "peer"
            )
            for peer in peers[:20]
            if isinstance(peer, dict)
        ]
        attrs[f"wg{wg_id}"] = {"count": len(peers), "peers": names}
    return attrs or None


def _wireguard_count(data: IkuaiExtendedData) -> int | None:
    if data.wireguard_peers is None:
        return None
    return sum(len(peers) for peers in data.wireguard_peers.values())


EXTENDED_SENSORS: tuple[ExtendedSensorDescription, ...] = (
    ExtendedSensorDescription(
        key="dhcp_leases",
        translation_key="dhcp_leases",
        name="DHCP 租约数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.dhcp_clients),
    ),
    ExtendedSensorDescription(
        key="dhcp_static",
        translation_key="dhcp_static",
        name="DHCP 静态绑定数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.dhcp_static),
    ),
    ExtendedSensorDescription(
        key="auth_users",
        translation_key="auth_users",
        name="认证用户数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.auth_users),
    ),
    ExtendedSensorDescription(
        key="wireless_clients",
        translation_key="wireless_clients",
        name="无线终端数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _wireless_clients(d).get("clt_count"),
    ),
    ExtendedSensorDescription(
        key="wireless_aps",
        translation_key="wireless_aps",
        name="AP 数量",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _ap_status(d).get("ap_count"),
    ),
    ExtendedSensorDescription(
        key="wireless_aps_online",
        translation_key="wireless_aps_online",
        name="AP 在线数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _ap_status(d).get("ap_online"),
    ),
    ExtendedSensorDescription(
        key="cpu_avg_1h",
        translation_key="cpu_avg_1h",
        name="CPU 近1小时均值",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.cpu_hour_avg,
    ),
    ExtendedSensorDescription(
        key="memory_avg_1h",
        translation_key="memory_avg_1h",
        name="内存近1小时均值",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.memory_hour_avg,
    ),
    ExtendedSensorDescription(
        key="top_terminal",
        translation_key="top_terminal",
        name="流量最高终端",
        value_fn=_top_terminal_name,
        attrs_fn=lambda d: (
            {
                "mac": d.top_terminal.get("mac"),
                "total_up": d.top_terminal.get("sum_total_up"),
                "total_down": d.top_terminal.get("sum_total_down"),
            }
            if d.top_terminal
            else None
        ),
    ),
    ExtendedSensorDescription(
        key="wireless_score",
        translation_key="wireless_score",
        name="无线网络评分",
        native_unit_of_measurement="分",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_wireless_score_value,
        attrs_fn=lambda d: d.wireless_score or None,
    ),
    ExtendedSensorDescription(
        key="ssid_clients",
        translation_key="ssid_clients",
        name="SSID 终端统计",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.ssid_clients),
        attrs_fn=_ssid_clients_attrs,
    ),
    ExtendedSensorDescription(
        key="channel_clients",
        translation_key="channel_clients",
        name="信道终端统计",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.channel_clients),
        attrs_fn=_channel_clients_attrs,
    ),
    # -- Phase 4: extended monitoring (Tier A) --------------------------------
    ExtendedSensorDescription(
        key="connections_monitor",
        translation_key="connections_monitor",
        name="连接数监控",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _series_last(
            d.connections_series, ("value", "connect_num", "total", "count")
        ),
        attrs_fn=lambda d: _series_attrs(
            d.connections_series, ("value", "connect_num", "total", "count")
        ),
    ),
    ExtendedSensorDescription(
        key="disk_usage_monitor",
        translation_key="disk_usage_monitor",
        name="磁盘使用率",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _series_last(
            d.disk_series, ("value", "percent", "usage", "disk")
        ),
        attrs_fn=lambda d: _series_attrs(
            d.disk_series, ("value", "percent", "usage", "disk")
        ),
    ),
    ExtendedSensorDescription(
        key="network_load",
        translation_key="network_load",
        name="网络负载监控",
        native_unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _series_last(
            d.network_series, ("value", "total", "rate", "up", "down")
        ),
        attrs_fn=lambda d: _series_attrs(
            d.network_series, ("value", "total", "rate", "up", "down")
        ),
    ),
    ExtendedSensorDescription(
        key="clients_offline",
        translation_key="clients_offline",
        name="IPv4 离线终端数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.clients_offline),
        attrs_fn=lambda d: _rows_attrs(
            d.clients_offline, ("mac", "ip", "termname", "hostname")
        ),
    ),
    ExtendedSensorDescription(
        key="clients_ip6_online",
        translation_key="clients_ip6_online",
        name="IPv6 在线终端数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.clients_ip6_online),
        attrs_fn=lambda d: _rows_attrs(
            d.clients_ip6_online, ("mac", "ip6", "host", "termname")
        ),
    ),
    ExtendedSensorDescription(
        key="clients_ip6_offline",
        translation_key="clients_ip6_offline",
        name="IPv6 离线终端数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.clients_ip6_offline),
        attrs_fn=lambda d: _rows_attrs(
            d.clients_ip6_offline, ("mac", "ip6", "host", "termname")
        ),
    ),
    ExtendedSensorDescription(
        key="app_protocols",
        translation_key="app_protocols",
        name="应用协议速率",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.app_protocols),
        attrs_fn=lambda d: _rows_attrs(
            d.app_protocols,
            ("appname", "app_name", "name", "tagname"),
            ("rate", "up", "down", "total"),
        ),
    ),
    ExtendedSensorDescription(
        key="app_traffic_summary",
        translation_key="app_traffic_summary",
        name="24h 应用流量",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _dict_metric(d.app_traffic_summary),
        attrs_fn=lambda d: _trim_attrs(d.app_traffic_summary),
    ),
    ExtendedSensorDescription(
        key="protocols",
        translation_key="protocols",
        name="协议分类流量",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.protocols),
        attrs_fn=lambda d: _rows_attrs(
            d.protocols,
            ("proto", "protocol", "name", "tagname"),
            ("total", "up", "down"),
        ),
    ),
    ExtendedSensorDescription(
        key="wireless_traffic",
        translation_key="wireless_traffic",
        name="无线流量统计",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _dict_metric(d.wireless_traffic),
        attrs_fn=lambda d: _trim_attrs(d.wireless_traffic),
    ),
    ExtendedSensorDescription(
        key="flow_shunting",
        translation_key="flow_shunting",
        name="分流统计",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _dict_metric(d.flow_shunting),
        attrs_fn=lambda d: _trim_attrs(d.flow_shunting),
    ),
    ExtendedSensorDescription(
        key="policy_traffic",
        translation_key="policy_traffic",
        name="策略监控",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _dict_metric(d.policy_traffic),
        attrs_fn=lambda d: _trim_attrs(d.policy_traffic),
    ),
    ExtendedSensorDescription(
        key="aps_channel_noise",
        translation_key="aps_channel_noise",
        name="AP 信道底噪",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.aps_channel_noise),
        attrs_fn=lambda d: _rows_attrs(
            d.aps_channel_noise,
            ("tagname", "apname", "name", "ssid"),
            ("noise", "channel"),
        ),
    ),
    ExtendedSensorDescription(
        key="cameras",
        translation_key="cameras",
        name="摄像头数量",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.cameras),
        attrs_fn=lambda d: _rows_attrs(
            d.cameras, ("ip", "name", "tagname", "mac")
        ),
    ),
    ExtendedSensorDescription(
        key="cloud_switches",
        translation_key="cloud_switches",
        name="云管交换机数量",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.cloud_switches),
        attrs_fn=lambda d: _rows_attrs(
            d.cloud_switches, ("ip", "name", "model", "mac")
        ),
    ),
    ExtendedSensorDescription(
        key="downstream",
        translation_key="downstream",
        name="周边设备数量",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.downstream),
        attrs_fn=lambda d: _rows_attrs(
            d.downstream, ("ip", "name", "type", "mac")
        ),
    ),
    ExtendedSensorDescription(
        key="dns_stats",
        translation_key="dns_stats",
        name="DNS 缓存状态",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _dict_metric(d.dns_stats),
        attrs_fn=lambda d: _trim_attrs(d.dns_stats),
    ),
    ExtendedSensorDescription(
        key="cpu_freq",
        translation_key="cpu_freq",
        name="CPU 实时频率",
        native_unit_of_measurement="MHz",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _dict_metric(d.cpu_freq),
        attrs_fn=lambda d: _trim_attrs(d.cpu_freq),
    ),
    ExtendedSensorDescription(
        key="system_disks",
        translation_key="system_disks",
        name="系统磁盘",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.system_disks),
        attrs_fn=lambda d: _rows_attrs(
            d.system_disks,
            ("filesys", "dev", "name", "mount", "mounted"),
            ("total", "used", "free"),
        ),
    ),
    ExtendedSensorDescription(
        key="interfaces_traffic",
        translation_key="interfaces_traffic",
        name="线路 24h 流量",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _dict_metric(d.interfaces_traffic),
        attrs_fn=lambda d: _trim_attrs(d.interfaces_traffic),
    ),
    ExtendedSensorDescription(
        key="interfaces_config",
        translation_key="interfaces_config",
        name="接口配置",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _dict_metric(d.interfaces_config),
        attrs_fn=lambda d: _trim_attrs(d.interfaces_config),
    ),
    ExtendedSensorDescription(
        key="interfaces_physical",
        translation_key="interfaces_physical",
        name="物理网卡",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _dict_metric(d.interfaces_physical),
        attrs_fn=lambda d: _trim_attrs(d.interfaces_physical),
    ),
    ExtendedSensorDescription(
        key="terminal_names",
        translation_key="terminal_names",
        name="终端备注数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.terminal_names),
        attrs_fn=_terminal_name_attrs,
    ),
    ExtendedSensorDescription(
        key="auth_accounts",
        translation_key="auth_accounts",
        name="认证账号数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.auth_accounts),
        attrs_fn=lambda d: _rows_attrs(
            d.auth_accounts, ("username", "name"), ("enabled", "expires")
        ),
    ),
    ExtendedSensorDescription(
        key="auth_packages",
        translation_key="auth_packages",
        name="认证套餐数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.auth_packages),
        attrs_fn=lambda d: _rows_attrs(
            d.auth_packages,
            ("packname", "name"),
            ("price", "up_speed", "down_speed"),
        ),
    ),
    ExtendedSensorDescription(
        key="dhcp6_clients",
        translation_key="dhcp6_clients",
        name="DHCPv6 客户端数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.dhcp6_clients),
    ),
    ExtendedSensorDescription(
        key="ac_status",
        translation_key="ac_status",
        name="AC 服务状态",
        value_fn=lambda d: _on_off(d.ac_service),
        attrs_fn=lambda d: _trim_attrs(d.ac_service),
    ),
    ExtendedSensorDescription(
        key="ap_list",
        translation_key="ap_list",
        name="AP 列表",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _count(d.ap_list),
        attrs_fn=lambda d: _rows_attrs(
            d.ap_list,
            ("tagname", "name", "model"),
            ("ip", "online", "status"),
        ),
    ),
    ExtendedSensorDescription(
        key="wireguard_peers",
        translation_key="wireguard_peers",
        name="WireGuard 隧道数",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_wireguard_count,
        attrs_fn=_wireguard_attrs,
    ),
)


def _first(value: Any) -> Any:
    """Return the first item of a list, or the value itself."""
    if isinstance(value, (list, tuple)):
        return value[0] if value else None
    return value


def _memory(s: dict[str, Any]) -> dict[str, Any]:
    return s.get("memory") or {}


def _stream(s: dict[str, Any]) -> dict[str, Any]:
    return s.get("stream") or {}


def _online(s: dict[str, Any]) -> dict[str, Any] | None:
    return s.get("online_user")


def _verinfo(s: dict[str, Any]) -> dict[str, Any] | None:
    return s.get("verinfo")


def _uptime_ts(s: dict[str, Any]) -> datetime | None:
    uptime = _to_float(s.get("uptime"))
    if not uptime:
        return None
    return datetime.now(timezone.utc) - timedelta(seconds=uptime)


def _to_float(value: Any) -> float | None:
    try:
        return float(str(value).rstrip("%"))
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int | None:
    number = _to_float(value)
    return int(number) if number is not None else None


def _kb_to_mb(value: Any) -> float | None:
    number = _to_float(value)
    return round(number / 1024, 1) if number is not None else None


def _device_info(
    entry: ConfigEntry, coordinator: IkuaiDataUpdateCoordinator
) -> DeviceInfo:
    sysinfo = _sysinfo(coordinator)
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title,
        manufacturer=MANUFACTURER,
        entry_type=DeviceEntryType.SERVICE,
        model=str((_verinfo(sysinfo) or {}).get("modelname") or "iKuaiOS Router"),
        sw_version=(_verinfo(sysinfo) or {}).get("version") or None,
    )


class IkuaiSensor(CoordinatorEntity[IkuaiDataUpdateCoordinator], SensorEntity):
    """System sensor backed by /monitoring/system."""

    entity_description: IkuaiSensorDescription

    def __init__(
        self,
        coordinator: IkuaiDataUpdateCoordinator,
        entry: ConfigEntry,
        description: IkuaiSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = _device_info(entry, coordinator)

    @property
    def native_value(self) -> Any:
        value = self.entity_description.value_fn(_sysinfo(self.coordinator))
        return value if value is not None else STATE_UNKNOWN

    @property
    def available(self) -> bool:
        # Temperature is unavailable on fanless devices (cputemp: [])
        if self.entity_description.key == "cpu_temp":
            return super().available and _to_float(
                _first(_sysinfo(self.coordinator).get("cputemp"))
            ) is not None
        return super().available


class IkuaiExtendedSensor(CoordinatorEntity[IkuaiExtendedCoordinator], SensorEntity):
    """Sensor fed by the slow-polling coordinator."""

    entity_description: ExtendedSensorDescription

    def __init__(
        self,
        coordinator: IkuaiExtendedCoordinator,
        entry: ConfigEntry,
        description: ExtendedSensorDescription,
        main: IkuaiDataUpdateCoordinator,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = _device_info(entry, main)

    @property
    def native_value(self) -> Any:
        value = self.entity_description.value_fn(self.coordinator.data)
        return value if value is not None else STATE_UNKNOWN

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attrs_fn is None:
            return None
        return self.entity_description.attrs_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        # Features missing on the device report no value but keep the entity
        if self.native_value in (STATE_UNKNOWN, None):
            return False
        return super().available


class IkuaiWanSensor(CoordinatorEntity[IkuaiDataUpdateCoordinator], SensorEntity):
    """Per-WAN traffic sensor backed by /monitoring/interfaces-status."""

    entity_description: WanSensorDescription

    def __init__(
        self,
        coordinator: IkuaiDataUpdateCoordinator,
        entry: ConfigEntry,
        interface: str,
        ip_addr: str | None,
        description: WanSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._interface = interface
        self._attr_unique_id = f"{entry.entry_id}_{interface}_{description.key}"
        self._attr_name = f"{entry.title} {interface.upper()} {description.name}"
        self._attr_device_info = _device_info(entry, coordinator)
        self._attr_extra_state_attributes = {"ip_addr": ip_addr}

    def _line(self) -> dict[str, Any] | None:
        for line in ((self.coordinator.data.interfaces or {}).get("iface_stream")) or []:
            if line.get("interface") == self._interface:
                return line
        return None

    @property
    def native_value(self) -> Any:
        line = self._line()
        if line is None:
            return STATE_UNKNOWN
        value = self.entity_description.value_fn(line)
        return value if value is not None else STATE_UNKNOWN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up iKuai sensors from a config entry."""
    runtime: IkuaiRuntimeData = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.main

    async_add_entities(
        IkuaiSensor(coordinator, entry, description) for description in SENSORS
    )
    async_add_entities(
        IkuaiExtendedSensor(runtime.extended, entry, description, coordinator)
        for description in EXTENDED_SENSORS
    )

    known: set[str] = set()

    @callback
    def _async_add_wan_sensors() -> None:
        """Add traffic sensors for every line reported by the router.

        Lines come from `iface_check` so that VPN lines (ovpn2, ...) are covered
        too; interfaces without a traffic entry are skipped. Fallback: any
        `wan*` interface of `iface_stream` when the check list is unavailable.
        """
        interfaces = coordinator.data.interfaces or {}
        streams = interfaces.get("iface_stream") or []
        checks = interfaces.get("iface_check") or []

        if checks:
            candidates = [c.get("interface") for c in checks]
        else:
            candidates = [
                s.get("interface")
                for s in streams
                if str(s.get("interface", "")).startswith("wan")
            ]

        by_name = {s.get("interface"): s for s in streams}
        new = [
            name
            for name in candidates
            if name and name in by_name and name not in known
        ]
        if not new:
            return
        known.update(new)
        entities: list[SensorEntity] = []
        for name in new:
            entities.extend(
                IkuaiWanSensor(
                    coordinator, entry, name, by_name[name].get("ip_addr"), desc
                )
                for desc in WAN_SENSORS
            )
        async_add_entities(entities)

    _async_add_wan_sensors()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_wan_sensors))
