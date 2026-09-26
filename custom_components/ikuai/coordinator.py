"""Data update coordinator for the iKuai Router integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IkuaiApiClient, IkuaiApiError
from .const import DEFAULT_CLIENT_LIMIT, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class IkuaiData:
    """Aggregated data polled from the router."""

    system: dict[str, Any] = field(default_factory=dict)
    interfaces: dict[str, Any] = field(default_factory=dict)
    clients: list[dict[str, Any]] = field(default_factory=list)


class IkuaiDataUpdateCoordinator(DataUpdateCoordinator[IkuaiData]):
    """Polls the router every scan_interval."""

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
