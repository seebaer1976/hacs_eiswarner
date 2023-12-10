import logging

import voluptuous as vol
from homeassistant import config_entries

from const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class EiswarnerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:

            # Überprüfen, ob der API-Schlüssel gültig ist
            if not is_valid_api_key(user_input['api_key']):
                return self.async_show_form(
                    step_id="user",
                    data_schema=self.schema,
                    errors={"api_key": "Ungültiger API-Schlüssel"},
                )

            # Überprüfen, ob der Längengrad im gültigen Bereich liegt (-180 bis 180)
            if user_input['longitude'] < -180 or user_input['longitude'] > 180:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self.schema,
                    errors={"longitude": "Ungültiger Längengrad"},
                )

            # Überprüfen, ob der Breitengrad im gültigen Bereich liegt (-90 bis 90)
            if user_input['latitude'] < -90 or user_input['latitude'] > 90:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self.schema,
                    errors={"latitude": "Ungültiger Breitengrad"},
                )

            # Wenn die Eingabe gültig ist, Konfigurationseintrag erstellen
            return self.async_create_entry(title="Eiswarner Integration", data=user_input)

        # Zeigen Sie das Eingabeformular an
        return self.async_show_form(
            step_id="user",
            data_schema=self.schema,
        )

    @property
    def schema(self):
        # Hier Eingabeformulardaten definieren
        return vol.Schema(
            {
                vol.Required("api_key"): str,
                vol.Required("longitude"): float,
                vol.Required("latitude"): float,
            }
        )


def is_valid_api_key(api_key):
    # Fügen Sie hier die Logik zur Überprüfung der Gültigkeit des API-Schlüssels hinzu
    # Zum Beispiel könnten Sie eine API-Anfrage durchführen, um die Gültigkeit zu überprüfen
    # und True zurückgeben, wenn der Schlüssel gültig ist, andernfalls False
    return True
