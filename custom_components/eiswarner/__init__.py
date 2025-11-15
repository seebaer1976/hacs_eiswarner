"""Eiswarner Integration mit API-Support."""
import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE

from .const import DOMAIN

PLATFORMS = ["sensor", "switch"]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Eiswarner from config entry."""
    hass.data.setdefault(DOMAIN, {})
    coordinator = EiswarnerCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Eiswarner config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    await coordinator.async_stop()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class EiswarnerCoordinator:
    """Coordinator for API data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        self.data = {}
        self._stop = None

    async def async_start(self):
        """Start polling."""
        self._stop = asyncio.create_task(self._async_update_loop())

    async def _async_update_loop(self):
        """Update data periodically."""
        while True:
            try:
                data = await self._fetch_api_data()
                self.data = data
                await self.hass.async_add_executor_job(self._check_ice_warning, data)
            except Exception as err:
                _LOGGER.error(f"API-Fehler: {err}")
            await asyncio.sleep(1800)  # 30 Min

    async def _fetch_api_data(self):
        """Fetch from Eiswarnung API."""
        import aiohttp

        config = self.entry.data
        api_key = config.get(CONF_API_KEY)
        if config.get(CONF_USE_HA_GEO):
            lat = self.hass.config.latitude
            lon = self.hass.config.longitude
        else:
            lat = config.get(CONF_LATITUDE)
            lon = config.get(CONF_LONGITUDE)

        if not all([api_key, lat, lon]):
            raise ValueError("API-Key oder Koordinaten fehlen!")

        url = f"{API_BASE}{API_ENDPOINT}?key={api_key}&lat={lat}&lon={lon}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise ValueError(f"API-Fehler {resp.status}: {await resp.text()}")
                return await resp.json()

    def _check_ice_warning(self, data):
        """Berechne Warnung aus API-Daten."""
        temp = data.get("temperature", 0)
        humidity = data.get("humidity", 0)
        frost = self.entry.options.get(CONF_FROST_THRESHOLD, DEFAULT_FROST_THRESHOLD)
        hum_th = self.entry.options.get(CONF_HUMIDITY_THRESHOLD, DEFAULT_HUMIDITY_THRESHOLD)
        risk = temp <= frost and humidity >= hum_th
        data["is_ice_warning"] = risk
        data["risk_level"] = "Hoch" if risk else "Niedrig"

    async def async_stop(self):
        """Stop polling."""
        if self._stop:
            self._stop.cancel()
