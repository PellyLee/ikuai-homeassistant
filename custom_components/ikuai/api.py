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
    API_AUTH_USERS,
    API_CLIENTS_ONLINE,
    API_CPU_HISTORY,
    API_DHCP_CLIENTS,
    API_DHCP_STATIC,
    API_INTERFACES_STATUS,
    API_MEMORY_HISTORY,
    API_SYSTEM,
    API_TRAFFIC_AUDIT_TERMINALS,
    API_UPGRADE,
    API_WIRELESS_STATISTICS,
    DEFAULT_CLIENT_LIMIT,
    DEFAULT_TIMEOUT,
    DEFAULT_VERIFY_SSL,
)
from .helpers import decode_payload, normalize_host


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

    async def _get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = f"{self._base_url}/api/v4.0/{path}"
        try:
            async with self._session.get(
                url,
                params=params,
                headers=self._headers,
                timeout=self._timeout,
                ssl=self._ssl,
                allow_redirects=True,
            ) as resp:
                if resp.status in (401, 403):
                    raise IkuaiApiAuthError(f"Token rejected ({resp.status}) by {url}")
                if resp.status == 404:
                    raise IkuaiApiNotFoundError(f"{url} is not available on this device")
                if resp.status != 200:
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

        results = data.get("results", data)
        return results if isinstance(results, dict) else {"data": results}

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
