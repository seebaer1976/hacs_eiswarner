"""Eiswarner Switch (unverändert, aber triggert bei API-Warnung)."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eiswarner switches."""
    switch = EiswarnerSwitch(hass, entry)
    async_add_entities([switch])

class EiswarnerSwitch(SwitchEntity):
    """Eiswarner Switch Entity."""

    _attr_name = "Eiskratzen Modus"
    _attr_unique_id = "eiswarner_switch"
    _attr_icon = "mdi:scraper"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize switch."""
        self._hass = hass
        self._entry = entry
        self._state = False

    @property
    def is_on(self) -> bool:
        """Return true if on."""
        return self._state

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the switch."""
        self._state = True
        coordinator = self._hass.data[DOMAIN][self._entry.entry_id]["coordinator"]
        data = coordinator.data
        message = f"Eiskratzen-Modus aktiviert! Risiko: {data.get('risk_level', 'Unbekannt')} ❄️"
        self._hass.services.async_call(
            "notify",
            "persistent_notification",
            {"message": message},
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the switch."""
        self._state = False
        self.async_write_ha_state()
