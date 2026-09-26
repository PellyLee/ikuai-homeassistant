#!/usr/bin/env python3
"""
live_check_free.py — 用集成自带的资源表，对一台 iKuai 真机做只读联调验证。

只发 GET，绝不写操作。验证五件事：
  1. 版本识别（免费版/企业版）是否与 resources.py 的 enterprise_only 标记一致
  2. 43 个 CRUD 资源组在真机上哪些能正常返回、哪些 404（免费版特性缺失）
  3. Phase 4 扩展监控（QUERY_PATHS，~58 个 GET 端点）的真机可用性
  4. 22 个单例配置（CONFIG_RESOURCES）GET 可读性
  5. filter_by_edition() / filter_configs_by_edition() 在免费版上是否正确隐藏企业版独占组

纯标准库实现（urllib），无第三方依赖。

用法：
    export IKUAI_HOST="10.10.10.1"
    export IKUAI_TOKEN="<base64 token>"
    python3 tools/live_check_free.py
"""
import importlib
import json
import os
import ssl
import sys
import time
import types
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PKG_DIR = os.path.join(ROOT, "custom_components", "ikuai")

# Register a lightweight stand-in package so `resources.py`'s relative
# `from .const import ...` resolves WITHOUT executing the integration's
# real __init__.py (which imports homeassistant, unavailable on a PC).
_pkg = types.ModuleType("ikuai")
_pkg.__path__ = [PKG_DIR]
sys.modules["ikuai"] = _pkg
QUERY_PATHS = None  # populated below; keeps linters quiet about import order
_resources = importlib.import_module("ikuai.resources")
QUERY_PATHS = _resources.QUERY_PATHS
CONFIG_RESOURCES = _resources.CONFIG_RESOURCES
RESOURCES = _resources.RESOURCES
filter_by_edition = _resources.filter_by_edition
filter_configs_by_edition = _resources.filter_configs_by_edition

HOST = os.environ.get("IKUAI_HOST") or "10.10.10.1"
TOKEN = os.environ.get("IKUAI_TOKEN") or ""
VERIFY_SSL = os.environ.get("IKUAI_VERIFY_SSL", "0") == "1"

# datetype 系列监控历史（需 datetype/math 参数才返回有效数据）
SERIES_PATHS = {
    "monitoring/connections",
    "monitoring/cputemp",
    "monitoring/disk",
    "monitoring/network",
    "monitoring/terminals",
}

def _make_ctx():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


CTX = ssl.create_default_context() if VERIFY_SSL else _make_ctx()


def detect_edition(verinfo, override=None):
    if override in ("free", "enterprise"):
        return override
    if verinfo and (verinfo.get("modelname") or verinfo.get("sn")):
        return "enterprise"
    return "free"


def decode(raw: bytes) -> dict:
    return json.loads(raw.decode("utf-8", "replace"))


def get(path, params=None):
    url = f"https://{HOST}/api/v4.0/{path}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15, context=CTX) as resp:
        return resp.status, resp.read()


def _classify(data, res=None):
    """Shared business-code / row-count classification for a 200 response."""
    code = data.get("code", 0)
    if code not in (0, "0"):
        if code == 1003:
            return "PERM", f"code={code} {data.get('message')}（令牌权限/授权范围；集成列表路径忽略业务码→0行，不致命）", 0
        return "BIZ_ERR", f"code={code} {data.get('message')}", 0
    body = data.get("results", data)
    rows = []
    list_keys = (*res.list_keys, "data", "rows", "list") if res else ("data", "rows", "list")
    for k in list_keys:
        v = body.get(k)
        if isinstance(v, list):
            rows = [r for r in v if isinstance(r, dict)]
            break
    if not rows:
        for v in body.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                rows = [r for r in v if isinstance(r, dict)]
                break
    n = len(rows)
    extra = f" keys={sorted(body)[:6]}" if not n and isinstance(body, dict) else ""
    return "OK", (f"{n} rows" if n else "OK(标量/空)") + extra, n


def probe_query(item):
    """Probe one QUERY_PATHS entry (key, path). Retries with series params."""
    key, path = item
    attempts = [None]
    if path in SERIES_PATHS:
        attempts = [None, {"datetype": "hour", "math": "avg"}]
    last = None
    for params in attempts:
        try:
            status, raw = get(path, params=params)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return key, ("404", "not available on this device", 0)
            if e.code in (401, 403):
                return key, ("AUTH", f"HTTP {e.code}", 0)
            return key, ("HTTP_ERR", f"HTTP {e.code}", 0)
        except Exception as e:
            return key, ("ERROR", str(e)[:80], 0)
        if status >= 400:
            return key, ("HTTP_ERR", f"HTTP {status}", 0)
        try:
            data = decode(raw)
        except Exception:
            return key, ("BADJSON", "decode fail", 0)
        state, msg, n = _classify(data)
        last = (state, msg, n)
        if state == "OK":
            return key, last
        # series path with BIZ_ERR → retry with datetype params
    return key, last


def probe_config(res):
    """Probe one singleton config GET (CONFIG_RESOURCES entry)."""
    try:
        status, raw = get(res.path)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return res.key, ("404", "not available on this device", 0)
        if e.code in (401, 403):
            return res.key, ("AUTH", f"HTTP {e.code}", 0)
        return res.key, ("HTTP_ERR", f"HTTP {e.code}", 0)
    except Exception as e:
        return res.key, ("ERROR", str(e)[:80], 0)
    if status >= 400:
        return res.key, ("HTTP_ERR", f"HTTP {status}", 0)
    try:
        data = decode(raw)
    except Exception:
        return res.key, ("BADJSON", "decode fail", 0)
    code = data.get("code", 0)
    if code not in (0, "0"):
        if code == 1003:
            return res.key, ("PERM", f"code={code} {data.get('message')}", 0)
        return res.key, ("BIZ_ERR", f"code={code} {data.get('message')}", 0)
    body = data.get("results", data)
    n = len(body) if isinstance(body, dict) else 0
    return res.key, ("OK", f"{n} fields", n)


def main():
    if not TOKEN:
        print("ERROR: 未设置 IKUAI_TOKEN"); sys.exit(2)

    # 1) 版本识别
    status, raw = get("monitoring/system")
    verinfo, edition = {}, "unknown"
    if status == 200:
        try:
            data = decode(raw)
            verinfo = (data.get("results") or data).get("sysinfo", {}).get("verinfo", {})
            edition = detect_edition(verinfo)
        except Exception as e:
            print("  解析 monitoring/system 失败:", e)
    print(f"[版本识别] monitoring/system HTTP={status}  edition={edition}")
    print(f"  verinfo={json.dumps(verinfo, ensure_ascii=False)}")

    # 2) CRUD 资源组探测
    def probe(res):
        try:
            status, raw = get(res.path, params={"limit": 200})
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return res.key, ("404", "not available on this device", 0)
            if e.code in (401, 403):
                return res.key, ("AUTH", f"HTTP {e.code}", 0)
            return res.key, ("HTTP_ERR", f"HTTP {e.code}", 0)
        except Exception as e:
            return res.key, ("ERROR", str(e)[:80], 0)
        if status >= 400:
            return res.key, ("HTTP_ERR", f"HTTP {status}", 0)
        try:
            data = decode(raw)
        except Exception:
            return res.key, ("BADJSON", "decode fail", 0)
        state, msg, n = _classify(data, res)
        return res.key, (state, msg, n)

    with ThreadPoolExecutor(max_workers=8) as ex:
        table = dict(ex.map(probe, RESOURCES))

    print("\n[资源组探测]")
    ok = [k for k, (s, _, _) in table.items() if s == "OK"]
    n404 = [k for k, (s, _, _) in table.items() if s == "404"]
    nperm = [k for k, (s, _, _) in table.items() if s == "PERM"]
    errs = [(k, s, m) for k, (s, m, _) in table.items() if s not in ("OK", "404", "PERM")]
    for r in RESOURCES:
        s, m, _ = table[r.key]
        tag = "  " if s == "OK" else ("!!" if s in ("404", "PERM") else "XX")
        print(f"  {tag} {r.key:22s} {s:8s} {m}  {'(企业版独占)' if r.enterprise_only else ''}")
    print(f"\n[统计] OK={len(ok)}  404(免费版无此功能)={len(n404)}  权限受限(PERM,不致命)={len(nperm)}  致命错误={len(errs)}")
    if errs:
        print("  错误明细:")
        for k, s, m in errs:
            print(f"    - {k}: {s} {m}")

    # 3) Phase 4 扩展监控（QUERY_PATHS，剔除 CONFIG_RESOURCES 已覆盖的 key）
    config_keys = {res.key for res in CONFIG_RESOURCES}
    query_items = [(k, p) for k, p in QUERY_PATHS.items() if k not in config_keys]
    with ThreadPoolExecutor(max_workers=8) as ex:
        qtable = dict(ex.map(probe_query, query_items))

    print(f"\n[Phase 4 扩展监控探测] 共 {len(qtable)} 个 GET 端点")
    qok = [k for k, (s, _, _) in qtable.items() if s == "OK"]
    q404 = [k for k, (s, _, _) in qtable.items() if s == "404"]
    qperm = [k for k, (s, _, _) in qtable.items() if s == "PERM"]
    qerrs = [(k, s, m) for k, (s, m, _) in qtable.items() if s not in ("OK", "404", "PERM")]
    for k in QUERY_PATHS:
        if k in config_keys:
            continue
        s, m, _ = qtable[k]
        tag = "  " if s == "OK" else ("!!" if s in ("404", "PERM") else "XX")
        print(f"  {tag} {k:24s} {s:8s} {m}")
    print(f"[统计] OK={len(qok)}  404={len(q404)}  PERM={len(qperm)}  其它={len(qerrs)}")
    if q404:
        print(f"  免费版缺失(将产生 0 行/空实体，由 edition 过滤或容错吸收): {q404}")
    if qerrs:
        print("  错误明细:")
        for k, s, m in qerrs:
            print(f"    - {k}: {s} {m}")

    # 4) 单例配置 GET 探测
    with ThreadPoolExecutor(max_workers=8) as ex:
        ctable = dict(ex.map(probe_config, CONFIG_RESOURCES))

    print(f"\n[单例配置探测] 共 {len(ctable)} 个")
    cok = [k for k, (s, _, _) in ctable.items() if s == "OK"]
    c404 = [k for k, (s, _, _) in ctable.items() if s == "404"]
    for res in CONFIG_RESOURCES:
        s, m, _ = ctable[res.key]
        tag = "  " if s == "OK" else ("!!" if s == "404" else "XX")
        print(f"  {tag} {res.key:22s} {s:8s} {m}  {'(dangerous)' if res.dangerous else ''}")
    print(f"[统计] OK={len(cok)}  404={len(c404)}  其它={len(ctable) - len(cok) - len(c404)}")

    # 5) filter_by_edition / filter_configs_by_edition 校验
    print("\n[filter_by_edition 校验]")
    visible = [r.key for r in filter_by_edition(list(RESOURCES), edition)]
    if edition == "free":
        dropped = [r.key for r in RESOURCES if r.enterprise_only and r.key not in visible]
        print(f"  免费版可见资源数={len(visible)}；被隐藏的企业版独占组={dropped}")
        assert "ikev2_clients" not in visible, "ikev2_clients 不应在免费版可见！"
        print("  ✅ ikev2_clients 已在免费版被正确隐藏")
    else:
        print(f"  企业版可见资源数={len(visible)}（含企业版独占组）")

    cvisible = [r.key for r in filter_configs_by_edition(list(CONFIG_RESOURCES), edition)]
    cdrop = [r.key for r in CONFIG_RESOURCES if r.enterprise_only and r.key not in cvisible]
    print(f"  单例配置可见数={len(cvisible)}；被隐藏的企业版独占配置={cdrop or '无'}")

    fatal = len(errs) + len(qerrs) + sum(
        1 for s, _, _ in ctable.values() if s not in ("OK", "404", "PERM"))
    print("\n[结论] 集成资源引擎与免费版真机联调",
          "通过 ✅" if (edition == "free" and fatal == 0) else "存在异常 ❌")
    print("  说明：404=免费版无此功能（集成侧应隐藏/0行），PERM=令牌权限不足（列表忽略，不致命），"
          "BIZ_ERR/AUTH/HTTP_ERR 需要人工排查。")


if __name__ == "__main__":
    main()
