"""Device tracker for online clients.

Data source: GET /api/v4.0/monitoring/clients-online

One tracker entity per client. Clients present in the online list are reported
as connected/homed.

Field notes from real devices (values may be missing, empty or 0):
  hostname / comment / client_vendor / client_model -> name and model hints
  ip_addr, mac, ssid, signal, upload, download, interface, connect_num
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker.config_entry import ScannerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .. import IkuaiRuntimeData
from .const import DOMAIN, MANUFACTURER
from .coordinator import IkuaiDataUpdateCoordinator
from .helpers import client_name


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up client trackers, adding entities dynamically as devices appear."""
    runtime: IkuaiRuntimeData = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.main
    known: set[str] = set()

    @callback
    def _async_add_new_clients() -> None:
        macs = {
            str(c.get("mac", "")).lower()
            for c in coordinator.data.clients
            if c.get("mac")
        }
        new = sorted(m for m in macs if m not in known)
        if not new:
            return
        known.update(new)
        async_add_entities(IkuaiClientTracker(coordinator, entry, mac) for mac in new)

    _async_add_new_clients()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_clients))


def _clean(value: Any) -> Any:
    """Drop placeholders (empty string, "--", 0-ish noise) from attributes."""
    if isinstance(value, str) and (value == "" or value == "--"):
        return None
    return value


class IkuaiClientTracker(CoordinatorEntity[IkuaiDataUpdateCoordinator], ScannerEntity):
    """Representation of a client reported by the router."""

    def __init__(
        self,
        coordinator: IkuaiDataUpdateCoordinator,
        entry: ConfigEntry,
        mac: str,
    ) -> None:
        super().__init__(coordinator)
        self._mac = mac
        self._attr_unique_id = f"{entry.entry_id}_client_{mac}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            entry_type=DeviceEntryType.SERVICE,
        )

    def _client(self) -> dict[str, Any] | None:
        for client in self.coordinator.data.clients:
            if str(client.get("mac", "")).lower() == self._mac:
                return client
        return None

    @property
    def name(self) -> str:
        """Prefer readable fields; fall back to the MAC for binary junk hostnames."""
        return client_name(self._client() or {}, self._mac)

    @property
    def mac_address(self) -> str | None:
        return self._mac

    @property
    def source_type(self) -> str:
        return "router"

    @property
    def ip_address(self) -> str | None:
        return (self._client() or {}).get("ip_addr")

    @property
    def hostname(self) -> str | None:
        return (self._client() or {}).get("hostname")

    @property
    def is_connected(self) -> bool:
        """Connected while the client appears in the online list."""
        return self._client() is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        client = self._client()
        if not client:
            return None
        attrs: dict[str, Any] = {}
        for key in (
            "comment",
            "total_up",
            "total_down",
            "client_vendor",
            "client_model",
            "interface",
            "connect_num",
            "static_status",
            "ppptype",
            "vlan_id",
        ):
            value = _clean(client.get(key))
            if value is not None:
                attrs[key] = value

        # rate values are often returned as "", but sometimes as bytes/s
        for key in ("upload", "download"):
            value = _clean(client.get(key))
            if isinstance(value, (int, float)):
                attrs[key] = value

        if client.get("ssid"):
            attrs["ssid"] = client["ssid"]
            attrs["wireless"] = True
            signal = _clean(client.get("signal"))
            if signal not in (None, 0):
                attrs["signal"] = signal
        return attrs
