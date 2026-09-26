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
    CONF_EDITION,
    CONF_ENABLE_WRITE,
    CONF_RESOURCE_GROUPS,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    CONF_VERIFY_SSL,
    DEFAULT_CLIENT_LIMIT,
    DEFAULT_EDITION,
    DEFAULT_ENABLE_WRITE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    EDITION_FREE,
    EXTENDED_SCAN_INTERVAL,
    PLATFORMS,
    RESOURCE_SCAN_INTERVAL,
    WRITE_PLATFORMS,
)
from .coordinator import (
    IkuaiDataUpdateCoordinator,
    IkuaiExtendedCoordinator,
    IkuaiResourceCoordinator,
)
from .helpers import detect_edition
from .resources import filter_by_edition, resolve
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)


@dataclass
class IkuaiRuntimeData:
    """Coordinators stored for a config entry."""

    main: IkuaiDataUpdateCoordinator
    extended: IkuaiExtendedCoordinator
    entry: ConfigEntry | None = None
    resources: IkuaiResourceCoordinator | None = None
    edition: str = EDITION_FREE
    """Resolved edition (free/enterprise), override applied over auto-detect."""


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

    runtime = IkuaiRuntimeData(main=main, extended=extended, entry=entry)

    # Edition: auto-detect from the firmware, but let the user override when
    # detection disagrees. Used to hide enterprise-only resource groups.
    override = config.get(CONF_EDITION, DEFAULT_EDITION)
    runtime.edition = (
        override
        if override in (EDITION_FREE, EDITION_ENTERPRISE)
        else main.data.edition
    )

    # Phase 2: write support is opt-in and requires both enable_write and at
    # least one selected resource group. Without it no extra request is made.
    platforms = list(PLATFORMS)
    if config.get(CONF_ENABLE_WRITE, DEFAULT_ENABLE_WRITE):
        chosen = resolve(config.get(CONF_RESOURCE_GROUPS) or [])
        resources = filter_by_edition(chosen, runtime.edition)
        skipped = {r.key for r in chosen} - {r.key for r in resources}
        if skipped:
            _LOGGER.info(
                "Edition %s: skipping enterprise-only group(s): %s",
                runtime.edition,
                ", ".join(sorted(skipped)),
            )
        runtime.resources = IkuaiResourceCoordinator(
            hass, client, resources, RESOURCE_SCAN_INTERVAL
        )
        await runtime.resources.async_config_entry_first_refresh()
        platforms.extend(WRITE_PLATFORMS)
        if resources:
            _LOGGER.debug(
                "Write support enabled for %d resource group(s): %s",
                len(resources),
                ", ".join(res.key for res in resources),
            )

    hass.data[DOMAIN][entry.entry_id] = runtime

    # Phase 3: scenario services (block/allow terminal, parental control).
    # Registration is idempotent; handlers resolve the target entry per call.
    async_setup_services(hass)

    await hass.config_entries.async_forward_entry_setups(entry, platforms)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    platforms = list(PLATFORMS)
    if merged_config(entry).get(CONF_ENABLE_WRITE, DEFAULT_ENABLE_WRITE):
        platforms.extend(WRITE_PLATFORMS)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, platforms)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
