"""Constants for the iKuai Router integration."""

DOMAIN = "ikuai"
MANUFACTURER = "iKuai"
DEFAULT_NAME = "iKuai Router"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_CLIENT_LIMIT = 256
DEFAULT_VERIFY_SSL = False  # iKuai serves a self-signed certificate
DEFAULT_TIMEOUT = 15

CONF_TOKEN = "token"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_VERIFY_SSL = "verify_ssl"

# Slower polling for data that changes rarely or costs more to fetch.
EXTENDED_SCAN_INTERVAL = 300

# iKuaiOS 4.x forces HTTPS: plain http requests answer with a 302 to https:443.
DEFAULT_SCHEME = "https"

# Polling endpoints (official REST API, base: https://<router>/api/v4.0/)
API_SYSTEM = "monitoring/system"
API_INTERFACES_STATUS = "monitoring/interfaces-status"
API_CLIENTS_ONLINE = "monitoring/clients-online"

# Phase 1: read-only breadth
API_DHCP_CLIENTS = "network/dhcp/clients"
API_DHCP_STATIC = "network/dhcp/static"
API_AUTH_USERS = "auth/online-users"
API_UPGRADE = "system/upgrade"
API_WIRELESS_STATISTICS = "monitoring/wireless-statistics"
API_TRAFFIC_AUDIT_TERMINALS = "monitoring/traffic-audit/terminals"
API_CPU_HISTORY = "monitoring/cpu"
API_MEMORY_HISTORY = "monitoring/memory"

PLATFORMS = ["binary_sensor", "device_tracker", "sensor"]
