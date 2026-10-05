# Betriebsanleitung AUDI Climate Cube

Diese Anleitung beschreibt den vorgesehenen Betrieb der Climate-Cube-Software
auf Raspberry Pi Picos mit CircuitPython, LoRa-Erweiterung, SD-Karte und SEN66.
Sie gilt fuer den aktuellen Projektstand und ersetzt keine Sicherung vor
Hardware- oder Softwareaenderungen.

## 1. Systemueberblick

Ein Climate Cube ist entweder ein **Slave** oder ein **Master**.

| Rolle | Aufgabe |
|---|---|
| Slave | misst im 15-Minuten-Rhythmus, speichert lokal auf SD und sendet per LoRa an den Master |
| Master | misst selbst, empfaengt Slave-Daten, bestaetigt sie per ACK und speichert sie zentral auf SD |
| Relay (optional) | ist ein Slave im `mesh`-Modus und leitet Daten und ACKs entlang einer fest konfigurierten Kette weiter |

Der normale Startmodus ist `star`: Jeder Slave sendet direkt an M01. Im
`mesh`-Modus gibt es keine automatische Wegsuche. Jeder naechste Hop wird in
der jeweiligen `config.json` fest eingetragen.

## 2. Voraussetzungen

Pro Geraet werden benoetigt:

- Raspberry Pi Pico mit installierter CircuitPython-Firmware,
- LoRa-Antenne am SX1262-Modul,
- SD-Karte fuer den regulären Betrieb,
- SEN66 fuer Luftmesswerte,
- USB-Datenkabel oder eine geeignete Stromversorgung,
- eine eindeutige Geraete-ID, zum Beispiel `C01` oder `M01`.

Das OLED ist fuer den Kernbetrieb nicht erforderlich. Keine SD-Karte darf
waehrend des Betriebs entfernt werden.

## 3. Sicherung Vor Aenderungen

1. Geraet vollstaendig ausschalten.
2. Den Inhalt von `CIRCUITPY` und der SD-Karte getrennt pro Geraet sichern.
3. Insbesondere `config.json`, `data/`, `diagnostics/`,
   `climate_state.json` und bei Slaves `pending_records.jsonl` sichern.
4. Erst danach Softwaredateien oder Konfiguration aendern.

Sicherungen bleiben lokal und werden nicht in Git eingecheckt.

## 4. Dateien Auf Den Pico Uebertragen

CircuitPython startet `/code.py` auf dem Laufwerk `CIRCUITPY` automatisch.
Der zusammengehoerige Programmstand muss in derselben Struktur auf dem Pico
liegen:

```text
CIRCUITPY/
|-- code.py
|-- config.json
|-- adapters/
|-- application/
|-- domain/
|-- ports/
`-- lib/
```

Bei einem `MemoryError` werden die eigenen Projektmodule als passende `.mpy`
Dateien installiert. Dafuer gibt es getrennte Firmwarepakete fuer RP2040 und
RP2350 unter `firmware/`; sie duerfen nicht zwischen den Geraetetypen gemischt
werden. Gleichnamige `.py`- und `.mpy`-Dateien duerfen nicht gleichzeitig im
selben Pfad liegen. Details und der reproduzierbare Build stehen in
[`firmware/README.md`](../firmware/README.md).

Beim Update immer alle geaenderten Dateien eines zusammengehoerigen Standes
uebertragen. Besonders wichtig sind bei diesem Stand:

```text
code.py
adapters/clock.py
adapters/configuration.py
adapters/sd_storage.py
application/master_controller.py
application/slave_controller.py
domain/measurement.py
domain/plausibility.py
ports/contracts.py
```

Danach das Geraet sicher auswerfen, die Stromversorgung kurz trennen und neu
starten. Die SD-Messdaten und die echte `config.json` werden nicht durch
Beispieldateien ersetzt.

## 5. Konfiguration

Die Vorlagen im Repository sind:

```text
config.example.json                 Slave im Sternnetz
config.master.example.json          Master im Sternnetz
config.mesh.example.json            End-Slave einer Mesh-Kette
config.mesh.relay.example.json      Relay-Slave
config.mesh.relay-c01.example.json  Relay C01
config.mesh.master.example.json     Master einer Mesh-Kette
```

Die passende Vorlage wird als `/config.json` auf das zugehoerige
`CIRCUITPY`-Laufwerk kopiert und danach angepasst.

### 5.1 Mindestangaben Fuer Einen Slave

```json
{
  "role": "slave",
  "device_id": "C01",
  "network_mode": "star",
  "master_id": "M01",
  "time_epoch_utc": 1780000000,
  "measurement_interval_s": 900
}
```

### 5.2 Mindestangaben Fuer Einen Master

```json
{
  "role": "master",
  "device_id": "M01",
  "network_mode": "star",
  "monitored_slaves": ["C01", "C02"],
  "time_epoch_utc": 1780000000,
  "measurement_interval_s": 900
}
```

`time_epoch_utc` ist eine Unixzeit in UTC. Unter Linux wird ein aktueller Wert
so ermittelt:

```sh
date -u +%s
```

Der Wert wird als Zahl ohne Anfuehrungszeichen eingetragen. Beim ersten Start
ohne bisherige Messdaten ist er erforderlich.

### 5.3 Mesh-Konfiguration

Beispielkette:

```text
C03 -> C02 -> C01 -> M01
```

Dann verwendet C03 `next_hop_id: "C02"`, C02 `next_hop_id: "C01"` und C01
`next_hop_id: "M01"`. M01 enthaelt C01, C02 und C03 in `monitored_slaves` und
kennt die Rueckwege in `return_next_hops`. Die fertigen Mesh-Vorlagen sind als
Ausgangspunkt zu verwenden; keine IDs oder Wege nur auf einem einzelnen
Geraet aendern.

### 5.4 Funkparameter Und Plausibilitaet

Alle Geraete einer Funkgruppe muessen dieselben Werte unter `radio` verwenden.
Die Entwicklungswerte sind in den Vorlagen eingetragen.

`plausibility_limits` bleibt leer, bis fachlich bestätigte Sensorgrenzen
vorliegen. Ein spaeterer Eintrag sieht beispielsweise so aus:

```json
"plausibility_limits": {
  "co2_ppm": {"min": 400, "max": 10000}
}
```

Werte ausserhalb eines eingetragenen Bereichs werden nicht geloescht. Sie
erhalten nur das Statusflag `MEASUREMENT_IMPLAUSIBLE`.

## 6. Normaler Start

1. SD-Karte und LoRa-Antenne anschliessen.
2. M01 einschalten und OLED oder Konsolenausgabe pruefen.
3. Warten, bis SD, LoRa und SEN66 initialisiert sind.
4. Slaves einschalten. Bei Mesh zuerst M01, dann die Relays von oben nach
   unten und zuletzt den End-Slave starten.
5. Nach der SEN66-Aufwaermzeit dauert die erste vollständige Messung
   normalerweise etwa 65 Sekunden.

Erwartete Startmeldungen sind unter anderem:

```text
SD card ready
LoRa ready
SEN66 initialized
master M01 started
slave C01 started
```

Ein Slave sendet beim Start einmal `DEVICE_RESTARTED`. Das ist bei einem
bewussten Einschalten erwartbar. Weitere Neustart-Ereignisse ohne geplante
Stromunterbrechung sind im Stabilitaetstest auffaellig.

## 7. Was Im Betrieb Passiert

### Slave

1. Erfasst die Messwerte.
2. Speichert den Datensatz auf der eigenen SD-Karte.
3. Sendet alle noch ausstehenden Datensaetze in Sequenzreihenfolge.
4. Wartet je Datensatz auf ein ACK des Masters.
5. Bei fehlendem ACK bleiben dieser und alle neueren Datensaetze ausstehend
   und werden im naechsten Zyklus erneut versucht.

Ist die Slave-SD beim Start nicht lesbar oder tritt ein Schreibfehler auf,
arbeitet der Slave begrenzt im RAM weiter und fragt seine Sequenznummer beim
Master ab. Dieser Zustand ist ein Fehlerfall und kein Ersatz fuer das lokale
Jahresbackup.

### Master

1. Fuehrt eigene SEN66-Messungen aus.
2. Bleibt fuer Slave-Pakete empfangsbereit.
3. Speichert einen empfangenen Datensatz zuerst zentral auf SD.
4. Sendet erst danach das ACK.
5. Schreibt alle 15 Minuten fuer fehlende ueberwachte Slaves vorlaeufige
   `NO_PACKET`-Zeilen. Eine eindeutig nachgelieferte Messung ersetzt diese
   Zeile wieder.

## 8. Dateien Und Auswertung

Die Messdateien liegen auf der SD-Karte unter:

```text
/sd/data/C01/measurements_000000-002999.csv
/sd/data/M01/measurements_000000-002999.csv
/sd/diagnostics/C01/events.csv
```

Die Master-CSV besitzt pro Messung genau eine Zeile. Sie enthaelt neben den
Messwerten unter anderem:

| Feld | Bedeutung |
|---|---|
| `sequence_number` | chronologische Reihenfolge je Geraet |
| `receive_status` | `0` fuer gespeichert, `NO_PACKET` fuer eine noch offene Luecke |
| `restart_count` | Neustarts mit Bezug auf diese Messung |
| `sd_write_error_count` | lokale Slave-SD-Schreibfehler mit Bezug auf diese Messung |
| `diagnostics` | weitere zusammengefasste Ereignisse, zum Beispiel `SEN66_ERROR:1` |
| `status_flags` | vierstellige Hexadezimalzahl fuer Mess-, Zeit- und Speicherzustand |

Die vollstaendige Ereignishistorie bleibt in `diagnostics/<device_id>/events.csv`.
In Excel kann die Master-CSV direkt fuer Diagramme verwendet werden: Zeit und
Messwertspalte auswaehlen; Diagnosefelder bleiben feste Zusatzspalten und
erzeugen keine eigenen Zwischenzeilen.

### Wichtige Statusflags

| Wert | Bedeutung |
|---|---|
| `0001` | SEN66-Messfehler |
| `0002` | DS18B20-Bodentemperaturfehler |
| `0008` | Slave-SD nicht verfuegbar |
| `0010` | Slave-SD-Schreibfehler |
| `0020` | mindestens ein erwarteter Messwert fehlt |
| `0040` | Zeit aus CSV fortgesetzt; Reihenfolge nutzbar, UTC nicht garantiert |
| `0080` | Wert ausserhalb konfigurierter Plausibilitaetsgrenze |

## 9. Neustart Und Zeit

Nach einem Neustart verwendet das Geraet die letzte eigene gueltige
`measurement_timestamp` aus der CSV und setzt die Zeit fuer die naechste
Messung um ein Intervall fort. Damit bleiben Tageswechsel und Diagramme
chronologisch. Der fortgesetzte Zeitwert bleibt sichtbar und traegt `0040`
(`TIME_UNSYNCED`), weil die reale ausgeschaltete Zeit nicht bekannt ist.

Ohne vorhandene CSV-Zeit wird `time_epoch_utc` aus der Konfiguration benutzt.
Weitere Details stehen in [Master_Messung_und_Zeit.md](Master_Messung_und_Zeit.md).

## 10. Stabilitaetstest

Vor einem 24-Stunden-Test Startzeit, Sequenznummern, Aufstellorte und
Konfiguration notieren. Erwartet werden 96 Messintervalle je Geraet. Nach dem
Test pruefen:

- fortlaufende Sequenznummern ohne Duplikate,
- keine unerwarteten Neustarts,
- keine dauerhaften `NO_PACKET`-Luecken,
- keine SD- oder SEN66-Fehler,
- lesbare CSV-Dateien und passende Diagnoseereignisse,
- Zeitfolge auch ueber Mitternacht.

Die sichere Entscheidung zwischen Test ohne Reset und neuem Testlauf ab
Sequenz 0 steht in [Reset_Stabilitaetstest.md](Reset_Stabilitaetstest.md).

## 11. Fehlersuche

| Beobachtung | Erste Pruefung |
|---|---|
| OLED bleibt leer | USB-Stromversorgung, `code.py`, OLED-Kabel und Konsolenausgabe pruefen; Kernbetrieb kann trotzdem laufen |
| `ACK missing for sequence ...` | Master eingeschaltet, Antennen, gleiche Funkparameter, Route und Abstand/Metallhindernisse pruefen |
| `SLAVE_SD_UNAVAILABLE` | Geraet ausschalten, SD-Karte, Kartenleser und Dateisystem pruefen; nicht im Betrieb ziehen |
| `Error 5` | Vollstaendige Meldung sichern, SD-Karte sichern und getrennt testen; keine Daten loeschen |
| `LoRa receive setup failed: -1` | Stromversorgung, SX1262-Verbindung, Antenne und Neustart pruefen; Fehler im Testprotokoll notieren |
| `TIME_UNSYNCED` | nach Neustart erwartbar, wenn Zeit aus CSV fortgesetzt wurde; bei frischem Reset aktuellen `time_epoch_utc` setzen |
| keine neue Messung sichtbar | SEN66-Aufwaermzeit abwarten, CSV-Pfad und passende Geraete-ID pruefen |

Bei einem auffaelligen Fehler nicht sofort mehrere Kabel, Konfigurationen und
Softwaredateien gleichzeitig aendern. Erst Ausgangszustand, genaue Meldung,
Uhrzeit und betroffene Sequenznummer notieren.

## 12. Weiterfuehrende Dokumente

- [Datenformat_V1_Entwurf.md](Datenformat_V1_Entwurf.md): Felder, Statusflags und Speicherformat.
- [Reset_Stabilitaetstest.md](Reset_Stabilitaetstest.md): sicherer Start eines neuen Testlaufs.
- [Testprotokoll_Mesh_Stabilitaet_2026-09-17.md](Testprotokoll_Mesh_Stabilitaet_2026-09-17.md): bisherige Mesh-Beobachtungen.
- [Pflichtenheft_AUDI_Climate_Cube.md](Pflichtenheft_AUDI_Climate_Cube.md): Anforderungen und technische Entscheidungen.
