"""Constants for Eiswarner."""

DOMAIN = "eiswarner"

# Config entry keys
CONF_API_KEY = "api_key"
CONF_USE_HA_GEO = "use_ha_geo"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"

# Options keys
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL = 1800  # 30 Minuten

# API
API_URL = "https://api.eiswarnung.de/"

# forecastId values
FORECAST_NO_ICE = 0
FORECAST_ICE = 1
FORECAST_MAYBE_ICE = 2

FORECAST_ID_TO_TEXT = {
    FORECAST_NO_ICE: "Kein Eis",
    FORECAST_ICE: "Eis",
    FORECAST_MAYBE_ICE: "Eventuell Eis",
}
