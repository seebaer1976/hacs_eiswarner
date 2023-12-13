"""Eiswarner"""
from __future__ import annotations

import asyncio
import datetime

import requests
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

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

def setup():
    # Importiere die API-Schlüssel und Koordinaten aus der configuration.yaml
    config_file = config.configuration.yaml
    config_data = config.load_yaml(config_file)
    api_key = config_data['sensor']['eiswarner']['api_key']
    latitude = config_data['sensor']['eiswarner']['latitude']
    longitude = config_data['sensor']['eiswarner']['longitude']

class Eiswarner(SensorEntity):
    """Eiswarner Sensor."""

    def __init__(self, config):
        super().__init__(config)
        self._api_key: str = config.get("api_key")
        self._latitude: float = config.get("latitude")
        self._longitude: float = config.get("longitude")

    @property
    def state(self) -> None:
        """Return the current state."""
        response = requests.get(
            "https://api.eiswarnung.de/v1/current?api_key={}".format(self._api_key)
        )
        if response.status_code == 200:
            data = response.json()
            return data["warning_level"]
        else:
            return None

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "warning_level"


class EiswarnerEntity(Entity):
    latitude = float
    longitude = float

    def __init__(self, hass: HomeAssistant, config: ConfigEntry):
        super().__init__(hass, config)
        self._date = None
        self._city = None
        self._left = None
        self._code = None
        self._state = None
        self._probability = None
        self._api_key: str = config.data.get("api_key")
        self._latitude: float = config.data.get("latitude")
        self._longitude: float = config.data.get("longitude")

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
