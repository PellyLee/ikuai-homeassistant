import asyncio, os, sys
import aiohttp
from pathlib import Path
ROOT = Path("C:/Users/momol/Documents/agent/iKuai API") / "custom_components" / "ikuai"
import types
pkg = types.ModuleType("ikuai"); pkg.__path__=[str(ROOT)]; sys.modules["ikuai"]=pkg
import importlib.util
def _load(name, fn):
    spec = importlib.util.spec_from_file_location(f"ikuai.{name}", ROOT/fn)
    m = importlib.util.module_from_spec(spec); sys.modules[f"ikuai.{name}"]=m
    spec.loader.exec_module(m); return m
h = _load("ikuai_helpers","helpers.py"); api = _load("ikuai_api","api.py")
res = _load("ikuai_resources","resources.py")

async def main():
    host = h.normalize_host(os.environ["IKUAI_HOST"]); token = os.environ["IKUAI_TOKEN"]
    import ssl
    ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    async with aiohttp.ClientSession() as s:
        client = api.IkuaiApiClient(s, host, token, verify_ssl=False, timeout=8)
        system = await client.async_get_system()
        verinfo = (system.get("sysinfo") or {}).get("verinfo") or {}
        print("verinfo.modelname =", repr(verinfo.get("modelname")))
        print("verinfo.sn        =", repr(verinfo.get("sn")))
        print("verinfo.is_enterprise =", repr(verinfo.get("is_enterprise")))
        print("detect_edition(auto)     =", h.detect_edition(verinfo))
        print("detect_edition(enterprise)=", h.detect_edition(verinfo, "enterprise"))
        print("detect_edition(free)     =", h.detect_edition(verinfo, "free"))
        all_keys = [r.key for r in res.RESOURCES]
        chosen = res.resolve(all_keys)
        free_f = res.filter_by_edition(chosen, "free")
        ent_f = res.filter_by_edition(chosen, "enterprise")
        free_keys = {r.key for r in free_f}
        print("total groups      =", len(chosen))
        print("enterprise_only    =", [r.key for r in chosen if r.enterprise_only])
        print("on free, skipped   =", sorted(set(all_keys)-free_keys))
        print("on enterprise, has ikev2 =", "ikev2_clients" in {r.key for r in ent_f})

asyncio.run(main())
