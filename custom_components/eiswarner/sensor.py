from datetime import timedelta

import requests
from homeassistant.helpers.event import async_track_time_interval

from const import DOMAIN
from entity import EiswarnerEntity


async def update(hass, sensor):
    """Aktualisiert den Sensorwert."""
    await sensor.async_update(hass)
    interval = timedelta(hours=1)
    async_track_time_interval(hass, lambda now: update(hass, sensor), interval)


class EiswarnerSensor(EiswarnerEntity):
    def __init__(self):
        super().__init__()

    async def async_update(self, hass):
        for entry in hass.config_entries.async_entries(DOMAIN):
            api_key = entry.data.get("api_key")
            longitude = entry.data.get("longitude")
            latitude = entry.data.get("latitude")

            url = "https://api.eiswarnung.de"
            payload = {'key': api_key, 'lat': latitude, 'lng': longitude}

            try:
                response = requests.get(url, params=payload)
                response.raise_for_status()
                data = response.json()

                if data["success"] and data["code"] == 200:
                    self._state = data["result"]["forecastText"]
                    self._code = data["code"]
                    self._left = data["callsLeft"]
                    self._city = data["result"]["forecastCity"]
                    self._date = data["result"]["forecastDate"]
                else:
                    self._state = None
                    print("UNKNOWN STATUS")

            except requests.exceptions.RequestException as e:
                self._state = None
                print(f"Error: {e}")

        await update(hass, self)
        return True
