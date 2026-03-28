"""Eiswarner Switch – manueller Eiskratzen-Modus."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
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
    """Eiskratzen-Modus Switch.

    Schaltet sich automatisch ein wenn Eis vorhergesagt wird (forecastId 1 oder 2),
    kann aber manuell übersteuert werden. Kategorie CONFIG damit er unter
    'Steuerelemente' erscheint.
    """

    _attr_icon = "mdi:scraper"
    _attr_has_entity_name = True
    _attr_name = "Eiskratzen Modus"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: EiswarnerCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_switch"
        self._attr_device_info = coordinator.device_info
        self._manual_override: bool | None = None

    @property
    def is_on(self) -> bool:
        if self._manual_override is not None:
            return self._manual_override
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("forecast_id") in (FORECAST_ICE, FORECAST_MAYBE_ICE)

    async def async_turn_on(self, **kwargs) -> None:
        self._manual_override = True
        self.async_write_ha_state()
        self.hass.services.async_call(
            "persistent_notification", "create",
            {"title": "Eiswarner", "message": "Eiskratzen-Modus manuell aktiviert ❄️",
             "notification_id": "eiswarner_notification"},
        )

    async def async_turn_off(self, **kwargs) -> None:
        self._manual_override = False
        self.async_write_ha_state()

    def _handle_coordinator_update(self) -> None:
        """Bei API-Update: manuelle Überschreibung zurücksetzen."""
        self._manual_override = None
        super()._handle_coordinator_update()

    @property
    def extra_state_attributes(self) -> dict:
        return {"manual_override": self._manual_override is not None}
