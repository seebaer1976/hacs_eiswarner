import voluptuous as vol
from homeassistant import config_entries

from const import DOMAIN


class BeispielConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Hier können Sie die eingegebenen Daten verarbeiten
            # und überprüfen, ob die Werte gültig sind
            return self.async_create_entry(title="Eiswarner Integration", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_key"): str,
                    vol.Required("longitude"): float,
                    vol.Required("latitude"): float,
                }
            ),
        )
