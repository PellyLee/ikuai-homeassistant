"""One-shot action buttons (POST endpoints).

Only present when write support is enabled in the options. Reboot is the
destructive one: it is created disabled in the entity registry so it has to be
enabled on purpose before it can ever be pressed.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Callable, Coroutine, Any

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import IkuaiApiClient, IkuaiApiError
from .const import DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class IkuaiButtonDescription(ButtonEntityDescription):
    """Describes an iKuai action button."""

    press_fn: Callable[[IkuaiApiClient], Coroutine[Any, Any, None]]


BUTTONS: tuple[IkuaiButtonDescription, ...] = (
    IkuaiButtonDescription(
        key="check_upgrade",
        name="检测固件更新",
        translation_key="check_upgrade",
        icon="mdi:update",
        press_fn=lambda client: client.async_check_upgrade(),
    ),
    IkuaiButtonDescription(
        key="ntp_sync",
        name="同步时间 (NTP)",
        translation_key="ntp_sync",
        icon="mdi:clock-check-outline",
        press_fn=lambda client: client.async_ntp_sync(),
    ),
    IkuaiButtonDescription(
        key="backup",
        name="备份配置",
        translation_key="backup",
        icon="mdi:content-save-cog-outline",
        press_fn=lambda client: client.async_backup(),
    ),
    IkuaiButtonDescription(
        key="reboot",
        name="重启路由器",
        translation_key="reboot",
        device_class=ButtonDeviceClass.RESTART,
        # Never enabled automatically: pressing it drops the whole network.
        entity_registry_enabled_default=False,
        press_fn=lambda client: client.async_reboot(),
    ),
)


class IkuaiButton(ButtonEntity):
    """Runs one POST action."""

    _attr_has_entity_name = True

    entity_description: IkuaiButtonDescription

    def __init__(
        self,
        client: IkuaiApiClient,
        entry: ConfigEntry,
        description: IkuaiButtonDescription,
    ) -> None:
        self.entity_description = description
        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer=MANUFACTURER,
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_press(self) -> None:
        try:
            await self.entity_description.press_fn(self._client)
        except IkuaiApiError as err:
            _LOGGER.error("iKuai action %s failed: %s", self.entity_description.key, err)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add the action buttons (write support only)."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    client: IkuaiApiClient = runtime.main.client
    async_add_entities(IkuaiButton(client, entry, desc) for desc in BUTTONS)
