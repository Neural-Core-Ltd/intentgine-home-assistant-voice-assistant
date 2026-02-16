"""Constants for the Intentgine integration."""

DOMAIN = "intentgine"

CONF_API_KEY = "api_key"
CONF_ENDPOINT = "endpoint"
CONF_SYNC_FREQUENCY = "sync_frequency"
CONF_ENABLE_AREA_TOOLSETS = "enable_area_toolsets"

DEFAULT_ENDPOINT = "https://api.intentgine.dev"
DEFAULT_SYNC_FREQUENCY = "daily"

TOOLSET_PREFIX = "ha"
TOOLSET_VERSION = "v1"
TOOLSET_GLOBAL = f"{TOOLSET_PREFIX}-global-{TOOLSET_VERSION}"

CORRECTION_BANK_NAME = "ha-corrections-v1"
CORRECTION_WINDOW_SECONDS = 30

SERVICE_EXECUTE_COMMAND = "execute_command"
SERVICE_SYNC_TOOLSETS = "sync_toolsets"

ATTR_QUERY = "query"
