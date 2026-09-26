#!/usr/bin/env python3
"""
verify_ha.py — 在能连通 Home Assistant 的机器上验证 iKuai 集成是否加载、实体是否注册。

用法（在本机/与 HA 同局域网机器运行，不要从沙箱跑）：
    export HA_URL="http://10.10.10.253:80"         # 前端与 REST API 同在 80 上（已实测）
    export HA_TOKEN="eyJ...你的Long-Lived Token"
    python3 tools/verify_ha.py

说明：
- 脚本只读，不会修改 HA 任何配置。
- 不依赖第三方库，仅用标准库 urllib。
- 令牌只从环境变量读取，绝不写死在脚本里。
"""
import os
import sys
import json
import urllib.request
import urllib.error

HA_URL = (os.environ.get("HA_URL") or "http://10.10.10.253:80").rstrip("/")
HA_TOKEN = os.environ.get("HA_TOKEN") or ""

if not HA_TOKEN:
    print("ERROR: 未设置 HA_TOKEN 环境变量。请先 export HA_TOKEN=...")
    sys.exit(2)


def _get(path):
    url = f"{HA_URL}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {HA_TOKEN}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        ctype = resp.headers.get("Content-Type", "")
        body = resp.read().decode("utf-8", "replace")
        if "application/json" in ctype:
            return resp.status, json.loads(body)
        return resp.status, body


def section(title):
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


ok = True

# 1) 令牌有效性
section("1) 令牌有效性  GET /api/")
try:
    code, data = _get("/api/")
    if isinstance(data, dict) and str(data.get("message", "")).startswith("API running"):
        print(f"  [OK] HTTP {code} — 令牌有效，API 可达")
    else:
        print(f"  [WARN] HTTP {code} — 响应异常: {str(data)[:200]}")
        ok = False
except urllib.error.HTTPError as e:
    print(f"  [FAIL] HTTP {e.code} — 令牌可能被拒（401=无效/权限不足）")
    ok = False
except Exception as e:
    print(f"  [FAIL] 无法连接 {HA_URL}: {e}")
    ok = False

# 2) 集成是否加载
section("2) 集成加载情况  GET /api/config")
try:
    code, data = _get("/api/config")
    if isinstance(data, dict):
        ver = data.get("version")
        comps = data.get("components") or []
        print(f"  HA 版本: {ver}")
        print(f"  已加载组件数: {len(comps)}")
        if "ikuai" in comps:
            print("  [OK] ikuai 已出现在 components 列表 —— 集成加载成功")
        else:
            print("  [FAIL] components 中无 ikuai —— 集成未加载/未安装/加载报错")
            ok = False
    else:
        print(f"  [WARN] 响应非 JSON: {str(data)[:200]}")
except Exception as e:
    print(f"  [FAIL] {e}")
    ok = False

# 3) ikuai 实体清单
section("3) ikuai 实体注册  GET /api/states (过滤 ikuai.)")
try:
    code, data = _get("/api/states")
    if isinstance(data, list):
        ikuai = [s for s in data if s.get("entity_id", "").startswith("ikuai.")]
        if ikuai:
            print(f"  [OK] 共 {len(ikuai)} 个 ikuai 实体：")
            for s in sorted(ikuai, key=lambda x: x["entity_id"]):
                print(f"    - {s['entity_id']:42s} state={s.get('state')}")
        else:
            print("  [WARN] 无 ikuai. 实体 —— 可能集成未配置，或所选资源组为空")
    else:
        print(f"  [WARN] 响应非列表: {str(data)[:200]}")
except Exception as e:
    print(f"  [FAIL] {e}")
    ok = False

# 4) 错误日志
section("4) 错误日志  GET /api/error_log (过滤 ikuai)")
try:
    code, data = _get("/api/error_log")
    text = data if isinstance(data, str) else str(data)
    lines = [ln for ln in text.splitlines() if "ikuai" in ln.lower()]
    if lines:
        print(f"  [WARN] 发现 {len(lines)} 行 ikuai 相关日志：")
        for ln in lines[-40:]:
            print(f"    {ln}")
        ok = False
    else:
        print("  [OK] 错误日志中无 ikuai 相关条目")
except urllib.error.HTTPError as e:
    if e.code == 404:
        print("  [WARN] /api/error_log 在此 HA 版本不可用（404），已跳过")
    else:
        print(f"  [FAIL] HTTP {e.code} — {e}")
        ok = False
except Exception as e:
    print(f"  [FAIL] {e}")
    ok = False

section("结论")
print("  PASS ✅" if ok else "  FAIL ❌（见上方明细；FAIL 多为未安装/未配置所致）")
sys.exit(0 if ok else 1)
