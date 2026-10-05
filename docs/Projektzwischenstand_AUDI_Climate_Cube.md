# Projektzwischenstand AUDI Climate Cube

Projekt: Offline-Messdatenerfassung und LoRa-Übertragung für Climate Cubes
Bearbeiter: Immanuel Mauch
Datum: 07.09.2026
Rolle: Gesprächsleitfaden für den Termin mit Herrn Schnabel

---

## 1. Projektziel

Mehrere Slave-Climate-Cubes erfassen im 15-Minuten-Rhythmus Umweltmessdaten, sichern
diese lokal auf SD-Karte und übertragen sie per LoRa an einen zentralen Master. Der
Master speichert die Daten aller Slaves zentral, bestätigt den Empfang per ACK und
führt je Slave die chronologische Reihenfolge über eine persistente Sequenznummer.
Ziel ist ein offlinefähiges, autarkes Erfassungssystem ohne Abhängigkeit von einer
LoRaWAN-Infrastruktur.

## 2. Aktueller Entwicklungsstand

Bereits funktionsfähig und nachgewiesen:

- **Sensoranbindung**: SEN66-Luftsensor über I2C (GP0/GP1) an Raspberry Pi Pico 2 W;
  optionaler DS18B20-Bodensensor im Code enthalten, am 11.08.2026 nicht angeschlossen
  nachgewiesen.
- **SD-Speicherung**: lokales Schreiben auf Slave- und Master-SD auf beiden
  Testgeräten erfolgreich; die geplante Blockaufteilung zu je 3.000
  Sequenznummern ist noch nicht implementiert.
- **LoRa-Kommunikation**: Waveshare Pico-LoRa-SX1262-868M; 21 vollständige
  bidirektionale Ping-Pong-Folgen am 11.08.2026 nachgewiesen; produktive
  Datenübertragung im Systemintegrationstest am 21.08.2026.
- **ACK-Verfahren**: Master sendet ein Erfolgs-ACK erst nach erfolgreicher
  zentraler Speicherung. Das neunfeldrige V1-ACK ordnet die Bestätigung über
  Master-Ursprung, Slave-Ziel und Sequenznummer eindeutig zu; der vorläufige
  Timeout beträgt 3 s.
- **Sequenzverwaltung**: persistente Sequenznummer je Slave; lokale Rekonstruktion
  des Sequenzstands nach Neustart aus der Slave-SD; FIFO-Nachsenden ausstehender
  Datensätze mit Abbruch beim ersten fehlenden ACK.
- **Konfiguration**: lokale `/config.json` pro Gerät mit Rollenvalidierung;
  `config.example.json` (Slave) und `config.master.example.json` (Master) als
  versionierte Vorlagen; feste `master_id` beim Slave, `monitored_slaves` (mindestens eine ID, keine feste Obergrenze)
  beim Master.
- **Vorhandene Tests**: 52 Unit-Tests auf dem Entwicklungsrechner für
  Architekturgrenzen, Composition Root, Fehlerbehandlung, Codec-Rundlauf,
  Speichern-vor-Senden, FIFO-Abbruch, Duplikat-ACK und SD-Rekonstruktion.

Seit dem 03.09.2026 implementiert und per Unit-Test geprüft: routingfähiges
V1-Datenpaket mit 22 Feldern und neunfeldriges ACK. Noch nicht umgesetzt sind das
elffeldrige Diagnoseereignis, das V1-Speicherformat und die
`NO_PACKET`-Lückenlogik. Die Sequenzabfrage ohne Slave-SD ist noch auf echter
Hardware zu testen.

## 3. Systemablauf

Weg eines Messdatensatzes im Normalfall:

```
Sensoren -> Slave-SD -> LoRa -> Master-SD -> ACK
```

1. **Sensoren**: Der Slave löst im 15-Minuten-Intervall genau einen Messzyklus aus
   und erzeugt einen logischen Messdatensatz mit Sequenznummer und Statusflags.
2. **Slave-SD**: Der Datensatz wird vor dem Funkversuch lokal gesichert; bei
   SD-Fehler wird er direkt übertragen und der Speicherfehler im Status markiert
   (UC-13).
3. **LoRa**: Der Slave sendet das Paket an den konfigurierten Master
   (`master_id`).
4. **Master-SD**: Der Master validiert das Paket, ordnet es dem Slave zu, ergänzt
   Empfangszeitstempel und Funkmetadaten (RSSI, SNR) und speichert es zentral.
5. **ACK**: Erst nach erfolgreicher Speicherung sendet der Master die
   Empfangsbestätigung.

**Verhalten bei fehlendem ACK**:

- Der Datensatz bleibt beim Slave als ausstehend erhalten und wird im nächsten
  15-Minuten-Zyklus erneut gesendet.
- Der Slave sendet ausstehende Datensätze in FIFO-Reihenfolge; beim ersten
  fehlenden oder unpassenden ACK endet der Sendedurchlauf bis zum nächsten Zyklus.
- Empfang der Bestätigung mit anderer Master-ID wird abgelehnt.
- Ein erneut empfangenes Duplikat speichert der Master nicht noch einmal und
  bestätigt es mit ACK-Ergebniscode `2`.

## 4. Technische Entscheidungen

- **Sternstruktur**: direkte Punkt-zu-Punkt-Kommunikation jeder Slave zu einem
  Master; im Kernsystem keine Paketweiterleitung durch Slaves.
- **Master-Zuordnung über Konfiguration**: jeder Slave enthält die feste
  `master_id` in seiner `/config.json`; keine automatische Master-Erkennung, kein
  Erkennungssignal.
- **überwachte Slaves**: der Master führt `monitored_slaves` (mindestens eine eindeutige
  ID, keine feste Obergrenze); nur eingetragene Slaves werden als reguläre Datenquellen akzeptiert.
- **15-Minuten-Zyklus**: autonomer Messrhythmus je Slave; chronologische Ordnung
  über persistente Sequenznummer, nicht über absolute Zeit.
- **Optionale Mesh-Erweiterung**: V1-Kopf ist routingfähig vorbereitet (Ursprung,
  Endziel, nächster Hop, Hop-Zähler, Hop-Limit); statisches Relay oder
  dynamisches Mesh nur als Kann-Erweiterung bei verbleibender Zeit, nicht Teil der
  Kernumsetzung.

## 5. Teststand

Erfolgreich durchgeführt:

- **Ping-Pong-Test** (11.08.2026): 21 bidirektionale PING/PONG-Folgen, isolierter
  SX1262-Transport.
- **Master-Starttest** (20.08.2026): konsolidierter Start mit OLED, `/config.json`,
  SD-Karte, SX1262 bis in die Empfangsschleife.
- **Master-Slave-Systemintegrationstest** (21.08.2026): Sequenzen 5-16 in zwölf
  aufeinanderfolgenden 15-Minuten-Intervallen; Datentransfer, zentrale Speicherung,
  ACK und Slave-Neustart.
- **ACK-Wiederholtest**: nach `ACK missing for sequence 21` später erfolgreiche
  Übertragung; Duplikatvermeidung nachgewiesen.
- **Speichertests**: lokales Schreiben auf beiden Geräten; SD-Rekonstruktion des
  Sequenzstands nach Neustart.
- **Unit-Tests**: 52 Tests für Architektur, Adapterverträge, Fehlerbehandlung,
  Codec, FIFO und Persistenz.

- **V1-Hardwaretest** (04.09.2026): drei bestätigte Übertragungen, einmalige
  zentrale Speicherung und korrekte Sequenzfortsetzung nach Slave-Neustart.
  Nachweis: [Testprotokoll](Testprotokoll_V1_Hardwaretest_2026-09-04.md).

Offene Tests und Implementierungen:

- Master-Neustart und Rekonstruktion des Sequenzstands je Slave auf echter
  Hardware.
- Mehrere während eines Master-Ausfalls aufgelaufene Datensätze.
- Mehrgerätetest mit mehr als einem realen Slave plus zehn simulierten Slaves.
- Reichweiten- und Störungstest unter realen Einsatzbedingungen.
- Dauerbetrieb (zunächst 24 h, vor Freigabe mindestens 7 Tage).
- Hardwaretest der `Q`/`R`-Sequenzabfrage ohne Slave-SD.
- Hardwarevalidierung des 3-Sekunden-ACK-Timeouts.
- Implementierung und Test des V1-Diagnose- und Speicherformats.
- Energiebilanz und praktischer Einjahres-Laufzeitnachweis.

## 6. Offene Punkte

- **Zusätzliche Picos**: weitere Raspberry Pi Pico 2 W für Mehrgerätetests
  benötigt.
- **Strommessgerät**: für die rechnerische und praktische Energiebilanz sowie den
  Einjahres-Laufzeitnachweis erforderlich.
- **Sensorgrenzen**: Plausibilitätsgrenzen je Sensorfeld aus den Datenblättern
  der tatsächlich eingesetzten Sensorversion ableiten und versionieren.
- **Funkparameter**: entwicklungsspezifische Werte (868,1 MHz, 125 kHz, SF7, CR5,
  10 dBm, Sync Word 18) festgelegt; einsatzort-spezifische Werte nach Reichweiten-
  und regulatorischer Prüfung offen.
- **Reichweite**: zulässige Funkreichweite und Hindernisverhalten noch zu messen.
- **Dauerbetrieb**: Langzeitstabilität, Speicherwachstum und Paketverlustgrenzen
  offen.
- **Dokumentenabstimmung**: Das Lastenheft 0.4 wurde fachlich positiv
  rückgemeldet. Für das Pflichtenheft 0.4 stehen Durchsicht, Rückmeldung und die
  Klärung des formalen Freigabewegs noch aus.

## 7. Nächste geplante Schritte

1. Pflichtenheft mit Herrn Schnabel abstimmen und den formalen Freigabeweg klären.
2. Intervallüberwachung (NO_PACKET-Lückenlogik je Slave und 15-Minuten-Intervall)
   implementieren.
3. Mehrgerätetests mit mindestens zwei realen Slaves und zusätzlich zehn
   simulierten Slaves durchführen.
4. Energie- und Dauertests (zunächst 24 h, dann mindestens 7 Tage) ausführen.

## 8. Fragen an Herrn Schnabel

### Priorität 1: Im Termin unbedingt klären

1. Entsprechen die bisherige Umsetzung und die beschriebenen Abläufe Ihren
   Erwartungen? Gibt es etwas, das ich ändern soll?

2. Gibt es noch Änderungswünsche am Pflichtenheft? Wer bestätigt den abgestimmten
   Stand, und wie soll ich das dokumentieren?

3. Ich würde als Nächstes das V1-Speicherformat umsetzen, anschließend die Diagnose
   und die Erfassung fehlender Übertragungen (`NO_PACKET`). Gibt es aus Ihrer
   Sicht andere Prioritäten?

Das V1-Funkformat ist bereits implementiert und wurde am 04.09.2026 auf zwei
Picos getestet. Die vorgeschlagene Reihenfolge ist im Gespräch abzustimmen.

### Priorität 2: Hardware und Abnahmekriterien

4. Wann stehen die zwei zusätzlichen Raspberry Pi Picos zur Verfügung? Welches
   Strommessgerät beziehungsweise Labornetzteil kann ich nutzen, und wann?
   Kann es den Verbrauch über einen vollständigen Messzyklus aufzeichnen und
   kurze Stromspitzen beim LoRa-Senden erfassen?

5. Welche Reichweite und Einsatzbedingungen sollen wir nachweisen? Passen ein
   zunächst 24-stündiger, anschließend mindestens siebentägiger Dauerlauf sowie
   Tests mit zwei realen und zehn simulierten Slaves als Grundlage für die Abnahme?

### Priorität 3: Bei verbleibender Gesprächszeit

6. Welche genaue SEN66-Version wird eingesetzt, damit ich die passenden
   Plausibilitätsgrenzen aus dem Datenblatt ableiten kann?

7. Müssen die Funkparameter für den späteren Einsatzort bereits in diesem Projekt
   festgelegt werden, und wer übernimmt die regulatorische Prüfung?

8. Soll Mesh weiterhin ausschließlich eine optionale Erweiterung bleiben, die erst
   nach Fertigstellung und Prüfung des Sternsystems betrachtet wird?

## 9. Checkliste für die Demonstration

### 9.1 Benötigte Unterlagen und Hardware

- [ ] Projektzwischenstand und aktuelles Pflichtenheft lokal bereithalten.
- [ ] Zwei Raspberry Pi Pico 2 W mit montierten SX1262-Modulen und Antennen bereithalten.
- [ ] USB-Datenkabel, beide SD-Karten und den Entwicklungsrechner bereithalten.
- [ ] Sicherstellen, dass die ursprünglichen Pico-Stände weiterhin gesichert sind.
- [ ] Aktuellen Git-Commit beziehungsweise Softwarestand notieren.

### 9.2 Software vor dem Termin vorbereiten

- [ ] Aktuellen Repository-Stand auf beide Pico-Geräte übertragen.
- [ ] Auf dem Master `config.master.example.json` als Grundlage für `/config.json`
  verwenden.
- [ ] Master mit `device_id` `M01` und `monitored_slaves` `["C01"]` konfigurieren.
- [ ] Auf dem Slave `config.example.json` als Grundlage für `/config.json` verwenden.
- [ ] Slave mit `device_id` `C01` und `master_id` `M01` konfigurieren.
- [ ] Für beide Geräte einen gültigen aktuellen Wert für `time_epoch_utc` eintragen.
  Der aktuelle Unix-Zeitwert kann unmittelbar vor dem Kopieren mit
  `date -u +%s` ermittelt werden.
- [ ] Auf beiden Geräten identische Funkparameter einstellen.
- [ ] Für den Vorabtest `measurement_interval_s` vorübergehend auf `60` setzen.
- [ ] Gerätespezifische `/config.json` nicht in Git aufnehmen.

### 9.3 Vorabtest am Montag

- [ ] Zuerst den Master einschalten und warten, bis SD-Karte, LoRa und
  Empfangsschleife erfolgreich gestartet sind.
- [ ] Danach den Slave einschalten und mindestens einen vollständigen Messzyklus
  abwarten.
- [ ] Am Slave die lokale Speicherung und die Meldung `sequence ... acknowledged`
  kontrollieren.
- [ ] Am Master die Meldung `stored and acknowledged C01:...` kontrollieren.
- [ ] Auf der Slave-SD prüfen, ob der Datensatz lokal vorhanden ist.
- [ ] Auf der Master-SD prüfen, ob derselbe Datensatz mit Slave-ID und
  Sequenznummer genau einmal zentral gespeichert wurde.
- [ ] Prüfen, ob Datenpaket und ACK mit dem neuen V1-Format funktionieren.
- [ ] Erste und letzte gezeigte Sequenznummer notieren.
- [ ] Eine funktionierende Master-CSV und bei Bedarf serielle Ausgaben als
  Ersatznachweis sichern.

### 9.4 Ablauf der Live-Demonstration

1. Kurz das Ziel erklären: Slave misst, speichert lokal, sendet per LoRa und
   erhält erst nach zentraler Speicherung ein ACK.
2. Master starten und erfolgreichen Systemstart zeigen.
3. Slave starten und lokalen Messzyklus zeigen.
4. LoRa-Übertragung und ACK anhand der Ausgaben zeigen.
5. Master-CSV öffnen und Slave-ID, Sequenznummer sowie Messwerte zeigen.
6. Erklären, dass ein fehlendes ACK den Datensatz für einen späteren
   FIFO-Wiederholungsversuch ausstehend lässt.
7. Den erfolgreichen V1-Hardwaretest vom 04.09. nennen und anschließend die
   offenen Arbeiten erläutern: Speicherformat, Diagnose, `NO_PACKET`,
   Mehrgeräte-, Reichweiten-, Dauer- und Energietests.

### 9.5 Ersatzplan bei einem Demonstrationsfehler

- [ ] Keine längere Fehlersuche während des Gesprächs beginnen.
- [ ] Gesicherte Master-CSV des erfolgreichen Vorabtests zeigen.
- [ ] Testprotokoll und relevante Unit-Tests als reproduzierbaren Nachweis zeigen.
- [ ] Fehlerbild und Zeitpunkt notieren und die Ursache nach dem Termin prüfen.

### 9.6 Nach der Demonstration

- [ ] `measurement_interval_s` auf Master und Slave wieder auf `900` setzen.
- [ ] Prüfen, dass die produktive Konfiguration auf beiden Geräten gespeichert ist.
- [ ] Ergebnisse, Rückmeldungen und neue Entscheidungen im Projekttagebuch
  dokumentieren.
- [ ] Änderungen am Pflichtenheft erst anhand der besprochenen Entscheidungen
  vornehmen.
