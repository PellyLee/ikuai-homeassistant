"""Switches that enable/disable iKuai rules (generic resource engine).

One switch entity is created per row of every resource group the user selected
in the integration options, e.g. "停用 MAC 限速 MQ_2". Nothing at all is
created unless the user turned on write support *and* picked at least one group.

The entities are dynamically added/removed as rules appear on the router, the
same way the WAN traffic sensors are.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import IkuaiApiError
from .const import DOMAIN, MANUFACTURER
from .coordinator import IkuaiResourceCoordinator
from .helpers import is_enabled, row_label
from .resources import IkuaiResource

_LOGGER = logging.getLogger(__name__)

_SWITCH_ICON = "mdi:toggle-switch"
_SWITCH_OFF_ICON = "mdi:toggle-switch-off-outline"


class IkuaiResourceSwitch(CoordinatorEntity[IkuaiResourceCoordinator], SwitchEntity):
    """Enable/disable one iKuai rule."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IkuaiResourceCoordinator,
        entry: ConfigEntry,
        resource: IkuaiResource,
        row_id: Any,
    ) -> None:
        super().__init__(coordinator)
        self._resource = resource
        self._row_id = row_id
        self._attr_unique_id = f"{entry.entry_id}_{resource.key}_{row_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer=MANUFACTURER,
            entry_type=DeviceEntryType.SERVICE,
        )
        self._attr_icon = _SWITCH_ICON
        # Dangerous groups (ACL, 限速, 分流 ...) are not enabled by default: the
        # user explicitly opts in per entity, which avoids an automation
        # accidentally disabling a rule that keeps the network working.
        self._attr_entity_registry_enabled_default = not resource.dangerous

    @property
    def _row(self) -> dict[str, Any] | None:
        for row in self.coordinator.rows_for(self._resource):
            if str(row.get(self._resource.id_field)) == str(self._row_id):
                return row
        return None

    @property
    def name(self) -> str:
        row = self._row or {}
        label = row_label(row, self._resource.label_fields, f"#{self._row_id}")
        return f"{self._resource.name} {label}"

    @property
    def available(self) -> bool:
        return super().available and self._row is not None

    @property
    def is_on(self) -> bool | None:
        row = self._row
        if row is None:
            return None
        return is_enabled(row, self._resource.enabled_field)

    @property
    def icon(self) -> str:
        return _SWITCH_ICON if self.is_on else _SWITCH_OFF_ICON

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        row = self._row or {}
        attrs: dict[str, Any] = {
            "resource": self._resource.key,
            "path": self._resource.path,
            "row_id": self._row_id,
        }
        for key in self._resource.extra_attrs:
            value = row.get(key)
            # Nested address groups ({"object": [...], "custom": [...]}) are not
            # usable as attributes, keep them flat.
            if isinstance(value, (str, int, float, bool)) or value is None:
                attrs[key] = value
        return attrs

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_set(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_set(False)

    async def _async_set(self, enabled: bool) -> None:
        try:
            await self.coordinator.client.async_set_resource_enabled(
                self._resource, self._row_id, enabled
            )
        except IkuaiApiError as err:
            _LOGGER.error(
                "Could not %s %s #%s: %s",
                "enable" if enabled else "disable",
                self._resource.key,
                self._row_id,
                err,
            )
            # Leave the state untouched; the next refresh shows reality.
            return
        # Write succeeded: refresh so the UI shows the router's own state
        # instead of an optimistic guess.
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create switches for the selected resource groups."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator: IkuaiResourceCoordinator | None = getattr(runtime, "resources", None)
    if coordinator is None:
        return

    known: dict[tuple[str, str], IkuaiResourceSwitch] = {}

    @callback
    def _async_sync() -> None:
        """Add switches for new rules and drop the ones deleted on the router."""
        added: list[IkuaiResourceSwitch] = []
        seen: set[tuple[str, str]] = set()

        for resource in coordinator.resources:
            for row in coordinator.rows_for(resource):
                row_id = row.get(resource.id_field)
                if row_id is None:
                    continue
                marker = (resource.key, str(row_id))
                seen.add(marker)
                if marker in known:
                    continue
                entity = IkuaiResourceSwitch(coordinator, entry, resource, row_id)
                known[marker] = entity
                added.append(entity)

        stale = [entity for marker, entity in known.items() if marker not in seen]
        for marker in [m for m in known if m not in seen]:
            known.pop(marker)

        if added:
            async_add_entities(added)
        for entity in stale:
            # The rule no longer exists on the router.
            hass.async_create_task(entity.async_remove(force_removal=True))

    _async_sync()
    entry.async_on_unload(coordinator.async_add_listener(_async_sync))
