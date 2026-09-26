"""Binary sensors for WAN line health.

Data source: GET /api/v4.0/monitoring/interfaces-status -> results.iface_check
One binary sensor per WAN line: "on" = line check success.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import IkuaiDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WAN line binary sensors (dynamic per line)."""
    coordinator: IkuaiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    known: set[str] = set()

    def _async_add_new_lines() -> None:
        lines = _wan_lines(coordinator)
        new = [line for line in lines if line["interface"] not in known]
        if not new:
            return
        known.update(line["interface"] for line in new)
        async_add_entities(
            IkuaiWanBinarySensor(coordinator, entry, line["interface"]) for line in new
        )

    _async_add_new_lines()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_lines))


def _wan_lines(coordinator: IkuaiDataUpdateCoordinator) -> list[dict[str, Any]]:
    return ((coordinator.data.interfaces or {}).get("iface_check")) or []


class IkuaiWanBinarySensor(
    CoordinatorEntity[IkuaiDataUpdateCoordinator], BinarySensorEntity
):
    """WAN line check status."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: IkuaiDataUpdateCoordinator,
        entry: ConfigEntry,
        interface: str,
    ) -> None:
        super().__init__(coordinator)
        self._interface = interface
        self._attr_unique_id = f"{entry.entry_id}_wan_{interface}"
        self._attr_name = f"{entry.title} {interface.upper()} 线路"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def is_on(self) -> bool | None:
        """True when the line check reports success."""
        for line in _wan_lines(self.coordinator):
            if line.get("interface") == self._interface:
                return str(line.get("result", "")).lower() == "success"
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        for line in _wan_lines(self.coordinator):
            if line.get("interface") == self._interface:
                return {
                    "ip_addr": line.get("ip_addr"),
                    "gateway": line.get("gateway"),
                    "internet": line.get("internet"),
                    "errmsg": line.get("errmsg"),
                }
        return None
