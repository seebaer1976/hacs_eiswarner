"""Eiswarner Intregatoin"""
import asyncio
from const import DOMAIN


async def async_setup(hass, config):
    api_key = config[DOMAIN]["api_key"]
    longitude = config[DOMAIN]["longitude"]
    latitude = config[DOMAIN]["latitude"]

    # Hier können Sie Ihre Add-on-Initialisierung mit den Konfigurationsdaten durchführen

    return True
