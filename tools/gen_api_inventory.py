#!/usr/bin/env python3
"""Generate docs/api-inventory.md from the official iKuai API docs site.

The docs site (https://rapi-docs.ikuai8.com/) is a Redoc SPA whose OpenAPI
specs are bundled into a single JS asset, so the endpoint list has to be
scraped out of that bundle.

    python tools/gen_api_inventory.py            # fetch and regenerate
    python tools/gen_api_inventory.py --from FILE  # reuse a downloaded bundle
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

DOCS_URL = "https://rapi-docs.ikuai8.com/"
ASSET_RE = re.compile(r'src="\./(assets/index-[A-Za-z0-9_-]+\.js)"')
PATH_RE = re.compile(r'"/api/v4\.0/([^"]+)":\{')
SUMMARY_RE = re.compile(r'summary:"([^"\\]*(?:\\.[^"\\]*)*)"')
TAGS_RE = re.compile(r"tags:\[([^\]]*)\]")
METHOD_KEYS = ("get", "post", "put", "delete", "patch")


def download_bundle() -> str:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    html = urllib.request.urlopen(DOCS_URL, timeout=30, context=ctx).read().decode()
    match = ASSET_RE.search(html)
    if not match:
        raise SystemExit("could not locate the JS asset in the docs page")
    url = DOCS_URL + match.group(1)
    return urllib.request.urlopen(url, timeout=60, context=ctx).read().decode(
        "utf-8", errors="replace"
    )


def _match_brace(text: str, start: int) -> int:
    """Return the index just past the closing brace of the block at `start`."""
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
    """Extract the `{...}` block following `key:` within [start, end)."""
    match = re.search(rf"\b{key}:\{{", text[start:end])
    if not match:
        return None
    open_idx = start + match.end() - 1
    close_idx = _match_brace(text, open_idx)
    return text[open_idx : min(close_idx, end)]


def parse(bundle: str) -> dict[str, dict[str, Any]]:
    endpoints: dict[str, dict[str, Any]] = {}
    for match in PATH_RE.finditer(bundle):
        path = match.group(1)
        open_idx = match.end() - 1
        close_idx = _match_brace(bundle, open_idx)
        block = bundle[open_idx:close_idx]
        methods: dict[str, dict[str, Any]] = {}
        for method in METHOD_KEYS:
            sub = _block(bundle, method, open_idx, close_idx)
            if sub is None:
                continue
            # only take the block that belongs directly to this path
            summary = SUMMARY_RE.search(sub)
            tags = TAGS_RE.search(sub)
            methods[method] = {
                "summary": summary.group(1) if summary else "",
                "tags": json.loads(f"[{tags.group(1)}]") if tags else [],
            }
        if methods:
            endpoints[path] = methods
    return endpoints


def render(endpoints: dict[str, dict[str, Any]]) -> str:
    groups: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for path, methods in sorted(endpoints.items()):
        for method, info in methods.items():
            tag = (info["tags"] or ["misc"])[0]
            groups[tag].append((path, method.upper(), info["summary"]))

    total = sum(len(v) for v in endpoints.values())
    lines = [
        "# 官方 API 接口清单",
        "",
        f"> 由 `tools/gen_api_inventory.py` 从 <{DOCS_URL}> 自动生成，请勿手工编辑。",
        "",
        f"共 **{len(endpoints)}** 个路径 / **{total}** 个操作，基址 `https://<路由器>/api/v4.0/`。",
        "",
        "图例：🔵 GET（读取） / 🟠 POST 新建 / 🔴 DELETE 删除 / 🟣 PUT 更新 / ⚪ PATCH 启用停用",
        "",
    ]
    read = write = 0
    for tag in sorted(groups):
        entries = groups[tag]
        lines.append(f"## {tag}（{len(entries)}）")
        lines.append("")
        lines.append("| 方法 | 路径 | 说明 |")
        lines.append("|---|---|---|")
        for path, method, summary in sorted(entries, key=lambda e: (e[0], e[1])):
            icon = {"GET": "🔵", "POST": "🟠", "DELETE": "🔴", "PUT": "🟣"}.get(method, "⚪")
            if method == "GET":
                read += 1
            else:
                write += 1
            lines.append(f"| {icon} {method} | `/{path}` | {summary} |")
        lines.append("")
    lines.insert(6, f"其中读取 {read} 个、写入类 {write} 个。")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="src", help="use a previously downloaded JS bundle")
    args = parser.parse_args()

    bundle = Path(args.src).read_text(encoding="utf-8", errors="replace") if args.src else download_bundle()
    endpoints = parse(bundle)
    if not endpoints:
        raise SystemExit("no endpoints parsed - the docs bundle layout may have changed")

    out = Path(__file__).resolve().parent.parent / "docs" / "api-inventory.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(endpoints), encoding="utf-8")
    print(f"wrote {out} ({len(endpoints)} paths)")


if __name__ == "__main__":
    sys.exit(main())
