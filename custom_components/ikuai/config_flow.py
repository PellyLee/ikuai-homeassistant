"""Config flow to configure the iKuai Router integration.

Two entry points matter for a public integration:
* setup  - every user has their own router IP and token
* reauth - tokens can expire / be regenerated in the router admin
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    IkuaiApiAuthError,
    IkuaiApiClient,
    IkuaiApiConnectionError,
    IkuaiApiError,
)
from .const import (
    CONF_EDITION,
    CONF_ENABLE_WRITE,
    CONF_RESOURCE_GROUPS,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    CONF_VERIFY_SSL,
    DEFAULT_EDITION,
    DEFAULT_ENABLE_WRITE,
    DEFAULT_NAME,
    DEFAULT_RESOURCE_GROUPS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    EDITION_ENTERPRISE,
    EDITION_FREE,
)
from .helpers import detect_edition, edition_label, normalize_host
from .resources import RESOURCES

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="https://192.168.1.1"): str,
        vol.Required(CONF_TOKEN): str,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=3600)
        ),
    }
)

STEP_REAUTH_SCHEMA = vol.Schema({vol.Required(CONF_TOKEN): str})


async def _test_connection(hass, host: str, token: str, verify_ssl: bool) -> str | None:
    """Return an error code, or None when the router answers with valid data."""
    session = async_get_clientsession(hass, verify_ssl=verify_ssl)
    client = IkuaiApiClient(session, host, token, verify_ssl=verify_ssl)
    try:
        await client.async_verify()
    except IkuaiApiAuthError:
        return "invalid_auth"
    except IkuaiApiConnectionError:
        return "cannot_connect"
    except IkuaiApiError:
        return "unknown"
    except Exception:  # noqa: BLE001 - never crash the config flow
        return "unknown"
    return None


class IkuaiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the iKuai config flow."""

    VERSION = 1

    _reauth_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                host = normalize_host(user_input[CONF_HOST])
            except ValueError:
                errors["base"] = "invalid_host"
            else:
                error = await _test_connection(
                    self.hass,
                    host,
                    user_input[CONF_TOKEN],
                    user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                )
                if error:
                    errors["base"] = error
                else:
                    data = dict(user_input)
                    data[CONF_HOST] = host
                    await self.async_set_unique_id(host)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=user_input.get(CONF_NAME, DEFAULT_NAME), data=data
                    )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a token rejected at startup."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        entry = self._reauth_entry
        if user_input is not None and entry is not None:
            error = await _test_connection(
                self.hass,
                entry.data[CONF_HOST],
                user_input[CONF_TOKEN],
                entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            )
            if error:
                errors["base"] = error
            else:
                self.hass.config_entries.async_update_entry(
                    entry, data={**entry.data, CONF_TOKEN: user_input[CONF_TOKEN]}
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm", data_schema=STEP_REAUTH_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> IkuaiOptionsFlow:
        return IkuaiOptionsFlow(config_entry)


class IkuaiOptionsFlow(config_entries.OptionsFlow):
    """Options: router IP, token, polling interval, TLS and (opt-in) write support.

    Write support needs two independent confirmations on purpose:
    * `enable_write` - the master switch, off by default
    * `resource_groups` - which rule groups may be exposed as switches
    """

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    def _current(self, key: str, default: Any) -> Any:
        return self.config_entry.options.get(
            key, self.config_entry.data.get(key, default)
        )

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        known_keys = {res.key for res in RESOURCES}
        selected = [
            key
            for key in (self._current(CONF_RESOURCE_GROUPS, DEFAULT_RESOURCE_GROUPS) or [])
            if key in known_keys
        ]

        # Detect the edition live so the picker can explain which groups are
        # unavailable. A failed detection (offline box) just hides the hint.
        detected = None
        try:
            session = async_get_clientsession(
                self.hass,
                verify_ssl=self._current(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            )
            client = IkuaiApiClient(
                session,
                self._current(CONF_HOST, ""),
                self._current(CONF_TOKEN, ""),
                verify_ssl=self._current(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            )
            system = await client.async_get_system()
            verinfo = (system.get("sysinfo") or {}).get("verinfo") or {}
            detected = detect_edition(verinfo)
        except IkuaiApiError:
            detected = None

        edition_options = {
            DEFAULT_EDITION: (
                f"自动检测（当前：{edition_label(detected)}）"
                if detected
                else "自动检测"
            ),
            EDITION_FREE: "免费版",
            EDITION_ENTERPRISE: "企业版",
        }

        group_labels = {}
        for res in RESOURCES:
            label = f"{res.name}（/{res.path}）"
            if res.enterprise_only:
                label += "（仅企业版）"
            group_labels[res.key] = label

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=self._current(CONF_HOST, "")): str,
                vol.Required(CONF_TOKEN, default=self._current(CONF_TOKEN, "")): str,
                vol.Required(
                    CONF_VERIFY_SSL,
                    default=self._current(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                ): bool,
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=self._current(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),
                vol.Required(
                    CONF_EDITION,
                    default=self._current(CONF_EDITION, DEFAULT_EDITION),
                ): vol.In(edition_options),
                vol.Required(
                    CONF_ENABLE_WRITE,
                    default=self._current(CONF_ENABLE_WRITE, DEFAULT_ENABLE_WRITE),
                ): bool,
                vol.Optional(
                    CONF_RESOURCE_GROUPS, default=selected
                ): cv.multi_select(group_labels),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
