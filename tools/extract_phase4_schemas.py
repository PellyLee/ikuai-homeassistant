#!/usr/bin/env python3
"""Extract request/response schema info for ALL Phase 4 (Tier A+B) endpoints.

Outputs docs/api-schemas-phase4.md with, per path+method:
- query/path parameters (name, in, required)
- request body schema: resolved component (required fields + property types)
- response example top-level keys (first level only)

Run:  python tools/extract_phase4_schemas.py [--from FILE]
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import urllib.request
from pathlib import Path

DOCS_URL = "https://rapi-docs.ikuai8.com/"
ASSET_RE = re.compile(r'src="\./(assets/index-[A-Za-z0-9_-]+\.js)"')
PATH_RE = re.compile(r'"/api/v4\.0/([^"]+)":\{')
METHOD_KEYS = ("get", "post", "put", "delete", "patch")

TIER_A = [
    "monitoring/connections", "monitoring/cputemp", "monitoring/disk",
    "monitoring/network", "monitoring/terminals",
    "monitoring/interfaces-config", "monitoring/interfaces-physical",
    "monitoring/interfaces-traffic", "monitoring/interfaces-traffic-v6",
    "monitoring/clients-offline", "monitoring/clients-ip6-online",
    "monitoring/clients-ip6-offline", "monitoring/clients-traffic-summary",
    "monitoring/clients-traffic-load", "monitoring/clients/app-protocols/load",
    "monitoring/clients/protocols", "monitoring/clients/protocols/history-load",
    "monitoring/app-protocols/load", "monitoring/app-protocols/history-load",
    "monitoring/app-protocols/terminal-load", "monitoring/app-traffic-summary",
    "monitoring/protocols", "monitoring/protocols/history-load",
    "monitoring/traffic-audit/accounts", "monitoring/traffic-audit/accounts/applications",
    "monitoring/traffic-audit/accounts/trend", "monitoring/traffic-audit/terminals/applications",
    "monitoring/traffic-audit/terminals/trend",
    "monitoring/wireless-traffic", "monitoring/flow-shunting",
    "monitoring/policy-traffic", "monitoring/aps-channel-noise",
    "monitoring/cameras", "monitoring/switch", "monitoring/downstream",
    "network/dns/stats", "system/cpufreq", "system/disks",
    "advanced-service/speed-test", "monitoring/router-health",
]
TIER_B = [
    "network/pppoe/services", "vpn/pptp/services", "vpn/l2tp/services",
    "vpn/ikev2/services", "vpn/openvpn/services",
    "interfaces/wan-config", "interfaces/wan-config/{id}", "interfaces/wan-lines",
    "interfaces/wan-lines/{id}", "interfaces/wan-vlan-config",
    "interfaces/lan-config", "interfaces/lan-config/{id}", "interfaces/lan-lines",
    "interfaces/lan-lines/{id}", "interfaces/physical",
    "network/dns/config", "network/dhcp/access-control/mode",
    "network/dhcp6/access-control/mode", "network/dhcp6/access-control/rules",
    "network/dhcp6/access-control/rules/{id}", "network/dhcp6/clients",
    "auth/users", "auth/users/{id}", "auth/packages", "auth/packages/{id}",
    "auth/web/services",
    "system/alg", "advanced-service/snmpd-config", "advanced-service/samba-config",
    "advanced-service/ftp-config", "security/advanced/config", "security/mac-mode",
    "system/remote-access", "security/secondary-route/config", "system/kernel-params",
    "system/cpufreq/mode", "system/backup-auto", "system/basic/config",
    "system/vrrp/config", "system/vrrp:start", "system/vrrp:stop",
    "network/ac/services", "network/ac/services:start", "network/ac/services:stop",
    "network/ac/ap-config", "network/ac/ap-config/{id}", "network/ac/ssid-quick",
    "network/ac/ssid-union", "network/dhcp/services:restart",
    "security/terminals", "security/terminals/{id}",
    "vpn/wireguard/{wg_id}/peers", "vpn/wireguard/{wg_id}/peers/{peer_id}",
]
TARGETS = TIER_A + TIER_B


def download_bundle() -> str:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    html = urllib.request.urlopen(DOCS_URL, timeout=30, context=ctx).read().decode()
    match = ASSET_RE.search(html)
    if not match:
        raise SystemExit("could not locate the JS asset in the docs page")
    url = DOCS_URL + match.group(1)
    print(f"# bundle: {match.group(1)}", file=sys.stderr)
    return urllib.request.urlopen(url, timeout=120, context=ctx).read().decode(
        "utf-8", errors="replace"
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


def _block(text: str, key: str, start: int, end: int) -> tuple[int, int] | None:
    """Return (open_idx, close_idx_exclusive) of the {...} after `key:` in range."""
    match = re.search(rf"\b{re.escape(key)}:\{{", text[start:end])
    if not match:
        return None
    open_idx = start + match.end() - 1
    close_idx = _match_brace(text, open_idx)
    return open_idx, close_idx


def parse_components(bundle: str) -> dict[str, str]:
    """Extract named schemas from components:{schemas:{Name:{...},...}}."""
    found = _block(bundle, "schemas", 0, len(bundle))
    if not found:
        return {}
    open_idx, close_idx = found
    schemas: dict[str, str] = {}
    i = open_idx + 1
    name_re = re.compile(r'([A-Za-z0-9_$]+):\{')
    while i < close_idx:
        m = name_re.match(bundle, i)
        if not m:
            i += 1
            continue
        name = m.group(1)
        body_open = m.end() - 1
        body_close = _match_brace(bundle, body_open)
        schemas[name] = bundle[body_open : body_close + 1]
        i = body_close + 1
    return schemas


def summarize_schema(body: str, components: dict[str, str], depth: int = 0) -> str:
    """Render a compact description of a schema block (resolves $ref one level)."""
    ref = re.search(r'\$ref:"#/components/schemas/([^"]+)"', body)
    if ref and ref.group(1) in components:
        return summarize_schema(components[ref.group(1)], components, depth)
    # required list
    req_m = re.search(r'required:\[([^\]]*)\]', body)
    required = [x.strip('"\'') for x in req_m.group(1).split(",") if x.strip()] if req_m else []
    # properties block
    props_found = _block(body, "properties", 0, len(body))
    lines = []
    if required:
        lines.append("required: " + ", ".join(required))
    if props_found:
        p_open, p_close = props_found
        prop_re = re.compile(r'([A-Za-z0-9_$]+):\{')
        i = p_open + 1
        while i < p_close:
            m = prop_re.match(body, i)
            if not m:
                i += 1
                continue
            pname = m.group(1)
            po = m.end() - 1
            pc = _match_brace(body, po)
            pbody = body[po : pc + 1]
            tm = re.search(r'type:"([^"]+)"', pbody)
            ptype = tm.group(1) if tm else ("$ref:" + (re.search(r'\$ref:"#/components/schemas/([^"]+)"', pbody).group(1) if re.search(r'\$ref:"#/components/schemas/([^"]+)"', pbody) else "?"))
            desc = re.search(r'description:"([^"]{0,120})', pbody)
            mark = "*" if pname in required else ""
            d = f" — {desc.group(1)}" if desc else ""
            lines.append(f"  {pname}{mark} ({ptype}){d}")
            i = pc + 1
    return "\n".join(lines) if lines else body[:400]


def method_params(block: str) -> list[str]:
    params: list[str] = []
    pm = re.search(r'parameters:\[', block)
    if not pm:
        return params
    start = pm.end() - 1
    end = _match_brace(block, start)  # matches the closing ] ? brace matcher handles []? no
    # fallback: scan until "requestBody" or end of block
    seg = block[pm.start():]
    for m in re.finditer(r'\{name:"([^"]+)",in:"([^"]+)"(,required:true)?', seg[:4000]):
        req = "*" if m.group(3) else ""
        params.append(f"{m.group(1)}{req} ({m.group(2)})")
    return params


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="src")
    args = parser.parse_args()
    bundle = Path(args.src).read_text(encoding="utf-8", errors="replace") if args.src else download_bundle()

    components = parse_components(bundle)

    blocks: dict[str, dict[str, str]] = {}
    for match in PATH_RE.finditer(bundle):
        path = match.group(1)
        if path not in TARGETS:
            continue
        open_idx = match.end() - 1
        close_idx = _match_brace(bundle, open_idx)
        methods = {}
        for method in METHOD_KEYS:
            found = _block(bundle, method, open_idx, close_idx)
            if found:
                methods[method] = bundle[found[0] : found[1]]
        blocks[path] = methods

    out = ["# Phase 4 端点 schema 摘要", "",
           f"> 自动生成于 tools/extract_phase4_schemas.py；components 共 {len(components)} 个。", ""]
    for path in TARGETS:
        methods = blocks.get(path)
        out.append(f"## /{path}")
        if not methods:
            out.append("（bundle 中未找到）")
            out.append("")
            continue
        for method, block in methods.items():
            out.append(f"### {method.upper()}")
            params = method_params(block)
            if params:
                out.append("parameters: " + "; ".join(params))
            rb = re.search(r'requestBody', block)
            if rb:
                content = _block(block, "schema", rb.start(), len(block))
                if content:
                    out.append("requestBody:")
                    out.append(summarize_schema(block[content[0]:content[1]], components))
            # response example top keys
            ex = re.search(r'example:\{', block)
            if ex:
                eo = ex.end() - 1
                ec = _match_brace(block, eo)
                exbody = block[eo:ec]
                keys = re.findall(r'([A-Za-z0-9_$]+):\{', exbody)[:12]
                out.append(f"example keys: {', '.join(keys)}")
            out.append("")
        out.append("")

    dest = Path(__file__).resolve().parent.parent / "docs" / "api-schemas-phase4.md"
    dest.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {dest} ({len(blocks)}/{len(TARGETS)} targets found)")


if __name__ == "__main__":
    sys.exit(main())
