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

# Phase 4: extended monitoring sensors (Tier A, read-only).
API_MONITOR_CONNECTIONS = "monitoring/connections"
API_MONITOR_CPUTEMP = "monitoring/cputemp"
API_MONITOR_DISK = "monitoring/disk"
API_MONITOR_NETWORK = "monitoring/network"
API_MONITOR_TERMINALS = "monitoring/terminals"
API_INTERFACES_CONFIG = "monitoring/interfaces-config"
API_INTERFACES_PHYSICAL_MON = "monitoring/interfaces-physical"
API_INTERFACES_TRAFFIC = "monitoring/interfaces-traffic"
API_INTERFACES_TRAFFIC_V6 = "monitoring/interfaces-traffic-v6"
API_CLIENTS_OFFLINE = "monitoring/clients-offline"
API_CLIENTS_IP6_ONLINE = "monitoring/clients-ip6-online"
API_CLIENTS_IP6_OFFLINE = "monitoring/clients-ip6-offline"
API_CLIENTS_TRAFFIC_SUMMARY = "monitoring/clients-traffic-summary"
API_CLIENTS_TRAFFIC_LOAD = "monitoring/clients-traffic-load"
API_APP_PROTOCOLS_LOAD = "monitoring/app-protocols/load"
API_APP_PROTOCOLS_HISTORY = "monitoring/app-protocols/history-load"
API_APP_PROTOCOLS_TERMINAL_LOAD = "monitoring/app-protocols/terminal-load"
API_APP_TRAFFIC_SUMMARY = "monitoring/app-traffic-summary"
API_PROTOCOLS = "monitoring/protocols"
API_PROTOCOLS_HISTORY = "monitoring/protocols/history-load"
API_AUDIT_ACCOUNTS = "monitoring/traffic-audit/accounts"
API_AUDIT_ACCOUNT_APPS = "monitoring/traffic-audit/accounts/applications"
API_AUDIT_ACCOUNT_TREND = "monitoring/traffic-audit/accounts/trend"
API_AUDIT_TERMINAL_APPS = "monitoring/traffic-audit/terminals/applications"
API_AUDIT_TERMINAL_TREND = "monitoring/traffic-audit/terminals/trend"
API_WIRELESS_TRAFFIC = "monitoring/wireless-traffic"
API_FLOW_SHUNTING = "monitoring/flow-shunting"
API_POLICY_TRAFFIC = "monitoring/policy-traffic"
API_APS_CHANNEL_NOISE = "monitoring/aps-channel-noise"
API_CAMERAS = "monitoring/cameras"
API_CLOUD_SWITCHES = "monitoring/switch"
API_DOWNSTREAM = "monitoring/downstream"
API_DNS_STATS = "network/dns/stats"
API_CPUFREQ = "system/cpufreq"
API_SYSTEM_DISKS = "system/disks"
API_SPEED_TEST = "advanced-service/speed-test"
API_ROUTER_HEALTH = "monitoring/router-health"

# Phase 4: configuration endpoints (Tier B). Singleton GET/PUT pairs are
# declared in resources.CONFIG_RESOURCES; the paths below are shared by the
# services and the query whitelist.
API_DHCP6_RULES = "network/dhcp6/access-control/rules"
API_DHCP6_CLIENTS = "network/dhcp6/clients"
API_DNS_CONFIG = "network/dns/config"
API_DHCP_ACCESS_MODE = "network/dhcp/access-control/mode"
API_DHCP6_ACCESS_MODE = "network/dhcp6/access-control/mode"
API_PPPOE_SERVER = "network/pppoe/services"
API_PPTP_SERVER = "vpn/pptp/services"
API_L2TP_SERVER = "vpn/l2tp/services"
API_IKEV2_SERVER = "vpn/ikev2/services"
API_OPENVPN_SERVER = "vpn/openvpn/services"
API_WEB_AUTH_SERVICE = "auth/web/services"
API_AUTH_ACCOUNTS = "auth/users"
API_AUTH_PACKAGES = "auth/packages"
API_ALG = "system/alg"
API_SNMP = "advanced-service/snmpd-config"
API_SAMBA = "advanced-service/samba-config"
API_FTP = "advanced-service/ftp-config"
API_SECURITY_ADVANCED = "security/advanced/config"
API_MAC_MODE = "security/mac-mode"
API_REMOTE_ACCESS = "system/remote-access"
API_SECONDARY_ROUTE = "security/secondary-route/config"
API_KERNEL_PARAMS = "system/kernel-params"
API_CPUFREQ_MODE = "system/cpufreq/mode"
API_BACKUP_AUTO = "system/backup-auto"
API_SYSTEM_BASIC = "system/basic/config"
API_VRRP_CONFIG = "system/vrrp/config"
API_VRRP_START = "system/vrrp:start"
API_VRRP_STOP = "system/vrrp:stop"
API_AC_SERVICE = "network/ac/services"
API_AC_START = "network/ac/services:start"
API_AC_STOP = "network/ac/services:stop"
API_AP_CONFIG = "network/ac/ap-config"
API_AP_SSID_QUICK = "network/ac/ssid-quick"
API_AP_SSID_UNION = "network/ac/ssid-union"
API_DHCP_RESTART = "network/dhcp/services:restart"
API_TERMINAL_NAMES = "security/terminals"
API_WIREGUARD = "vpn/wireguard"

# Phase 4: service names.
SERVICE_QUERY = "query"
SERVICE_SET_CONFIG = "set_config"
SERVICE_SPEED_TEST = "speed_test"
SERVICE_ROUTER_HEALTH = "router_health"
SERVICE_AC_SERVICE = "ac_service"
SERVICE_RESTART_DHCP = "restart_dhcp"
SERVICE_SET_TERMINAL_NAME = "set_terminal_name"
SERVICE_SET_SSID = "set_ssid"
SERVICE_API_REQUEST = "api_request"

# Resource state changes rarely, but a switch must not feel laggy.
RESOURCE_SCAN_INTERVAL = 60

PLATFORMS = ["binary_sensor", "device_tracker", "sensor"]
WRITE_PLATFORMS = ["button", "switch"]
