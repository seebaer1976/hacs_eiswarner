"""Eiswarner Switch – manueller Eiskratzen-Modus."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EiswarnerCoordinator
from .const import DOMAIN, FORECAST_ICE, FORECAST_MAYBE_ICE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Switch-Entity einrichten."""
    coordinator: EiswarnerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EiswarnerSwitch(coordinator, entry)])


class EiswarnerSwitch(CoordinatorEntity, SwitchEntity):
    """Switch-Entity für den Eiskratzen-Modus.

    Schaltet sich automatisch ein wenn Eis vorhergesagt wird,
    kann aber auch manuell übersteuert werden.
    Nutzt CoordinatorEntity damit der Zustand bei Updates
    automatisch aktualisiert wird.
    """

    _attr_icon = "mdi:scraper"
    _attr_has_entity_name = True
    _attr_name = "Eiskratzen Modus"

    def __init__(self, coordinator: EiswarnerCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_switch"
        self._manual_override: bool | None = None  # None = automatisch

    @property
    def is_on(self) -> bool:
        """Eingeschaltet wenn Eis vorhergesagt oder manuell aktiviert."""
        if self._manual_override is not None:
            return self._manual_override
        if not self.coordinator.data:
            return False
        forecast_id = self.coordinator.data.get("forecast_id")
        return forecast_id in (FORECAST_ICE, FORECAST_MAYBE_ICE)

    async def async_turn_on(self, **kwargs) -> None:
        """Manuell einschalten."""
        self._manual_override = True
        self.async_write_ha_state()
        self._send_notification("Eiskratzen-Modus manuell aktiviert ❄️")

    async def async_turn_off(self, **kwargs) -> None:
        """Manuell ausschalten (übersteuert auch die automatische Aktivierung)."""
        self._manual_override = False
        self.async_write_ha_state()

    def _handle_coordinator_update(self) -> None:
        """Bei neuem API-Update: manuelle Überschreibung zurücksetzen."""
        self._manual_override = None
        super()._handle_coordinator_update()

    def _send_notification(self, message: str) -> None:
        """Persistente Benachrichtigung senden."""
        self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Eiswarner",
                "message": message,
                "notification_id": "eiswarner_notification",
            },
        )

    @property
    def extra_state_attributes(self) -> dict:
        """Zeigt ob der Zustand automatisch oder manuell gesetzt ist."""
        return {
            "manual_override": self._manual_override is not None,
        }
