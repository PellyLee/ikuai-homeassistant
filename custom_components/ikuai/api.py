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
    API_CLIENTS_ONLINE,
    API_INTERFACES_STATUS,
    API_SYSTEM,
    DEFAULT_CLIENT_LIMIT,
    DEFAULT_TIMEOUT,
    DEFAULT_VERIFY_SSL,
)
from .helpers import decode_payload, normalize_host


class IkuaiApiError(Exception):
    """Base error for the iKuai API client."""


class IkuaiApiConnectionError(IkuaiApiError):
    """Cannot connect to the router."""


class IkuaiApiAuthError(IkuaiApiError):
    """Invalid, missing or expired token (HTTP 401/403)."""


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
