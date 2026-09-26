#!/usr/bin/env python3
"""Probe an iKuai router without Home Assistant.

Zero credentials are stored in this repository. Provide them through env vars:

    export IKUAI_HOST=10.10.10.1
    export IKUAI_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    export IKUAI_VERIFY_SSL=0        # 1 to validate the self-signed cert
    python tools/dump_api.py         # summary
    python tools/dump_api.py --raw   # dump every raw JSON payload

Useful both for contributors adapting the integration and for bug reports
(pipe the output through a redaction step before sharing it - it contains
MAC addresses and IPs of your LAN).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import ssl
import sys
import types
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load the module files directly: importing them as a package would pull in the
# Home Assistant runtime, which is not available outside HA.
ROOT = Path(__file__).resolve().parent.parent / "custom_components" / "ikuai"


def _load(name: str, filename: str) -> Any:
    # Load through a synthetic "ikuai" package so the module's relative imports
    # resolve without pulling in the Home Assistant runtime.
    pkg = types.ModuleType("ikuai")
    pkg.__path__ = [str(ROOT)]  # type: ignore[attr-defined]
    sys.modules["ikuai"] = pkg
    spec = importlib.util.spec_from_file_location(f"ikuai.{name}", ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[f"ikuai.{name}"] = module
    spec.loader.exec_module(module)
    return module


_const = _load("ikuai_const", "const.py")
_helpers = _load("ikuai_helpers", "helpers.py")

normalize_host = _helpers.normalize_host
decode_payload = _helpers.decode_payload
client_name = _helpers.client_name
API_SYSTEM = _const.API_SYSTEM
API_INTERFACES_STATUS = _const.API_INTERFACES_STATUS
API_CLIENTS_ONLINE = _const.API_CLIENTS_ONLINE
API_DHCP_CLIENTS = _const.API_DHCP_CLIENTS
API_DHCP_STATIC = _const.API_DHCP_STATIC
API_AUTH_USERS = _const.API_AUTH_USERS
API_UPGRADE = _const.API_UPGRADE
API_WIRELESS_STATISTICS = _const.API_WIRELESS_STATISTICS
API_TRAFFIC_AUDIT_TERMINALS = _const.API_TRAFFIC_AUDIT_TERMINALS
API_CPU_HISTORY = _const.API_CPU_HISTORY
API_MEMORY_HISTORY = _const.API_MEMORY_HISTORY

ENDPOINTS = {
    "system": API_SYSTEM,
    "interfaces": API_INTERFACES_STATUS,
    "clients": f"{API_CLIENTS_ONLINE}?limit=256",
    # Phase 1: read-only breadth. Unavailable endpoints are tolerated.
    "dhcp_clients": f"{API_DHCP_CLIENTS}?limit=500",
    "dhcp_static": f"{API_DHCP_STATIC}?limit=500",
    "auth_users": f"{API_AUTH_USERS}?limit=200",
    "upgrade": API_UPGRADE,
    "wireless": API_WIRELESS_STATISTICS,
    "traffic_audit": f"{API_TRAFFIC_AUDIT_TERMINALS}?limit=10",
    "cpu_hour": f"{API_CPU_HISTORY}?datetype=hour&math=avg",
    "memory_hour": f"{API_MEMORY_HISTORY}?datetype=hour&math=avg",
}

# Endpoints that legitimately return 404 on devices without the feature.
OPTIONAL = {"traffic_audit", "wireless", "dhcp_static", "auth_users"}


def build_opener(verify_ssl: bool) -> urllib.request.OpenerDirector:
    if verify_ssl:
        return urllib.request.build_opener()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))


def fetch(
    opener: urllib.request.OpenerDirector,
    url: str,
    token: str,
    optional: bool = False,
) -> Any:
    request = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}
    )
    try:
        with opener.open(request, timeout=15) as response:
            if response.status == 401:
                raise SystemExit("401 Unauthorized - the token is invalid or expired")
            if response.status == 403:
                raise SystemExit(
                    "403 Forbidden - enable the API switch on the router, "
                    "or use https instead of http"
                )
            # decode_payload tolerates the malformed hostnames some clients send
            return decode_payload(response.read())
    except urllib.error.HTTPError as err:
        if optional and err.code == 404:
            print(f"  (optional endpoint missing: {url})")
            return {}
        raise SystemExit(f"HTTP {err.code} for {url}") from err
    except (urllib.error.URLError, TimeoutError) as err:
        raise SystemExit(
            f"Cannot reach {url}: {err}\n"
            "Check the address (https is enforced by iKuaiOS 4.x) and reachability."
        ) from err


def to_float(value: Any) -> float | None:
    try:
        return float(str(value).rstrip("%"))
    except (TypeError, ValueError):
        return None


def first(value: Any) -> Any:
    return value[0] if isinstance(value, (list, tuple)) and value else value


def summarize(payloads: dict[str, Any]) -> None:
    sysinfo = (payloads["system"].get("results") or {}).get("sysinfo", {})
    memory = sysinfo.get("memory") or {}
    stream = sysinfo.get("stream") or {}
    online = sysinfo.get("online_user") or {}

    print("== system")
    print(f"  hostname        : {sysinfo.get('hostname')}")
    print(f"  version         : {(sysinfo.get('verinfo') or {}).get('version')}")
    print(f"  cpu             : {first(sysinfo.get('cpu'))}")
    print(f"  cputemp         : {first(sysinfo.get('cputemp')) or '(no sensor)'}")
    print(f"  memory used     : {memory.get('used')}")
    if memory.get("total") and memory.get("available") is not None:
        print(f"  memory used MiB : {round((memory['total'] - memory['available']) / 1024, 1)}")
    print(f"  connections     : {stream.get('connect_num')} (tcp {stream.get('tcp_connect_num')}, udp {stream.get('udp_connect_num')})")
    print(f"  online clients  : {online.get('count')}")
    print(f"  up/down rate    : {stream.get('upload')} / {stream.get('download')} B/s")
    print(f"  uptime          : {sysinfo.get('uptime')} s")

    print("== interfaces")
    checks = (payloads["interfaces"].get("results") or {}).get("iface_check") or []
    for line in checks:
        print(f"  {line.get('interface')}: {line.get('ip_addr')} -> {line.get('result')} ({line.get('errmsg')})")
    streams = (payloads["interfaces"].get("results") or {}).get("iface_stream") or []
    wan = [line for line in streams if str(line.get("interface", "")).startswith("wan")]
    for line in wan:
        print(f"  {line.get('interface')}: up {line.get('upload')} B/s, down {line.get('download')} B/s")

    print("== clients")
    clients = (payloads["clients"].get("results") or {}).get("data") or []
    print(f"  {len(clients)} online")
    for client in clients:
        name = client_name(client, client.get("mac") or "?")
        print(f"  - {name} / {client.get('ip_addr')} / {client.get('mac')} / ssid={client.get('ssid') or '-'}")

    # --- Phase 1: read-only breadth -------------------------------------
    print("== dhcp / auth")
    leases = (payloads["dhcp_clients"].get("results") or {}).get("data") or []
    static = (payloads["dhcp_static"].get("results") or {}).get("static_data")
    if static is None:
        static = (payloads["dhcp_static"].get("results") or {}).get("data") or []
    auth = (payloads["auth_users"].get("results") or {}).get("data") or []
    print(f"  dhcp leases     : {len(leases) or '(none)'}")
    print(f"  static bindings : {len(static) or '(none)'}")
    print(f"  auth users      : {len(auth) or '(none)'}")

    print("== firmware")
    upgrade = (payloads["upgrade"].get("results") or {}).get("data") or {}
    current = upgrade.get("system_ver")
    offered = upgrade.get("new_system_ver")
    state = "unknown"
    if current and offered:
        state = "update available" if offered != current else "up to date"
    print(f"  installed       : {current}")
    print(f"  offered         : {offered}")
    print(f"  state           : {state}")

    print("== wireless")
    wireless = payloads["wireless"].get("results") or {}
    ap = wireless.get("ap_status") or {}
    clt = wireless.get("clt_status") or {}
    print(f"  ap              : {ap.get('ap_count', '-')} total, {ap.get('ap_online', '-')} online")
    print(f"  clients         : {clt.get('clt_count', '-')} (2.4G {clt.get('clt_count_2g', '-')}, 5G {clt.get('clt_count_5g', '-')})")

    print("== traffic audit (optional)")
    audit = payloads["traffic_audit"].get("results") or {}
    terminals = audit.get("daytime") or audit.get("data") or []
    if terminals:
        top = max(
            terminals,
            key=lambda t: (t.get("sum_total_down") or 0) + (t.get("sum_total_up") or 0),
        )
        print(f"  top terminal    : {client_name(top, top.get('mac') or '?')} "
              f"(up {top.get('sum_total_up')}, down {top.get('sum_total_down')})")
    else:
        print("  (not available)")

    print("== hourly averages")
    for key, field, unit in (("cpu_hour", "cpu", "cpu"), ("memory_hour", "memory", "memory_use")):
        series = (payloads[key].get("results") or {}).get(field) or []
        values = [to_float(item.get(unit)) for item in series if isinstance(item, dict)]
        values = [v for v in values if v is not None]
        avg = round(sum(values) / len(values), 1) if values else None
        print(f"  {key:<12} : {avg if avg is not None else '(no data)'}")

    print("\nNote: this output contains private LAN details - redact before sharing.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", action="store_true", help="dump raw JSON payloads")
    args = parser.parse_args()

    host = os.environ.get("IKUAI_HOST")
    token = os.environ.get("IKUAI_TOKEN")
    if not host or not token:
        raise SystemExit(
            "Set IKUAI_HOST and IKUAI_TOKEN first, e.g.\n"
            "  IKUAI_HOST=10.10.10.1 IKUAI_TOKEN=xxxx python tools/dump_api.py"
        )

    verify_ssl = os.environ.get("IKUAI_VERIFY_SSL", "0") in ("1", "true", "yes")
    base = normalize_host(host)
    opener = build_opener(verify_ssl)

    payloads: dict[str, Any] = {}
    for key, path in ENDPOINTS.items():
        payloads[key] = fetch(
            opener, f"{base}/api/v4.0/{path}", token, optional=key in OPTIONAL
        )

    if args.raw:
        print(json.dumps(payloads, ensure_ascii=False, indent=2))
        return
    summarize(payloads)


if __name__ == "__main__":
    main()
