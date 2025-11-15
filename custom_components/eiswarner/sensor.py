"""Eiswarner Sensor mit API-Daten."""
import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eiswarner sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    await coordinator.async_start()

    sensor = EiswarnerSensor(coordinator, entry)
    async_add_entities([sensor])

class EiswarnerSensor(CoordinatorEntity, SensorEntity):
    """Eiswarner Sensor Entity."""

    _attr_name = "Eiswarnung"
    _attr_unique_id = "eiswarner_sensor"
    _attr_icon = "mdi:ice-cream"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "°C"

    def __init__(self, coordinator, entry: ConfigEntry):
        """Initialize sensor."""
        super().__init__(coordinator)
        self._entry = entry

    @property
    def native_value(self):
        """Return sensor state."""
        if self.coordinator.data.get("is_ice_warning"):
            return self.coordinator.data.get("temperature")
        return None

    @property
    def extra_state_attributes(self):
        """Return entity attributes."""
        data = self.coordinator.data
        return {
            "is_ice_warning": data.get("is_ice_warning"),
            "risk_level": data.get("risk_level"),
            "humidity": data.get("humidity"),
            "next_ice_time": data.get("forecast_time", "Morgen früh"),
        }
