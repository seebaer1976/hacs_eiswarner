"""Eiswarner Sensor."""
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

from .const import (
    DOMAIN,
    CONF_FROST_THRESHOLD,
    CONF_HUMIDITY_THRESHOLD,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eiswarner sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    @callback
    def _async_update_data():
        """Update data from weather entity."""
        weather_state = hass.states.get(entry.data["weather_entity"])
        if not weather_state:
            return {"is_ice_warning": False, "frost_temp": None}

        temp = float(weather_state.attributes.get("temperature", 0))
        humidity = float(weather_state.attributes.get("humidity", 0))

        frost_threshold = entry.options.get(CONF_FROST_THRESHOLD, 0.0)
        humidity_threshold = entry.options.get(CONF_HUMIDITY_THRESHOLD, 80.0)

        is_ice = temp <= frost_threshold and humidity >= humidity_threshold
        return {"is_ice_warning": is_ice, "frost_temp": temp}

    coordinator["update_fn"] = _async_update_data
    coordinator_data = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="eiswarner",
        update_method=_async_update_data,
        update_interval=timedelta(minutes=15),  # Check every 15 min
    )

    await coordinator_data.async_config_entry_first_refresh()

    async_add_entities([EiswarnerSensor(coordinator_data, entry)])

class EiswarnerSensor(CoordinatorEntity, SensorEntity):
    """Eiswarner Sensor Entity."""

    _attr_name = "Eiswarnung"
    _attr_unique_id = "eiswarner_sensor"
    _attr_icon = "mdi:ice-cream"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "°C"

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry):
        """Initialize sensor."""
        super().__init__(coordinator)
        self._entry = entry

    @property
    def native_value(self):
        """Return sensor state."""
        data = self.coordinator.data
        if data["is_ice_warning"]:
            return data["frost_temp"]
        return None

    @property
    def extra_state_attributes(self):
        """Return entity attributes."""
        data = self.coordinator.data
        return {
            "is_ice_warning": data["is_ice_warning"],
            "frost_threshold": self._entry.options.get(CONF_FROST_THRESHOLD, 0.0),
        }
