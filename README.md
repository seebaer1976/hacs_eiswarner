<div align="center">

<img src="custom_components/eiswarner/brand/icon.png" alt="Eiswarner Logo" width="200"/>

# Eiswarner ❄️

**Smartes Eiskratzen dank Eiswarnung für Home Assistant**

[![GitHub Release](https://img.shields.io/github/release/seebaer1976/hacs_eiswarner.svg?style=for-the-badge&color=0078d4)](https://github.com/seebaer1976/hacs_eiswarner/releases)
[![GitHub Issues](https://img.shields.io/github/issues/seebaer1976/hacs_eiswarner.svg?style=for-the-badge&color=orange)](https://github.com/seebaer1976/hacs_eiswarner/issues)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.1%2B-blue?style=for-the-badge&logo=home-assistant)](https://www.home-assistant.io)

</div>

---

## Was ist Eiswarner?

**Eiswarner** ist eine Home Assistant Custom Integration, die dich rechtzeitig vor vereisten Fahrzeugscheiben warnt – damit du nie wieder unvorbereitet zum Auto kommst. ❄️🚗

Die Integration nutzt die [eiswarnung.de REST API](https://www.eiswarnung.de/rest-api/), die auf Basis deiner Geokoordinaten und Wetterdaten von OpenWeatherMap die Wahrscheinlichkeit von Eisbildung für den nächsten Morgen berechnet.

---

## Features

- 🌡️ **Eiswarnung-Sensor** – Zeigt die aktuelle Vorhersage: `Kein Eis`, `Eventuell Eis` oder `Eis`
- 🔀 **Eiskratzen-Modus Switch** – Schaltet sich automatisch ein wenn Eis vorhergesagt wird, kann aber auch manuell aktiviert werden
- 📍 **Automatische Standortermittlung** – Nutzt den in Home Assistant konfigurierten Standort oder manuelle Koordinaten
- 📊 **Diagnose-Attribute** – Zeigt verbleibende API-Calls, letzten Abruf und tägliches Limit
- ⚙️ **Konfigurierbares Intervall** – Abfrageintervall über die UI anpassbar (Standard: 30 Minuten)
- 🔔 **Push-Benachrichtigung** – Beim manuellen Aktivieren des Eiskratzen-Modus wird eine persistente Benachrichtigung ausgelöst

---

## Voraussetzungen

- Home Assistant **2025.1** oder neuer
- HACS installiert (für HACS-Installation)
- Kostenloser **API-Key** von [eiswarnung.de](https://www.eiswarnung.de/get-api/) *(bis zu 50 Abfragen/Tag kostenlos)*

---

## Installation

### Option 1: Über HACS (empfohlen)

#### Schritt 1 – Repository als Custom Repository hinzufügen

Klicke auf den Button oder folge der manuellen Anleitung darunter:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=seebaer1976&repository=hacs_eiswarner&category=integration)

**Oder manuell:**
1. HACS öffnen
2. Oben rechts auf die **drei Punkte** klicken → **„Benutzerdefinierte Repositories"**
3. URL eingeben: `https://github.com/seebaer1976/hacs_eiswarner`
4. Kategorie: **Integration** wählen
5. **„Hinzufügen"** klicken

#### Schritt 2 – Integration installieren

1. In HACS nach **„Eiswarner"** suchen
2. **„Herunterladen"** klicken
3. Home Assistant **neu starten**

#### Schritt 3 – Integration einrichten

Klicke auf den Button oder gehe manuell zu Einstellungen → Geräte & Dienste:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=eiswarner)

**Oder manuell:**
1. **Einstellungen** → **Geräte & Dienste** → **„Integration hinzufügen"**
2. Nach **„Eiswarner"** suchen
3. API-Key eingeben und Standort auswählen

---

### Option 2: Manuelle Installation

1. Lade die [neueste Version](https://github.com/seebaer1976/hacs_eiswarner/releases/latest) herunter
2. Entpacke das Archiv
3. Kopiere den Ordner `custom_components/eiswarner/` in dein HA-Konfigurationsverzeichnis:
   ```
   /config/custom_components/eiswarner/
   ```
4. Home Assistant **neu starten**
5. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen → Eiswarner**

---

## Konfiguration

### Setup

| Feld | Beschreibung |
|------|-------------|
| `**API-Key** `| Dein kostenloser Key von [eiswarnung.de/get-api](https://www.eiswarnung.de/get-api/) |
| `**HA-Standort verwenden**` | Nutzt automatisch die in HA konfigurierten Koordinaten |
| `**Breitengrad / Längengrad** `| Manuelle Koordinaten (nur wenn HA-Standort deaktiviert) |

### Optionen (nach der Einrichtung)

Über das **Zahnrad-Symbol** am Integrationseintrag:

| Option | Standard | Beschreibung |
|--------|---------|-------------|
| `**Aktualisierungsintervall**` | 1800 s | Abfrageintervall in Sekunden (min. 300, max. 86400) |

> 💡 **Tipp:** Laut eiswarnung.de sind Abfragen **8–10 Stunden vor dem Morgen** am genauesten. Eine Automation um 22:00 Uhr ist ideal.

---

## Entitäten

| Entität | Typ | Beschreibung |
|---------|-----|-------------|
| `sensor.eiswarnung` | Sensor | Vorhersage: `Kein Eis` / `Eventuell Eis` / `Eis` |
| `switch.eiskratzen_modus` | Switch | Automatisch EIN bei Eis-Vorhersage, manuell überschreibbar |

### Sensor-Attribute

| Attribut | Beschreibung |
|----------|-------------|
| `forecast_id` | Rohwert: `0` = kein Eis, `1` = Eis, `2` = eventuell Eis |
| `is_ice_warning` | `true` wenn Eis sicher vorhergesagt |
| `is_ice_possible` | `true` wenn Eis oder eventuell Eis |
| `forecast_city` | Erkannter Ort für die Koordinaten |
| `forecast_date` | Datum für das die Vorhersage gilt |
| `calls_left` | Verbleibende API-Abfragen heute |

---

## Beispiel-Automation

Push-Benachrichtigung jeden Abend um 22:00 Uhr wenn Eis vorhergesagt wird:

```yaml
automation:
  - alias: "Eiswarnung Abend-Benachrichtigung"
    trigger:
      - platform: time
        at: "22:00:00"
    condition:
      - condition: state
        entity_id: sensor.eiswarnung
        state: "Eis"
    action:
      - service: notify.mobile_app_dein_handy
        data:
          title: "❄️ Eiswarnung!"
          message: "Morgen früh ist mit Eis zu rechnen. Denk ans Eiskratzen!"
```

---

## API-Informationen

Die Integration nutzt die [eiswarnung.de REST API](https://www.eiswarnung.de/rest-api/):

- **Kostenlos:** bis zu **50 Abfragen/Tag**
- **Methode:** POST an `https://api.eiswarnung.de/`
- **API-Key:** kostenlos registrieren unter [eiswarnung.de/get-api](https://www.eiswarnung.de/get-api/)

---

## Changelog

### v2.0.0
- Komplette Neuentwicklung mit echtem `DataUpdateCoordinator`
- Korrekte Anbindung der eiswarnung.de API (POST, echte Felder)
- Device-Seite mit Sensor + Switch
- Config Flow + Options Flow
- HACS-kompatibel mit Brand-Icon

---

## Credits

Erstellt von [@seebaer1976](https://github.com/seebaer1976)  
API bereitgestellt von [eiswarnung.de](https://www.eiswarnung.de) – vielen Dank! ❄️

---

<div align="center">

Wenn dir die Integration gefällt, freue ich mich über einen ⭐ auf GitHub!

</div>
