#!/usr/bin/env python3
"""Extract request-body schemas for Phase 3 target endpoints from the docs bundle.

Dumps the raw minified method blocks (post/put/delete + get example) so the
payload field names can be read out manually. Output is trimmed per block.
"""

from __future__ import annotations

import re
import ssl
import sys
import urllib.request

DOCS_URL = "https://rapi-docs.ikuai8.com/"
ASSET_RE = re.compile(r'src="\./(assets/index-[A-Za-z0-9_-]+\.js)"')
PATH_RE = re.compile(r'"/api/v4\.0/([^"]+)":\{')
METHOD_KEYS = ("get", "post", "put", "delete", "patch")
TRIM = 2600

TARGETS = (
    "security/mac-rules",
    "security/acl-rules",
    "object-mac",
    "object-time",
    "object-ip",
    "wireless/access-control/rules",
    "monitoring/ssid-clients",
    "monitoring/channel-clients",
    "monitoring/wireless-score",
)


def _match_brace(text: str, start: int) -> int:
    depth = 0
    in_string = False
    escape = False
    quote = ""
    for i in range(start, len(text)):
        char = text[i]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                in_string = False
            continue
        if char in "\"'`":
            in_string = True
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(text)


def _block(text: str, key: str, start: int, end: int) -> str | None:
    match = re.search(rf"\b{key}:\{{", text[start:end])
    if not match:
        return None
    open_idx = start + match.end() - 1
    close_idx = _match_brace(text, open_idx)
    return text[open_idx : min(close_idx, end)]


def download_bundle() -> str:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    html = urllib.request.urlopen(DOCS_URL, timeout=30, context=ctx).read().decode()
    match = ASSET_RE.search(html)
    if not match:
        raise SystemExit("could not locate the JS asset in the docs page")
    url = DOCS_URL + match.group(1)
    print(f"# bundle: {match.group(1)}")
    return urllib.request.urlopen(url, timeout=60, context=ctx).read().decode(
        "utf-8", errors="replace"
    )


def main() -> None:
    bundle = download_bundle()
    blocks: dict[str, dict[str, str]] = {}
    for match in PATH_RE.finditer(bundle):
        path = match.group(1)
        if path not in TARGETS:
            continue
        open_idx = match.end() - 1
        close_idx = _match_brace(bundle, open_idx)
        methods = {}
        for method in METHOD_KEYS:
            sub = _block(bundle, method, open_idx, close_idx)
            if sub is not None:
                methods[method] = sub
        blocks[path] = methods

    if not blocks:
        raise SystemExit("none of the target paths were found in the bundle")

    for path in TARGETS:
        methods = blocks.get(path)
        if not methods:
            print(f"\n{'=' * 70}\n!! {path} — NOT FOUND in bundle\n")
            continue
        for method, sub in methods.items():
            if method == "get":
                # 只关心响应示例，抓 example 关键字附近
                idx = sub.find("example")
                snippet = sub[idx : idx + TRIM] if idx != -1 else sub[:TRIM]
            else:
                idx = sub.find("requestBody")
                snippet = sub[idx : idx + TRIM] if idx != -1 else sub[:TRIM]
            print(f"\n{'=' * 70}\n== {method.upper()} /{path}\n{snippet}")


if __name__ == "__main__":
    sys.exit(main())
