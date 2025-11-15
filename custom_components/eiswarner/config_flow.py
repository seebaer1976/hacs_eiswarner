"""Config flow for Eiswarner."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_WEATHER_ENTITY,
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
        return "Eiswarnung für " + options.get(CONF_WEATHER_ENTITY, "Wetter")

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle user step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_WEATHER_ENTITY],
                data=user_input,
            )

        weather_entities = [
            entity["entity_id"]
            for entity in self.hass.states.async_all("weather")
        ]

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_WEATHER_ENTITY,
                    default=weather_entities[0] if weather_entities else "",
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="weather")
                ),
                vol.Optional(
                    CONF_FROST_THRESHOLD,
                    default=DEFAULT_FROST_THRESHOLD,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(min= -10.0, max=10.0, step=0.5)
                ),
                vol.Optional(
                    CONF_HUMIDITY_THRESHOLD,
                    default=DEFAULT_HUMIDITY_THRESHOLD,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=50.0, max=100.0, step=5.0)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )
