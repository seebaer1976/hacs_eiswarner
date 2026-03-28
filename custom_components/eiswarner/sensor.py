"""Eiswarner Sensor – zeigt Eiswahrscheinlichkeit."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EiswarnerCoordinator
from .const import (
    DOMAIN,
    FORECAST_ICE,
    FORECAST_ID_TO_TEXT,
    FORECAST_MAYBE_ICE,
    FORECAST_NO_ICE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensor-Entity einrichten."""
    coordinator: EiswarnerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EiswarnerSensor(coordinator, entry)])


class EiswarnerSensor(CoordinatorEntity, SensorEntity):
    """Sensor-Entity für die Eiswarnung.

    Zustand = Vorhersagetext (z.B. "Kein Eis", "Eis", "Eventuell Eis").
    Zusätzliche Attribute enthalten alle weiteren API-Felder.
    """

    _attr_icon = "mdi:car-defrost-front"
    _attr_has_entity_name = True
    _attr_name = "Eiswarnung"

    def __init__(self, coordinator: EiswarnerCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        # Unique ID pro Config-Entry (unterstützt mehrere Standorte)
        self._attr_unique_id = f"{entry.entry_id}_sensor"
        self._entry = entry

    @property
    def native_value(self) -> str | None:
        """Zustand: Vorhersagetext aus der API."""
        if not self.coordinator.data:
            return None
        forecast_id = self.coordinator.data.get("forecast_id")
        if forecast_id is None:
            return None
        return FORECAST_ID_TO_TEXT.get(forecast_id, self.coordinator.data.get("forecast_text"))

    @property
    def extra_state_attributes(self) -> dict:
        """Alle verfügbaren API-Felder als Attribute."""
        if not self.coordinator.data:
            return {}
        data = self.coordinator.data
        forecast_id = data.get("forecast_id")
        return {
            "forecast_id": forecast_id,
            "is_ice_warning": forecast_id == FORECAST_ICE,
            "is_ice_possible": forecast_id in (FORECAST_ICE, FORECAST_MAYBE_ICE),
            "forecast_text": data.get("forecast_text"),
            "forecast_city": data.get("forecast_city"),
            "forecast_date": data.get("forecast_date"),
            "request_date": data.get("request_date"),
            "calls_left": data.get("calls_left"),
            "calls_daily_limit": data.get("calls_daily_limit"),
        }
