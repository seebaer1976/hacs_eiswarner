from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .config_flow import EiswarnerConfigFlow

DOMAIN = "eiswarner"

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry: ConfigEntry):
    return True

async def async_get_config_flow(hass, entry):
    return EiswarnerConfigFlow(hass, entry)