"""Diagnostics for the iKuai Router integration.

Exposes the detected edition and the raw `verinfo` so a user can confirm why a
resource group was hidden (edition mismatch vs. a real 404 on their box).
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, EDITION_FREE
from .helpers import edition_label
from .coordinator import IkuaiDataUpdateCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    runtime = hass.data[DOMAIN].get(entry.entry_id)
    coordinator: IkuaiDataUpdateCoordinator | None = (
        runtime.main if runtime else None
    )
    system = coordinator.data.system if coordinator and coordinator.data else {}
    verinfo = (system.get("sysinfo") or {}).get("verinfo") or {}

    edition = getattr(runtime, "edition", EDITION_FREE) if runtime else EDITION_FREE
    return {
        "edition": edition,
        "edition_label": edition_label(edition),
        "edition_override": entry.options.get("edition", "auto"),
        "enable_write": entry.options.get("enable_write", False),
        "resource_groups": entry.options.get("resource_groups", []),
        "verinfo": {
            "modelname": verinfo.get("modelname"),
            "sn": verinfo.get("sn"),
            "version": verinfo.get("version"),
            "arch": verinfo.get("arch"),
            "is_enterprise": verinfo.get("is_enterprise"),
        },
    }
