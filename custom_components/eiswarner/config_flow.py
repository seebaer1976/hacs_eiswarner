from homeassistant.config_entries import ConfigFlow, ConfigEntry, SOURCE_USER
from homeassistant.const import CONF_API_KEY, CONF_LONGITUDE, CONF_LATITUDE

from . import DOMAIN


class EiswarnerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Eiswarner Integration Konfiguration."""

    def __init__(self):
        super().__init__()
        self._is_valid_api_key = None

    async def async_step_user(self, user_input: dict):
        """Schritt 1: Eingaben des Benutzers abfragen."""

        # Abrufen des API-Schlüssels
        api_key = user_input.get(CONF_API_KEY)

        # Überprüfen der Gültigkeit des API-Schlüssels
        if api_key is None:
            # Der Benutzer hat keinen API-Schlüssel angegeben
            return self.async_show_form(
                step_id="user",
                data={"errors": ["API-Schlüssel ist erforderlich"]},
            )

        self._is_valid_api_key = self._is_valid_api_key(api_key)
        if not self._is_valid_api_key:
            # Der API-Schlüssel ist ungültig
            return self.async_show_form(
                step_id="user",
                data={"errors": ["API-Schlüssel ist ungültig"]},
            )

        # Abrufen der Längengrad
        longitude = user_input.get(CONF_LONGITUDE)
        if longitude is None:
            # Der Benutzer hat keine Längengrad angegeben
            return self.async_show_form(
                step_id="user",
                data={"errors": ["Längengrad ist erforderlich"]},
            )

        # Abrufen der Breitengrad
        latitude = user_input.get(CONF_LATITUDE)
        if latitude is None:
            # Der Benutzer hat keine Breitengrad angegeben
            return self.async_show_form(
                step_id="user",
                data={"errors": ["Breitengrad ist erforderlich"]},
            )

        # Senden einer API-Anfrage an den Eiswarner-Dienst
        url = "https://api.eiswarnung.de"
        payload = {'key': api_key, 'longitude': longitude, 'latitude': latitude}
        response = requests.get(url, params=payload)

        # Überprüfen der Antwort
        if response.status_code == 200:
            # Der API-Schlüssel ist gültig und die Koordinaten sind gültig
            return self.async_create_entry(
                title="Eiswarner",
                data={
                    CONF_API_KEY: api_key,
                    CONF_LONGITUDE: longitude,
                    CONF_LATITUDE: latitude,
                },
            )
        else:
            # Der API-Schlüssel ist gültig, aber die Koordinaten sind ungültig
            return self.async_show_form(
                step_id="user",
                data={"errors": ["Die Koordinaten sind ungültig"]},
            )

    async def async_step_import(self, import_config: dict):
        """Schritt 2: Import einer vorhandenen Konfiguration."""

        return self.async_create_entry(
            title="Eiswarner",
            data=import_config,
        )

    def _is_valid_api_key(self, api_key):
        """Überprüft die Gültigkeit des API-Schlüssels."""

        # Senden einer API-Anfrage an den Eiswarner-Dienst
        url = "https://api.eiswarnung.de"
        payload = {'key': api_key}
        response = requests.get(url, params=payload)

        # Überprüfen der Antwort
        if response.status_code == 200:
            return True
        else:
            return False
