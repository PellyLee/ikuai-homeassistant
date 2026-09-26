"""iKuai v4.0 REST API client.

Official API docs: https://rapi-docs.ikuai8.com/
Auth: Bearer token generated in the iKuai web admin ("系统设置 → API/第三方对接").

Notes derived from real devices:
* iKuaiOS 4.x answers plain HTTP requests with a 302 to https://<router>:443,
  so https is preferred (it is the default when no scheme is given).
* The certificate is self-signed: certificate verification must be disable-able.
* Successful payloads look like
  {"code": 0, "message": "Success", "results": {...}}.
"""

from __future__ import annotations

import asyncio
import json
import ssl
from typing import Any

import aiohttp

from .const import (
    API_AC_SERVICE,
    API_AC_START,
    API_AC_STOP,
    API_AP_CONFIG,
    API_AP_SSID_QUICK,
    API_AUTH_ACCOUNTS,
    API_AUTH_PACKAGES,
    API_AUTH_USERS,
    API_BACKUP,
    API_CHANNEL_CLIENTS,
    API_CLIENTS_ONLINE,
    API_CPU_HISTORY,
    API_DHCP6_CLIENTS,
    API_DHCP_CLIENTS,
    API_DHCP_RESTART,
    API_DHCP_STATIC,
    API_INTERFACES_STATUS,
    API_MEMORY_HISTORY,
    API_NTP_SYNC,
    API_REBOOT_TASKS,
    API_ROUTER_HEALTH,
    API_SPEED_TEST,
    API_SSID_CLIENTS,
    API_SYSTEM,
    API_TERMINAL_NAMES,
    API_TRAFFIC_AUDIT_TERMINALS,
    API_UPGRADE,
    API_UPGRADE_CHECK,
    API_VRRP_START,
    API_VRRP_STOP,
    API_WIREGUARD,
    API_WIRELESS_SCORE,
    API_WIRELESS_STATISTICS,
    DEFAULT_CLIENT_LIMIT,
    DEFAULT_TIMEOUT,
    DEFAULT_VERIFY_SSL,
)
from .helpers import decode_payload, normalize_host
from .resources import TOGGLE_BATCH, IkuaiResource


def _to_number(value: Any) -> float | None:
    try:
        return float(str(value).rstrip("%"))
    except (TypeError, ValueError):
        return None


class IkuaiApiError(Exception):
    """Base error for the iKuai API client."""


class IkuaiApiConnectionError(IkuaiApiError):
    """Cannot connect to the router."""


class IkuaiApiAuthError(IkuaiApiError):
    """Invalid, missing or expired token (HTTP 401/403)."""


class IkuaiApiNotFoundError(IkuaiApiError):
    """Endpoint missing - the feature is unavailable on this device/license."""


class IkuaiApiBusinessError(IkuaiApiError):
    """HTTP 200 but `code != 0`: the router refused the operation.

    iKuai reports business failures (invalid parameter, conflict, ...) in the
    body, so the HTTP status alone is never enough to trust a write.
    """


class IkuaiApiClient:
    """Small async client for the iKuaiOS 4.x OpenAPI."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        token: str,
        verify_ssl: bool = DEFAULT_VERIFY_SSL,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._session = session
        self._base_url = normalize_host(host)
        self._token = (token or "").strip()
        self._verify_ssl = verify_ssl
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    @property
    def base_url(self) -> str:
        """Normalized router base URL (useful for diagnostics)."""
        return self._base_url

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }

    @property
    def _ssl(self) -> bool | ssl.SSLContext:
        if self._verify_ssl:
            return True
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a request and return the decoded envelope (code / message / results)."""
        url = f"{self._base_url}/api/v4.0/{path}"
        headers = dict(self._headers)
        if payload is not None:
            headers["Content-Type"] = "application/json"
        try:
            async with self._session.request(
                method,
                url,
                params=params,
                json=payload,
                headers=headers,
                timeout=self._timeout,
                ssl=self._ssl,
                allow_redirects=True,
            ) as resp:
                if resp.status in (401, 403):
                    raise IkuaiApiAuthError(f"Token rejected ({resp.status}) by {url}")
                if resp.status == 404:
                    raise IkuaiApiNotFoundError(f"{url} is not available on this device")
                if resp.status >= 400:
                    raise IkuaiApiError(f"HTTP {resp.status} from {url}")
                raw = await resp.read()
        except aiohttp.ContentTypeError as err:
            # Not the iKuai API (for example redirected to the admin login page)
            raise IkuaiApiConnectionError(
                f"Unexpected content from {url} - check the host and the API switch: {err}"
            ) from err
        except (TimeoutError, asyncio.TimeoutError) as err:
            raise IkuaiApiConnectionError(f"Timeout requesting {url}") from err
        except aiohttp.ClientSSLError as err:
            raise IkuaiApiConnectionError(
                "TLS error; disable certificate validation if the router uses "
                f"its self-signed certificate ({err})"
            ) from err
        except aiohttp.ClientError as err:
            raise IkuaiApiConnectionError(f"Connection error: {err}") from err

        # Router payloads are not always valid UTF-8 (some clients report binary
        # hostnames), so decoding is deliberately forgiving.
        try:
            data = decode_payload(raw)
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as err:
            raise IkuaiApiError(f"Malformed response from {url}: {err}") from err

        return data

    async def _get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """GET and return the `results` object as a dict."""
        data = await self._request("get", path, params=params)
        results = data.get("results", data)
        return results if isinstance(results, dict) else {"data": results}

    # -- Phase 2: write channel ---------------------------------------------

    async def async_request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Write helper: verifies the business `code`, not just the HTTP status.

        iKuai answers rejected writes with HTTP 200 and ``{"code": 30001, ...}``,
        so anything but ``code == 0`` is raised as an error.
        """
        data = await self._request(method, path, params=params, payload=payload)
        code = data.get("code", 0)
        if code not in (0, "0"):
            message = data.get("message") or "unknown error"
            details = data.get("details")
            suffix = ""
            if isinstance(details, list) and details:
                suffix = "; " + ", ".join(
                    f"{item.get('field', '?')}: {item.get('msg', '')}"
                    for item in details
                    if isinstance(item, dict)
                )
            raise IkuaiApiBusinessError(f"{method} {path} failed ({code}): {message}{suffix}")
        return data

    async def async_list_resource(
        self, resource: IkuaiResource, limit: int = 200
    ) -> list[dict[str, Any]]:
        """Rows of a generic resource group (empty list when unavailable)."""
        results = await self._get(resource.path, params={"limit": limit})
        for key in (*resource.list_keys, "data", "rows", "list"):
            value = results.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
        # Last resort: the first list-typed value in the payload.
        for value in results.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                return [row for row in value if isinstance(row, dict)]
        return []

    async def async_set_resource_enabled(
        self, resource: IkuaiResource, row_id: Any, enabled: bool
    ) -> None:
        """Toggle one rule. `enabled` must be the string "yes"/"no"."""
        state = "yes" if enabled else "no"
        if resource.toggle == TOGGLE_BATCH:
            # Collection-level toggle: ids are passed comma separated in the body.
            await self.async_request(
                "patch", resource.path, {"id": str(row_id), "enabled": state}
            )
            return
        await self.async_request(
            "patch", f"{resource.path}/{row_id}", {"enabled": state}
        )

    async def async_create_resource(
        self, resource: IkuaiResource, payload: dict[str, Any]
    ) -> Any:
        """Create one row (POST /path) and return the new row id.

        iKuai answers a successful create with ``{"code": 0, "rowid": 1}``;
        the id is what services need to undo themselves later.
        """
        data = await self.async_request("post", resource.path, payload)
        rowid = data.get("rowid")
        return rowid if rowid not in (None, "") else data.get("results", {}).get("rowid")

    async def async_delete_resource(self, resource: IkuaiResource, row_id: Any) -> None:
        """Delete one row (DELETE /path/{id}). Raises on business errors."""
        await self.async_request("delete", f"{resource.path}/{row_id}")

    async def async_trigger(self, path: str, payload: dict[str, Any] | None = None) -> None:
        """Fire a one-shot POST action (reboot, backup, NTP sync, ...)."""
        await self.async_request("post", path, payload or {})

    async def async_reboot(self) -> None:
        """Reboot the router now - only ever called from an explicit button."""
        await self.async_trigger(API_REBOOT_TASKS)

    async def async_backup(self) -> None:
        """Create a configuration backup on the router."""
        await self.async_trigger(API_BACKUP)

    async def async_ntp_sync(self) -> None:
        """Force an NTP synchronisation."""
        await self.async_trigger(API_NTP_SYNC)

    async def async_check_upgrade(self) -> None:
        """Ask the router to re-check the cloud for a newer firmware."""
        await self.async_trigger(API_UPGRADE_CHECK)

    async def async_get_system(self) -> dict[str, Any]:
        """Real-time system status: CPU, temp, memory, connections, uptime, version."""
        return await self._get(API_SYSTEM)

    async def async_get_interfaces_status(self) -> dict[str, Any]:
        """WAN/LAN interface status and live traffic (iface_check + iface_stream)."""
        return await self._get(API_INTERFACES_STATUS)

    async def async_get_online_clients(
        self, limit: int = DEFAULT_CLIENT_LIMIT
    ) -> list[dict[str, Any]]:
        """Currently online IPv4 clients (device tracking source)."""
        results = await self._get(API_CLIENTS_ONLINE, params={"limit": limit})
        return results.get("data") or []

    async def async_verify(self) -> dict[str, Any]:
        """Validate connectivity + token during config flow."""
        return await self.async_get_system()

    # -- Phase 1: read-only breadth -----------------------------------------

    async def async_get_dhcp_clients(self, limit: int = 500) -> list[dict[str, Any]]:
        """Active DHCPv4 leases."""
        results = await self._get(API_DHCP_CLIENTS, params={"limit": limit})
        return results.get("data") or []

    async def async_get_dhcp_static(self, limit: int = 500) -> list[dict[str, Any]]:
        """DHCP static bindings (results key differs from the other list APIs)."""
        results = await self._get(API_DHCP_STATIC, params={"limit": limit})
        return results.get("static_data") or results.get("data") or []

    async def async_get_auth_users(self, limit: int = 200) -> list[dict[str, Any]]:
        """Authenticated (PPPoE/PPTP/L2TP...) users."""
        results = await self._get(API_AUTH_USERS, params={"limit": limit})
        return results.get("data") or []

    async def async_get_upgrade_info(self) -> dict[str, Any]:
        """Installed firmware version and the version offered by the cloud."""
        results = await self._get(API_UPGRADE)
        data = results.get("data")
        return data if isinstance(data, dict) else results

    async def async_get_wireless_statistics(self) -> dict[str, Any]:
        """AP and wireless client counters (zeros when no AP is managed)."""
        return await self._get(API_WIRELESS_STATISTICS)

    async def async_get_traffic_audit_terminals(
        self, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Per-terminal traffic totals (404 when auditing is not enabled)."""
        results = await self._get(API_TRAFFIC_AUDIT_TERMINALS, params={"limit": limit})
        data = results.get("daytime") or results.get("data") or []
        return data if isinstance(data, list) else []

    async def async_get_cpu_history(self) -> float | None:
        """Average CPU load over the last hour (percent)."""
        results = await self._get(API_CPU_HISTORY, params={"datetype": "hour", "math": "avg"})
        series = results.get("cpu") or []
        values = [_to_number(item.get("cpu")) for item in series if isinstance(item, dict)]
        values = [v for v in values if v is not None]
        return round(sum(values) / len(values), 1) if values else None

    async def async_get_memory_history(self) -> float | None:
        """Average memory usage over the last hour (percent)."""
        results = await self._get(
            API_MEMORY_HISTORY, params={"datetype": "hour", "math": "avg"}
        )
        series = results.get("memory") or []
        values = [
            _to_number(item.get("memory_use")) for item in series if isinstance(item, dict)
        ]
        values = [v for v in values if v is not None]
        return round(sum(values) / len(values), 1) if values else None

    # -- Phase 3: read-only wireless detail ----------------------------------

    async def async_get_wireless_score(self) -> dict[str, Any]:
        """Wireless quality scores over the last 24h (empty dict when no AP)."""
        return await self._get(API_WIRELESS_SCORE)

    async def async_get_ssid_clients(self) -> list[dict[str, Any]]:
        """Per-SSID client statistics (hourly aggregates)."""
        return self._first_list(await self._get(API_SSID_CLIENTS))

    async def async_get_channel_clients(self) -> list[dict[str, Any]]:
        """Per-channel client statistics (hourly aggregates)."""
        return self._first_list(await self._get(API_CHANNEL_CLIENTS))

    @staticmethod
    def _first_list(results: dict[str, Any]) -> list[dict[str, Any]]:
        """First list-of-dicts value in the payload, tolerating unknown shapes."""
        for key in ("data", "rows", "list"):
            value = results.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
        for value in results.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                return [row for row in value if isinstance(row, dict)]
        return []

    # -- Phase 4: extended monitoring (Tier A) --------------------------------

    async def async_get_path(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Raw GET returning the unwrapped `results` dict (query service)."""
        return await self._get(path, params=params)

    async def async_get_rows(
        self, path: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """GET a list endpoint, tolerating unknown row keys."""
        return self._first_list(await self._get(path, params=params))

    async def async_get_monitor_series(
        self, path: str, datetype: str = "hour", math: str = "avg"
    ) -> list[dict[str, Any]]:
        """History series of the datetype monitor family (connections/disk/...)."""
        results = await self._get(path, params={"datetype": datetype, "math": math})
        return self._first_list(results)

    async def async_get_speed_test(self) -> dict[str, Any]:
        """One-click speed test status and last results."""
        return await self._get(API_SPEED_TEST)

    async def async_start_speed_test(self, interface: str | None = None) -> None:
        """Start the speed test (`all`/empty lets the router pick the lines)."""
        payload: dict[str, Any] = {}
        if interface and str(interface).strip() and str(interface) != "all":
            payload["interface"] = str(interface).strip()
        await self.async_request("post", API_SPEED_TEST, payload)

    async def async_stop_speed_test(self) -> None:
        """Cancel a running speed test."""
        await self.async_request("delete", API_SPEED_TEST)

    async def async_get_router_health(self) -> dict[str, Any]:
        """Router health check status and findings."""
        return await self._get(API_ROUTER_HEALTH)

    async def async_start_router_health(self) -> None:
        """Start the router health check (takes a while, poll the status)."""
        await self.async_request("post", API_ROUTER_HEALTH, {})

    async def async_stop_router_health(self) -> None:
        """Stop the router health check."""
        await self.async_request("delete", API_ROUTER_HEALTH)

    # -- Phase 4: service actions (Tier B) ------------------------------------

    async def async_get_ac_service(self) -> dict[str, Any]:
        """Wireless AC service status."""
        return await self._get(API_AC_SERVICE)

    async def async_set_ac_service(self, enabled: bool) -> None:
        """Start or stop the wireless AC service."""
        await self.async_request("post", API_AC_START if enabled else API_AC_STOP, {})

    async def async_restart_dhcp(self) -> None:
        """Restart the DHCP service."""
        await self.async_request("post", API_DHCP_RESTART, {})

    async def async_set_vrrp(self, enabled: bool) -> None:
        """Start or stop VRRP hot standby."""
        await self.async_request(
            "post", API_VRRP_START if enabled else API_VRRP_STOP, {}
        )

    # -- Phase 4: configuration (Tier B) --------------------------------------

    async def async_read_modify_write_config(
        self, path: str, fields: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge `fields` into the current singleton config and PUT it back.

        The official PUT schemas mark nearly every field required (the WEB auth
        config has ~150), so the router's current values must always be echoed
        back. ``None`` values in `fields` are dropped ("keep original").
        """
        current = await self._get(path)
        merged = {k: v for k, v in current.items() if k != "code"}
        for key, value in fields.items():
            if value is None:
                merged.pop(key, None)
            else:
                merged[key] = value
        await self.async_request("put", path, merged)
        return merged

    # -- Phase 4: Phase 4 lists ----------------------------------------------

    async def async_get_terminal_names(self, limit: int = 500) -> list[dict[str, Any]]:
        """Terminal device name annotations (mac -> tagname)."""
        return await self.async_get_rows(API_TERMINAL_NAMES, {"limit": limit})

    async def async_set_terminal_name(
        self, mac: str, tagname: str, comment: str | None = None
    ) -> str:
        """Create or update one terminal name annotation; returns the row id."""
        rows = await self.async_get_terminal_names()
        existing = None
        for row in rows:
            if str(row.get("mac") or "").lower() == mac.lower():
                existing = row
                break
        payload: dict[str, Any] = {"mac": mac, "tagname": tagname}
        if comment is not None:
            payload["comment"] = comment
        if existing is None:
            data = await self.async_request("post", API_TERMINAL_NAMES, payload)
            return data.get("rowid") or (data.get("results") or {}).get("rowid")
        row_id = existing.get("id")
        await self.async_request("put", f"{API_TERMINAL_NAMES}/{row_id}", payload)
        return row_id

    async def async_get_auth_accounts(self, limit: int = 200) -> list[dict[str, Any]]:
        """Authentication user accounts (auth/users)."""
        return await self.async_get_rows(
            API_AUTH_ACCOUNTS, {"limit": limit, "page": 1}
        )

    async def async_get_auth_packages(self, limit: int = 100) -> list[dict[str, Any]]:
        """Authentication packages (auth/packages)."""
        return await self.async_get_rows(
            API_AUTH_PACKAGES, {"limit": limit, "page": 1}
        )

    async def async_get_dhcp6_clients(self, limit: int = 500) -> list[dict[str, Any]]:
        """DHCPv6 client list."""
        return await self.async_get_rows(API_DHCP6_CLIENTS, {"limit": limit})

    async def async_get_ap_config(self) -> list[dict[str, Any]]:
        """Managed AP list with their configuration summary."""
        return await self.async_get_rows(API_AP_CONFIG)

    async def async_set_ap_ssid_quick(
        self,
        ap_id: int,
        radio: str,
        ssid_index: int,
        ssid: str,
        optional: dict[str, Any] | None = None,
    ) -> None:
        """Quick-update one SSID of an AP (APSSIDQuickUpdate schema).

        `optional` may carry key/hide/isolate/vlan/vlan_id/channel/
        channel_width/txpower/enc; the router keeps current values otherwise.
        """
        if radio not in ("2g", "5g"):
            raise ValueError("radio must be '2g' or '5g'")
        if ssid_index not in (1, 2, 3, 4):
            raise ValueError("ssid_index must be 1-4")
        payload: dict[str, Any] = {
            "id": int(ap_id),
            "radio": radio,
            "ssid_index": int(ssid_index),
            "ssid": ssid,
        }
        for key, value in (optional or {}).items():
            if value is not None:
                payload[key] = value
        await self.async_request("put", API_AP_SSID_QUICK, payload)

    async def async_get_wireguard_interfaces(self) -> list[dict[str, Any]]:
        """WireGuard interface rows (empty on devices without WireGuard)."""
        return await self.async_get_rows(API_WIREGUARD)

    async def async_get_wireguard_peers(self, wg_id: Any) -> list[dict[str, Any]]:
        """Tunnel/peer rows of one WireGuard interface."""
        return await self.async_get_rows(f"{API_WIREGUARD}/{wg_id}/peers")
