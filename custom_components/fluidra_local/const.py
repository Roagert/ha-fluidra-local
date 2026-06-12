"""Constants for Fluidra Local Server integration."""
DOMAIN = "fluidra_local"
CONF_BASE_URL = "base_url"
CONF_DEVICE_ID = "device_id"
CONF_AUTH_TOKEN = "auth_token"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_NAME = "Fluidra Local Heat Pump"
DEFAULT_BASE_URL = "http://127.0.0.1:8765"
DEFAULT_DEVICE_ID = "LG24440781"
DEFAULT_AUTH_TOKEN = ""
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300
PLATFORMS = ["climate", "sensor", "binary_sensor", "switch"]

MODE_TO_VALUE = {
    "Smart Heating": 0,
    "Smart Cooling": 1,
    "Smart Auto": 2,
    "Boost Heating": 3,
    "Silence Heating": 4,
    "Boost Cooling": 5,
    "Silence Cooling": 6,
}
VALUE_TO_MODE = {value: name for name, value in MODE_TO_VALUE.items()}
