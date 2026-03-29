"""Eiswarner Sensoren – alle API-Felder als eigene Entities."""
from __future__ import annotations

import logging
from datetime import date, datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import EiswarnerCoordinator
from .const import (
    DOMAIN,
    FORECAST_ICE,
    FORECAST_ID_TO_TEXT,
    FORECAST_MAYBE_ICE,
)

_LOGGER = logging.getLogger(__name__)

# API-Code → Deutsche Bedeutung
API_CODE_MEANINGS_DE = {
    200: "Aufruf erfolgreich",
    300: "Geokoordinaten fehlen",
    400: "API Key fehlt",
    401: "API Key ungültig",
    402: "Tägliches Call-Limit erreicht",
}

# API-Code → Englische Bedeutung
API_CODE_MEANINGS_EN = {
    200: "Request successful",
    300: "Geo coordinates missing",
    400: "API key missing",
    401: "API key invalid",
    402: "Daily call limit reached",
}

# API message → Deutsche Übersetzung
API_MESSAGE_TRANSLATIONS = {
    "Request successful!": "Anfrage erfolgreich!",
    "API key is missing!": "API Key fehlt!",
    "API key is invalid!": "API Key ungültig!",
    "Daily call limit reached!": "Tägliches Limit erreicht!",
    "Geo coordinates are missing!": "Geokoordinaten fehlen!",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Alle Sensor-Entities einrichten."""
    coordinator: EiswarnerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        EiswarnerForecastSensor(coordinator, entry),
        EiswarnerForecastIdSensor(coordinator, entry),
        EiswarnerCitySensor(coordinator, entry),
        EiswarnerForecastDateSensor(coordinator, entry),
        EiswarnerRequestDateSensor(coordinator, entry),
        EiswarnerCallsLeftSensor(coordinator, entry),
        EiswarnerCallsLimitSensor(coordinator, entry),
        EiswarnerCallsResetSensor(coordinator, entry),
        EiswarnerApiSuccessSensor(coordinator, entry),
        EiswarnerApiMessageSensor(coordinator, entry),
        EiswarnerApiCodeSensor(coordinator, entry),
    ])


class _EiswarnerBaseSensor(CoordinatorEntity, SensorEntity):
    """Basis-Klasse für alle Eiswarner-Sensoren."""

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


# ---------------------------------------------------------------------------
# Hauptsensoren
# ---------------------------------------------------------------------------

class EiswarnerForecastSensor(_EiswarnerBaseSensor):
    """Hauptsensor: Vorhersagetext."""

    _attr_icon = "mdi:car-defrost-front"
    _attr_name = "Eiswarnung"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "forecast")

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        forecast_id = self.coordinator.data.get("forecast_id")
        if forecast_id is None:
            return None
        return FORECAST_ID_TO_TEXT.get(
            forecast_id, self.coordinator.data.get("forecast_text")
        )

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        data = self.coordinator.data
        forecast_id = data.get("forecast_id")
        return {
            "is_ice_warning": forecast_id == FORECAST_ICE,
            "is_ice_possible": forecast_id in (FORECAST_ICE, FORECAST_MAYBE_ICE),
        }


class EiswarnerForecastIdSensor(_EiswarnerBaseSensor):
    """Vorhersage-ID: 0 = kein Eis, 1 = Eis, 2 = eventuell Eis."""

    _attr_icon = "mdi:numeric"
    _attr_name = "Vorhersage ID"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "forecast_id")

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("forecast_id")


class EiswarnerCitySensor(_EiswarnerBaseSensor):
    """Erkannter Ort zu den Koordinaten."""

    _attr_icon = "mdi:city"
    _attr_name = "Ort"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "city")

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("forecast_city")


class EiswarnerForecastDateSensor(_EiswarnerBaseSensor):
    """Datum für das die Vorhersage gilt."""

    _attr_icon = "mdi:calendar-month"
    _attr_name = "Vorhersage Datum"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "forecast_date")

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get("forecast_date")
        if not raw:
            return None
        try:
            d = date.fromisoformat(raw)
            return d.strftime("%d.%m.%Y")
        except ValueError:
            return raw


# ---------------------------------------------------------------------------
# Diagnose-Sensoren
# ---------------------------------------------------------------------------

class EiswarnerRequestDateSensor(_EiswarnerBaseSensor):
    """Zeitpunkt des letzten API-Abrufs."""

    _attr_icon = "mdi:clock-outline"
    _attr_name = "Letzter Abruf"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "request_date")

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get("request_date")
        if not raw:
            return None
        try:
            # API liefert "2026-03-28 13:53:52" → "28.03.2026 13:53:52"
            dt = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        except ValueError:
            return raw


class EiswarnerCallsLeftSensor(_EiswarnerBaseSensor):
    """Verbleibende API-Abfragen heute."""

    _attr_icon = "mdi:counter"
    _attr_name = "Abfragen verbleibend"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "calls_left")

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("calls_left")


class EiswarnerCallsLimitSensor(_EiswarnerBaseSensor):
    """Tägliches API-Limit."""

    _attr_icon = "mdi:speedometer"
    _attr_name = "Tägliches Limit"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "calls_limit")

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("calls_daily_limit")


class EiswarnerCallsResetSensor(_EiswarnerBaseSensor):
    """Sekunden bis zum Reset des API-Limits."""

    _attr_icon = "mdi:timer-refresh-outline"
    _attr_name = "Limit Reset in"
    _attr_native_unit_of_measurement = "s"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "calls_reset")

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("calls_reset_in_seconds")


class EiswarnerApiSuccessSensor(_EiswarnerBaseSensor):
    """API-Status: Anfrage erfolgreich oder nicht."""

    _attr_icon = "mdi:check-network-outline"
    _attr_name = "API Status"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "api_success")

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        return "OK" if self.coordinator.data.get("api_success") else "Fehler"


class EiswarnerApiMessageSensor(_EiswarnerBaseSensor):
    """API-Nachricht – übersetzt auf Deutsch."""

    _attr_icon = "mdi:message-text-outline"
    _attr_name = "API Nachricht"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "api_message")

    @property
    def native_value(self) -> str | None:
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get("api_message", "")
        # Übersetzung DE, fallback auf Original (EN)
        return API_MESSAGE_TRANSLATIONS.get(raw, raw)


class EiswarnerApiCodeSensor(_EiswarnerBaseSensor):
    """API-Antwortcode mit Bedeutung als Attribut."""

    _attr_icon = "mdi:identifier"
    _attr_name = "API Code"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "api_code")

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("api_code")

    @property
    def extra_state_attributes(self) -> dict:
        if not self.coordinator.data:
            return {}
        code = self.coordinator.data.get("api_code")
        return {
            "bedeutung": API_CODE_MEANINGS_DE.get(code, "Unbekannt"),
            "meaning": API_CODE_MEANINGS_EN.get(code, "Unknown"),
        }
