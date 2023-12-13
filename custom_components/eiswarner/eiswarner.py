"""Eiswarner"""
from __future__ import annotations

import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from requests import get

DOMAIN = "eiswarner"


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([Eiswarner()])


class Eiswarner(SensorEntity):
    """Eiswarner Sensor."""
    latitude = float
    longitude = float

    def __init__(self, hass: HomeAssistant, config: ConfigEntry):
        super().__init__(hass, config)
        self._probability = None
        self._date = None
        self._city = None
        self._left = None
        self._code = None
        self._state = None

    @property
    def name(self) -> str:
        return "Eiswarner"

    @property
    def state(self) -> str:
        return self._state

    @property
    def status_code(self) -> int:
        return self._code

    @property
    def calls_left(self) -> int:
        return self._left

    @property
    def forecast_city(self) -> str:
        return self._city

    @property
    def forecast_date(self) -> datetime.datetime:
        return self._date

    @property
    def probability(self) -> float:
        return self._probability

    async def async_update(self):
        """Aktualisiert den Sensorwert."""
        # Sende eine API-Anfrage
        response = get(
            "https://api.eiswarnung.de",
            params={"key": self.hass.data["config"]["api_key"], "lat": self.latitude, "lng": self.longitude},
        )

        # Überprüfe den Antwortstatus
        if response.status_code != 200:
            raise ValueError(f"Fehler beim Abrufen von Daten von der API: {response.status_code}")

        # Verarbeite die Antwort
        data = response.json()

        # Extrahiere die Wahrscheinlichkeit einer Eisbildung
        if data["result"].get("probability"):
            self._probability = data["result"]["probability"]
        else:
            self._probability = None

        # Zeige die Wahrscheinlichkeit an
        self._state = f"Wahrscheinlichkeit für Eisbildung: {self._probability}%"
        self._code = data["code"]
        self._left = data["callsLeft"]
        self._city = data["result"]["forecastCity"]
        self._date = data["result"]["forecastDate"]
