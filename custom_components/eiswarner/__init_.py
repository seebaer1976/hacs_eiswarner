"""Eiswarner Intregatoin"""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "eiswarner"


async def async_setup(hass: HomeAssistant, config: dict):
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Hier können Sie die Konfigurationsdaten aus entry.data verwenden
    api_key = entry.data.get("api_key")
    longitude = entry.data.get("longitude")
    latitude = entry.data.get("latitude")

    # Fügen Sie hier Ihren eigentlichen Setup-Code hinzu

    return True
