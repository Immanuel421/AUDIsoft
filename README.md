# AUDI Climate Cube

Softwareprojekt zur Messdatenerfassung, lokalen Sicherung und direkten LoRa-Kommunikation zwischen Climate Cubes im Rahmen des Pflichtpraktikums bei der AUDI Umweltstiftung.

## Projektziel

Mehrere Slave-ClimateCubes sollen Messdaten im vorgesehenen 15-Minuten-Rhythmus erfassen, lokal auf SD-Karte sichern und per LoRa Peer-to-Peer an einen Master senden. Der genaue Uebertragungszeitpunkt und ein genauer absoluter Messzeitpunkt sind unkritisch; die chronologische Ordnung wird je Slave durch eine persistente Sequenznummer hergestellt. Der Master soll die Daten der Slaves zentral speichern. Jeder Slave muss mindestens 35.040 Messdatensätze eines Jahres lokal als Backup aufnehmen können; der Master muss bei zehn Slaves mindestens 350.400 Datensätze zuzüglich Sicherheitsreserve speichern können. Als nachzuweisende Zielgroesse wurden ungefaehr zehn Slaves je Master genannt; dies ist keine softwareseitige Obergrenze. LoRaWAN soll wegen möglicher Einsatzorte ohne passende Infrastruktur nicht vorausgesetzt werden.

Der genaue fachliche und technische Umfang wird derzeit in Lasten- und Pflichtenheft festgelegt. Aussagen, die dort als offen oder als Entwurf gekennzeichnet sind, gelten noch nicht als freigegebene Anforderungen.

## Vorgehensweise

Das Projekt wird dokumentationsgeleitet bearbeitet:

1. Bestand und Anforderungen erfassen.
2. Lastenheft mit Rollen, Projektumfang und Abnahmeszenarien abstimmen.
3. Pflichtenheft mit Anwendungsfällen und technischer Erfüllung abstimmen.
4. Architektur, Schnittstellen, Datenformat und Testkonzept freigeben.
5. Erst danach die eigentliche Produktsoftware implementieren.
6. Anforderungen durch Tests nachweisen und das Ergebnis in Dokumentation und Abschluss-Paper auswerten.

Die bereits ausgeführten Hardware- und LoRa-Tests sind technische Voruntersuchungen und keine vorgezogene Festlegung der Produktarchitektur.

## Aktueller Stand

Am 11.08.2026 wurden zwei vorhandene Geräte untersucht:

- Raspberry Pi Pico 2 W mit RP2350A
- Adafruit CircuitPython 10.2.1
- Waveshare Pico-LoRa-SX1262-868M
- SEN66 auf beiden Geräten grundsätzlich funktionsfähig
- SD-Speicherung auf beiden Geräten grundsätzlich funktionsfähig
- bidirektionale LoRa-Kommunikation mit 21 vollständig dokumentierten PING/PONG-Paaren nachgewiesen
- ursprüngliche `code.py` nach dem Funkversuch auf beiden Geräten wiederhergestellt und byteweise geprüft

Der Funkversuch belegt die grundsätzliche Kommunikation der zwei Geräte bei kurzem Abstand. Reichweite, Dauerstabilität, Fehlerverhalten, Betrieb mit mehreren Slaves und das spätere Anwendungsprotokoll sind damit noch nicht nachgewiesen.

## Vorhandener Softwarestand

Der bisherige CircuitPython-Prototyp wurde in eine schlanke hexagonale Architektur ueberfuehrt. Der aktuelle Repository-Stand enthaelt:

- ein gemeinsames hardwareunabhaengiges Messdatenmodell,
- getrennte Master- und Slave-Anwendungsfaelle,
- Ports fuer Sensor, Zeit, Speicher, Funk und Diagnose,
- CircuitPython-Adapter fuer SEN66, SD-Karte und SX1262,
- rollenabhaengigen Start ueber `config.json`,
- lokale Speicherung vor dem Funkversuch,
- FIFO-Uebertragung ausstehender Datensaetze mit Abbruch beim ersten fehlenden ACK,
- ACK erst nach erfolgreicher Master-Speicherung,
- erneutes ACK fuer bereits gespeicherte Duplikate,
- hardwareunabhaengige Unit-Tests fuer Codec und Kernablaeufe, einschließlich des
  routingfaehigen V1-Datenpakets und neunfeldrigen ACKs.

Die Architektur ist implementiert und durch Unit-Tests auf dem Entwicklungsrechner abgesichert. Der konsolidierte Master-Start wurde auf einem Raspberry Pi Pico 2 W mit CircuitPython 10.2.1 getestet: OLED, Konfiguration, SD-Karte, SX1262 und die Empfangsschleife starten fehlerfrei. Der vollstaendige Slave-Mess- und Uebertragungsablauf ist auf dem zweiten Geraet noch zu testen. Insbesondere Zeitreferenz, SD-Wiederanlauf, Funk-Timeouts, Reichweite und Dauerbetrieb bleiben zu pruefen. Die optionale Bodenmessung und das OLED sind nicht Teil des Kernpfads.


## V1-Speicherstruktur (09.09.2026)

Neue Messungen liegen auf der jeweiligen SD-Karte unter:

```text
/sd/data/C01/measurements_000000-002999.csv
/sd/data/C01/measurements_003000-005999.csv
/sd/data/C02/measurements_000000-002999.csv
```

Ein Dateiblock umfasst 3.000 Sequenznummern, nicht einen Kalendermonat.
Der Slave verwendet seinen eigenen Geräteordner; der Master einen Ordner je
Slave. Der Mountpunkt bleibt `/sd`. Ordner werden automatisch angelegt.

Die V1-Kopfzeilen entsprechen [Datenformat V1](docs/Datenformat_V1_Entwurf.md).
Die Slave-Laufzeit heißt `slave_uptime_s`; die Master-CSV enthält zusätzlich
`master_uptime_s` und `missing_intervals`. Für empfangene Messungen sind
`receive_status=0` und `missing_intervals=0`. Automatische
`NO_PACKET`-Zeilen sind noch nicht implementiert.

### Umstieg und Datensicherung

- Vor einem Geräteupdate die SD und den bisherigen Softwarestand sichern.
- Den konsistenten Projektstand einschließlich `adapters/csv_migration.py`,
  `ports/errors.py` und `code.py` auf beiden Geräten verwenden. Konfigurationen beibehalten.
- Beim ersten Start der aktualisierten Software werden vorhandene
  `/sd/slave_measurements.csv` und `/sd/master_measurements.csv` automatisch
  in die V1-Blöcke übernommen, bevor der normale Betrieb beginnt. Auf einer
  neuen SD ohne diese Altdateien wird der Migrationscode nicht geladen.
- Alte und neue Messungen liegen danach gemeinsam unter `/sd/data/<ID>/`,
  je Block nach Sequenz sortiert. Erst nach erfolgreicher Übernahme aller Blöcke
  wird die jeweilige Quelldatei in `slave_measurements.csv.pre_v1` beziehungsweise
  `master_measurements.csv.pre_v1` umbenannt; ihr Inhalt bleibt unverändert.
  Diese Archive sind Sicherungen und dürfen bei der Auswertung nicht zusätzlich
  zu den V1-Blöcken als neue Messungen eingelesen werden.
- Die bisherige Spalte `uptime_s` wird als `slave_uptime_s` übernommen.
  Eine nicht aufgezeichnete Master-Laufzeit bleibt `NA`; sie wird nicht geschätzt.
  Der alte Empfangsstatus `OK` wird zu `0`, `missing_intervals` wird mit `0` ergänzt.
  Historische Messwerte, Zeitstempel und Statusflags werden nicht neu interpretiert.
- Identische Messungen derselben ID und Sequenz werden nur einmal übernommen.
  Bei bereits vorhandenen V1-Datensätzen bleiben deren Empfangsmetadaten erhalten.
  Widersprüchliche Messwerte, ungültige Kopfzeilen und unvollständige Datensätze
  führen zu einem Migrationsfehler, der auch beim Slave den Programmstart stoppt.
- Die Übernahme verwendet temporäre Blockdateien und kann nach einem Abbruch
  beim nächsten Start wiederholt werden. Vorher die Ursache eines Schreibfehlers
  beheben. Quelldateien und `.migration.bak`-Dateien nicht manuell löschen.
- Ausreichend freien SD-Speicher für die kopierten Daten plus einen temporären
  Block einplanen. Die Erstmigration kann länger dauern: Die Quelle wird je
  Zielblock erneut gelesen. Währenddessen läuft noch kein normaler Messbetrieb.
  Laufzeit, RAM-Bedarf und Verhalten bei realem Stromausfall sind auf Hardware zu prüfen.
- `climate_state.json` und `pending_records.jsonl` bleiben am bisherigen Ort.
  Vorhandene ausstehende Datensätze können weiter übertragen werden.
  Die Warteschlange wird durch diese Änderung nicht rotiert oder verkleinert.
- Eine verlorene Warteschlange wird nicht aus der CSV neu aufgebaut; daraus wird
  lediglich der nächste lokale Sequenzstand rekonstruiert.
- Abweichende Kopfzeilen oder unvollständige letzte Zeilen in einem Zielblock
  führen zu einem Speicherfehler statt zu automatischem Überschreiben.
  Betroffene Dateien zunächst sichern und untersuchen.
- Master- und Slave-Dateien mit unterschiedlichen Kopfzeilen dürfen nicht in
  demselben Geräteordner auf derselben SD gemischt werden.

### Prüfung

`python3 -m unittest discover -s tests/unit -v` prüft unter anderem
Blockwechsel 2.999/3.000, mehrere Geräte, FIFO nach Neustart, Wiederherstellung
ohne Statusdatei, Übernahme alter CSV-Dateien, Konflikterkennung und simulierte
Unterbrechungen während der Migration.

Die neue Speicherstruktur ist noch nicht auf den Picos nachgewiesen.
Beim nächsten Hardwaretest neue Pfade und Kopfzeilen, ACK, einmalige
Master-Speicherung und Sequenzfortsetzung nach Neustart kontrollieren.
Den Blockwechsel nur mit gesicherten Testdaten auf einer separaten Test-SD
prüfen; produktive Sequenzstände nicht dafür verändern.

## RP2040-LoRa-Treiber

Die zwei zusätzlich erhaltenen Geräte melden sich als Raspberry Pi Pico mit
RP2040 und CircuitPython 10.3.0, nicht als Pico 2 W. Beim Import des
SX1262-Quellcodes trat dort ein MemoryError auf. Für diese Geräte liegen
kompilierte, zu CircuitPython 10.3.0 passende LoRa-Treiber unter
firmware/rp2040/lib/.

Für einen RP2040-Pico mit CircuitPython 10.3.0:

1. Den bisherigen Inhalt von CIRCUITPY/lib/ sichern.
2. Nur die drei Quelltreiber _sx126x.py, sx126x.py und sx1262.py
aus CIRCUITPY/lib/ entfernen.
3. Die gleichnamigen Dateien mit Endung .mpy aus firmware/rp2040/lib/
nach CIRCUITPY/lib/ kopieren.
4. Alle übrigen Bibliotheken und die Projektordner unverändert lassen.
5. Pico neu starten und den Start mit gültiger time_epoch_utc prüfen.

.py- und .mpy-Versionen desselben Treibers dürfen nicht gleichzeitig
auf dem Pico liegen. Die Dateien sind nur mit CircuitPython 10.3.0 kompatibel.
Bei einer Firmwareaktualisierung müssen sie mit dem passenden
mpy-cross-Compiler neu erstellt werden. Die Quelltreiber unter lib/
bleiben die wartbare Referenz für die bisher getesteten Pico-2-W-Geräte.

## Hardware Und Pins

Das vorhandene OLED ist fuer den Kernbetrieb optional; Messung, Speicherung und Funkkommunikation muessen ohne Display funktionieren. Die aus vorhandenem Code und LoRa-Test abgeleitete Belegung ist noch als Arbeitsstand zu behandeln:

| Funktion | Signal | Pico-Pin |
|---|---|---|
| I2C | SDA | GP0 |
| I2C | SCL | GP1 |
| Bodenfeuchte laut Ausgangscode | Analog | GP26 |
| DS18B20 laut Ausgangscode | OneWire | GP27 |
| SD-Karte | MISO | GP16 |
| SD-Karte | CS | GP17 |
| SD-Karte | SCK | GP18 |
| SD-Karte | MOSI | GP19 |
| SX1262 | BUSY | GP2 |
| SX1262 | CS / NSS | GP3 |
| SX1262 | CLK | GP10 |
| SX1262 | MOSI | GP11 |
| SX1262 | MISO | GP12 |
| SX1262 | RESET | GP15 |
| SX1262 | DIO1 / IRQ | GP20 |

Das Waveshare-Modul führt `BAT_AD` auf GP26. Der mögliche Konflikt ist nur dann für den Projektumfang relevant, wenn die optionale Bodenfeuchtemessung umgesetzt wird.

## Softwareumgebung

CircuitPython führt `code.py` auf dem Laufwerk `CIRCUITPY` automatisch aus. Benötigte Bibliotheken liegen dort unter `lib/`. Die installierte Firmware wird über `boot_out.txt` festgestellt.

Für einen Slave wird `config.example.json`, fuer einen Master `config.master.example.json` als Vorlage fuer die nicht versionierte `config.json` verwendet. Neben Rolle, Geraete-ID, Funkparametern und Zeitreferenz benoetigt ein Slave eine `master_id`; ein Master benoetigt `monitored_slaves` mit mindestens einer eindeutigen Slave-ID; eine softwareseitige Obergrenze besteht nicht. Der Beispielwert für `time_epoch_utc` ist absichtlich `null`; mit fehlender Zeitreferenz startet die Produktlogik nicht, damit keine scheinbar gültigen falschen Messzeitstempel gespeichert werden. Die endgültige Zeitsynchronisation ist noch festzulegen.

Die SX1262-Treiberdateien stammen aus [`ehong-tl/micropySX126X`](https://github.com/ehong-tl/micropySX126X). Der MIT-Lizenztext ist im Repository enthalten.

## Projektstruktur

```text
audi-climate-cube/
|-- code.py
|-- config.example.json
|-- config.master.example.json
|-- domain/
|   |-- measurement.py
|   `-- protocol.py
|-- application/
|   |-- slave_controller.py
|   `-- master_controller.py
|-- ports/
|   `-- contracts.py
|-- adapters/
|   |-- configuration.py
|   |-- clock.py
|   |-- diagnostics.py
|   |-- oled_display.py
|   |-- ds18b20_sensor.py
|   |-- sd_card.py
|   |-- sd_storage.py
|   |-- sen66_sensor.py
|   `-- sx1262_radio.py
|-- lib/
|-- docs/
`-- tests/
    |-- unit/
    `-- lora_ping_pong/
```

## Zentrale Dokumente

- `docs/Lastenheft_AUDI_Climate_Cube.md`: bearbeitbare Quelle des fachlichen Entwurfs
- `docs/Lastenheft_AUDI_Climate_Cube.pdf`: lesbare PDF-Fassung zur fachlichen Pruefung
- `docs/Pflichtenheft_AUDI_Climate_Cube.md`: technischer Lösungsentwurf mit Rollen und Anwendungsfällen
- `docs/Architektur_Hexagonal.md`: Grenzen, Bausteine und offene Punkte der Softwarearchitektur
- `docs/Projektplan_AUDI_Climate_Cube.md`: Ablauf, Freigabepunkte, Termine und Risiken
- `docs/Anforderungen_AUDI_Climate_Cube.md`: bisherige Informations- und Arbeitsgrundlage
- `docs/Datenformat_V1_Entwurf.md`: noch nicht freigegebener Datenformatentwurf
- `docs/Projekttagebuch_Climate_Cube.md`: chronologische Tätigkeits- und Entscheidungsdokumentation
- `docs/Betriebsanleitung_Climate_Cube.md`: Einrichtung, Betrieb, Auswertung und Fehlersuche auf den Picos
- `docs/Reset_Stabilitaetstest.md`: sicherer Neustart eines abgegrenzten Stabilitaetstests
- `docs/Paper_Struktur_AUDI_Climate_Cube.md`: geplante Struktur des Abschluss-Papers
- `tests/lora_ping_pong/TESTPROTOKOLL_LoRa_Ping_Pong.md`: Testaufbau und Ergebnisse des Funknachweises

## Nächste Schritte

1. `config.example.json` für je ein Master- und Slave-Gerät konkretisieren.
2. V1-Datenpaket und ACK auf zwei Pico-Geraeten integrieren und testen.
3. Codec und SD-Wiederanlauf mit realistischen Datensätzen weiter testen.
4. Architekturstand zunächst auf zwei gesicherten Pico-Kopien integrieren.
5. FIFO-, ACK-, Duplikat- und Neustartverhalten auf realer Hardware prüfen.
6. `NO_PACKET`-Intervallueberwachung implementieren.
7. Danach Mehrgeräte-, Reichweiten-, Fehlerfall- und Dauerlauftests durchführen.

## Status

Arbeitsstand vom 14.08.2026. Das Lastenheft wurde fachlich rückgemeldet; Pflichtenheft, Protokoll, Zeitkonzept und Hardwareintegration bleiben technische Arbeitsstände.
