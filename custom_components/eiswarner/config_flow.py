"""Config flow for Eiswarner."""
from __future__ import annotations

import logging

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

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


class EiswarnerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für die Eiswarner Integration."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Erster Setup-Schritt: API-Key und Koordinaten."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Koordinaten für den API-Test bestimmen
            if user_input.get(CONF_USE_HA_GEO):
                lat = self.hass.config.latitude
                lng = self.hass.config.longitude
            else:
                lat = user_input.get(CONF_LATITUDE)
                lng = user_input.get(CONF_LONGITUDE)
                if lat is None or lng is None:
                    errors["base"] = "coords_missing"

            if not errors:
                error = await self._test_api(user_input[CONF_API_KEY], lat, lng)
                if error:
                    errors["base"] = error
                else:
                    # Unique ID = Domain + Koordinaten (verhindert Doppel-Setup)
                    unique_id = f"eiswarner_{lat:.4f}_{lng:.4f}"
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Eiswarnung ({lat:.4f}, {lng:.4f})",
                        data=user_input,
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_USE_HA_GEO, default=True): bool,
                vol.Optional(CONF_LATITUDE): vol.Coerce(float),
                vol.Optional(CONF_LONGITUDE): vol.Coerce(float),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "api_url": "https://www.eiswarnung.de/get-api/"
            },
        )

    async def _test_api(self, api_key: str, lat: float, lng: float) -> str | None:
        """API-Verbindung testen. Gibt None zurück wenn OK, sonst Fehler-Key."""
        session = async_get_clientsession(self.hass)
        try:
            async with session.post(
                API_URL,
                data={"key": api_key, "lat": str(lat), "lng": str(lng)},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    return "cannot_connect"
                data = await resp.json(content_type=None)
                code = data.get("code", 0)
                if code == 401:
                    return "invalid_api_key"
                if code == 402:
                    return "limit_reached"
                if code == 300:
                    return "coords_missing"
                if not data.get("success") and code != 200:
                    _LOGGER.warning("API Fehler beim Test: %s", data.get("message"))
                    return "api_error"
        except aiohttp.ClientError:
            return "cannot_connect"
        return None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Options Flow zurückgeben."""
        return EiswarnerOptionsFlow()


class EiswarnerOptionsFlow(config_entries.OptionsFlow):
    """Options Flow: Scan-Intervall anpassen."""

    async def async_step_init(self, user_input: dict | None = None):
        """Einziger Options-Schritt."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                    int, vol.Range(min=300, max=86400)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
