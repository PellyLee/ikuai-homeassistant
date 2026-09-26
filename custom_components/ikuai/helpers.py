"""Normalization helpers shared by the config flow, the API client and tools.

Two problems are solved here, both found on real devices:

1. Users paste almost anything into the "host" field: `10.10.10.1`,
   `http://10.10.10.1`, `https://10.10.10.1:8443`. https is assumed because
   iKuaiOS 4.x refuses or redirects plain http API calls (behaviour differs
   between firmware versions: 302 on some boxes, 403 on others).
2. Router payloads are not always valid UTF-8. Some clients report binary
   garbage (observed: a switch sending its own MAC bytes) as `hostname`, so a
   strict decode would break the whole payload.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import unquote, urlparse

from .const import DEFAULT_EDITION, DEFAULT_SCHEME, EDITION_ENTERPRISE, EDITION_FREE


def normalize_host(host: str) -> str:
    """Return a scheme+host base URL without a trailing slash or custom path."""
    value = (host or "").strip()
    if not value:
        raise ValueError("empty host")

    if "://" not in value:
        value = f"{DEFAULT_SCHEME}://{value}"

    parsed = urlparse(value)
    if not parsed.hostname:
        raise ValueError(f"invalid host: {host}")

    scheme = parsed.scheme or DEFAULT_SCHEME
    netloc = parsed.netloc or parsed.path
    return f"{scheme}://{netloc}".rstrip("/")


def decode_payload(raw: bytes) -> dict[str, Any]:
    """Decode a possibly malformed router response.

    Steps: replace raw control bytes (illegal inside JSON strings), then decode
    with replacement instead of raising, then parse JSON.
    """
    sanitized = bytes(byte if byte >= 0x20 else 0x20 for byte in raw)
    text = sanitized.decode("utf-8", errors="replace")
    if text.startswith("\ufeff"):
        text = text[1:]
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"unexpected payload: {text[:200]!r}")
    return data


_PLACEHOLDERS = {"unknown", "none", "null", "--", "?", "-", "*"}


def is_printable(value: Any) -> bool:
    """Whether a router-provided string is usable as a display name."""
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text or text.lower() in _PLACEHOLDERS:
        return False
    return "�" not in text and text.isprintable()


def _best_label(value: Any) -> str | None:
    """Return a clean display string, decoding %20-style hostnames."""
    if not is_printable(value):
        return None
    text = str(value).strip()
    if "%" in text:
        try:
            decoded = unquote(text, errors="strict")
        except Exception:  # noqa: BLE001 - malformed escapes, keep the original
            decoded = text
        if is_printable(decoded):
            return decoded
    return text


def client_name(client: dict[str, Any], fallback: str) -> str:
    """Best display name for a client: preferred fields first.

    Some clients report neither a usable hostname nor a comment (binary junk or
    URL-escaped names), in which case the MAC is used.
    """
    for key in ("comment", "termname", "hostname", "client_vendor", "username"):
        label = _best_label(client.get(key))
        if label:
            return label
    return fallback


def row_label(row: dict[str, Any], fields: tuple[str, ...], fallback: str) -> str:
    """Display name for a generic resource row.

    Rule rows are usually unnamed: `comment` is empty and the only stable text
    is the auto-generated `tagname` (e.g. "PM_1"). Fields are tried in the
    order declared by the resource, and `tagname` is only a last resort before
    falling back to `#<id>`.
    """
    for key in fields:
        label = _best_label(row.get(key))
        if label:
            return label
    return fallback


def is_enabled(row: dict[str, Any], field: str = "enabled") -> bool:
    """`enabled` is the string "yes"/"no" - but accept 1/0/True defensively."""
    value = row.get(field)
    if isinstance(value, str):
        return value.strip().lower() in ("yes", "true", "1", "on")
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return False


def detect_edition(verinfo: dict[str, Any] | None, override: str = DEFAULT_EDITION) -> str:
    """Decide whether the router runs free or enterprise iKuaiOS.

    The firmware itself does not expose a single reliable "edition" flag:
    ``is_enterprise`` is 0 on both real devices we tested. The pragmatic signal
    is the hardware identity from ``verinfo`` (only the enterprise appliance
    carries a ``modelname`` and a serial number; the free software build leaves
    both empty). The result can be forced with ``override`` ("free"/"enterprise")
    when auto-detection disagrees with reality.

    Returns :data:`EDITION_FREE` or :data:`EDITION_ENTERPRISE`.
    """
    if override in (EDITION_FREE, EDITION_ENTERPRISE):
        return override
    info = verinfo or {}
    if info.get("is_enterprise") in (1, "1", True, "true"):
        return EDITION_ENTERPRISE
    model = str(info.get("modelname") or "").strip()
    serial = str(info.get("sn") or "").strip()
    if model or serial:
        return EDITION_ENTERPRISE
    return EDITION_FREE


def edition_label(edition: str) -> str:
    """Human readable edition name for diagnostics / the UI."""
    return "企业版" if edition == EDITION_ENTERPRISE else "免费版"
