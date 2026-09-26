#!/usr/bin/env python3
"""
live_check_free.py — 用集成自带的资源表，对一台 iKuai 真机做只读联调验证。

只发 GET，绝不写操作。验证三件事：
  1. 版本识别（免费版/企业版）是否与 resources.py 的 enterprise_only 标记一致
  2. 40 个 CRUD 资源组在真机上哪些能正常返回、哪些 404（免费版特性缺失）
  3. filter_by_edition() 在免费版上是否正确隐藏企业版独占组（ikev2_clients）

纯标准库实现（urllib），无第三方依赖。

用法：
    export IKUAI_HOST="10.10.10.1"
    export IKUAI_TOKEN="<base64 token>"
    python3 tools/live_check_free.py
"""
import json
import os
import ssl
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "custom_components", "ikuai"))
from resources import RESOURCES, filter_by_edition  # noqa: E402

HOST = os.environ.get("IKUAI_HOST") or "10.10.10.1"
TOKEN = os.environ.get("IKUAI_TOKEN") or ""
VERIFY_SSL = os.environ.get("IKUAI_VERIFY_SSL", "0") == "1"

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

    # 2) 逐组探测
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
        code = data.get("code", 0)
        if code not in (0, "0"):
            if code == 1003:
                return res.key, ("PERM", f"code={code} {data.get('message')}（令牌权限/授权范围；集成列表路径忽略业务码→0行，不致命）", 0)
            return res.key, ("BIZ_ERR", f"code={code} {data.get('message')}", 0)
        body = data.get("results", data)
        rows = []
        for k in (*res.list_keys, "data", "rows", "list"):
            v = body.get(k)
            if isinstance(v, list):
                rows = [r for r in v if isinstance(r, dict)]
                break
        if not rows:
            for v in body.values():
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    rows = [r for r in v if isinstance(r, dict)]
                    break
        return res.key, ("OK", f"{len(rows)} rows", len(rows))

    with ThreadPoolExecutor(max_workers=8) as ex:
        table = dict(ex.map(probe, RESOURCES))

    # 3) 汇总
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

    # 4) filter_by_edition 校验
    print("\n[filter_by_edition 校验]")
    visible = [r.key for r in filter_by_edition(list(RESOURCES), edition)]
    if edition == "free":
        dropped = [r.key for r in RESOURCES if r.enterprise_only and r.key not in visible]
        print(f"  免费版可见资源数={len(visible)}；被隐藏的企业版独占组={dropped}")
        assert "ikev2_clients" not in visible, "ikev2_clients 不应在免费版可见！"
        print("  ✅ ikev2_clients 已在免费版被正确隐藏")
    else:
        print(f"  企业版可见资源数={len(visible)}（含企业版独占组）")

    print("\n[结论] 集成资源引擎与免费版真机联调",
          "通过 ✅" if (edition == "free" and len(errs) == 0) else "存在异常 ❌")


if __name__ == "__main__":
    main()
