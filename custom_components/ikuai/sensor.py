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
