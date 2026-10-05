# Reset Fuer Einen Sauberen Stabilitaetstest

Zweck: Einen neuen, klar abgegrenzten Stabilitaetstest vorbereiten, ohne
Sequenzstand, Warteschlange, Zeitfortsetzung und CSV-Dateien gegeneinander
inkonsistent zu machen.

Diese Anleitung betrifft nur bewusst vorbereitete Testlaeufe. Messdaten eines
echten Einsatzes werden nicht geloescht.

## Entscheidung Vor Dem Start

### Variante A: Dauerlauf Ohne Reset

Diese Variante ist fuer den normalen weiteren Betrieb vorzuziehen.

- Bestehende Daten, Sequenznummern und Zeitfortsetzung bleiben erhalten.
- Vor dem Test nur Startzeit sowie letzte Sequenznummer je Geraet notieren.
- Nach dem Test die neuen Datensaetze anhand der notierten Startwerte
  auswerten.

Sie ist besonders geeignet, wenn die bisherigen Daten nicht nur Testdaten
sind oder bereits eine laengere chronologische Zeitreihe besteht.

### Variante B: Neuer Testlauf Ab Sequenz 0

Diese Variante erzeugt eine vollstaendig neue Testreihe. Sie ist nur sinnvoll,
wenn alle beteiligten Geraete gemeinsam zurueckgesetzt werden und vorher eine
Sicherung existiert.

## Variante B Schritt Fuer Schritt

### 1. Testumfang Festlegen

Vor dem Ausschalten notieren:

- Testname, Datum und geplante Laufzeit, zum Beispiel 24 Stunden.
- Beteilige Geraete und Route, zum Beispiel `C03 -> C02 -> C01 -> M01`.
- Aktuelle `device_id`, Rolle und verwendete `config.json` jedes Geraets.
- Letzte Sequenznummer und letzten Dateinamen je Geraet.

Alle Geraete, die an diesem Test beteiligt sind, werden zusammen behandelt.
Ein Reset nur des Masters oder nur eines Slaves erzeugt keinen sauberen
Testbeginn.

### 2. Alle Geraete Ausschalten

1. Jeden Pico von USB, Akku und Netzteil trennen.
2. Warten, bis OLED und LEDs aus sind.
3. Erst dann die SD-Karten entnehmen oder als USB-Laufwerk einbinden.

Die SD-Karte wird niemals waehrend eines laufenden Schreibvorgangs entfernt.

### 3. Vollstaendige Sicherung Erstellen

Fuer **jedes** Geraet einen getrennten lokalen Sicherungsordner anlegen, zum
Beispiel:

```text
ClimateCube_Sicherungen/Stabilitaetstest_vor_Reset_2026-09-24/C01/
ClimateCube_Sicherungen/Stabilitaetstest_vor_Reset_2026-09-24/C02/
ClimateCube_Sicherungen/Stabilitaetstest_vor_Reset_2026-09-24/C03/
ClimateCube_Sicherungen/Stabilitaetstest_vor_Reset_2026-09-24/M01/
```

Den **gesamten Inhalt** der jeweiligen SD-Karte in den passenden Ordner
kopieren. Anschliessend pruefen, dass mindestens diese Dateien oder Ordner in
der Sicherung enthalten sind:

```text
data/
diagnostics/
climate_state.json
climate_state.json.bak
pending_records.jsonl          (bei Slaves, falls vorhanden)
config.json
```

Vorhandene Altdateien wie `slave_measurements.csv`,
`master_measurements.csv` und deren `.pre_v1`-Archive ebenfalls sichern.
Sicherungen werden nicht in das Git-Repository aufgenommen.

### 4. Aktiven Laufzeit-Zustand Entfernen

Nach der erfolgreichen Sicherung auf **jeder beteiligten SD-Karte** nur diese
aktiven Laufzeitdaten loeschen:

```text
data/
diagnostics/
climate_state.json
climate_state.json.bak
pending_records.jsonl
slave_measurements.csv
master_measurements.csv
slave_measurements.csv.pre_v1
master_measurements.csv.pre_v1
```

`pending_records.jsonl` existiert normalerweise nur auf Slaves. Nicht
vorhandene Dateien werden einfach uebersprungen.

**Nicht loeschen:**

```text
config.json
code.py
lib/
boot_out.txt
```

Die Testdaten muessen nicht dauerhaft geloescht werden: Nach Abschluss der
externen Sicherung duerfen sie alternativ in einen nicht von der Software
verwendeten Ordner wie `/sd/archive_vor_reset/` verschoben werden. Die externe
Sicherung auf dem Laptop bleibt trotzdem die verbindliche Rueckfallkopie.

### 5. Konfiguration Pruefen

Vor dem Wiedereinschalten auf jedem Geraet pruefen:

- richtige Rolle und `device_id`,
- richtige `master_id`, `next_hop_id` und `hop_limit` bei Mesh,
- auf M01 vollstaendige `monitored_slaves`,
- aktueller `time_epoch_utc`-Wert.

Weil nach dem Reset keine CSV-Zeit existiert, verwendet das Geraet beim ersten
Start wieder `time_epoch_utc`. Der Wert sollte daher unmittelbar vor dem Test
aktuell gesetzt werden.

### 6. Testlauf Starten

1. Zuerst M01 einschalten und den erfolgreichen Start von SD, LoRa und Sensor
   pruefen.
2. Danach die Slaves entsprechend der geplanten Route einschalten.
3. Bei jedem Slave ist beim bewussten Start genau ein `DEVICE_RESTARTED`
   Ereignis erwartbar.
4. Die erste gespeicherte Messung jedes Geraets kontrollieren: Sequenz `0`,
   passende CSV-Kopfzeile und keine unerwarteten Fehlerflags.
5. Startzeit, Startsequenz und Aufstellort im Testprotokoll notieren.

## Abbruch Und Wiederherstellung

Den Test abbrechen und den Zustand sichern, wenn ein nicht erwarteter Neustart,
`SLAVE_SD_WRITE_ERROR`, `SLAVE_SD_UNAVAILABLE`, wiederholter `SEN66_ERROR`,
dauerhaftes `NO_PACKET` oder ein LoRa-Fehler auftritt.

Um einen vor dem Reset gesicherten Stand wiederherzustellen:

1. Alle Geraete vollstaendig ausschalten.
2. Aktive Testdaten nach demselben Muster wie in Schritt 4 entfernen oder
   separat sichern.
3. Nur die Sicherung des passenden Geraets zurueck auf dessen SD-Karte
   kopieren.
4. `config.json` vor dem Einschalten auf die zu dieser Sicherung passende
   Rolle und Geraete-ID pruefen.

Keine Dateien verschiedener Geraete oder verschiedener Zeitpunkte mischen.
Insbesondere `climate_state.json`, `pending_records.jsonl` und `data/` muessen
immer aus derselben Sicherung stammen.

## Warum Kein Reset-Skript Auf Dem Pico?

Ein Skript auf dem Pico koennte ohne sichtbare Sicherheitsabfrage Daten eines
echten Einsatzes loeschen. Der manuelle Ablauf mit ausgeschaltetem Geraet,
vollstaendiger Sicherung und gemeinsamer Behandlung aller Testgeraete ist fuer
dieses Projekt sicherer und nachvollziehbarer.
