# Datenformat Version 1 - Zielspezifikation

Projekt: AUDI Climate Cube  
Stand: 09.09.2026
Status: Technisch festgelegte Zielspezifikation; V1-Funkformat, Sequenzabfrage, Speicherformat und zentrale Diagnoseereignisse sind implementiert und per Unit-Test geprueft. `NO_PACKET`-Lueckenzeilen stehen noch aus; die neue Speicherstruktur und Diagnoseereignisse sind noch auf Hardware zu testen.

## 1. Zweck

Dieses Dokument definiert ein gemeinsames Datenformat fuer:

- den Messdatensatz eines Slave-ClimateCubes,
- die lokale Sicherung auf der Slave-SD-Karte,
- die LoRa-Peer-to-Peer-Uebertragung zum Master,
- die zentrale Speicherung mit chronologischer Sequenzordnung und optionalen Zeitstempeln,
- die Erkennung fehlender, doppelter oder unvollstaendiger Datensaetze.

V1 legt Messwertumfang, Routingkopf, Statusflags, ACK-Grundablauf und Dateiaufteilung fest. Das 22-Felder-Datenpaket, das neunfeldrige ACK, Sequenzpersistenz, FIFO-Reihenfolge, die achtfeldrige `Q`-/`R`-Sequenzabfrage, Master-Zuordnungspruefung und der definierte RAM-Betrieb ohne Slave-SD sind implementiert und durch Unit-Tests abgesichert. Die V1-Dateiaufteilung, CSV-Kopfzeilen und das elffeldrige zentrale Diagnoseformat sind implementiert und per Unit-Test geprueft. Der vorhandene No-SD-Pfad sendet `SLAVE_SD_UNAVAILABLE`; weitere spezifizierte Ereignisquellen folgen mit ihrer jeweiligen Statussemantik. Der direkte V1-Daten-/ACK-Hardwaretest vom 04.09.2026 ist separat dokumentiert; neue Speicherstruktur, Sequenzabfrage, Diagnose und No-SD-Betrieb benoetigen weitere Hardwaretests. Der konkrete ACK-Timeout und fachliche Plausibilitaetsgrenzen bleiben Testparameter und aendern die Feldstruktur von V1 nicht.

## 2. Bestaetigte Grundlage Und Arbeitsannahmen

### Bestaetigte Projektinformationen

- Messungen erfolgen im vorgesehenen Betrieb alle 15 Minuten. Daraus entstehen mindestens 35.040 Datensaetze je Slave und Jahr.
- Slaves speichern ihre eigenen Messdaten bei verfuegbarer SD lokal; bei einem Slave-SD-Fehler gilt der definierte Weiterbetrieb ohne lokales Backup.
- Slaves senden Messdaten per LoRa Peer-to-Peer an einen Master.
- Der Master speichert die Daten mehrerer Slaves zentral.
- Die Slaves besitzen nach aktuellem Stand keine RTC.
- Ein genauer absoluter Messzeitpunkt ist nicht erforderlich; die chronologische Ordnung wird je Slave durch die persistente Sequenznummer bestimmt.
- Der vorhandene `code.py` liefert elf Messwerte: Lufttemperatur, Luftfeuchtigkeit, CO2, PM1, PM2.5, PM4, PM10, VOC-Index, NOx-Index, Bodenfeuchte und Bodentemperatur.

### Technische Entscheidungen Fuer V1

- Jeder Datensatz erhaelt eine Formatversion.
- Jeder Slave erhaelt eine eindeutige kurze Kennung.
- Jeder Datensatz erhaelt pro Slave eine fortlaufende Sequenznummer.
- Das bestehende Feld `measurement_timestamp` bleibt in V1 aus Kompatibilitaetsgruenden erhalten, ist ohne gueltige Zeitsynchronisation jedoch nur Zusatzinformation; eine Laufzeit seit Start kann ebenfalls enthalten sein.
- Das Funkpaket verwendet fuer V1 eine feste Feldreihenfolge und ASCII-Zeichen.
- Messwerte werden im Funkpaket als skalierte Ganzzahlen uebertragen, um Dezimaltrennzeichen und lange Flieskommadarstellungen zu vermeiden.
- Der Master kann einen getrennten Empfangszeitstempel sowie RSSI und SNR ergaenzen. Weder Mess- noch Empfangszeitstempel ersetzen die chronologische Sequenzordnung.

Aenderungen an Feldreihenfolge oder Feldbedeutung erfordern nach der Implementierung eine neue Formatversion.

## 3. Grundregel Fuer Den Datenfluss

Ein Messzyklus soll genau einen logischen Messdatensatz erzeugen:

```text
Sensoren
   |
   v
gemeinsamer Messdatensatz mit Slave-ID und Sequenznummer
   |                         |
   v                         v
Slave-CSV                LoRa-Paket
                             |
                             v
                          Master
                             |
                             v
              Messzeitstempel, optionaler Empfangszeitstempel und Funkmetadaten
                             |
                             v
                        Master-CSV
```

Die lokale Speicherung und das Funkpaket sollen aus demselben Datenobjekt erzeugt werden. Messwerte duerfen nicht fuer die SD-Karte erneut gelesen oder fuer die Funkuebertragung unabhaengig neu berechnet werden.

## 4. Logischer Messdatensatz V1

Der fachliche Messdatensatz enthaelt unabhaengig vom Transport:

- `origin_id` als eindeutige Kennung des erfassenden Slaves,
- persistente `sequence_number`,
- optionale `measurement_timestamp`-Information,
- `slave_uptime_s`,
- neun verbindliche SEN66-Werte,
- zwei optionale Bodenmesswerte,
- `status_flags`.

Die Kombination aus `origin_id` und `sequence_number` identifiziert einen Messdatensatz eindeutig. Zeitstempel sind keine Ordnungsmerkmale.

## 5. Funkdarstellung V1

### 5.1 Routingkopf Und Datenpaket

V1 verwendet ASCII, Semikolon als Trennzeichen und eine feste Reihenfolge mit genau 22 Feldern:

| Position | Feld | Bedeutung |
|---:|---|---|
| 1 | `format_version` | Wert `1` |
| 2 | `message_type` | Messdatensatz `D` |
| 3 | `origin_id` | urspruenglicher Slave |
| 4 | `destination_id` | endgueltiger Master |
| 5 | `next_hop_id` | naechster vorgesehener Empfaenger |
| 6 | `sequence_number` | persistente Sequenz des Slaves |
| 7 | `hop_count` | bisherige Weiterleitungen, Startwert `0` |
| 8 | `hop_limit` | maximal zulaessige Weiterleitungen |
| 9 | `measurement_timestamp` | ISO-8601-Zeit oder `NA` |
| 10 | `slave_uptime_s` | Sekunden seit Programmstart |
| 11-21 | Messwerte | feste Reihenfolge aus Abschnitt 5.2 |
| 22 | `status_flags` | vierstellige Hexadezimalzahl |

Direkte Sternkommunikation:

```text
1;D;C01;M01;M01;125;0;1;NA;3720;224;581;430;42;51;63;81;104;12;NA;NA;0040
```

Vorbereitete statische Relay-Route `C03 -> C02 -> C01 -> M01`:

```text
1;D;C01;M01;C02;125;0;3;NA;3720;224;581;430;42;51;63;81;104;12;NA;NA;0040
```

Ein Relay nimmt nur Pakete mit eigener `next_hop_id` an, liest den folgenden Hop fuer `destination_id` aus seiner Konfiguration, ersetzt `next_hop_id` und erhoeht `hop_count`. Bei `hop_count >= hop_limit` wird nicht weitergeleitet. Duplikate werden ueber `message_type`, `origin_id`, `destination_id` und `sequence_number` erkannt. Die Kernumsetzung verwendet zunaechst einen direkten Hop; Relay ist nur vorbereitet.

### 5.1.1 Auswahl Des Netzmodus

Die Topologie wird nicht aus den Paketdaten geraten, sondern auf jedem Geraet explizit in `/config.json` festgelegt. Der Standardmodus ist `star`:

```json
{
  "network_mode": "star",
  "master_id": "M01"
}
```

Die spaetere, statische Mehrsprungvariante verwendet `mesh`. Sie benoetigt mindestens den festen ersten Hop und ein Hop-Limit:

```json
{
  "network_mode": "mesh",
  "master_id": "M01",
  "next_hop_id": "C02",
  "hop_limit": 3
}
```

`mesh` bedeutet ausschliesslich statisches Relay-Routing. Es gibt keine automatische Suche nach Nachbarn, keine Berechnung alternativer Wege und keine stillschweigende Umschaltung von `star` nach `mesh`. Die Daten- und ACK-Weiterleitung einer statischen Kette ist implementiert und unit-getestet. Fuer einen Hardwareeinsatz fehlen noch die persistente Relay-Warteschlange, Relay-Duplikatbehandlung und der Hardwaretest.

### 5.2 Messwertreihenfolge Und Skalierung

| Position | Feld | Funkwert |
|---:|---|---|
| 11 | `air_temperature_c` | Wert mal 10 |
| 12 | `relative_humidity_pct` | Wert mal 10 |
| 13 | `co2_ppm` | ganze ppm |
| 14 | `pm1_0_ug_m3` | Wert mal 10 |
| 15 | `pm2_5_ug_m3` | Wert mal 10 |
| 16 | `pm4_0_ug_m3` | Wert mal 10 |
| 17 | `pm10_ug_m3` | Wert mal 10 |
| 18 | `voc_index` | Wert mal 10 |
| 19 | `nox_index` | Wert mal 10 |
| 20 | `soil_moisture_pct` | ganze Prozent oder `NA` |
| 21 | `soil_temperature_c` | Wert mal 10 oder `NA` |

Messwerte werden gerundet als Ganzzahlen uebertragen und beim Dekodieren anhand der dokumentierten Skalierung zurueckgewandelt. Negative Werte sind nur fuer physikalisch passende Messgroessen, insbesondere Temperaturen, erlaubt.

### 5.3 Fehlende Und Unplausible Werte

Ein fehlender Wert wird als `NA` uebertragen; seine Position bleibt erhalten. Nicht konfigurierte optionale Bodensensoren verwenden `NA` ohne Fehlerbit. Wird ein konfigurierter Sensor nicht erfolgreich gelesen, werden das sensorspezifische Bit und `MEASUREMENT_MISSING` gesetzt. Dies ist fuer SEN66 und den angeschlossenen DS18B20 implementiert. Ein lokaler Slave-SD-Schreibfehler setzt `SLAVE_SD_WRITE_ERROR` und `SLAVE_SD_UNAVAILABLE`; der Datensatz wird anschliessend ausschliesslich ueber den sicheren RAM-/Sequenzabfragebetrieb behandelt.

Unplausible Messwerte werden nicht verworfen. Sie bleiben fuer die Auswertung erhalten und setzen `MEASUREMENT_IMPLAUSIBLE`. Plausibilitaetsgrenzen werden aus den Datenblaettern der tatsaechlich eingesetzten Sensorversionen abgeleitet und als versionierte Test- oder Konfigurationswerte gepflegt; ihre Aenderung ist keine Aenderung des V1-Formats. Bis zur Bestaetigung der Sensorversionen werden keine erfundenen Grenzwerte als verbindlich behandelt.

Die optionale Konfiguration `plausibility_limits` wird auf Master und Slave
gleich angewandt. Jeder Eintrag besitzt exakt `min` und `max`; nur bekannte
Messfelder sind zulaessig. Beispiel, erst nach fachlicher Bestaetigung der
Grenzen einzutragen:

```json
"plausibility_limits": {
  "co2_ppm": {"min": 400, "max": 2000}
}
```

Ohne Eintrag bleibt ein Feld ungeprueft. Ein Wert ausserhalb eines
konfigurierten Bereichs wird unveraendert gespeichert und erhaelt ausschliesslich
das Flag `MEASUREMENT_IMPLAUSIBLE`.

### 5.4 Formatregeln

- Zeichencodierung: ASCII
- Trennzeichen: Semikolon `;`
- Datenpaket: genau 22 Felder
- maximale Payload-Laenge: 160 ASCII-Bytes
- Kennungen: 1 bis 8 Zeichen aus `A-Z`, `0-9`, `_` oder `-`
- `sequence_number`, `hop_count`, `hop_limit` und `slave_uptime_s`: nichtnegative Ganzzahlen
- fuehrende oder nachfolgende Leerzeichen und Zeilenumbrueche: nicht erlaubt
- SX1262-Paket-CRC wird verwendet; keine zusaetzliche V1-Pruefsumme
- unbekannte Versionen oder Nachrichtentypen werden abgelehnt

Die maximale Laenge wird vor dem Senden und nach dem Empfang geprueft. Fuer minimale und maximale gueltige Testwerte wird ein Codec-Grenztest angelegt.

## 6. Statusflags V1

`status_flags` ist eine vierstellige Hexadezimalzahl. `0000` bedeutet, dass kein bekannter Status gesetzt ist.

| Bit | Hexwert | Symbol | Bedeutung |
|---:|---:|---|---|
| 0 | `0001` | `SEN66_ERROR` | SEN66-Messung fehlgeschlagen oder unvollstaendig |
| 1 | `0002` | `SOIL_TEMPERATURE_ERROR` | konfigurierter DS18B20 nicht erfolgreich gelesen |
| 2 | `0004` | `SOIL_MOISTURE_ERROR` | konfigurierte Bodenfeuchtemessung fehlgeschlagen |
| 3 | `0008` | `SLAVE_SD_UNAVAILABLE` | Slave-SD nicht verfuegbar |
| 4 | `0010` | `SLAVE_SD_WRITE_ERROR` | lokaler Schreibvorgang fehlgeschlagen |
| 5 | `0020` | `MEASUREMENT_MISSING` | mindestens ein erwarteter Messwert fehlt |
| 6 | `0040` | `TIME_UNSYNCED` | Zeitwert aus lokaler Fortsetzung; chronologisch nutzbar, aber keine garantierte UTC-Zeit |
| 7 | `0080` | `MEASUREMENT_IMPLAUSIBLE` | mindestens ein Messwert ausserhalb der festgelegten Plausibilitaetsgrenze |
| 8-15 |  | reserviert | fuer spaetere Formatversionen |

Beispiel `0032` kombiniert `SLAVE_SD_WRITE_ERROR`, `MEASUREMENT_MISSING` und `SOIL_TEMPERATURE_ERROR`. Uebertragungsfehler werden ausserhalb der Statusflags behandelt. Ein fehlendes ACK laesst den Datensatz ausstehend, erzeugt in V1 jedoch gemaess Abschnitt 11.2 kein eigenes Diagnoseereignis.

## 6.1 Dateiaufteilung

Slave und Master verwenden eine uhrzeitunabhaengige Ablage nach Geraete-ID und Sequenzbereich:

```text
/data/C01/measurements_000000-002999.csv
/data/C01/measurements_003000-005999.csv
/data/C02/measurements_000000-002999.csv
```

Die Pfade in diesem Abschnitt sind relativ zur SD-Wurzel; bei Mountpunkt `/sd` lautet der vollstaendige Pfad beispielsweise `/sd/data/C01/measurements_000000-002999.csv`.

Jede Datei umfasst hoechstens 3.000 fortlaufende Sequenznummern. Der Blockindex wird mit `sequence_number / 3000` ganzzahlig bestimmt. Auf der Slave-SD wird der Ordner des eigenen Geraets verwendet; die Master-SD fuehrt einen getrennten Ordner fuer jeden Slave. Die Dateien bleiben dadurch ohne gueltige Kalenderzeit chronologisch zuordenbar.

### 6.2 Umstieg vorhandener CSV-Dateien

Beim ersten Start mit dem V1-Speicheradapter werden vorhandene
`slave_measurements.csv` beziehungsweise `master_measurements.csv` vor dem
normalen Messbetrieb in die V1-Blockdateien übernommen. Nach erfolgreicher
Übernahme wird die jeweilige Quelldatei unverändert als `.pre_v1`-Sicherung
archiviert. Alte und neue Messungen liegen damit gemeinsam in der
sequenzbasierten Ablage.

Der Umstieg ist wiederholbar: Bei einer Unterbrechung bleiben die Quelldatei
und vollständige Zielblöcke erhalten; beim nächsten Start wird die Übernahme
fortgesetzt. Identische Datensätze werden nicht doppelt eingefügt.
Widersprüchliche Datensätze mit gleicher Geräte-ID und Sequenznummer, falsche
Kopfzeilen oder unvollständige Zeilen brechen die Übernahme kontrolliert ab.
Der Slave wechselt bei einem solchen Fehler nicht in den Betrieb ohne SD,
sondern stoppt, damit kein fehlerhafter Datenbestand übergangen wird.

Die bisherige Spalte `uptime_s` wird als `slave_uptime_s` übernommen.
Nicht vorhandene historische Master-Laufzeiten bleiben `NA`; der alte
Empfangsstatus `OK` wird als erfolgreicher Status `0` übernommen und
`missing_intervals` mit `0` ergänzt. Historische Messwerte werden nicht
neu berechnet oder fachlich neu bewertet.

## 7. Slave-CSV V1

Die Slave-SD speichert lesbare Werte mit Dezimalpunkt. Verbindliche Kopfzeile:

```text
format_version,device_id,sequence_number,measurement_timestamp,slave_uptime_s,air_temperature_c,relative_humidity_pct,co2_ppm,pm1_0_ug_m3,pm2_5_ug_m3,pm4_0_ug_m3,pm10_ug_m3,voc_index,nox_index,soil_moisture_pct,soil_temperature_c,status_flags
```

Beispieldatensatz:

```text
1,C01,125,NA,3720,22.4,58.1,430,4.2,5.1,6.3,8.1,10.4,1.2,,,0040
```

Regeln:

- Dezimaltrennzeichen ist ein Punkt.
- Fehlende Messwerte bleiben als leeres CSV-Feld erhalten.
- `status_flags` dokumentiert den bekannten Zustand des Datensatzes.
- Eine neue Formatversion erfordert mindestens eine neue Datei oder eine eindeutig versionierte Kopfzeile.
- Die V1-Kopfzeile und Dateiaufteilung sind implementiert und per Unit-Test geprueft. Die vollstaendige Statussemantik und Hardwarevalidierung bleiben offen.

## 8. Master-CSV V1

Der Master speichert den dekodierten Slave-Datensatz und ergaenzt Empfangsinformationen.

Verbindliche Kopfzeile:

```text
received_timestamp,master_uptime_s,master_id,format_version,device_id,sequence_number,measurement_timestamp,slave_uptime_s,air_temperature_c,relative_humidity_pct,co2_ppm,pm1_0_ug_m3,pm2_5_ug_m3,pm4_0_ug_m3,pm10_ug_m3,voc_index,nox_index,soil_moisture_pct,soil_temperature_c,status_flags,rssi_dbm,snr_db,receive_status,missing_intervals,restart_count,sd_write_error_count,diagnostics
```

Beispieldatensatz:

```text
NA,7200,M01,1,C01,125,NA,3720,22.4,58.1,430,4.2,5.1,6.3,8.1,10.4,1.2,,,0040,-96,7.5,0,0,1,0,SEN66_ERROR:1
```

Zeit- und Zusatzfelder der Master-CSV:

| Feld | Bedeutung | V1-Regel |
|---|---|---|
| `measurement_timestamp` | optionale Zeitinformation des Slaves | bei `TIME_UNSYNCED` fortgefuehrter, nur chronologisch zu nutzender Zeitwert |
| `received_timestamp` | optionale Empfangszeit am Master | ISO 8601 UTC oder `NA` |
| `master_uptime_s` | monotone Master-Laufzeit beim Empfang oder Rasterzeitpunkt | nichtnegative Ganzzahl |
| `master_id` | Kennung des speichernden Masters | gleiche Kennungsregel wie Routing-IDs |
| `rssi_dbm` | Empfangsstaerke des SX1262 | numerischer Treiberwert |
| `snr_db` | Signal-Rausch-Verhaeltnis | numerischer Treiberwert |
| `receive_status` | Empfangsstatus | `0` fuer erfolgreichen Empfang; `NO_PACKET` fuer eine noch nicht aufgeloeste vorlaeufige Lueckenzeile |
| `missing_intervals` | aufeinanderfolgende Intervalle ohne empfangenes Paket | bei echtem Datensatz `0`, bei Lueckenzeilen ab `1` aufsteigend |
| `restart_count` | Neustarts seit der vorherigen Messzeile desselben Geraets | Anzahl `DEVICE_RESTARTED` mit Bezug auf diese Sequenz; Standard `0` |
| `sd_write_error_count` | lokale SD-Schreibfehler mit Bezug auf diese Messung | Anzahl `SLAVE_SD_WRITE_ERROR`; Standard `0` |
| `diagnostics` | weitere Diagnoseereignisse mit Bezug auf diese Messung | durch Semikolon getrennte Eintraege `EREIGNIS:ANZAHL`; leer ohne Ereignis |

Falls Zeitstempel verwendet werden, ist ISO 8601 in UTC mit `Z` die empfohlene Darstellung. Ohne gueltige Zeitsynchronisation werden Zeitfelder nicht fuer die chronologische Auswertung verwendet.

### 8.1 Master-Konfiguration Und Lueckenzeilen

Die Master-Konfiguration enthaelt das Pflichtfeld `monitored_slaves` mit mindestens einer eindeutigen Slave-ID und ohne feste softwareseitige Obergrenze. Die Master-ID darf nicht enthalten sein. Nur eingetragene Slaves gelten als regulaere Datenquellen und werden im 15-Minuten-Raster ueberwacht. Pakete unbekannter Slaves werden nicht als normale Messdaten gespeichert.

Empfaengt der Master innerhalb eines vollstaendigen Intervalls kein Paket eines konfigurierten Slaves, erzeugt er fuer diesen Slave zunaechst eine vorlaeufige Lueckenzeile. `device_id`, `master_id`, `master_uptime_s`, optionaler `received_timestamp`, `receive_status=NO_PACKET` und `missing_intervals` sind gesetzt. `format_version`, `sequence_number`, Slave-Zeit, Slave-Laufzeit, Messwerte, Statusflags, RSSI und SNR werden als `NA` beziehungsweise leere CSV-Felder gespeichert. Die Lueckenzeile beschreibt nur den bis dahin fehlenden Empfang beim Master und ist kein erfundener Messdatensatz. Kann ein spaeter empfangener Datensatz dem Intervall eindeutig zugeordnet werden, ersetzt er die vorlaeufige Luecke. Nur nicht nachgelieferte Daten bleiben als `NO_PACKET` erhalten.

Die drei Auswertungsspalten werden fuer Excel fest in jede Master-Zeile geschrieben. Sie enthalten nur die Zusammenfassung; die vollstaendige Ereignishistorie bleibt unter `/diagnostics/<device_id>/events.csv`. Ein `DEVICE_RESTARTED` wird beim Slave-Start mit Bezug auf dessen naechste Messsequenz gesendet. Dadurch kann ein Diagramm direkt aus den festen Messspalten erstellt werden, ohne Diagnosezeilen zwischen Messungen filtern zu muessen.

Beispiel nach zwei Intervallen ohne Paket:

```text
NA,8100,M01,NA,C01,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NO_PACKET,2
```

Aenderungen an `monitored_slaves` werden nach einem Master-Neustart wirksam. Ein neu hinzugefuegter Slave wird ab dem ersten danach vollstaendig begonnenen Intervall ueberwacht. Entfernte Slaves erzeugen keine neuen Lueckenzeilen; vorhandene Dateien bleiben bestehen.

## 9. Validierung Am Master

Der Master prueft ein V1-Datenpaket in dieser Reihenfolge:

1. Payload-Laenge ist hoechstens 160 Byte und ASCII-dekodierbar.
2. Formatversion und Nachrichtentyp werden unterstuetzt.
3. Das Datenpaket besitzt genau 22 Felder.
4. `destination_id` und `next_hop_id` entsprechen der eigenen Master-ID.
5. Kennungen entsprechen dem erlaubten Zeichensatz.
6. Sequenz-, Hop- und Laufzeitfelder sind nichtnegative Ganzzahlen.
7. `hop_count` ueberschreitet `hop_limit` nicht.
8. Messfelder sind `NA` oder gueltige Ganzzahlen.
9. Statusflags sind vier Hexadezimalstellen.
10. Die Sequenznummer wird mit dem letzten gespeicherten Stand von `origin_id` verglichen.

Ein syntaktisch ungueltiges oder falsch adressiertes Paket wird nicht als gueltige Messung gespeichert. Der Fehler wird nach der begrenzten Diagnoseregel protokolliert, sofern eine SD-Karte verfuegbar ist. Ein syntaktisch gueltiger, aber fachlich unplausibler Messwert wird gespeichert und per Statusflag markiert.

## 10. Sequenznummer Und Neustart

Jeder Slave verwendet eine monoton steigende, nichtnegative Sequenznummer. Bei verfuegbarer Slave-SD werden der naechste Sequenzstand und der Lesepunkt der FIFO-Warteschlange dort persistiert. Beim Start rekonstruiert der Speicheradapter einen verlorenen Sequenzstand aus der lokalen Warteschlange. Ohne lesbare Slave-SD gilt die Sequenzabfrage aus Abschnitt 11.1. Bereits gespeicherte Messdaten werden nicht ueberschrieben.

Kann der Master seinen Status nicht lesen, rekonstruiert er den letzten bekannten Sequenzstand je Slave aus seinen zentralen CSV-Dateien (Altdatei und V1-Bloecke). Ein verlorener Slave-Warteschlangenstatus kann zu erneuten Duplikatuebertragungen fuehren; der Master speichert diese nicht erneut als neue Messung, sendet aber nochmals ein ACK. Das Verhalten wird vor Freigabe durch Stromunterbrechungs- und SD-Fehlertests validiert.

## 11. Verbindliche ACK-Nachricht

Der Master bestaetigt einen Datensatz erst nach erfolgreicher zentraler Speicherung. Das ACK verwendet denselben routingfaehigen Kopf in Gegenrichtung und besitzt genau neun Felder:

```text
1;A;M01;C01;C01;125;0;1;0
```

| Position | Feld | Beispiel |
|---:|---|---|
| 1 | `format_version` | `1` |
| 2 | `message_type` | `A` |
| 3 | `origin_id` | Master `M01` |
| 4 | `destination_id` | Slave `C01` |
| 5 | `next_hop_id` | direkter Slave oder Relay |
| 6 | `sequence_number` | `125` |
| 7 | `hop_count` | `0` |
| 8 | `hop_limit` | `1` |
| 9 | `result_code` | `0` |

| Code | Bedeutung | Fuer Slave erfolgreich |
|---:|---|---|
| 0 | Datensatz zentral gespeichert | ja |
| 1 | Format oder Version ungueltig | nein |
| 2 | Datensatz bereits zentral vorhanden | ja |
| 3 | zentrale Speicherung fehlgeschlagen | nein |

Der Slave akzeptiert ein ACK nur, wenn `origin_id` seiner konfigurierten `master_id`, `destination_id` seiner eigenen ID und `sequence_number` dem ausstehenden Datensatz entsprechen. Ohne erfolgreiches ACK bleibt der Datensatz ausstehend. Fuer statische Relays wird der ACK-Rueckweg ueber dieselbe Ziel-/Next-Hop-Logik konfiguriert. Der vorlaeufige ACK-Timeout betraegt drei Sekunden. Dieser Wert wird im Funk-, Reichweiten- und Stoerungstest validiert und bleibt konfigurierbar.

## 11.1 Sequenzabfrage Ohne Slave-SD

Kann ein Slave beim Start keinen persistenten Sequenzstand von seiner SD lesen, fragt er die naechste freie Sequenznummer beim konfigurierten Master ab. Anfrage und Antwort verwenden den Routingkopf mit jeweils genau acht Feldern.

Anfrage:

```text
1;Q;C01;M01;M01;0;0;1
```

Antwort bei zuletzt zentral gespeicherter Sequenz 125:

```text
1;R;M01;C01;C01;126;0;1
```

| Position | `Q` | `R` |
|---:|---|---|
| 1 | Formatversion `1` | Formatversion `1` |
| 2 | Nachrichtentyp `Q` | Nachrichtentyp `R` |
| 3 | Slave als Ursprung | Master als Ursprung |
| 4 | Master als Endziel | Slave als Endziel |
| 5 | naechster Hop | naechster Hop |
| 6 | reserviert, Wert `0` | naechste freie Sequenznummer |
| 7 | `hop_count` | `hop_count` |
| 8 | `hop_limit` | `hop_limit` |

Der Master berechnet die Antwort als hoechste fuer `origin_id` zentral gespeicherte Sequenznummer plus eins. Existiert noch kein Datensatz des Slaves, antwortet er mit `0`. Der Slave akzeptiert nur eine korrekt adressierte `R`-Antwort seines konfigurierten Masters. Eine Abfragerunde umfasst hoechstens drei `Q`-Versuche. Je Versuch wartet der Slave drei Sekunden auf `R`; zwischen erfolglosen Versuchen liegen zwei Sekunden. Nach einer erfolglosen Runde startet er nach 60 Sekunden eine neue Runde. Ohne gueltige Antwort beginnt er nicht eigenmaechtig bei `0` und sendet keine neuen Messdatensaetze. Er haelt hoechstens die neueste noch nicht nummerierte Messung im RAM; erreicht ein neuer Messzyklus den Slave vor einer gueltigen Antwort, ersetzt die neue Messung die aeltere. Der RAM-Inhalt geht bei einem Neustart verloren. Nach einer gueltigen Antwort erhaelt die gehaltene Messung die gelieferte Sequenznummer und wird unmittelbar uebertragen. Der Slave fuehrt den Sequenzstand danach im RAM fort. Ein Wechsel zur SD-gestuetzten Sequenz- und FIFO-Verwaltung erfolgt nicht per Hot-Plug im laufenden Betrieb. Die Slave-SD wird nur spannungsfrei eingesetzt oder repariert; danach startet der Slave neu. Ist der lokale Sequenzstand nach dem Neustart nicht eindeutig rekonstruierbar, fragt der Slave erneut per `Q`/`R` beim Master an.

Verlorene ACKs verursachen keine Kollision: Ist der zuvor gesendete Datensatz bereits beim Master gespeichert, liefert der Master die darauffolgende Nummer; andernfalls liefert er die noch freie Nummer erneut.

## 11.2 Diagnoseereignis V1

Slaves speichern keine eigene Diagnosedatei. Ein Zustandswechsel wird als routingfaehiges Ereignispaket `E` an den Master gesendet:

```text
1;E;C01;M01;M01;125;0;1;SLAVE_SD_UNAVAILABLE;STARTED;1
```

Das Ereignispaket besitzt genau elf Felder:

| Position | Feld | Bedeutung |
|---:|---|---|
| 1-8 | Routingkopf | wie beim Datenpaket; Position 6 ist die Bezugssequenz |
| 9 | `event_code` | stabiler ASCII-Fehlercode |
| 10 | `event_state` | `STARTED`, `ENDED` oder `OCCURRED` |
| 11 | `repeat_count` | Anzahl zusammengefasster Vorkommnisse |

V1 definiert folgende zustandsbehaftete Ereigniscodes:

| Ereigniscode | Bedeutung | Zusaetzliches Statusflag |
|---|---|---|
| `SLAVE_SD_UNAVAILABLE` | Slave-SD nicht eingebunden oder nicht ansprechbar | `SLAVE_SD_UNAVAILABLE` |
| `SLAVE_SD_WRITE_ERROR` | Schreiben auf vorhandene Slave-SD fehlgeschlagen | `SLAVE_SD_WRITE_ERROR` |
| `SEN66_ERROR` | SEN66 fehlt oder liefert keine vollstaendige Messung | `SEN66_ERROR` |
| `SOIL_TEMPERATURE_ERROR` | konfigurierter DS18B20 ausgefallen | `SOIL_TEMPERATURE_ERROR` |
| `SOIL_MOISTURE_ERROR` | konfigurierte Bodenfeuchtemessung ausgefallen | `SOIL_MOISTURE_ERROR` |
| `RADIO_ERROR` | LoRa-Initialisierung oder Funkzugriff fehlgeschlagen | keines |
| `SEQUENCE_STATE_ERROR` | Sequenzstand nicht sicher rekonstruierbar | keines |

Einmalige Ereignisse verwenden `OCCURRED`:

| Ereigniscode | Bedeutung |
|---|---|
| `DEVICE_RESTARTED` | Slave wurde neu gestartet |
| `CONFIG_REJECTED` | Konfiguration wurde abgelehnt |
| `PAYLOAD_REJECTED` | Datensatz konnte nicht serialisiert werden |

Ein Slave sendet `STARTED` beim ersten Auftreten und `ENDED` bei der Behebung eines zustandsbehafteten Fehlers. Identische Wiederholungen erzeugen kein Paket je Programmschleife, sondern erhoehen `repeat_count`. Ohne Slave-SD wird der Zaehler nur im Arbeitsspeicher gehalten und darf bei einem Neustart verloren gehen. Fuer Diagnoseereignisse ist in V1 kein eigenes ACK erforderlich; SD- und Sensorzustaende werden zusaetzlich durch Statusflags in jedem Messpaket sichtbar. `ACK_MISSING`, `TIME_UNSYNCED`, einzelne unplausible Messwerte und nicht konfigurierte optionale Sensoren erzeugen kein separates Diagnoseereignis. Ein fehlendes ACK darf waehrend Inbetriebnahme und Test seriell mit der betroffenen Sequenznummer ausgegeben werden, wird aber nicht zusaetzlich auf SD protokolliert. Der Datensatz bleibt ausstehend; eine laenger anhaltende Verbindungsstoerung ist ueber die wachsende Anzahl ausstehender Datensaetze erkennbar.

`RADIO_ERROR` und `CONFIG_REJECTED` koennen nur nachtraeglich gesendet werden, wenn Funkverbindung und Zielkonfiguration wieder funktionsfaehig sind. Ihre zentrale Erfassung ist deshalb nicht garantiert; eine lokale serielle Diagnose bleibt fuer die Inbetriebnahme bestehen.

Der Master verwaltet den aktiven Zustand mit dem Schluessel `origin_id + event_code`. Ein erneutes `STARTED` fuer einen bereits aktiven Zustand eroeffnet keinen neuen Fehlerfall. `ENDED` schliesst den aktiven Zustand. Nach einem Master-Neustart wird der letzte Zustand aus `events.csv` rekonstruiert.

Der Master speichert empfangene Ereignisse ausschliesslich zentral unter:

```text
/diagnostics/<origin_id>/events.csv
```

Verbindliche Kopfzeile:

```text
device_id,reference_sequence,event_code,event_state,repeat_count
```

Die Master-SD ist Betriebsvoraussetzung. Ist sie nicht beschreibbar, kann der Master weder Mess- noch Diagnoseereignisse dauerhaft speichern und sendet kein erfolgreiches Daten-ACK.

## 12. Versionsregeln

- Das erste Feld identifiziert die Formatversion.
- Eine Aenderung der Feldreihenfolge, Skalierung oder Bedeutung erfordert eine neue Version.
- Neue Pflichtfelder werden nicht still an V1 angehaengt.
- Der Master verwirft unbekannte Versionen kontrolliert und protokolliert den Grund.
- Dokumentation, Slave-Code, Master-Code und Tests muessen dieselbe Version nennen.
- V1 gilt mit diesem Dokument als technisch festgelegt; die Freigabe fuer den Einsatz erfolgt nach erfolgreicher Implementierung sowie Kodier-, Dekodier- und Hardwaretests.

## 13. Abgrenzung Zum Vorhandenen Code

Der auf zwei realen Pico-Geraeten getestete Architektur-Prototyp verwendet noch ein Datenpaket mit 18 Feldern und ein ACK mit fuenf Feldern. Er weist Messung, lokale Speicherung, direkte LoRa-Uebertragung, zentrale Speicherung, ACK-Wiederholung, Duplikatvermeidung und Neustartverhalten nach.

Implementiert und durch Unit-Tests abgesichert sind das 22-feldrige V1-Datenpaket, das neunfeldrige ACK sowie die achtfeldrige `Q`-/`R`-Sequenzabfrage, die Adresspruefung gegen die konfigurierte `master_id`, die Ermittlung der naechsten zentral freien Sequenz sowie der definierte RAM-Betrieb ohne Slave-SD mit `SLAVE_SD_UNAVAILABLE`. Die sequenzbasierte V1-Dateiaufteilung und V1-CSV-Kopfzeilen sind seit 09.09.2026 implementiert. Das elffeldrige Diagnosepaket, die zentrale Master-Diagnoseablage und die Wiederherstellung aktiver Diagnosezustaende nach Master-Neustart sind nun ebenfalls implementiert. Ebenso implementiert ist die 15-Minuten-Intervallueberwachung: Der Master schreibt je ueberwachtem Slave vorlaeufige `NO_PACKET`-Zeilen und ersetzt sie bei passender nachgelieferter Sequenznummer atomar durch den echten Datensatz; die interne Zuordnung ueberlebt einen Master-Neustart. Altdateien bleiben unveraendert und werden bei der Sequenzrekonstruktion beruecksichtigt. Noch nicht implementiert sind weitere Ereignisausloeser ueber den vorhandenen No-SD-Pfad hinaus und die vollstaendige Statussemantik. Die implementierte Sequenzabfrage, Diagnose, Lueckenlogik und der No-SD-Betrieb sind noch nicht auf den Pico-Geraeten nachgewiesen.

## 14. Verbleibende Validierungen

- vorlaeufigen ACK-Timeout von drei Sekunden durch Funk-, Reichweiten- und Stoerungstest bestaetigen,
- 160-Byte-Grenze mit minimalen und maximalen gueltigen Messwerten testen,
- weitere Grenztests fuer konkrete Sensorbereiche und Statusbit-Kombinationen ergaenzen; Datenpaket, ACK, `NA`, Routingzuordnung, Payloadgrenze und Sequenzabfrage sind auf Unit-Ebene abgedeckt,
- direkte Master-Zuordnung und Ablehnung falscher ACK-Absender testen,
- Dateiblockwechsel bei Sequenz 2.999 auf 3.000 auf Hardware testen (Unit-Test bestanden),
- Diagnosepakete, zentrale Master-Ablage und Weiterbetrieb ohne Slave-SD testen,
- konkrete Plausibilitaetsgrenzen aus den Datenblaettern der bestaetigten Sensorversionen ableiten und versionieren,
- routingfaehigen Kopf im direkten Ein-Hop-Betrieb auf beiden Picos testen.

Eine Relay-Implementierung ist fuer die Freigabe des Kernsystems nicht erforderlich.

## 15. Naechste Schritte

1. Implementierte `Q`-/`R`-Sequenzabfrage und No-SD-Ablauf mit `SEQ-02`, `SEQ-04`, `SEQ-08` und `SEQ-09` auf beiden Picos testen.
2. Implementierten V1-SD-Adapter auf gesicherten Pico-Testgeraeten pruefen: Geraeteordner, CSV-Kopfzeilen und Blockwechsel.
3. Sequenzfortsetzung und Duplikatvermeidung mit Altdateien und neuen V1-Bloecken auf Hardware pruefen.
4. Wiederanlauf und Fehlerverhalten der neuen Speicherstruktur auf Hardware validieren.
5. `SOIL_MOISTURE_ERROR` und `MEASUREMENT_IMPLAUSIBLE` erst mit Bodenfeuchteintegration beziehungsweise festgelegten Plausibilitaetsgrenzen aktivieren. `TIME_UNSYNCED` wird bei einer aus CSV fortgesetzten Zeit bereits gesetzt.
6. Direkten Master-/Slave-Gesamtablauf erneut auf beiden Picos testen.
7. Erst danach optional statische Relay-Weiterleitung implementieren.
