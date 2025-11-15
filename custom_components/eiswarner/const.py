"""Constants for Eiswarner."""
DOMAIN = "eiswarner"

CONF_API_KEY = "api_key"
CONF_USE_HA_GEO = "use_ha_geo"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_FROST_THRESHOLD = "frost_threshold"
CONF_HUMIDITY_THRESHOLD = "humidity_threshold"

DEFAULT_FROST_THRESHOLD = 0.0
DEFAULT_HUMIDITY_THRESHOLD = 80.0

API_BASE = "https://api.eiswarnung.de/"
API_ENDPOINT = "v1/forecast"  # Angenommenes Endpoint basierend auf Docs; passe an wenn nötig
