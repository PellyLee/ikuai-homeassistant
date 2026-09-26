"""Data update coordinators for the iKuai Router integration."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import timedelta
import logging
from typing import Any, Callable, Coroutine

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    IkuaiApiClient,
    IkuaiApiError,
    IkuaiApiNotFoundError,
)
from .const import (
    API_AC_SERVICE,
    API_APP_PROTOCOLS_LOAD,
    API_APP_TRAFFIC_SUMMARY,
    API_APS_CHANNEL_NOISE,
    API_CAMERAS,
    API_CLIENTS_IP6_OFFLINE,
    API_CLIENTS_IP6_ONLINE,
    API_CLIENTS_OFFLINE,
    API_CLIENTS_TRAFFIC_SUMMARY,
    API_CLOUD_SWITCHES,
    API_CPUFREQ,
    API_DHCP6_CLIENTS,
    API_DOWNSTREAM,
    API_DNS_STATS,
    API_FLOW_SHUNTING,
    API_INTERFACES_CONFIG,
    API_INTERFACES_PHYSICAL_MON,
    API_INTERFACES_TRAFFIC,
    API_MONITOR_CONNECTIONS,
    API_MONITOR_DISK,
    API_MONITOR_NETWORK,
    API_AUTH_ACCOUNTS,
    API_AUTH_PACKAGES,
    API_POLICY_TRAFFIC,
    API_PROTOCOLS,
    API_SYSTEM_DISKS,
    API_TERMINAL_NAMES,
    API_WIRELESS_TRAFFIC,
    DEFAULT_CLIENT_LIMIT,
    DOMAIN,
    EDITION_FREE,
    EXTENDED_SCAN_INTERVAL,
    RESOURCE_SCAN_INTERVAL,
)
from .helpers import detect_edition
from .resources import IkuaiResource

_LOGGER = logging.getLogger(__name__)


@dataclass
class IkuaiData:
    """Fast-polling data (system status, lines, online clients)."""

    system: dict[str, Any] = field(default_factory=dict)
    interfaces: dict[str, Any] = field(default_factory=dict)
    clients: list[dict[str, Any]] = field(default_factory=list)
    edition: str = EDITION_FREE
    """Auto-detected edition (free/enterprise) from `verinfo`."""


@dataclass
class IkuaiExtendedData:
    """Slow-polling data (DHCP, wireless, firmware, audit, hourly averages).

    Every field stays None when the endpoint is unavailable on the device, so a
    single missing feature never breaks the rest.
    """

    dhcp_clients: list[dict[str, Any]] | None = None
    dhcp_static: list[dict[str, Any]] | None = None
    auth_users: list[dict[str, Any]] | None = None
    upgrade: dict[str, Any] | None = None
    wireless: dict[str, Any] | None = None
    top_terminal: dict[str, Any] | None = None
    cpu_hour_avg: float | None = None
    memory_hour_avg: float | None = None
    # Phase 3: read-only wireless detail (None when unavailable / no AP).
    wireless_score: dict[str, Any] | None = None
    ssid_clients: list[dict[str, Any]] | None = None
    channel_clients: list[dict[str, Any]] | None = None
    # Phase 4: extended monitoring (Tier A). None = endpoint unavailable or
    # not fetched yet; failed refreshes keep the previous value.
    connections_series: list[dict[str, Any]] | None = None
    disk_series: list[dict[str, Any]] | None = None
    network_series: list[dict[str, Any]] | None = None
    clients_offline: list[dict[str, Any]] | None = None
    clients_ip6_online: list[dict[str, Any]] | None = None
    clients_ip6_offline: list[dict[str, Any]] | None = None
    clients_traffic_summary: dict[str, Any] | None = None
    app_protocols: list[dict[str, Any]] | None = None
    app_traffic_summary: dict[str, Any] | None = None
    protocols: list[dict[str, Any]] | None = None
    wireless_traffic: dict[str, Any] | None = None
    flow_shunting: dict[str, Any] | None = None
    policy_traffic: dict[str, Any] | None = None
    aps_channel_noise: list[dict[str, Any]] | None = None
    cameras: list[dict[str, Any]] | None = None
    cloud_switches: list[dict[str, Any]] | None = None
    downstream: list[dict[str, Any]] | None = None
    dns_stats: dict[str, Any] | None = None
    cpu_freq: dict[str, Any] | None = None
    system_disks: list[dict[str, Any]] | None = None
    interfaces_traffic: dict[str, Any] | None = None
    interfaces_config: dict[str, Any] | None = None
    interfaces_physical: dict[str, Any] | None = None
    terminal_names: list[dict[str, Any]] | None = None
    auth_accounts: list[dict[str, Any]] | None = None
    auth_packages: list[dict[str, Any]] | None = None
    dhcp6_clients: list[dict[str, Any]] | None = None
    ac_service: dict[str, Any] | None = None
    ap_list: list[dict[str, Any]] | None = None
    wireguard_peers: dict[str, list[dict[str, Any]]] | None = None


@dataclass
class IkuaiResourceData:
    """Rows of every selected CRUD group, keyed by resource key."""

    rows: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


class IkuaiDataUpdateCoordinator(DataUpdateCoordinator[IkuaiData]):
    """Polls the router every scan_interval (default 30s)."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: IkuaiApiClient,
        scan_interval: int,
        client_limit: int = DEFAULT_CLIENT_LIMIT,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self._client_limit = client_limit

    async def _async_update_data(self) -> IkuaiData:
        data = IkuaiData()
        try:
            data.system = await self.client.async_get_system()
            data.interfaces = await self.client.async_get_interfaces_status()
            data.clients = await self.client.async_get_online_clients(self._client_limit)
        except IkuaiApiError as err:
            raise UpdateFailed(str(err)) from err
        verinfo = (data.system.get("sysinfo") or {}).get("verinfo") or {}
        data.edition = detect_edition(verinfo)
        return data


class IkuaiExtendedCoordinator(DataUpdateCoordinator[IkuaiExtendedData]):
    """Polls slower and degrades gracefully per endpoint."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: IkuaiApiClient,
        scan_interval: int = EXTENDED_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_extended",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_safe(
        self,
        name: str,
        call: Callable[[], Coroutine[Any, Any, Any]],
        default: Any = None,
    ) -> Any:
        """Run one request without letting a missing endpoint fail the cycle."""
        try:
            return await call()
        except IkuaiApiNotFoundError:
            _LOGGER.debug("%s is not supported on this device, skipping", name)
            return default
        except IkuaiApiError as err:
            _LOGGER.debug("Could not refresh %s: %s", name, err)
            return default

    async def _async_update_data(self) -> IkuaiExtendedData:
        client = self.client
        previous = self.data or IkuaiExtendedData()
        # Two-tier polling: light monitors every cycle, expensive aggregates
        # and device lists every 3rd cycle (~15 min at the default interval).
        self._cycle = (getattr(self, "_cycle", -1) + 1) % 3
        heavy = self._cycle == 0

        data = replace(previous)

        def keep(name: str) -> Any:
            """On failure keep the previous value so entities never flicker."""
            return getattr(previous, name, None)

        # -- light monitors (every cycle) ------------------------------------
        data.connections_series = await self._async_safe(
            "connections history",
            lambda: client.async_get_monitor_series(API_MONITOR_CONNECTIONS),
            keep("connections_series"),
        )
        data.disk_series = await self._async_safe(
            "disk history",
            lambda: client.async_get_monitor_series(API_MONITOR_DISK),
            keep("disk_series"),
        )
        data.network_series = await self._async_safe(
            "network load",
            lambda: client.async_get_monitor_series(API_MONITOR_NETWORK),
            keep("network_series"),
        )
        data.clients_offline = await self._async_safe(
            "clients offline",
            lambda: client.async_get_rows(API_CLIENTS_OFFLINE),
            keep("clients_offline"),
        )
        data.clients_ip6_online = await self._async_safe(
            "clients ip6 online",
            lambda: client.async_get_rows(API_CLIENTS_IP6_ONLINE),
            keep("clients_ip6_online"),
        )
        data.clients_ip6_offline = await self._async_safe(
            "clients ip6 offline",
            lambda: client.async_get_rows(API_CLIENTS_IP6_OFFLINE),
            keep("clients_ip6_offline"),
        )
        data.app_protocols = await self._async_safe(
            "app protocols load",
            lambda: client.async_get_rows(API_APP_PROTOCOLS_LOAD),
            keep("app_protocols"),
        )
        data.aps_channel_noise = await self._async_safe(
            "aps channel noise",
            lambda: client.async_get_rows(API_APS_CHANNEL_NOISE),
            keep("aps_channel_noise"),
        )
        data.cameras = await self._async_safe(
            "cameras", lambda: client.async_get_rows(API_CAMERAS), keep("cameras")
        )
        data.cloud_switches = await self._async_safe(
            "cloud switches",
            lambda: client.async_get_rows(API_CLOUD_SWITCHES),
            keep("cloud_switches"),
        )
        data.downstream = await self._async_safe(
            "downstream", lambda: client.async_get_rows(API_DOWNSTREAM), keep("downstream")
        )
        data.dns_stats = await self._async_safe(
            "dns stats", lambda: client.async_get_path(API_DNS_STATS), keep("dns_stats")
        )
        data.cpu_freq = await self._async_safe(
            "cpu freq", lambda: client.async_get_path(API_CPUFREQ), keep("cpu_freq")
        )
        data.system_disks = await self._async_safe(
            "system disks",
            lambda: client.async_get_rows(API_SYSTEM_DISKS),
            keep("system_disks"),
        )
        data.wireless_traffic = await self._async_safe(
            "wireless traffic",
            lambda: client.async_get_path(API_WIRELESS_TRAFFIC),
            keep("wireless_traffic"),
        )
        data.flow_shunting = await self._async_safe(
            "flow shunting",
            lambda: client.async_get_path(API_FLOW_SHUNTING),
            keep("flow_shunting"),
        )
        data.policy_traffic = await self._async_safe(
            "policy traffic",
            lambda: client.async_get_path(API_POLICY_TRAFFIC),
            keep("policy_traffic"),
        )
        data.ac_service = await self._async_safe(
            "ac service", lambda: client.async_get_path(API_AC_SERVICE), keep("ac_service")
        )

        # -- heavy aggregates / device lists (every 3rd cycle) ---------------
        if heavy:
            data.app_traffic_summary = await self._async_safe(
                "app traffic summary",
                lambda: client.async_get_path(API_APP_TRAFFIC_SUMMARY),
                keep("app_traffic_summary"),
            )
            data.protocols = await self._async_safe(
                "protocols", lambda: client.async_get_rows(API_PROTOCOLS), keep("protocols")
            )
            data.clients_traffic_summary = await self._async_safe(
                "clients traffic summary",
                lambda: client.async_get_path(API_CLIENTS_TRAFFIC_SUMMARY),
                keep("clients_traffic_summary"),
            )
            data.interfaces_traffic = await self._async_safe(
                "interfaces traffic",
                lambda: client.async_get_path(API_INTERFACES_TRAFFIC),
                keep("interfaces_traffic"),
            )
            data.interfaces_config = await self._async_safe(
                "interfaces config",
                lambda: client.async_get_path(API_INTERFACES_CONFIG),
                keep("interfaces_config"),
            )
            data.interfaces_physical = await self._async_safe(
                "interfaces physical",
                lambda: client.async_get_path(API_INTERFACES_PHYSICAL_MON),
                keep("interfaces_physical"),
            )
            data.terminal_names = await self._async_safe(
                "terminal names",
                lambda: client.async_get_terminal_names(),
                keep("terminal_names"),
            )
            data.auth_accounts = await self._async_safe(
                "auth accounts",
                lambda: client.async_get_auth_accounts(),
                keep("auth_accounts"),
            )
            data.auth_packages = await self._async_safe(
                "auth packages",
                lambda: client.async_get_auth_packages(),
                keep("auth_packages"),
            )
            data.dhcp6_clients = await self._async_safe(
                "dhcp6 clients",
                lambda: client.async_get_dhcp6_clients(),
                keep("dhcp6_clients"),
            )
            data.ap_list = await self._async_safe(
                "ap list", lambda: client.async_get_ap_config(), keep("ap_list")
            )
            data.wireguard_peers = await self._async_safe(
                "wireguard peers", self._fetch_wireguard_peers, keep("wireguard_peers")
            )

        terminals = await self._async_safe(
            "traffic audit", lambda: client.async_get_traffic_audit_terminals(10), []
        )
        top: dict[str, Any] | None = None
        if terminals:
            top = max(
                terminals,
                key=lambda item: (item.get("sum_total_down") or 0)
                + (item.get("sum_total_up") or 0),
            )
        data.top_terminal = top

        data.dhcp_clients = await self._async_safe(
            "dhcp clients", lambda: client.async_get_dhcp_clients(), keep("dhcp_clients")
        )
        data.dhcp_static = await self._async_safe(
            "dhcp static", lambda: client.async_get_dhcp_static(), keep("dhcp_static")
        )
        data.auth_users = await self._async_safe(
            "auth users", lambda: client.async_get_auth_users(), keep("auth_users")
        )
        data.upgrade = await self._async_safe(
            "upgrade", client.async_get_upgrade_info, keep("upgrade")
        )
        data.wireless = await self._async_safe(
            "wireless", client.async_get_wireless_statistics, keep("wireless")
        )
        data.cpu_hour_avg = await self._async_safe(
            "cpu history", client.async_get_cpu_history, keep("cpu_hour_avg")
        )
        data.memory_hour_avg = await self._async_safe(
            "memory history", client.async_get_memory_history, keep("memory_hour_avg")
        )
        data.wireless_score = await self._async_safe(
            "wireless score", client.async_get_wireless_score, keep("wireless_score")
        )
        data.ssid_clients = await self._async_safe(
            "ssid clients", client.async_get_ssid_clients, keep("ssid_clients")
        )
        data.channel_clients = await self._async_safe(
            "channel clients", client.async_get_channel_clients, keep("channel_clients")
        )
        return data

    async def _fetch_wireguard_peers(self) -> dict[str, list[dict[str, Any]]]:
        """Peers per WireGuard interface (empty dict when none exist)."""
        peers: dict[str, list[dict[str, Any]]] = {}
        for interface in await self.client.async_get_wireguard_interfaces():
            wg_id = interface.get("wg_id") or interface.get("id")
            if wg_id is None:
                continue
            peers[str(wg_id)] = await self.client.async_get_wireguard_peers(wg_id)
        return peers


class IkuaiResourceCoordinator(DataUpdateCoordinator[IkuaiResourceData]):
    """Polls the CRUD groups the user opted into (switch platform source).

    Only created when write support is enabled, and only for the groups the
    user selected, so an unconfigured integration issues zero extra requests.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: IkuaiApiClient,
        resources: list[IkuaiResource],
        scan_interval: int = RESOURCE_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_resources",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self.resources = resources

    async def _async_update_data(self) -> IkuaiResourceData:
        rows: dict[str, list[dict[str, Any]]] = {}
        for resource in self.resources:
            try:
                rows[resource.key] = await self.client.async_list_resource(resource)
            except IkuaiApiNotFoundError:
                _LOGGER.debug(
                    "Resource group %s is unavailable on this device", resource.key
                )
                rows[resource.key] = []
            except IkuaiApiError as err:
                # Keep the previous rows so entities do not flicker to unknown.
                _LOGGER.debug("Could not refresh %s: %s", resource.key, err)
                previous = self.data.rows.get(resource.key) if self.data else None
                rows[resource.key] = previous if previous is not None else []
        return IkuaiResourceData(rows=rows)

    def rows_for(self, resource: IkuaiResource) -> list[dict[str, Any]]:
        """Rows of one group, or an empty list before the first refresh."""
        if not self.data:
            return []
        return self.data.rows.get(resource.key) or []
