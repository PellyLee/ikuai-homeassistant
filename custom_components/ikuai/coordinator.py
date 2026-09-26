"""Data update coordinators for the iKuai Router integration."""

from __future__ import annotations

from dataclasses import dataclass, field
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
    DEFAULT_CLIENT_LIMIT,
    DOMAIN,
    EXTENDED_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class IkuaiData:
    """Fast-polling data (system status, lines, online clients)."""

    system: dict[str, Any] = field(default_factory=dict)
    interfaces: dict[str, Any] = field(default_factory=dict)
    clients: list[dict[str, Any]] = field(default_factory=list)


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

        return IkuaiExtendedData(
            dhcp_clients=await self._async_safe(
                "dhcp clients", lambda: client.async_get_dhcp_clients()
            ),
            dhcp_static=await self._async_safe(
                "dhcp static", lambda: client.async_get_dhcp_static()
            ),
            auth_users=await self._async_safe(
                "auth users", lambda: client.async_get_auth_users()
            ),
            upgrade=await self._async_safe("upgrade", client.async_get_upgrade_info),
            wireless=await self._async_safe(
                "wireless", client.async_get_wireless_statistics
            ),
            top_terminal=top,
            cpu_hour_avg=await self._async_safe(
                "cpu history", client.async_get_cpu_history
            ),
            memory_hour_avg=await self._async_safe(
                "memory history", client.async_get_memory_history
            ),
        )
