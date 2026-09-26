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
    SERVICE_ALLOW_TERMINAL,
    SERVICE_BLOCK_TERMINAL,
    SERVICE_CLEAR_PARENTAL_CONTROL,
    SERVICE_PARENTAL_CONTROL,
)
from .helpers import (
    clamp_tagname,
    mac_for_router,
    normalize_mac,
    valid_hhmm,
)
from .resources import RESOURCE_BY_KEY

ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_MAC = "mac"
ATTR_NAME = "name"
ATTR_EXPIRES_HOURS = "expires_hours"
ATTR_TARGET = "target"
ATTR_WEEKDAYS = "weekdays"
ATTR_START_TIME = "start_time"
ATTR_END_TIME = "end_time"

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


def _pick(call: ServiceCall, hass: HomeAssistant) -> _Runtime:
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
    if not chosen.write_enabled:
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


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register the domain-level services (safe to call for every entry)."""
    hass.services.async_register(
        DOMAIN,
        SERVICE_BLOCK_TERMINAL,
        _async_block_terminal,
        schema=_BLOCK_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ALLOW_TERMINAL,
        _async_allow_terminal,
        schema=_ALLOW_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_PARENTAL_CONTROL,
        _async_parental_control,
        schema=_PARENTAL_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_PARENTAL_CONTROL,
        _async_clear_parental_control,
        schema=_CLEAR_PARENTAL_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
