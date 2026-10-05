# Lastenheft AUDI Climate Cube

Projekt: Offline-Messdatenerfassung und LoRa-Übertragung für Climate Cubes  
Bearbeiter: Immanuel Mauch  
Stand: 24.08.2026
Version: 0.4
Dokumentstatus: **Entwurf zur fachlichen Prüfung - nicht freigegeben**

## 1. Zweck Des Dokuments

Dieses Lastenheft beschreibt aus fachlicher Sicht, **was** das Climate-Cube-System leisten soll und **wozu** die Funktionen benötigt werden. Es legt noch nicht fest, wie die Software intern aufgebaut oder implementiert wird.

Grundlage sind:

- die bisherigen Informationen von Herrn Schnabel,
- der bereitgestellte Climate-Cube-Prototyp,
- die am 11.08.2026 untersuchte Hardware,
- der erfolgreiche isolierte LoRa-Ping-Pong-Test,
- noch offene Abstimmungen, die in diesem Dokument ausdrücklich als offen markiert sind.

Das zugehörige Pflichtenheft beschreibt nach fachlicher Prüfung dieses Lastenhefts die geplante technische Umsetzung.

## 2. Freigabe Und Änderungsstand

| Rolle | Person / Stelle | Aufgabe | Status |
|---|---|---|---|
| fachlicher Ansprechpartner | Herr Schnabel | Anforderungen prüfen, priorisieren und fachlich freigeben | offen |
| betreuender Professor | Herr Heym | wissenschaftliche und methodische Begleitung | Zuordnung nach aktuellem Informationsstand |
| Bearbeiter | Immanuel Mauch | Lastenheft pflegen und offene Punkte einarbeiten | in Bearbeitung |

Eine Freigabe ist erst erfolgt, wenn die offenen Muss-Entscheidungen geklärt und die freigegebene Version mit Datum dokumentiert wurde.

## 3. Ausgangssituation

Climate Cubes erfassen Umweltdaten. Die Geräte sollen auch an abgelegenen Einsatzorten ohne verlässliche Kommunikationsinfrastruktur betrieben werden können. Als Beispiel wurde ein Einsatz in Peru genannt. LoRaWAN kann deshalb nicht vorausgesetzt werden.

Nach bisheriger Vorgabe sollen mehrere als Slave betriebene Climate Cubes ihre Messdaten regelmäßig erfassen, lokal sichern und direkt per LoRa an einen Master Climate Cube übertragen. Der Master soll die Daten mehrerer Slaves zentral speichern.

Am 11.08.2026 wurden zwei Raspberry Pi Pico 2 W mit CircuitPython 10.2.1 und Waveshare-SX1262-LoRa-Hardware untersucht. Die direkte bidirektionale LoRa-Kommunikation wurde in einem isolierten Test nachgewiesen. Dieser Test ist eine technische Voruntersuchung und ersetzt keine fachliche Freigabe des Gesamtsystems.

## 4. Zielbestimmung

### 4.1 Muss-Ziele

| ID | Ziel |
|---|---|
| LZ-M-01 | Ein Slave erfasst die festgelegten Umweltdaten in einem vorgesehenen Rhythmus von 15 Minuten. |
| LZ-M-02 | Ein Slave speichert seine eigenen Messdaten für mindestens ein Jahr lokal als Ausfallsicherung. |
| LZ-M-03 | Ein Slave überträgt jeden erzeugten Messdatensatz ohne LoRaWAN direkt per LoRa an einen Master; eine zeitliche Verzögerung der Übertragung ist zulässig. |
| LZ-M-04 | Ein Master empfängt und speichert die Daten mehrerer Slaves zentral. |
| LZ-M-05 | Jeder Datensatz ist ueber eine je Slave persistente Sequenznummer chronologisch eindeutig einzuordnen; ein genauer absoluter Messzeitpunkt ist nicht erforderlich. |
| LZ-M-06 | Das System funktioniert ohne Internet, Mobilfunk, WLAN und LoRaWAN-Infrastruktur. |
| LZ-M-07 | Herkunft und Vollständigkeit gespeicherter Datensätze sind nachvollziehbar. |
| LZ-M-08 | Anforderungen, Entwurf, Implementierung und Tests werden nachvollziehbar dokumentiert. |
| LZ-M-09 | Der Master bestätigt eine Übertragung erst nach erfolgreicher zentraler Speicherung; unbestätigte Datensätze bleiben am Slave für eine spätere Übertragung erhalten. |

### 4.2 Soll-Ziele

| ID | Ziel |
|---|---|
| LZ-S-01 | Ein Master soll für ungefähr zehn Slaves ausgelegt sein. |
| LZ-S-02 | Funk-, Sensor- und Speicherfehler sollen erkennbar dokumentiert werden. |
| LZ-S-03 | Fehlende oder doppelte Datensätze sollen erkennbar sein. |
| LZ-S-04 | Konfiguration und Datenausgabe sollen ohne Quellcodeänderung je Geräterolle nachvollziehbar sein. |
| LZ-S-05 | Die Software soll später um weitere Messwerte oder Geräte erweiterbar sein. |

### 4.3 Kann-Ziele

| ID | Ziel |
|---|---|
| LZ-K-02 | Bodenfeuchte und Bodentemperatur können als optionale Messgrößen erfasst werden. |
| LZ-K-03 | Zusätzliche Diagnose- oder Wartungsdaten können gespeichert werden. |
| LZ-K-04 | Bei verbleibender Projektzeit kann das Sternsystem um ein dynamisches Mesh erweitert werden, in dem Slaves Nachbarn und mehrstufige Wege zum Master automatisch erkennen. |

### 4.4 Abgrenzung

Nicht Bestandteil des derzeit bestätigten Kernauftrags sind:

- LoRaWAN-Betrieb,
- Cloud- oder Internetanbindung,
- eine Webplattform oder grafische Auswertungsoberfläche,
- ein dynamisches Mesh-Netz; es ist nur als optionale Erweiterung bei verbleibender Projektzeit vorgesehen,
- die Batteriespannung als priorisierter Messwert,
- Bodensensoren als verpflichtender Bestandteil des Kernsystems.

## 5. Stakeholder Und Rollen

### 5.1 Projektrollen

| Rolle | Interesse / Verantwortung |
|---|---|
| fachlicher Auftraggeber beziehungsweise Ansprechpartner | legt fachliche Ziele, Messumfang, Prioritäten und Abnahmekriterien fest |
| betreuender Professor | begleitet Vorgehen, Dokumentation und wissenschaftliche Einordnung |
| Entwickler | spezifiziert, entwirft, implementiert, testet und dokumentiert das System |
| spätere Betreiber | installieren, konfigurieren und warten die Climate Cubes |
| Datenauswerter | entnehmen gespeicherte Daten und müssen sie eindeutig interpretieren können |

Die genaue organisatorische Zuordnung von Auftraggeber, Eigentümer und Freigabeberechtigten ist noch schriftlich zu bestätigen.

### 5.2 Systemrollen

Eine Systemrolle beschreibt das Verhalten eines Geräts oder einer Person im Betrieb.

| Systemrolle | Erwartete Fähigkeiten |
|---|---|
| Slave Climate Cube | Messwerte erfassen, Datensatz bilden, lokal sichern, an Master senden und Fehler festhalten |
| Master Climate Cube | mehrere Slaves unterscheiden, Pakete empfangen, prüfen, den Messzeitbezug erhalten und zentral speichern |
| Betreiber / Installateur | Geräterolle und Kennung festlegen, Zeitreferenz einstellen beziehungsweise prüfen, Funkkonfiguration prüfen und gespeicherte Daten entnehmen |
| Datenauswerter | Dateien einem Master und Slave zuordnen sowie Felder, Einheiten, Zeitbezug und Fehlerstatus verstehen |

## 6. Produkteinsatz

### 6.1 Einsatzbereiche

- stationäre Umweltmessungen,
- abgelegene Standorte ohne Kommunikationsinfrastruktur,
- mehrere räumlich verteilte Slave-Geräte mit einem zentralen Master,
- langfristige Speicherung für eine spätere wissenschaftliche Auswertung.

### 6.2 Betriebsbedingungen

- dauerhafter beziehungsweise langandauernder Akkubetrieb ist vorgesehen,
- Funkverbindungen können zeitweise ausfallen,
- ein manueller Zugriff auf die SD-Karten ist möglich, aber nicht jederzeit,
- ein Internetzugang darf nicht erforderlich sein,
- die genaue Temperatur-, Feuchte- und Schutzklasse der Gehäuse ist noch nicht spezifiziert.

### 6.3 Benutzerkenntnisse

Betreiber sollen die Geräte anhand einer Betriebs- und Konfigurationsanleitung einrichten können. Datenauswerter sollen die gespeicherten Dateien ohne Kenntnis des Quellcodes interpretieren können.

## 7. Funktionale Anforderungen

### 7.1 Messung Und Datensatz

| ID | Priorität | Anforderung | Fachliches Abnahmekriterium |
|---|---|---|---|
| LH-F-001 | Muss | Ein Slave erzeugt regelmäßig einen Messdatensatz. | Im vorgesehenen Betrieb entsteht je Messzyklus ein nachvollziehbarer Datensatz. |
| LH-F-002 | Muss | Der vorgesehene Messrhythmus betraegt 15 Minuten; die Reihenfolge der Datensaetze wird je Slave durch persistente Sequenznummern bestimmt. | Aufeinanderfolgende Messzyklen sind ueber fortlaufende Sequenznummern nachvollziehbar; ein genauer absoluter Messzeitpunkt ist nicht erforderlich. |
| LH-F-003 | Muss | Ein Datensatz enthält alle neun bestätigten SEN66-Messgrößen aus Abschnitt 8.1. | Lufttemperatur, relative Luftfeuchtigkeit, CO2, PM1, PM2.5, PM4, PM10, VOC-Index und NOx-Index sind vorhanden oder eindeutig als fehlend markiert. |
| LH-F-004 | Muss | Fehlende Messwerte bleiben als fehlend erkennbar. | Ein Teilausfall wird nicht als gültiger Zahlenwert ausgegeben. |

### 7.2 Lokale Speicherung Am Slave

| ID | Priorität | Anforderung | Fachliches Abnahmekriterium |
|---|---|---|---|
| LH-F-010 | Muss | Jeder Slave speichert seine eigenen Messdatensätze für mindestens ein Jahr lokal auf SD-Karte. | Bei einem 15-Minuten-Messrhythmus können mindestens 35.040 aufeinanderfolgende Datensätze ohne Überschreiben gespeichert werden. |
| LH-F-011 | Muss | Bereits gespeicherte Messdaten dürfen beim Neustart nicht unbeabsichtigt überschrieben werden. | Ein Neustart erhält vorhandene Dateien beziehungsweise Datensätze. |
| LH-F-012 | Soll | Fehler beim lokalen Speichern werden sichtbar dokumentiert. | Ein Schreibfehler ist nach dem Betrieb nachvollziehbar. |

### 7.3 LoRa-Übertragung

| ID | Priorität | Anforderung | Fachliches Abnahmekriterium |
|---|---|---|---|
| LH-F-020 | Muss | Ein Slave überträgt jeden im 15-Minuten-Messrhythmus erzeugten Datensatz per LoRa Peer-to-Peer an den Master; der genaue Übertragungszeitpunkt ist nicht kritisch. | Der Master empfängt den zuvor lokal gesicherten Datensatz mit unveränderten fachlichen Werten und unverändertem Messzeitbezug. |
| LH-F-021 | Muss | LoRaWAN wird für den Datenweg nicht vorausgesetzt. | Der vollständige Ablauf funktioniert ohne LoRaWAN-Gateway. |
| LH-F-022 | Muss | Master und Slave verwenden eine kompatible, dokumentierte Funkkonfiguration. | Beide Rollen kommunizieren mit demselben freigegebenen Parametersatz. |
| LH-F-023 | Muss | Der Master sendet eine Empfangsbestätigung erst, nachdem ein gültiger Datensatz erfolgreich auf seiner SD-Karte gespeichert wurde. | Bei Empfang ohne erfolgreiche zentrale Speicherung wird kein Erfolgs-ACK gesendet. |
| LH-F-024 | Kann | Bei verbleibender Projektzeit kann ein dynamisches Mesh als gesonderte Erweiterung spezifiziert und umgesetzt werden. | Vor einer Umsetzung werden Lasten- und Pflichtenheft um Nachbarerkennung, Routensuche, Weiterleitung, Schleifen- und Duplikatbehandlung sowie ACK-Rückweg erweitert. |
| LH-F-025 | Muss | Der Slave markiert einen Datensatz erst nach einem passenden ACK als erfolgreich übertragen; ohne ACK bleibt er lokal als ausstehend erhalten und wird später erneut gesendet. | Ein fehlendes ACK führt weder zum Löschen noch zur Erfolgsmarkierung des Datensatzes. |

### 7.4 Masterbetrieb

| ID | Priorität | Anforderung | Fachliches Abnahmekriterium |
|---|---|---|---|
| LH-F-030 | Muss | Der Master empfängt Messdaten mehrerer Slaves. | Datensätze verschiedener Slaves werden korrekt unterschieden. |
| LH-F-031 | Soll | Der Master ist konzeptionell für ungefähr zehn Slaves ausgelegt. | Datenmodell und Ablauf besitzen keine feste Grenze unterhalb von zehn Slaves. |
| LH-F-032 | Muss | Der Master prüft empfangene Datensätze vor der regulären Speicherung. | Ungültige oder nicht unterstützte Pakete werden nicht still als gültige Messung gespeichert. |
| LH-F-033 | Muss | Der Master speichert gültige Messdaten zentral auf SD-Karte und ist für ein Jahr Datenaufkommen ausgelegt. | Die zentrale Ablage enthält Messwerte und Herkunftsinformationen; für zehn Slaves sind mindestens 350.400 Datensätze speicherbar. |
| LH-F-034 | Muss | Der Master erhaelt die Slave-ID und Sequenznummer jedes Datensatzes unveraendert und kann eine optionale Empfangszeit ergaenzen. | Die zentrale Ablage ist je Slave anhand der Sequenznummer chronologisch sortierbar; Zeitstempel sind optionale Zusatzinformationen. |
| LH-F-035 | Soll | Der Master speichert Empfangsinformationen, sofern diese für die Bewertung benötigt werden. | RSSI, SNR oder Empfangsstatus sind entsprechend der freigegebenen Struktur vorhanden. |

### 7.5 Konfiguration Und Datenentnahme

| ID | Priorität | Anforderung | Fachliches Abnahmekriterium |
|---|---|---|---|
| LH-F-040 | Muss | Master und Slaves besitzen eindeutige, dokumentierte Rollen und Kennungen. | Ein Datenauswerter kann jeden Datensatz einem Gerät zuordnen. |
| LH-F-041 | Muss | Der 15-Minuten-Messrhythmus und die persistente Sequenzverwaltung koennen vor dem Einsatz konfiguriert beziehungsweise geprueft werden. | Messintervall und Sequenzverhalten sind dokumentiert und reproduzierbar. |
| LH-F-042 | Muss | Gespeicherte Daten können ohne Spezialinfrastruktur entnommen werden. | Dateien sind über SD-Karte oder einen freigegebenen lokalen Weg lesbar. |
| LH-F-043 | Muss | Datenformat und Einheiten sind dokumentiert. | Eine gespeicherte Datei kann ohne Quellcodeanalyse interpretiert werden. |

## 8. Messdaten

### 8.1 Verbindliche SEN66-Messgrößen

Auf der untersuchten Hardware war ein SEN66 angeschlossen. Nach fachlicher Bestätigung vom 12.08.2026 müssen alle folgenden im Bestandscode ausgelesenen SEN66-Werte gespeichert und übertragen werden:

- Lufttemperatur,
- relative Luftfeuchtigkeit,
- CO2,
- PM1,
- PM2.5,
- PM4,
- PM10,
- VOC-Index,
- NOx-Index.

### 8.2 Optionale Messquellen

Bodenfeuchte und Bodentemperatur sind nach fachlicher Rückmeldung vom 12.08.2026 optionale Messgrößen und keine Muss-Anforderungen. Beim Hardwaretermin standen keine funktionsfähig angeschlossenen Bodensensoren für einen Test zur Verfügung.

Nur falls diese optionale Funktion umgesetzt wird, sind zu klären:
- welche konkreten Sensoren verwendet werden,
- welche Einheiten und Kalibrierverfahren gelten,
- welche GPIOs beziehungsweise Anschlüsse vorgesehen sind,
- wie fehlende Bodensensoren behandelt werden.

## 9. Nicht-Funktionale Anforderungen

| ID | Priorität | Anforderung | Nachweis |
|---|---|---|---|
| LH-NF-001 | Muss | Offline-Fähigkeit | Systemtest ohne Internet, WLAN, Mobilfunk und LoRaWAN |
| LH-NF-002 | Muss | Datenzuverlässigkeit | Lokale Slave-Daten bleiben bei Funkunterbrechung erhalten |
| LH-NF-003 | Muss | Nachvollziehbarkeit | Kennung, Zeitbezug, Datenformat, Einheiten und Status sind dokumentiert |
| LH-NF-004 | Soll | Robustheit | Definierte Reaktion auf Sensor-, SD-, Funk- und Neustartfehler |
| LH-NF-005 | Soll | Wartbarkeit | Messung, Speicherung, Protokoll und Rollensteuerung sind nachvollziehbar getrennt |
| LH-NF-006 | Soll | Erweiterbarkeit | Neue Messwerte oder Slaves können ohne vollständigen Neuentwurf ergänzt werden |
| LH-NF-007 | Soll | Energieeffizienz | Mess- und Funkaktivität werden auf den notwendigen Umfang begrenzt |
| LH-NF-008 | Muss | Reproduzierbarkeit | Softwarestand, Konfiguration und Testbedingungen sind versioniert dokumentiert |
| LH-NF-009 | Muss | Funkkonformität | Frequenz, Sendeleistung und Sendeverhalten werden vor Feldeinsatz für den Einsatzort freigegeben |
| LH-NF-010 | Muss | Speicherkapazität | Slave- und Master-SD besitzen Kapazität für mindestens ein Jahr Messdaten zuzüglich festgelegter Sicherheitsreserve |

## 10. Randbedingungen

| ID | Randbedingung | Status |
|---|---|---|
| LH-R-001 | Programmiersprache Python | vorgegeben |
| LH-R-002 | Zielhardware Raspberry Pi Pico 2 W mit RP2350A | am 11.08.2026 nachgewiesen |
| LH-R-003 | CircuitPython 10.2.1 war auf beiden Testgeräten installiert | nachgewiesen |
| LH-R-004 | Waveshare Pico-LoRa-SX1262-868M | laut Projektvorgabe und Funktionstest |
| LH-R-005 | direkte LoRa-Peer-to-Peer-Kommunikation | vorgegeben und technisch voruntersucht |
| LH-R-006 | kein LoRaWAN als erforderlicher Betriebsweg | vorgegeben |
| LH-R-007 | lokale SD-Karten an Slaves und Master | fachlich vorgesehen; konkrete Master-Ausführung noch zu bestätigen |
| LH-R-008 | Praktikumszeitraum 03.08.2026 bis 06.12.2026 | laut Vertrag |

## 11. Liefergegenstände

Zum Projektabschluss werden mindestens erwartet:

1. freigegebenes Lastenheft,
2. freigegebenes beziehungsweise abgestimmtes Pflichtenheft,
3. dokumentierte Systemrollen und Use Cases,
4. versionierter Quellcode für die vereinbarten Master- und Slave-Funktionen,
5. Konfigurations- und Betriebsanleitung,
6. dokumentiertes Daten- und Funkprotokoll,
7. Testkonzept, Testprotokolle und Testergebnisse,
8. Architektur- und Entscheidungsdokumentation,
9. fortlaufendes Projekttagebuch,
10. abschließendes wissenschaftliches Paper im vereinbarten Format,
11. reproduzierbarer Demonstrationsstand.

## 12. Fachliche Abnahme

Die fachliche Abnahme soll auf freigegebenen Testszenarien beruhen. Mindestens vorgesehen sind:

| ID | Abnahmeszenario |
|---|---|
| LA-01 | Ein Slave erzeugt, speichert und überträgt einen vollständigen Messdatensatz. |
| LA-02 | Der Master empfängt, prüft, zeitlich referenziert und speichert den Datensatz. |
| LA-03 | Bei nicht erreichbarem Master bleiben die Daten auf dem Slave erhalten. |
| LA-04 | Datensätze mehrerer Slaves werden korrekt unterschieden. |
| LA-05 | Neustart, fehlende SD-Karte, ungültiges Funkpaket und fehlender Sensor führen zu definiertem Verhalten. |
| LA-06 | Datenformat, Konfiguration und Softwarestand sind anhand der Dokumentation reproduzierbar. |
| LA-07 | Der Master sendet erst nach erfolgreicher zentraler Speicherung ein ACK; ohne ACK bleibt der Datensatz am Slave ausstehend. |
| LA-08 | Die nachgewiesene Speicherkapazität reicht je Slave und am Master für mindestens ein Jahr Datenaufkommen mit Sicherheitsreserve. |

Konkrete Toleranzen, Testdauer, Anzahl realer Slaves und Reichweitenszenarien sind noch festzulegen.

## 13. Offene Fachliche Entscheidungen

| ID | Frage | Freigabe erforderlich durch | Status |
|---|---|---|---|
| LO-01 | Welche Messgrößen gehören verbindlich in jeden Datensatz? | fachlicher Ansprechpartner | geklärt am 12.08.2026: alle neun aufgeführten SEN66-Werte |
| LO-02 | Sind Bodenfeuchte und Bodentemperatur Muss-Anforderungen? | fachlicher Ansprechpartner | geklärt am 12.08.2026: beide sind optional |
| LO-03 | Muss die Funkuebertragung exakt im 15-Minuten-Takt erfolgen? | fachlicher Ansprechpartner | praezisiert am 24.08.2026: Messungen im 15-Minuten-Rhythmus; Uebertragungszeitpunkt und genauer absoluter Messzeitpunkt unkritisch; chronologische Sequenznummer entscheidend |
| LO-04 | Wann gilt eine lokale Speicherung als ausreichend? | fachlicher Ansprechpartner | geklärt am 12.08.2026: mindestens ein Jahr Daten im 15-Minuten-Messrhythmus |
| LO-05 | Ist eine Empfangsbestätigung verbindlich? | fachlicher Ansprechpartner | geklärt am 12.08.2026: ACK nach erfolgreicher Master-Speicherung; ohne ACK spätere erneute Übertragung |
| LO-06 | Wie viele Wiederholungen und welche Zeitlimits sind zulässig? | fachlicher Ansprechpartner / Technik | offen |
| LO-07 | Ist Mesh Bestandteil des Kernsystems? | fachlicher Ansprechpartner / Technik | geklärt am 13.08.2026: nein; dynamisches Mesh nur als Kann-Erweiterung bei verbleibender Zeit |
| LO-08 | Ist ein genauer absoluter Messzeitpunkt erforderlich? | fachlicher Ansprechpartner / Technik | geklaert am 24.08.2026: nein; zeitliche Ordnung erfolgt ueber 15-Minuten-Rhythmus und persistente Sequenznummer |
| LO-09 | Welche Funkparameter sind für Entwicklung, Deutschland und Einsatzort zulässig? | fachlich und regulatorisch Verantwortliche | offen |
| LO-10 | Welche Testdauer und welche Fehlerfälle sind für die Abnahme verbindlich? | fachlicher Ansprechpartner | offen |
| LO-11 | Wer erteilt die formale Freigabe von Lasten- und Pflichtenheft? | Projektbeteiligte | offen |

## 14. Freigaberegel Vor Der Implementierung

Bis zur fachlichen Prüfung dieses Lastenhefts sind nur Bestandsanalyse, technische Voruntersuchungen, Dokumentation und gefahrlos rücksetzbare Prototypen vorgesehen. Die eigentliche Produktimplementierung beginnt erst, wenn:

1. Muss-Umfang und Rollen bestätigt sind,
2. offene Muss-Entscheidungen geklärt oder bewusst vertagt wurden,
3. Lastenheft und darauf basierendes Pflichtenheft einen dokumentierten Freigabestatus besitzen,
4. Abnahmekriterien den Anforderungen zugeordnet sind.

## 15. Freigabevermerk

| Version | Datum | Entscheidung | Person / Rolle | Bemerkung |
|---|---|---|---|---|
| 0.1 | 11.08.2026 | Entwurf erstellt | Immanuel Mauch | fachliche Prüfung ausstehend |
| 0.2 | 12.08.2026 | fachliche Rückmeldungen zu Sensoren, Zeitbezug, Speicherung und ACK eingearbeitet | Immanuel Mauch | zur fachlichen Prüfung |
| 0.3 | 13.08.2026 | Sternsystem als Kern und Mesh als Kann-Erweiterung eingeordnet | Immanuel Mauch | nach Versand von PDF 0.2; neue PDF erst nach weiterer Prüfung |
| 0.4 | 24.08.2026 | genauen absoluten Messzeitpunkt aus Muss-Umfang entfernt; chronologische Sequenznummer als massgeblich festgelegt | Immanuel Mauch | bestehende PDFs entsprechen noch Version 0.2 und muessen neu erzeugt werden |
