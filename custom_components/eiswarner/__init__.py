from homeassistant.config_entries import ConfigEntry

from config_flow import EiswarnerConfigFlow  # Korrigierter Import

DOMAIN = "eiswarner"


async def async_setup(hass, config):
    return True


async def async_setup_entry(hass, entry: ConfigEntry):
    return True


async def async_get_config_flow(hass, entry):
    return EiswarnerConfigFlow(hass, entry)
