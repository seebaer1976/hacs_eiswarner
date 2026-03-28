"""Eiswarner Binary Sensoren – Ja/Nein Aussagen aus der Vorhersage."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Binary Sensor Entities einrichten."""
    coordinator: EiswarnerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        EiswarnerIceBinarySensor(coordinator, entry),
        EiswarnerIcePossibleBinarySensor(coordinator, entry),
    ])


class _EiswarnerBaseBinary(CoordinatorEntity, BinarySensorEntity):
    """Basis-Klasse für Binary Sensoren."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EiswarnerCoordinator,
        entry: ConfigEntry,
        unique_suffix: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{unique_suffix}"
        self._attr_device_info = coordinator.device_info


class EiswarnerIceBinarySensor(_EiswarnerBaseBinary):
    """Sicheres Eis vorhergesagt (forecastId == 1)."""

    _attr_name = "Eis erwartet"
    _attr_device_class = BinarySensorDeviceClass.COLD
    _attr_icon = "mdi:snowflake-alert"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "ice_warning")

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("forecast_id") == FORECAST_ICE


class EiswarnerIcePossibleBinarySensor(_EiswarnerBaseBinary):
    """Eis möglich (forecastId == 1 oder 2)."""

    _attr_name = "Eis möglich"
    _attr_device_class = BinarySensorDeviceClass.COLD
    _attr_icon = "mdi:snowflake"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "ice_possible")

    @property
    def is_on(self) -> bool:
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("forecast_id") in (FORECAST_ICE, FORECAST_MAYBE_ICE)
