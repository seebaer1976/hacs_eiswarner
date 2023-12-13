"""Eiswarner"""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = 'eiswarner'


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    api_key = config.get("api_key")
    latitude = config.get("latitude")
    longitude = config.get("longitude")

    hass.helpers.discovery.load_platform('sensor', DOMAIN, {
        "api_key": api_key,
        "latitude": latitude,
        "longitude": longitude
    }, config)

    return True
