"""Phase 3 scenario services: terminal blocking and parental control.

All services are write operations, so they refuse to run unless the user has
enabled `enable_write` for their config entry. Rules created here carry a
`HA集成` comment marker so `allow_terminal` / `clear_parental_control` can find
them again regardless of what the user typed as the display name.

Payload shapes were taken from the official docs bundle (Redoc):

* POST /security/mac-rules requires {mac, enabled, tagname, expires}
  where `expires` is a unix timestamp (0 = never) and `tagname` is 1-15 chars.
* POST /security/acl-rules accepts inline targets via
  `src_addr.custom: ["<ip>|<mac>"]` and inline time templates via
  `time.custom: [{type: "weekly", weekdays: "12345", start_time, end_time}]`,
  so neither MAC nor time *objects* are required for these scenarios.
"""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import AddressValueError, IPv4Address
import time as time_module
from typing import Any

import voluptuous as vol

from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .api import IkuaiApiClient, IkuaiApiError
from .const import (
    API_ACL_RULES,
    API_MAC_RULES,
    BLOCK_MARKER,
    CONF_ENABLE_WRITE,
    DEFAULT_ENABLE_WRITE,
    DOMAIN,
    PARENTAL_MARKER,
    SERVICE_AC_SERVICE,
    SERVICE_ALLOW_TERMINAL,
    SERVICE_API_REQUEST,
    SERVICE_BLOCK_TERMINAL,
    SERVICE_CLEAR_PARENTAL_CONTROL,
    SERVICE_PARENTAL_CONTROL,
    SERVICE_QUERY,
    SERVICE_RESTART_DHCP,
    SERVICE_ROUTER_HEALTH,
    SERVICE_SET_CONFIG,
    SERVICE_SET_SSID,
    SERVICE_SET_TERMINAL_NAME,
    SERVICE_SPEED_TEST,
)
from .helpers import (
    clamp_tagname,
    mac_for_router,
    normalize_mac,
    valid_hhmm,
)
from .resources import (
    CONFIG_BY_KEY,
    QUERY_PATHS,
    RESOURCE_BY_KEY,
    query_path_allowed,
    write_path_allowed,
)

ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_MAC = "mac"
ATTR_NAME = "name"
ATTR_EXPIRES_HOURS = "expires_hours"
ATTR_TARGET = "target"
ATTR_WEEKDAYS = "weekdays"
ATTR_START_TIME = "start_time"
ATTR_END_TIME = "end_time"

# Phase 4 service fields.
ATTR_RESOURCE = "resource"
ATTR_PARAMS = "params"
ATTR_KEY = "key"
ATTR_FIELDS = "fields"
ATTR_CONFIRM = "confirm"
ATTR_ACTION = "action"
ATTR_INTERFACE = "interface"
ATTR_METHOD = "method"
ATTR_PATH = "path"
ATTR_PAYLOAD = "payload"
ATTR_COMMENT = "comment"
ATTR_AP_ID = "ap_id"
ATTR_RADIO = "radio"
ATTR_SSID_INDEX = "ssid_index"
ATTR_SSID = "ssid"
ATTR_SSID_OPTIONAL_KEYS = (
    "enc", "key", "hide", "isolate", "vlan", "vlan_id",
    "channel", "channel_width", "txpower",
)

_ACTIONS = ("start", "stop", "status")

_MAC_RULES = RESOURCE_BY_KEY["mac_rules"]
_ACL_RULES = RESOURCE_BY_KEY["acl_rules"]

_BLOCK_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MAC): cv.string,
        vol.Optional(ATTR_NAME): cv.string,
        vol.Optional(ATTR_EXPIRES_HOURS): vol.All(
            vol.Coerce(float), vol.Range(min=0.1, max=8760)
        ),
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
    }
)

_ALLOW_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_MAC): cv.string,
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
    }
)

_PARENTAL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TARGET): cv.string,
        vol.Required(ATTR_WEEKDAYS): cv.string,
        vol.Required(ATTR_START_TIME): cv.string,
        vol.Required(ATTR_END_TIME): cv.string,
        vol.Optional(ATTR_NAME): cv.string,
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
    }
)

_CLEAR_PARENTAL_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_NAME): cv.string,
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
    }
)

# -- Phase 4 schemas ---------------------------------------------------------

_QUERY_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_RESOURCE): cv.string,
        vol.Optional(ATTR_PARAMS): dict,
    }
)

_SET_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_KEY): vol.In(CONFIG_BY_KEY),
        vol.Required(ATTR_FIELDS): dict,
        vol.Optional(ATTR_CONFIRM, default=False): cv.boolean,
    }
)

_ACTION_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_ACTION): vol.In(_ACTIONS),
        vol.Optional(ATTR_INTERFACE): cv.string,
    }
)

_RESTART_DHCP_SCHEMA = vol.Schema(
    {vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string}
)

_SET_TERMINAL_NAME_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_MAC): cv.string,
        vol.Required(ATTR_NAME): cv.string,
        vol.Optional(ATTR_COMMENT): cv.string,
    }
)

_SET_SSID_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_AP_ID): vol.Coerce(int),
        vol.Required(ATTR_RADIO): vol.In(("2g", "5g")),
        vol.Required(ATTR_SSID_INDEX): vol.All(vol.Coerce(int), vol.Range(min=1, max=4)),
        vol.Required(ATTR_SSID): cv.string,
        **{
            vol.Optional(key): vol.Any(cv.string, cv.boolean, vol.Coerce(int))
            for key in ATTR_SSID_OPTIONAL_KEYS
        },
    }
)

_API_REQUEST_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_METHOD): vol.In(("get", "put", "post", "delete", "patch")),
        vol.Required(ATTR_PATH): cv.string,
        vol.Optional(ATTR_PARAMS): dict,
        vol.Optional(ATTR_PAYLOAD): dict,
    }
)


@dataclass
class _Runtime:
    """One config entry's client plus its write permission flag."""

    entry_id: str
    client: IkuaiApiClient
    write_enabled: bool
    name: str


def _runtimes(hass: HomeAssistant) -> list[_Runtime]:
    runtimes: list[_Runtime] = []
    for entry_id, runtime in (hass.data.get(DOMAIN) or {}).items():
        entry = runtime.entry
        merged = {**entry.data, **entry.options}
        runtimes.append(
            _Runtime(
                entry_id=entry_id,
                client=runtime.main.client,
                write_enabled=bool(
                    merged.get(CONF_ENABLE_WRITE, DEFAULT_ENABLE_WRITE)
                ),
                name=entry.title if entry else entry_id,
            )
        )
    return runtimes


def _pick(
    call: ServiceCall, hass: HomeAssistant, require_write: bool = True
) -> _Runtime:
    """Resolve the config entry the service call targets (default: the only one)."""
    wanted = call.data.get(ATTR_CONFIG_ENTRY_ID)
    runtimes = _runtimes(hass)
    if wanted:
        for runtime in runtimes:
            if runtime.entry_id == wanted:
                chosen = runtime
                break
        else:
            raise HomeAssistantError("未找到指定的 iKuai 配置条目")
    elif len(runtimes) == 1:
        chosen = runtimes[0]
    elif len(runtimes) > 1:
        raise HomeAssistantError(
            "存在多个 iKuai 配置条目，请在服务数据中指定 config_entry_id"
        )
    else:
        raise HomeAssistantError("尚未配置 iKuai 集成")
    if require_write and not chosen.write_enabled:
        raise HomeAssistantError(
            f"「{chosen.name}」未启用写操作：请先在集成选项中打开「启用写操作」"
        )
    return chosen


def _normalize_target(raw: str) -> str:
    """Accept a MAC (any spelling) or an IPv4 address for ACL sources."""
    text = str(raw or "").strip()
    mac = normalize_mac(text)
    if mac:
        return mac_for_router(mac)
    try:
        return str(IPv4Address(text))
    except AddressValueError as err:
        raise HomeAssistantError(
            f"目标 {raw!r} 不是合法的 MAC 地址或 IPv4 地址"
        ) from err


def _weekly_template(weekdays: str, start: str, end: str) -> dict[str, Any]:
    days = str(weekdays or "").strip()
    if not days or any(ch not in "1234567" for ch in days):
        raise HomeAssistantError(
            f"weekdays={weekdays!r} 不合法：应为 1-7 的组合，如 12345（周一至周五）"
        )
    start = str(start).strip()
    end = str(end).strip()
    if not valid_hhmm(start) or not valid_hhmm(end):
        raise HomeAssistantError(f"时间格式应为 HH:MM（24 小时制），收到 {start}/{end}")
    return {
        "type": "weekly",
        "weekdays": days,
        "start_time": start,
        "end_time": end,
        "comment": SERVICE_MARKER,
    }


async def _refresh_resource_coordinator(call_runtime: Any) -> None:
    coordinator = getattr(call_runtime, "resources", None)
    if coordinator is not None:
        await coordinator.async_request_refresh()


async def _async_block_terminal(call: ServiceCall) -> dict[str, Any]:
    runtime = _pick(call, call.hass)
    mac = normalize_mac(call.data[ATTR_MAC])
    if not mac:
        raise HomeAssistantError(f"{call.data[ATTR_MAC]!r} 不是合法的 MAC 地址")
    router_mac = mac_for_router(mac)
    name = str(call.data.get(ATTR_NAME) or "").strip()

    existing = await runtime.client.async_list_resource(_MAC_RULES, limit=500)
    duplicates = [
        row for row in existing if normalize_mac(row.get("mac")) == mac
    ]
    if duplicates:
        ids = ", ".join(str(row.get("id")) for row in duplicates)
        raise HomeAssistantError(f"该终端已在 MAC 黑名单中（规则 id：{ids}）")

    expires_hours = call.data.get(ATTR_EXPIRES_HOURS)
    payload = {
        "mac": router_mac,
        "enabled": "yes",
        "tagname": clamp_tagname(name, f"HA-BK-{mac.replace(':', '')[-6:]}"),
        "expires": int(time_module.time() + expires_hours * 3600)
        if expires_hours
        else 0,
        "comment": (f"{BLOCK_MARKER} {name}".strip())[:64],
    }
    try:
        row_id = await runtime.client.async_create_resource(_MAC_RULES, payload)
    except IkuaiApiError as err:
        raise HomeAssistantError(f"创建断网规则失败：{err}") from err

    await _refresh_resource_coordinator(runtime)
    return {"rule_id": row_id, "mac": router_mac}


async def _async_allow_terminal(call: ServiceCall) -> dict[str, Any]:
    runtime = _pick(call, call.hass)
    mac = normalize_mac(call.data[ATTR_MAC])
    if not mac:
        raise HomeAssistantError(f"{call.data[ATTR_MAC]!r} 不是合法的 MAC 地址")

    rows = await runtime.client.async_list_resource(_MAC_RULES, limit=500)
    matched = [row for row in rows if normalize_mac(row.get("mac")) == mac]
    if not matched:
        raise HomeAssistantError("MAC 黑名单中没有该终端的规则")

    removed: list[Any] = []
    try:
        for row in matched:
            await runtime.client.async_delete_resource(_MAC_RULES, row.get("id"))
            removed.append(row.get("id"))
    except IkuaiApiError as err:
        raise HomeAssistantError(f"删除规则失败（已删 {removed}）：{err}") from err

    await _refresh_resource_coordinator(runtime)
    return {"removed": removed, "mac": mac_for_router(mac)}


async def _async_parental_control(call: ServiceCall) -> dict[str, Any]:
    runtime = _pick(call, call.hass)
    target = _normalize_target(call.data[ATTR_TARGET])
    template = _weekly_template(
        call.data[ATTR_WEEKDAYS],
        call.data[ATTR_START_TIME],
        call.data[ATTR_END_TIME],
    )
    name = str(call.data.get(ATTR_NAME) or "").strip()

    payload = {
        "protocol": "any",
        "action": "drop",
        "dir": "forward",
        "ctdir": 0,
        "iinterface": "any",
        "ointerface": "any",
        "src_addr": {"custom": [target], "object": []},
        "src_addr_inv": 0,
        "dst_addr": "",
        "dst_addr_inv": 0,
        "dst_port": "",
        "src_type": 0,
        "dst_type": 0,
        "comment": (f"{PARENTAL_MARKER} {name}".strip())[:64],
        "enabled": "yes",
        "ip_type": "4",
        "src6_addr": "",
        "dst6_addr": "",
        "src6_mode": 1,
        "dst6_mode": 0,
        "src6_suffix": "",
        "dst6_suffix": "",
        "src_area_code": "",
        "dst_area_code": "",
        "prio": 10,
        "time": {"custom": [template], "object": []},
        "tagname": clamp_tagname(name, "HA-PC"),
    }
    try:
        row_id = await runtime.client.async_create_resource(_ACL_RULES, payload)
    except IkuaiApiError as err:
        raise HomeAssistantError(f"创建家长控制规则失败：{err}") from err

    await _refresh_resource_coordinator(runtime)
    return {"rule_id": row_id, "target": target, "schedule": template}


async def _async_clear_parental_control(call: ServiceCall) -> dict[str, Any]:
    runtime = _pick(call, call.hass)
    name = str(call.data.get(ATTR_NAME) or "").strip()

    rows = await runtime.client.async_list_resource(_ACL_RULES, limit=500)
    matched = []
    for row in rows:
        comment = str(row.get("comment") or "")
        if not comment.startswith(PARENTAL_MARKER):
            continue
        if name and name not in comment and name != str(row.get("tagname")):
            continue
        matched.append(row)
    if not matched:
        raise HomeAssistantError("没有找到由本集成创建的家长控制规则")

    removed: list[Any] = []
    try:
        for row in matched:
            await runtime.client.async_delete_resource(_ACL_RULES, row.get("id"))
            removed.append(row.get("id"))
    except IkuaiApiError as err:
        raise HomeAssistantError(f"删除规则失败（已删 {removed}）：{err}") from err

    await _refresh_resource_coordinator(runtime)
    return {"removed": removed}


# -- Phase 4 handlers --------------------------------------------------------


def _resolve_query_path(resource: str) -> str:
    """Accept a friendly key or a raw path; enforce the read whitelist."""
    text = str(resource or "").strip().lstrip("/")
    path = QUERY_PATHS.get(text, text)
    if not query_path_allowed(path):
        raise HomeAssistantError(
            f"路径 {path!r} 不在查询白名单内；可用键见 services.yaml 或文档"
        )
    return path


async def _async_query(call: ServiceCall) -> dict[str, Any]:
    """Read-only diagnostic query against a whitelisted GET endpoint."""
    runtime = _pick(call, call.hass, require_write=False)
    path = _resolve_query_path(call.data[ATTR_RESOURCE])
    try:
        results = await runtime.client.async_get_path(path, call.data.get(ATTR_PARAMS))
    except IkuaiApiError as err:
        raise HomeAssistantError(f"查询 {path} 失败：{err}") from err
    # Business failures keep their envelope (code/message) so callers can see
    # why a device refused - e.g. enterprise-only endpoints on free firmware.
    if isinstance(results, dict) and results.get("code") not in (None, 0, "0"):
        raise HomeAssistantError(
            f"路由器返回错误 code={results.get('code')}: {results.get('message')}"
        )
    return {"path": path, "results": results}


async def _async_set_config(call: ServiceCall) -> dict[str, Any]:
    """Read-modify-write one singleton configuration resource."""
    runtime = _pick(call, call.hass)
    key = call.data[ATTR_KEY]
    cfg = CONFIG_BY_KEY.get(key)
    if cfg is None:
        raise HomeAssistantError(
            f"未知配置项「{key}」。可选配置项：{', '.join(sorted(CONFIG_BY_KEY))}"
        )
    fields = dict(call.data.get(ATTR_FIELDS) or {})
    if cfg.dangerous and not call.data.get(ATTR_CONFIRM):
        raise HomeAssistantError(
            f"「{cfg.name}」属于高风险配置（写错可能断网/锁管理入口），"
            "请同时传入 confirm: true"
        )
    try:
        merged = await runtime.client.async_read_modify_write_config(cfg.path, fields)
    except IkuaiApiError as err:
        raise HomeAssistantError(f"写入 {cfg.path} 失败：{err}") from err
    return {"key": cfg.key, "path": cfg.path, "config": merged}


async def _async_speed_test(call: ServiceCall) -> dict[str, Any]:
    """Start / stop / check the one-click speed test."""
    runtime = _pick(call, call.hass)
    action = call.data[ATTR_ACTION]
    try:
        if action == "start":
            await runtime.client.async_start_speed_test(call.data.get(ATTR_INTERFACE))
            return {"action": "start", "note": "测速已启动，稍后用 action=status 查询结果"}
        if action == "stop":
            await runtime.client.async_stop_speed_test()
            return {"action": "stop"}
        status = await runtime.client.async_get_speed_test()
    except IkuaiApiError as err:
        raise HomeAssistantError(f"一键测速失败：{err}") from err
    return {"action": "status", "status": status}


async def _async_router_health(call: ServiceCall) -> dict[str, Any]:
    """Start / stop / check the router health check."""
    runtime = _pick(call, call.hass)
    action = call.data[ATTR_ACTION]
    try:
        if action == "start":
            await runtime.client.async_start_router_health()
            return {"action": "start", "note": "体检已启动，稍后用 action=status 查询结果"}
        if action == "stop":
            await runtime.client.async_stop_router_health()
            return {"action": "stop"}
        status = await runtime.client.async_get_router_health()
    except IkuaiApiError as err:
        raise HomeAssistantError(f"路由体检失败：{err}") from err
    return {"action": "status", "status": status}


async def _async_ac_service(call: ServiceCall) -> dict[str, Any]:
    """Start / stop / check the wireless AC service."""
    runtime = _pick(call, call.hass)
    action = call.data[ATTR_ACTION]
    try:
        if action == "start":
            await runtime.client.async_set_ac_service(True)
            return {"action": "start"}
        if action == "stop":
            await runtime.client.async_set_ac_service(False)
            return {"action": "stop"}
        status = await runtime.client.async_get_ac_service()
    except IkuaiApiError as err:
        raise HomeAssistantError(f"AC 服务操作失败：{err}") from err
    return {"action": "status", "status": status}


async def _async_restart_dhcp(call: ServiceCall) -> dict[str, Any]:
    """Restart the DHCP service (briefly interrupts new lease handout)."""
    runtime = _pick(call, call.hass)
    try:
        await runtime.client.async_restart_dhcp()
    except IkuaiApiError as err:
        raise HomeAssistantError(f"重启 DHCP 服务失败：{err}") from err
    return {"restarted": True}


async def _async_set_terminal_name(call: ServiceCall) -> dict[str, Any]:
    """Create or update one terminal name annotation (upsert by MAC)."""
    runtime = _pick(call, call.hass)
    mac = normalize_mac(call.data[ATTR_MAC])
    if not mac:
        raise HomeAssistantError(f"{call.data[ATTR_MAC]!r} 不是合法的 MAC 地址")
    router_mac = mac_for_router(mac)
    tagname = clamp_tagname(call.data[ATTR_NAME], f"HA-{mac.replace(':', '')[-6:]}")
    comment = call.data.get(ATTR_COMMENT)
    try:
        row_id = await runtime.client.async_set_terminal_name(
            router_mac, tagname, comment
        )
    except IkuaiApiError as err:
        raise HomeAssistantError(f"设置终端备注失败：{err}") from err
    return {"row_id": row_id, "mac": router_mac, "tagname": tagname}


async def _async_set_ssid(call: ServiceCall) -> dict[str, Any]:
    """Quick-update one SSID of a managed AP (name/password/hide/...)."""
    runtime = _pick(call, call.hass)
    optional = {
        key: call.data[key]
        for key in ATTR_SSID_OPTIONAL_KEYS
        if call.data.get(key) is not None
    }
    try:
        await runtime.client.async_set_ap_ssid_quick(
            call.data[ATTR_AP_ID],
            call.data[ATTR_RADIO],
            call.data[ATTR_SSID_INDEX],
            call.data[ATTR_SSID],
            optional,
        )
    except (IkuaiApiError, ValueError) as err:
        raise HomeAssistantError(f"修改 SSID 失败：{err}") from err
    return {"ap_id": call.data[ATTR_AP_ID], "ssid": call.data[ATTR_SSID]}


async def _async_api_request(call: ServiceCall) -> dict[str, Any]:
    """Whitelisted raw API escape hatch for endpoints without a bespoke service.

    GET requests only need a valid path inside the read whitelist; every other
    method requires write support and a path inside the write whitelist. Tier D
    endpoints (backup restore, firmware upgrade, admin accounts, system files)
    are not in either whitelist by design.
    """
    method: str = call.data[ATTR_METHOD]
    path = str(call.data[ATTR_PATH]).strip().lstrip("/")
    if "://" in path or path.startswith("api/"):
        raise HomeAssistantError(f"非法路径 {path!r}")
    params = call.data.get(ATTR_PARAMS)
    if method == "get":
        runtime = _pick(call, call.hass, require_write=False)
        if not query_path_allowed(path):
            raise HomeAssistantError(f"GET {path} 不在查询白名单内")
        try:
            results = await runtime.client.async_get_path(path, params)
        except IkuaiApiError as err:
            raise HomeAssistantError(f"GET {path} 失败：{err}") from err
        return {"path": path, "results": results}

    runtime = _pick(call, call.hass)
    if not write_path_allowed(path):
        raise HomeAssistantError(
            f"{method.upper()} {path} 不在写白名单内（备份恢复/固件升级/"
            "管理员账号等高危端点被永久禁止）"
        )
    try:
        data = await runtime.client.async_request(
            method, path, call.data.get(ATTR_PAYLOAD), params
        )
    except IkuaiApiError as err:
        raise HomeAssistantError(f"{method.upper()} {path} 失败：{err}") from err
    return {"path": path, "code": data.get("code"), "results": data.get("results")}


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register the domain-level services (safe to call for every entry)."""
    registrations: tuple[tuple[str, Any, vol.Schema], ...] = (
        (SERVICE_BLOCK_TERMINAL, _async_block_terminal, _BLOCK_SCHEMA),
        (SERVICE_ALLOW_TERMINAL, _async_allow_terminal, _ALLOW_SCHEMA),
        (SERVICE_PARENTAL_CONTROL, _async_parental_control, _PARENTAL_SCHEMA),
        (
            SERVICE_CLEAR_PARENTAL_CONTROL,
            _async_clear_parental_control,
            _CLEAR_PARENTAL_SCHEMA,
        ),
        (SERVICE_QUERY, _async_query, _QUERY_SCHEMA),
        (SERVICE_SET_CONFIG, _async_set_config, _SET_CONFIG_SCHEMA),
        (SERVICE_SPEED_TEST, _async_speed_test, _ACTION_SCHEMA),
        (SERVICE_ROUTER_HEALTH, _async_router_health, _ACTION_SCHEMA),
        (SERVICE_AC_SERVICE, _async_ac_service, _ACTION_SCHEMA),
        (SERVICE_RESTART_DHCP, _async_restart_dhcp, _RESTART_DHCP_SCHEMA),
        (
            SERVICE_SET_TERMINAL_NAME,
            _async_set_terminal_name,
            _SET_TERMINAL_NAME_SCHEMA,
        ),
        (SERVICE_SET_SSID, _async_set_ssid, _SET_SSID_SCHEMA),
        (SERVICE_API_REQUEST, _async_api_request, _API_REQUEST_SCHEMA),
    )
    for name, handler, schema in registrations:
        hass.services.async_register(
            DOMAIN,
            name,
            handler,
            schema=schema,
            supports_response=SupportsResponse.OPTIONAL,
        )
