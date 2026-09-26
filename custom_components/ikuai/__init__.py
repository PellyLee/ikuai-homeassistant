"""The iKuai Router integration (based on the official iKuaiOS 4.x OpenAPI)."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    IkuaiApiAuthError,
    IkuaiApiClient,
    IkuaiApiConnectionError,
)
from .const import (
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    CONF_VERIFY_SSL,
    DEFAULT_CLIENT_LIMIT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    EXTENDED_SCAN_INTERVAL,
    PLATFORMS,
)
from .coordinator import IkuaiDataUpdateCoordinator, IkuaiExtendedCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class IkuaiRuntimeData:
    """Coordinators stored for a config entry."""

    main: IkuaiDataUpdateCoordinator
    extended: IkuaiExtendedCoordinator


def merged_config(entry: ConfigEntry) -> dict:
    """Effective configuration: options override the values entered at setup."""
    data = dict(entry.data)
    data.update(entry.options)
    return data


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up iKuai from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    config = merged_config(entry)
    verify_ssl = config.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)
    scan_interval = config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    session = async_get_clientsession(hass, verify_ssl=verify_ssl)
    client = IkuaiApiClient(
        session, config[CONF_HOST], config[CONF_TOKEN], verify_ssl=verify_ssl
    )

    main = IkuaiDataUpdateCoordinator(hass, client, scan_interval, DEFAULT_CLIENT_LIMIT)
    extended = IkuaiExtendedCoordinator(hass, client, EXTENDED_SCAN_INTERVAL)

    try:
        await main.async_config_entry_first_refresh()
    except IkuaiApiAuthError as err:
        raise ConfigEntryAuthFailed(f"Invalid iKuai token: {err}") from err
    except IkuaiApiConnectionError as err:
        _LOGGER.warning("Cannot reach the iKuai router yet, will retry: %s", err)

    # Extended data is optional: failing calls must not block setup.
    await extended.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = IkuaiRuntimeData(main=main, extended=extended)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
