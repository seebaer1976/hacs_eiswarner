"""Eiswarner Integration – Eiswarnung für deine Windschutzscheibe."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_URL,
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_SCAN_INTERVAL,
    CONF_USE_HA_GEO,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eiswarner from a config entry."""
    coordinator = EiswarnerCoordinator(hass, entry)

    # Erster Datenabruf – wirft ConfigEntryNotReady wenn die API nicht erreichbar ist
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class EiswarnerCoordinator(DataUpdateCoordinator):
    """Koordinator für die Eiswarnung-API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.entry = entry
        self.session = async_get_clientsession(hass)

    @property
    def device_info(self) -> DeviceInfo:
        """Geräteinformationen – erzeugt die Device-Seite in HA."""
        lat, lng = self._get_coordinates()
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=f"Eiswarnung ({lat:.4f}, {lng:.4f})",
            manufacturer="eiswarnung.de",
            model="REST API v1",
            entry_type="service",
            configuration_url="https://www.eiswarnung.de/rest-api/",
        )

    def _get_coordinates(self) -> tuple[float, float]:
        """Koordinaten aus Config oder HA-Einstellungen holen."""
        if self.entry.data.get(CONF_USE_HA_GEO):
            return self.hass.config.latitude, self.hass.config.longitude
        return (
            self.entry.data[CONF_LATITUDE],
            self.entry.data[CONF_LONGITUDE],
        )

    async def _async_update_data(self) -> dict:
        """Daten von der Eiswarnung-API abrufen."""
        api_key = self.entry.data[CONF_API_KEY]
        lat, lng = self._get_coordinates()

        try:
            async with self.session.post(
                API_URL,
                data={"key": api_key, "lat": str(lat), "lng": str(lng)},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status} von der Eiswarnung-API")
                data = await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Verbindungsfehler zur Eiswarnung-API: {err}") from err

        if not data.get("success"):
            code = data.get("code", "?")
            msg = data.get("message", "Unbekannter Fehler")
            raise UpdateFailed(f"API Fehler {code}: {msg}")

        result = data.get("result", {})
        return {
            "forecast_id": result.get("forecastId"),
            "forecast_text": result.get("forecastText"),
            "forecast_city": result.get("forecastCity"),
            "forecast_date": result.get("forecastDate"),
            "request_date": result.get("requestDate"),
            "calls_left": data.get("callsLeft"),
            "calls_daily_limit": data.get("callsDailyLimit"),
            "calls_reset_in_seconds": data.get("callsResetInSeconds"),
            "api_success": data.get("success"),
            "api_message": data.get("message"),
            "api_code": data.get("code"),
        }
