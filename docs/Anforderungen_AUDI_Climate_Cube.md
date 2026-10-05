# Anforderungsdokument AUDI Climate Cube

Projekt: Datenübertragung und Speicherung für Climate Cubes  
Kontext: Pflichtpraktikum / AUDI Umweltstiftung  
Stand: 21.08.2026
Bearbeiter: Immanuel Mauch  
Dokumentstatus: **Arbeitsentwurf - noch nicht abschließend mit dem fachlichen Ansprechpartner Herrn Schnabel abgestimmt**

## Dokumentstatus Und Quellenlage

Dieses Dokument verbindet bestätigte fachliche Vorgaben von Herrn Schnabel, Erkenntnisse aus dem vorhandenen Code, Herstellerinformationen und technische Vorschläge. Nur Punkte mit dem Status **bestätigte fachliche Vorgabe von Herrn Schnabel** sind als bereits vorgegeben zu verstehen. Formulierungen wie `muss` oder `soll` beschreiben bei allen anderen Punkten den vorgeschlagenen Zielzustand und keine bereits erteilte Freigabe.

| Status | Bedeutung |
|---|---|
| bestätigte fachliche Vorgabe von Herrn Schnabel | aus der Rückmeldung von Herrn Schnabel abgeleitet |
| bereitgestellte Projektinformation | vom Bearbeiter als bereits feststehende Information genannt |
| durch Hardwareinformation bestätigt | konkret genanntes beziehungsweise verlinktes Bauteil |
| aus Bestandscode abgeleitet | im vorhandenen `code.py` oder in `lib/` festgestellt; reale Hardware noch prüfen |
| technischer Vorschlag | fachlich vorgeschlagene Ausgestaltung, noch mit Herrn Schnabel abzustimmen |
| vorläufige Arbeitsannahme | dient der aktuellen Planung, ist aber noch nicht entschieden |
| offen | Entscheidung oder praktischer Nachweis steht aus |

## 1. Ziel Des Projekts

Ziel des Projekts ist die Entwicklung einer Softwarelösung für Climate Cubes, mit der Messdaten regelmäßig erfasst, lokal gesichert und per LoRa Peer-to-Peer an einen zentralen Master-ClimateCube übertragen werden können.

Das System soll ohne vorhandene Kommunikationsinfrastruktur funktionieren, da die Climate Cubes auch an abgelegenen Orten, zum Beispiel in Peru, eingesetzt werden können. LoRaWAN ist daher nicht vorgesehen.

Der Master-ClimateCube soll die Daten mehrerer Slave-ClimateCubes zentral auf einer SD-Karte speichern. Jeder Slave-ClimateCube soll seine eigenen Messdaten zusätzlich lokal auf seiner eigenen SD-Karte sichern, damit bei Funkproblemen keine Daten verloren gehen.

## 2. Bekannte Hardwarebasis

Nach aktuellem Stand soll für die LoRa-Kommunikation folgendes Modul verwendet werden:

| Komponente | Stand |
|---|---|
| LoRa-Modul | Waveshare Pico-LoRa-SX1262-868M |
| Funkchip | SX1262 |
| Frequenzbereich | 868M-Variante, laut Hersteller 863 bis 870 MHz |
| Zielplattform | Raspberry Pi Pico / Pico-kompatible Boards |
| Kommunikationsbus | SPI |
| Versorgung | laut Pinout über Pico-VSYS; genaue elektrische Daten an der realen Hardware bestätigen |
| Modulation | LoRa, zusätzlich FSK/GFSK unterstützt |
| Sendeleistung | laut Hersteller bis 22 dBm programmierbar |
| Paketgröße | laut Hersteller Packet Engine bis 256 Bytes |
| Stromversorgung | Modul besitzt Batterieanschluss und Ladecontroller; konkrete Systemversorgung noch zu prüfen |
| Antenne | externer Antennenanschluss vorhanden; Antennentyp und Montage im Cube prüfen |

Wichtig: Das Modul unterstützt zwar LoRaWAN, im Projekt soll aber bewusst **kein LoRaWAN**, sondern **LoRa Peer-to-Peer** genutzt werden.

Quelle der Modulinfo: Waveshare Produktseite "Pico-LoRa-SX1262-868M", abgerufen am 04.08.2026.

### 2.1 Softwarebasis für Die LoRa-Ansteuerung

Die Programmiersprache Python wurde als bereitgestellte Projektinformation festgehalten. Da der vorhandene Climate-Cube-Code bereits als `code.py` mit CircuitPython-Bibliotheken aufgebaut ist, ist **CircuitPython** nach aktuellem Stand die bevorzugte Python-Laufzeit auf dem Raspberry Pi Pico.

Als möglicher Treiber für den SX1262 wurde die Open-Source-Bibliothek `micropySX126X` identifiziert. Laut Projektdokumentation unterstützt sie MicroPython und CircuitPython und wurde unter anderem mit einem Raspberry Pi Pico und dem Waveshare SX126x Pico LoRa HAT getestet. Die Bibliothek bietet direktes Senden und Empfangen ohne LoRaWAN sowie Python-Beispiele für Ping-Pong, TX und RX.

| Eigenschaft | Stand |
|---|---|
| Programmiersprache | Python, bereitgestellte Projektinformation |
| bevorzugte Laufzeit | CircuitPython, aufgrund des vorhandenen Climate-Cube-Codes |
| möglicher SX1262-Treiber | `micropySX126X` |
| Kommunikationsart | direktes LoRa Peer-to-Peer über `send()` und `recv()` |
| Bibliotheksstatus | Drittanbieterbibliothek; Funktion auf der konkreten Hardware muss getestet werden |
| Speicherhinweis | Bibliotheksdateien bei Speicherproblemen nach Empfehlung des Projekts als `.mpy` kompilieren |

Bekannte Pinbelegung des Waveshare-Moduls und des Python-Ping-Pong-Beispiels:

| SX1262-Signal | Raspberry Pi Pico |
|---|---|
| SCK / CLK | GP10 |
| MOSI | GP11 |
| MISO | GP12 |
| CS / NSS | GP3 |
| DIO1 / IRQ | GP20 |
| RESET | GP15 |
| BUSY | GP2 |

Die Python-Bibliothek besitzt ein Ping-Pong-Beispiel mit genau dieser GPIO-Zuordnung. Die dort voreingestellte Frequenz von 923 MHz darf für das eingesetzte 868-MHz-Modul nicht unverändert übernommen werden. Frequenz und weitere Funkparameter müssen für Modulvariante und Einsatzort passend konfiguriert werden.

## 3. Projektumfang

Der folgende Umfang ist ein Arbeitsstand. bestätigte Kernvorgaben und vorgeschlagene technische Ergänzungen werden in den Statusübersichten der Abschnitte 5 und 6 unterschieden.

### 3.1 Im Umfang Enthalten

| Bereich | Beschreibung |
|---|---|
| Messdatenerfassung | Slaves erfassen Messdaten in einem festen Zeitintervall |
| lokale Speicherung | Slaves speichern ihre eigenen Messdaten auf SD-Karte |
| LoRa-Kommunikation | Slaves senden Messdaten per LoRa Peer-to-Peer über das SX1262-Modul an den Master |
| zentrale Speicherung | Master speichert empfangene Daten aller Slaves auf SD-Karte |
| Zeitbezug | Sequenznummer und 15-Minuten-Rhythmus dokumentieren die Messreihenfolge; der Master ergänzt beim Speichern den Empfangszeitstempel |
| Slave-Verwaltung | pro Master sollen etwa 10 Slaves betrieben werden können |
| Datenformat | ein einheitliches, dokumentiertes und paketgrößenbewusstes Datenformat wird definiert |
| Fehlerbehandlung | grundlegende Fehlerfälle werden erkannt und dokumentiert |

### 3.2 Nicht Im Kernumfang Enthalten

| Bereich | Begründung |
|---|---|
| LoRaWAN | nicht nutzbar, da am Einsatzort keine Infrastruktur vorausgesetzt werden kann |
| Cloud-Anbindung | bisher nicht gefordert und für Offline-Betrieb nicht notwendig |
| Webplattform mit Benutzerverwaltung | wäre für den Kernumfang zu groß |
| vollständiges dynamisches Mesh-Netzwerk | vorläufig nicht im Kernumfang; Einordnung ist mit Herrn Schnabel abzustimmen |

## 4. Systemübersicht

Das geplante System besteht aus mehreren Slave-ClimateCubes und einem Master-ClimateCube. Die dargestellte direkte Sternstruktur ist eine vorläufige Arbeitsannahme und noch mit Herrn Schnabel abzustimmen.

```text
Slave 1  \
Slave 2   \
Slave 3    ---> LoRa Peer-to-Peer, SX1262 868 MHz ---> Master ClimateCube ---> SD-Karte
...       /
Slave 10 /
```

Jeder Slave arbeitet eigenständig:

```text
Sensoren -> Messdatensatz -> lokale SD-Karte
                          -> LoRa-Senden an Master
```

Der Master arbeitet zentral:

```text
LoRa-Empfang -> Daten prüfen -> Empfangszeitstempel ergänzen -> auf SD-Karte speichern
```

## 5. Funktionale Anforderungen

### Statusübersicht

| ID | Status / Herkunft |
|---|---|
| FA-01 | bestätigte fachliche Vorgabe von Herrn Schnabel: Messung alle 15 Minuten |
| FA-02 | bestätigte fachliche Vorgabe von Herrn Schnabel: lokale Slave-SD als Backup |
| FA-03 | bestätigte fachliche Vorgabe von Herrn Schnabel: LoRa Peer-to-Peer; SX1262-Modul durch Hardwareinformation konkretisiert |
| FA-04 | bestätigte fachliche Vorgabe von Herrn Schnabel: zentrale Speicherung auf der Master-SD |
| FA-05 | bereitgestellte Projektinformation: Ein genauer absoluter Messzeitpunkt ist nicht erforderlich; Sequenznummer und 15-Minuten-Rhythmus sichern Reihenfolge und Vollstaendigkeit; Master-Empfangszeit ist optional |
| FA-06 | technischer Vorschlag: eindeutige Slave-ID |
| FA-07 | technischer Vorschlag: fortlaufende Sequenznummer |
| FA-08 | bestätigte fachliche Vorgabe von Herrn Schnabel: ungefähr zehn Slaves pro Master |
| FA-09 | technischer Vorschlag: Fehlererkennung und Fehlerlogging |
| FA-10 | offener technischer Vorschlag: ACK und Wiederholungsstrategie noch abzustimmen |
| FA-11 | vorläufige Arbeitsannahme: direkte Verbindung zuerst; Bedeutung von Mesh noch abzustimmen |
| FA-12 | technischer Vorschlag aus den Hardwaregrenzen: kompakte Pakete |
| FA-13 | technischer Vorschlag: gemeinsame Funkparameter dokumentieren |

### FA-01: Regelmäßige Messdatenerfassung

**Beschreibung:**  
Jeder Slave-ClimateCube muss in einem festen Intervall Messdaten erfassen.

| Eigenschaft | Wert |
|---|---|
| Priorität | kritisch |
| Intervall | 15 Minuten |
| Akzeptanzkriterium | Der Slave erzeugt in einem 15-Minuten-Rhythmus einen Messdatensatz |

### FA-02: Lokale Speicherung Auf Dem Slave

**Beschreibung:**  
Jeder Slave muss die selbst erfassten Messdaten lokal auf seiner SD-Karte speichern.

| Eigenschaft | Wert |
|---|---|
| Priorität | kritisch |
| Zweck | Backup bei fehlgeschlagener Funkübertragung |
| Akzeptanzkriterium | Nach mehreren Messzyklen sind die Messwerte auf der Slave-SD-Karte nachvollziehbar gespeichert |

### FA-03: LoRa Peer-to-Peer-Übertragung Mit SX1262

**Beschreibung:**  
Jeder Slave muss seine Messdaten per LoRa Peer-to-Peer an den Master senden. Als Funkmodul ist das Waveshare Pico-LoRa-SX1262-868M vorgesehen.

| Eigenschaft | Wert |
|---|---|
| Priorität | kritisch |
| Technologie | LoRa Peer-to-Peer |
| Modul | Waveshare Pico-LoRa-SX1262-868M |
| Frequenz | 868 MHz / 863 bis 870 MHz |
| Bus | SPI |
| Software | Python, bevorzugt CircuitPython |
| möglicher Treiber | `micropySX126X` |
| Nicht erlaubt | LoRaWAN als Betriebsmodus |
| Akzeptanzkriterium | Zwei Picos können zunächst per Python einen Ping-Pong-Test durchführen; anschliessend kann ein Slave einen Datensatz erfolgreich über SX1262-LoRa an den Master übertragen |

### FA-04: Zentrale Speicherung Auf Dem Master

**Beschreibung:**  
Der Master muss empfangene Messdaten zentral auf seiner SD-Karte speichern.

| Eigenschaft | Wert |
|---|---|
| Priorität | kritisch |
| Akzeptanzkriterium | Der Master speichert empfangene Datensätze mehrerer Slaves in einer zentralen Datei oder Dateistruktur |

### FA-05: Zeitliche Nachvollziehbarkeit Und Master-Empfangszeit

**Beschreibung:**  
Jeder Datensatz besitzt eine pro Slave fortlaufende Sequenznummer. Zusammen mit dem vorgesehenen 15-Minuten-Messrhythmus macht sie Reihenfolge, Luecken und Wiederholungen nachvollziehbar. Der Master ergaenzt beim zentralen Speichern einen `received_timestamp`, der den Empfangs- beziehungsweise Speicherzeitpunkt beschreibt.

Ein `measurement_timestamp` des Slaves ist ohne RTC nach einem Neustart nicht zwingend eine verlaessliche absolute Uhrzeit. Er muss deshalb von der Master-Empfangszeit unterscheidbar bleiben und darf ohne gueltige Zeitsynchronisation nicht als exakter absoluter Messzeitpunkt ausgewertet werden. Bei spaeter nachgesendeten Datensaetzen entspricht der Master-Empfangszeitstempel nicht dem urspruenglichen Messzeitpunkt.

| Eigenschaft | Wert |
|---|---|
| Priorität | kritisch fuer Reihenfolge und Vollstaendigkeit; genaue absolute Uhrzeit nicht erforderlich |
| Begründung | Die Slaves besitzen keine RTC; im Hardwaretest wurde die Slave-Zeit nach einem Neustart zurueckgesetzt |
| Nachvollziehbarkeit | `device_id`, persistente `sequence_number`, 15-Minuten-Messrhythmus und `received_timestamp` des Masters |
| Akzeptanzkriterium | Datensaetze sind pro Slave eindeutig geordnet; Luecken und Duplikate sind anhand der Sequenznummer erkennbar; jeder zentral gespeicherte Datensatz enthaelt einen Master-Empfangszeitstempel |
| Entscheidung | 24.08.2026: Die Nachvollziehbarkeit ueber Sequenznummer und 15-Minuten-Rhythmus ist ausreichend |

### FA-06: Eindeutige Slave-ID

**Beschreibung:**  
Jeder Slave muss eine eindeutige Kennung besitzen, damit die Messdaten später zugeordnet werden können.

| Eigenschaft | Wert |
|---|---|
| Priorität | kritisch |
| Akzeptanzkriterium | Jeder empfangene Datensatz kann eindeutig einem Slave zugeordnet werden |

### FA-07: Sequenznummer Pro Slave

**Beschreibung:**  
Jeder Slave soll eine fortlaufende Sequenznummer mitschicken.

| Eigenschaft | Wert |
|---|---|
| Priorität | wichtig |
| Zweck | Erkennen fehlender oder doppelter Datensätze |
| Akzeptanzkriterium | Der Master speichert die Sequenznummer jedes empfangenen Datensatzes |

### FA-08: Unterstützung Mehrerer Slaves

**Beschreibung:**  
Ein Master soll Daten von mehreren Slaves empfangen und speichern können.

| Eigenschaft | Wert |
|---|---|
| Priorität | kritisch |
| Zielwert | etwa 10 Slaves pro Master |
| Akzeptanzkriterium | Das Konzept und die Datenstruktur sind für 10 Slaves ausgelegt; Tests erfolgen zunächst mit verfügbarer Hardware |

### FA-09: Fehlererkennung Und Fehlerlogging

**Beschreibung:**  
Das System soll grundlegende Fehler erkennen und dokumentieren.

| Eigenschaft | Wert |
|---|---|
| Priorität | wichtig |
| Beispiele | SD-Karte nicht verfügbar, ungültiger Datensatz, Funkfehler, LoRa-Modul nicht erreichbar |
| Akzeptanzkriterium | Fehler werden nicht still ignoriert, sondern im Systemstatus oder in einer Logdatei sichtbar |

### FA-10: Empfangsbestätigung

**Beschreibung:**  
Der Master kann optional eine Empfangsbestätigung an den sendenden Slave zurücksenden.

| Eigenschaft | Wert |
|---|---|
| Priorität | wichtig |
| Status | noch zu entscheiden |
| Zweck | Slave erkennt, ob der Datensatz erfolgreich angekommen ist |
| Akzeptanzkriterium | Wenn ACK umgesetzt wird, kann der Slave erfolgreiche und fehlgeschlagene Sendungen unterscheiden |

### FA-11: Mögliche Weiterleitung / Mesh (Vorläufig)

**Beschreibung:**  
Als vorläufige Arbeitsannahme wird zuerst eine direkte Kommunikation zwischen Slaves und Master vorgesehen. Falls ein Slave den Master nicht direkt erreicht, könnte eine Weiterleitung über andere Slaves ergänzt werden. Ob Mesh erforderlich oder nur optional ist, muss noch mit Herrn Schnabel abgestimmt und anhand von Reichweitentests bewertet werden.

| Eigenschaft | Wert |
|---|---|
| Priorität | vorläufig optional |
| Status | Arbeitsannahme; Bestätigung durch Herrn Schnabel ausstehend |
| Begründung | Die bisherigen Informationen nennen eine direkte Übertragung an den Master; Mesh wurde als mögliche Ergänzung angesprochen |
| Akzeptanzkriterium | Entscheidung ist mit Herrn Schnabel abgestimmt; eine Umsetzung erfolgt nur bei entsprechender Anforderung oder unzureichender direkter Reichweite |

### FA-12: Paketgröße Begrenzen

**Beschreibung:**  
Da LoRa-Pakete klein gehalten werden müssen und das SX1262-Modul laut Hersteller eine Packet Engine bis 256 Bytes unterstützt, muss das Nutzdatenformat kompakt bleiben.

| Eigenschaft | Wert |
|---|---|
| Priorität | kritisch |
| Ziel | ein Messdatensatz passt in ein einzelnes LoRa-Paket, sofern die Messwertanzahl dies erlaubt |
| Akzeptanzkriterium | Der definierte Nutzdatensatz wird auf Länge geprüft und bleibt innerhalb der nutzbaren Paketgröße |

### FA-13: Funkparameter Dokumentieren

**Beschreibung:**  
Die verwendeten LoRa-Funkparameter müssen dokumentiert werden, damit Slaves und Master kompatibel konfiguriert sind.

| Eigenschaft | Wert |
|---|---|
| Priorität | wichtig |
| Beispiele | Frequenz, Bandbreite, Spreading Factor, Coding Rate, Sendeleistung |
| Akzeptanzkriterium | Master und Slaves verwenden dieselben dokumentierten Funkparameter |

## 6. Nicht-Funktionale Anforderungen

### Statusübersicht

| ID | Status / Herkunft |
|---|---|
| NFA-01 | aus der bestätigten lokalen Backup-Speicherung abgeleitet |
| NFA-02 | bestätigte Rahmenbedingung: Betrieb ohne LoRaWAN-Infrastruktur |
| NFA-03 | technischer Vorschlag für die spätere Auswertbarkeit |
| NFA-04 | technischer Vorschlag für Erweiterbarkeit |
| NFA-05 | technischer Vorschlag für Wartbarkeit |
| NFA-06 | technische Arbeitsannahme aufgrund des Akkubetriebs |
| NFA-07 | aus der bestätigten Zielgröße von etwa zehn Slaves abgeleitet |
| NFA-08 | durch Hardwareinformation konkretisiert; praktischer Nachweis offen |
| NFA-09 | offener Prüfpunkt, keine bestätigte regulatorische Aussage |
| NFA-10 | Python ist festgelegt; CircuitPython und der konkrete Treiber sind vorläufig und praktisch zu prüfen |

### NFA-01: Zuverlässigkeit

Das System muss Messdaten auch bei temporären Funkproblemen lokal sichern.

| Priorität | Akzeptanzkriterium |
|---|---|
| kritisch | Slave-Daten gehen bei fehlgeschlagener Übertragung nicht verloren, da sie lokal gespeichert werden |

### NFA-02: Offline-Fähigkeit

Das System muss ohne Internet, Mobilfunk, WLAN oder LoRaWAN-Infrastruktur funktionieren.

| Priorität | Akzeptanzkriterium |
|---|---|
| kritisch | Messung, Speicherung und Übertragung funktionieren lokal zwischen Slaves und Master |

### NFA-03: Nachvollziehbarkeit

Die gespeicherten Daten müssen später auswertbar und eindeutig interpretierbar sein.

| Priorität | Akzeptanzkriterium |
|---|---|
| kritisch | Datenformat, Einheiten, Slave-ID, Sequenznummer und Zeitstempel sind dokumentiert |

### NFA-04: Erweiterbarkeit

Das System soll so aufgebaut sein, dass weitere Slaves oder Messwerte ergänzt werden können.

| Priorität | Akzeptanzkriterium |
|---|---|
| wichtig | Neue Sensorwerte können im Datenformat ergänzt werden, ohne das Gesamtsystem neu zu entwerfen |

### NFA-05: Wartbarkeit

Der Code soll strukturiert und verständlich sein.

| Priorität | Akzeptanzkriterium |
|---|---|
| wichtig | Funktionen für Messung, Speicherung und Kommunikation sind nachvollziehbar getrennt |

### NFA-06: Energieeffizienz

Da die Climate Cubes über Akku laufen, soll die Software unnötige Aktivität vermeiden.

| Priorität | Akzeptanzkriterium |
|---|---|
| wichtig | Messung und Senden erfolgen im festen Intervall; zwischen den Messungen wird keine unnötige Daueraktivität erzeugt |

### NFA-07: Skalierbarkeit Im Zielumfang

Ein Master soll für etwa 10 Slaves ausgelegt werden.

| Priorität | Akzeptanzkriterium |
|---|---|
| wichtig | Slave-IDs und Speicherstruktur unterstützen mindestens 10 Slaves |

### NFA-08: Hardwarekompatibilität

Die Software muss mit dem Waveshare Pico-LoRa-SX1262-868M und dem verwendeten Raspberry-Pi-Pico-kompatiblen Board lauffähig sein.

| Priorität | Akzeptanzkriterium |
|---|---|
| kritisch | LoRa-Kommunikation über SPI mit dem SX1262-Modul funktioniert auf der eingesetzten Hardware |

### NFA-09: Regulatorische Plausibilität

Die Nutzung der 868-MHz-Variante muss für den Einsatzort bewertet werden. für Europa ist 868 MHz typisch, für Peru muss geprüft werden, ob 868 MHz dort erlaubt und geeignet ist.

| Priorität | Akzeptanzkriterium |
|---|---|
| wichtig | Vor einem Feldeinsatz ist dokumentiert, ob die 868-MHz-Variante am Einsatzort verwendet werden darf |

### NFA-10: Python-Kompatibilität

Die Software einschließlich der SX1262-Ansteuerung muss direkt auf dem Raspberry Pi Pico in einer geeigneten Python-Laufzeit ausgeführt werden können. Bevorzugt wird CircuitPython, damit der vorhandene Climate-Cube-Code und die bereits eingesetzten Bibliotheken weiterverwendet werden können.

| Priorität | Akzeptanzkriterium |
|---|---|
| kritisch | Das SX1262-Modul kann aus Python initialisiert werden und zwei Testgeräte können ohne LoRaWAN Daten senden und empfangen |

## 7. Vorgeschlagenes Datenformat

Das konkrete Datenformat wird nach Sichtung der Sensoren finalisiert. Wegen der LoRa-Paketgröße sollte der übertragene Nutzdatensatz möglichst kompakt sein. Für die SD-Karte kann ein lesbares CSV-Format genutzt werden.

Ein detaillierter technischer Arbeitsentwurf liegt in `Datenformat_V1_Entwurf.md`. Er definiert vorläufig einen gemeinsamen logischen Messdatensatz, eine kompakte ASCII-Funkdarstellung sowie Slave- und Master-CSV-Strukturen. Der Entwurf ist im hexagonalen Architektur-Prototyp implementiert, aber noch nicht technisch freigegeben oder auf den beiden Pico-Geräten integriert getestet. Messwertumfang und ACK-Grundablauf sind bestätigt; insbesondere Zeitgenauigkeit, Geräte-ID-Vergabe, Plausibilitätsgrenzen und ACK-Timeout bleiben abzustimmen.

Bisheriges vereinfachtes Funkbeispiel (nicht verbindlich):

```text
cube_01,125,22.4,58.1,430,4.2,8.1,OK
```

Bisheriges vereinfachtes Master-CSV-Beispiel (nicht verbindlich):

```text
master_timestamp,slave_id,sequence_number,temperature,humidity,co2,pm25,pm10,status_code,rssi,snr
2026-08-11T10:15:00,cube_01,125,22.4,58.1,430,4.2,8.1,OK,-96,7.5
```

Pflichtfelder:

| Feld | Zweck |
|---|---|
| master_timestamp | zeitliche Einordnung des Datensatzes |
| slave_id | Zuordnung zum ClimateCube |
| sequence_number | Erkennung fehlender Messungen |
| sensor_values | eigentliche Messwerte |

Optionale Felder:

| Feld | Zweck |
|---|---|
| battery_voltage | Wartung und Diagnose |
| status_code | Fehler- oder Zustandsinformation |
| rssi | Bewertung der Funkqualität |
| snr | Bewertung der Funkqualität |

## 8. Schnittstellen Und Komponenten

| Komponente | Aufgabe | Status |
|---|---|---|
| Raspberry Pi Pico / Pico-kompatibles Board | Steuerung von Messung, SD und LoRa | wahrscheinlich gesetzt |
| Waveshare Pico-LoRa-SX1262-868M | LoRa Peer-to-Peer-Kommunikation | gesetzt |
| SX1262 | Funkchip für LoRa | gesetzt |
| Python / CircuitPython | Programmiersprache und bevorzugte Laufzeit auf dem Pico | Python gesetzt, CircuitPython praktisch prüfen |
| `micropySX126X` | möglicher Python-Treiber für direktes SX1262-LoRa | identifiziert, Hardwaretest ausstehend |
| SPI-Bus | Verbindung zwischen Pico und LoRa-Modul | LoRa nutzt nach Dokumentation GP10 bis GP12 sowie GP3; reale Belegung prüfen |
| Sensorik | Messwerte erfassen | aus `code.py` bekannt: SEN66, analoger Bodenfeuchtesensor und DS18B20; an Hardware bestätigen |
| OLED-Display | lokale Anzeige der Messwerte | aus `code.py` bekannt; I2C über GP0 und GP1, an Hardware bestätigen |
| SD-Karte Slave | lokales Backup | vorgesehen |
| SD-Karte Master | zentrale Speicherung | vorgesehen |
| Auswertungssoftware | späteres Einlesen und Darstellen | nicht Kernumfang dieser Anforderungen |

## 9. Abhängigkeiten

| Abhängigkeit | Auswirkung |
|---|---|
| genaue Pico-Variante | bestimmt Pinbelegung und verfügbare Ressourcen |
| Waveshare SX1262-Pinout | LoRa-Pins sind bekannt; besonders der Konflikt zwischen BAT_AD und Bodenfeuchte auf GP26 muss praktisch geklärt werden |
| Python-Laufzeit und SX1262-Treiber | `micropySX126X` muss mit der eingesetzten CircuitPython-Version und dem bestehenden Code getestet werden |
| Sensorliste | SEN66, analoger Bodenfeuchtesensor und DS18B20 sind im vorhandenen Code enthalten; reale Bestückung und Einheiten müssen bestätigt werden |
| SD-Kartenanbindung | vorhandener Code nutzt SPI mit GP18, GP19, GP16 und CS auf GP17; reale Verschaltung muss bestätigt werden |
| Messzeitplanung | vorhandener Code nutzt 900 Sekunden ab Messende; die SEN66-Aufwärmzeit kann den Abstand zwischen Messstarts verlängern |
| Energieversorgung | beeinflusst Intervall, Schlafmodus und Funkstrategie |
| Reichweite vor Ort | entscheidet, ob Mesh notwendig wird |
| 868-MHz-Zulässigkeit am Einsatzort | wichtig für realen Betrieb ausserhalb Europas |

## 10. Offene Punkte für Den Hardwaretermin Am 11.08.2026

| Nr. | Frage |
|---|---|
| 1 | Welche genaue Raspberry-Pi-Pico-Variante wird verwendet? |
| 2 | Ist das Waveshare Pico-LoRa-SX1262-868M tatsächlich auf allen Slaves und dem Master verbaut? |
| 3 | Stimmen die dokumentierten LoRa-Pins GP2, GP3, GP10, GP11, GP12, GP15 und GP20 mit der vorhandenen Hardware überein und welche GPIOs bleiben frei? |
| 4 | Wie wird der Konflikt auf GP26 gelöst? Der vorhandene Code nutzt GP26 für die Bodenfeuchte, das Waveshare-Modul verwendet GP26 als BAT_AD. |
| 5 | Sind SEN66, analoger Bodenfeuchtesensor und DS18B20 wie im vorhandenen `code.py` tatsächlich angeschlossen? |
| 6 | Werden Temperatur, Luftfeuchte, CO2, PM1, PM2.5, PM4, PM10, VOC-Index, NOx-Index, Bodenfeuchte und Bodentemperatur benötigt und welche Einheiten sollen gespeichert werden? |
| 7 | Entspricht die reale SD-Anbindung dem Code: SCK GP18, MOSI GP19, MISO GP16 und CS GP17? |
| 8 | Können SD-Karte und LoRa-Modul wie geplant über getrennte SPI-Busse betrieben werden und bestehen weitere elektrische Pin-Konflikte? |
| 9 | Ist das OLED-Display wie im Code über I2C an GP0 und GP1 angeschlossen und gibt es Taster oder weitere Peripherie? |
| 10 | Funktioniert das Python-Ping-Pong-Beispiel mit `micropySX126X` auf zwei vorhandenen Picos? |
| 11 | Welche CircuitPython-Version und welche Bibliotheksversionen verwendet der vorhandene Climate-Cube-Code? |
| 12 | Soll der Abstand zwischen den Messstarts exakt 15 Minuten betragen? Der aktuelle Code startet die 900 Sekunden erst nach Abschluss der Messung und kann sich durch die SEN66-Aufwärmzeit verschieben. |
| 13 | Geklaert am 24.08.2026: Kein genauer absoluter Messzeitpunkt erforderlich; chronologische Ordnung ueber persistente Sequenznummer und 15-Minuten-Rhythmus. |
| 14 | Reicht eine direkte Verbindung Slave zu Master voraussichtlich aus? |
| 15 | Gibt es konkrete Anforderungen an Reichweite, Akkulaufzeit oder Gehäusebetrieb? |
| 16 | Wie viele Picos und SX1262-Module stehen für Entwicklungs- und Mehrgerätetests zur Verfügung? |
| 17 | Muss die 868-MHz-Variante für Peru regulatorisch geprüft werden und wer übernimmt diese Klärung? |

## 11. Akzeptanzkriterien für Einen Vorzeigbaren Stand

Ein vorzeigbarer Stand des AUDI-Climate-Cube-Projekts ist erreicht, wenn folgende Punkte erfüllt sind:

| Nr. | Kriterium |
|---|---|
| 1 | Ein Slave erzeugt regelmäßig Messdatensätze |
| 2 | Ein Slave speichert Messdaten lokal auf SD-Karte |
| 3 | Ein Slave sendet Messdaten per SX1262-LoRa an den Master |
| 4 | Der Master empfängt Datensätze korrekt |
| 5 | Der Master speichert empfangene Daten mit eindeutig bezeichnetem Empfangszeitstempel auf SD-Karte |
| 6 | Die Daten enthalten mindestens Slave-ID, Sequenznummer und Messwerte |
| 7 | Das Datenformat ist dokumentiert und für LoRa-Pakete geeignet |
| 8 | Die verwendeten Funkparameter sind dokumentiert |
| 9 | Grundlegende Fehlerfälle sind dokumentiert oder geloggt |
| 10 | Das System ist konzeptionell für etwa 10 Slaves ausgelegt |
| 11 | Die Grenzen des Systems, insbesondere Zeitstempel, 868-MHz-Einsatzort und Mesh, sind dokumentiert |
| 12 | Die LoRa-Kommunikation läuft direkt auf dem Pico mit Python; bevorzugt wird CircuitPython |

## 12. Priorisierte Umsetzung

### Stufe 1: Minimal Funktionierendes System

| Aufgabe | Ergebnis |
|---|---|
| Python-Treiber bereitstellen | `micropySX126X` und benötigte Abhängigkeiten liegen auf dem Pico; bei Bedarf als `.mpy` |
| SX1262-Modul ansprechen | Pico kann das LoRa-Modul aus Python initialisieren |
| Ping-Pong-Hardwaretest | Zwei Picos können über SX1262 direkt senden und empfangen |
| Funkparameter auf 868-MHz-Modul anpassen | keine ungeeignete Beispielkonfiguration wie 923 MHz wird unverändert verwendet |
| Messdatensatz erzeugen | Slave kann Test- oder Sensordaten strukturieren |
| lokal speichern | Slave schreibt Daten auf SD |
| LoRa senden | Slave sendet Datensatz über SX1262 |
| empfangen | Master liest Datensatz über SX1262 |
| zentral speichern | Master schreibt Datensatz mit Zeitstempel auf SD |

### Stufe 2: Robustes System

| Aufgabe | Ergebnis |
|---|---|
| Sequenznummern nutzen | fehlende Daten erkennbar |
| Fehlerlogging einbauen | Probleme nachvollziehbar |
| mehrere Slaves testen | System funktioniert mit mehr als einem Slave |
| Funkparameter abstimmen | Master und Slaves sind kompatibel konfiguriert |
| Datei- und Datenstruktur verbessern | Daten sind auswertbar und gut importierbar |

### Stufe 3: Erweiterungen

| Aufgabe | Ergebnis |
|---|---|
| ACK/Wiederholversuche | bessere Übertragungssicherheit |
| RSSI/SNR speichern | Funkqualität bewertbar |
| Mesh prüfen | Weiterleitung bei Reichweitenproblemen möglich |

## 13. Hinweise Zum Umfang

Das Kernprojekt sollte bewusst klein und robust gehalten werden. Ein vollständiges Mesh-Netzwerk, Cloud-Anbindung oder eine große Webplattform würden den Projektumfang deutlich vergrößern und sollten nur umgesetzt werden, wenn der Kern stabil funktioniert und Herr Schnabel dies ausdrücklich verlangt.

Durch die konkrete Festlegung auf das Waveshare Pico-LoRa-SX1262-868M wird die Kommunikationsseite greifbarer. Gleichzeitig müssen jetzt Pinbelegung, SPI-Nutzung, Beispielbibliotheken und die Zulässigkeit der 868-MHz-Variante für den späteren Einsatzort geprüft werden.

Die technische Recherche zeigt, dass direktes LoRa Peer-to-Peer mit dem SX1262 auch in Python grundsätzlich möglich ist. Die Bibliothek `micropySX126X` enthält dafür passende Sende-, Empfangs- und Ping-Pong-Funktionen. Da es sich um eine Drittanbieterbibliothek handelt, bleibt ein früher Test mit zwei realen Climate-Cube-Picos ein wichtiger technischer Meilenstein.

Die wichtigste technische Grundlage bleibt ein verlässliches Datenformat und eine stabile Speicherung auf Slave- und Masterseite.

## 14. Technische Quellen

| Quelle | Verwendung |
|---|---|
| [Waveshare Pico-LoRa-SX1262 Wiki](https://www.waveshare.com/wiki/Pico-LoRa-SX1262) | Hardware, Pinbelegung und Herstellerressourcen |
| [CodeUnit10X LoRa Basics Modem Ports](https://github.com/CodeUnit10X/lora_basics_modem_ports) | C/C++-Referenz für SX1262 und direktes LoRa-Ping-Pong |
| [micropySX126X](https://github.com/ehong-tl/micropySX126X) | Python-Treiber für MicroPython und CircuitPython |
| [micropySX126X Ping-Pong-Beispiel](https://github.com/ehong-tl/micropySX126X/tree/master/example/Ping%20Pong) | direkter Peer-to-Peer-Test mit zwei SX1262-Geräten |
