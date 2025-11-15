# HA-Integration Eiswarner

**Smartes Eiskratzen dank Eiswarnung** ❄️

Diese Integration warnt dich vor Frost/Ice-Bildung basierend auf Wetterdaten. Perfekt für den Winter!

## Features
- **Sensor**: Zeigt "Eiswarnung: Ja/Nein" + voraussichtliche Frost-Temperatur.
- **Schalter**: "Eiskratzen-Modus" für Automationen (z. B. Heizung voraktivieren).
- **Automatische Benachrichtigungen**: Push bei Frost (< 0°C + Feuchtigkeit > 80%).
- **Kompatibel**: Home Assistant 2025.1+, HACS-Ready.

## Installation
1. Über **HACS**: Suche "Eiswarner" in Integrationen.
2. Oder manuell: Kopiere `custom_components/eiswarner/` in `/config/custom_components/`.
3. **Voraussetzung**: Installiere OpenWeatherMap-Integration (Einstellungen → Geräte & Dienste).
4. Neustart HA → Füge "Eiswarner" hinzu (gib deinen OpenWeatherMap-Entity ein, z. B. `weather.openweathermap`).

## Konfiguration
- Im Setup: Wähle deinen Wetter-Sensor.
- Schwellenwerte: Frost < 0°C, Feuchtigkeit > 80% (anpassbar in Options).

## Credits
Erstellt von [@seebaer1976](https://github.com/seebaer1976) mit Hilfe von Grok. Basierend auf ChatGPT-Start.

![Eiswarnung Demo](https://via.placeholder.com/800x400?text=Eiswarnung+Aktiv+%F0%9F%98%B1)
