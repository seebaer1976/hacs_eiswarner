from homeassistant import config_entries

from .config_flow import EiswarnerConfigFlow

DOMAIN = "eiswarner"


async def async_setup(hass, config):
    return True


async def async_setup_entry(hass, entry):
    return True


async def async_migrate_entry(hass, config_entry):
    return True


async def async_unload_entry(hass, config_entry):
    return True


async def async_get_config_flow():
    return EiswarnerConfigFlow()