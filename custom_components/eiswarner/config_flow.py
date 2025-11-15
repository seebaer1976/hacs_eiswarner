"""Config flow for Eiswarner mit API-Optionen."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback, HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_USE_HA_GEO,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_FROST_THRESHOLD,
    CONF_HUMIDITY_THRESHOLD,
    DEFAULT_FROST_THRESHOLD,
    DEFAULT_HUMIDITY_THRESHOLD,
)

class EiswarnerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle Eiswarner config flow."""

    VERSION = 1

    @callback
    def async_config_entry_title(self, options: dict) -> str:
        """Return config entry title."""
        return "Eiswarnung API"

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle user step."""
        errors = {}

        if user_input is not None:
            # Test API-Key (optional, aber empfohlen)
            if not await self._test_api(user_input):
                errors["base"] = "api_error"
            else:
                user_input["unique_id"] = f"eiswarnung_{user_input[CONF_LATITUDE]}_{user_input[CONF_LONGITUDE]}"
                return self.async_create_entry(
                    title=f"Eiswarnung für {user_input[CONF_LATITUDE]},{user_input[CONF_LONGITUDE]}",
                    data=user_input,
                    options={
                        CONF_FROST_THRESHOLD: DEFAULT_FROST_THRESHOLD,
                        CONF_HUMIDITY_THRESHOLD: DEFAULT_HUMIDITY_THRESHOLD,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Required(CONF_USE_HA_GEO, default=True): selector.BooleanSelector(),
                vol.Optional(CONF_LATITUDE, description="Latitude (falls nicht HA-Geo)"): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=-90, max=90, step=0.0001)
                ),
                vol.Optional(CONF_LONGITUDE, description="Longitude (falls nicht HA-Geo)"): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=-180, max=180, step=0.0001)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def _test_api(self, user_input: dict) -> bool:
        """Test API connection."""
        import aiohttp
        from . import API_BASE, API_ENDPOINT  # Importiere aus const

        api_key = user_input[CONF_API_KEY]
        if user_input.get(CONF_USE_HA_GEO):
            # Dummy-Koordinaten für Test (HA lat/lon)
            lat, lon = 52.52, 13.40
        else:
            lat = user_input.get(CONF_LATITUDE, 52.52)
            lon = user_input.get(CONF_LONGITUDE, 13.40)

        url = f"{API_BASE}{API_ENDPOINT}?key={api_key}&lat={lat}&lon={lon}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    return resp.status == 200
        except:
            return False
