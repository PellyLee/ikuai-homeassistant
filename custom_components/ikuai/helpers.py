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

from .const import DEFAULT_SCHEME


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
