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

# Phase 2: write support is opt-in. Both switches below must be turned on
# before a single write request is issued:
#   enable_write    - master switch (off by default)
#   resource_groups - the CRUD groups the user wants exposed (empty by default)
CONF_ENABLE_WRITE = "enable_write"
CONF_RESOURCE_GROUPS = "resource_groups"
DEFAULT_ENABLE_WRITE = False
DEFAULT_RESOURCE_GROUPS: list[str] = []

# Edition: iKuai ships a "免费版" (free, software installed on x86) and an
# "企业版" (enterprise, hardware appliance such as IK-M200). The two expose
# different endpoints, so we auto-detect the edition from `verinfo` and use it
# to hide enterprise-only resource groups on free firmware. The user can
# override the guess with CONF_EDITION when detection is wrong.
EDITION_FREE = "free"
EDITION_ENTERPRISE = "enterprise"
CONF_EDITION = "edition"
DEFAULT_EDITION = "auto"  # auto | free | enterprise

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

# Phase 2: one-shot actions (POST). All of them need CONF_ENABLE_WRITE.
API_REBOOT_TASKS = "system/reboot-tasks"          # 立即重启
API_BACKUP = "system/backup"                      # 手动备份配置
API_NTP_SYNC = "system/basic/ntp:sync"            # 立即 NTP 同步
API_UPGRADE_CHECK = "system/upgrade:check"        # 版本检测

# Phase 3: scenario services + their backing endpoints.
API_MAC_RULES = "security/mac-rules"
API_ACL_RULES = "security/acl-rules"
API_SSID_CLIENTS = "monitoring/ssid-clients"
API_CHANNEL_CLIENTS = "monitoring/channel-clients"
API_WIRELESS_SCORE = "monitoring/wireless-score"

SERVICE_BLOCK_TERMINAL = "block_terminal"
SERVICE_ALLOW_TERMINAL = "allow_terminal"
SERVICE_PARENTAL_CONTROL = "parental_control"
SERVICE_CLEAR_PARENTAL_CONTROL = "clear_parental_control"

# Rules created by services carry this comment marker so they can be found
# (and cleaned up) later regardless of what the user typed as the name.
SERVICE_MARKER = "HA集成"
BLOCK_MARKER = f"{SERVICE_MARKER}断网"
PARENTAL_MARKER = f"{SERVICE_MARKER}家长控制"

# Resource state changes rarely, but a switch must not feel laggy.
RESOURCE_SCAN_INTERVAL = 60

PLATFORMS = ["binary_sensor", "device_tracker", "sensor"]
WRITE_PLATFORMS = ["button", "switch"]
