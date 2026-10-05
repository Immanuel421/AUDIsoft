# Projektplan AUDI Climate Cube

**Stand:** 11.08.2026
**Zeitraum laut Praktikumsvertrag:** 03.08.2026 bis 06.12.2026
**Dokumentstatus:** Arbeitsentwurf; interne Termine und Freigabeverantwortung sind noch abzustimmen

Dieser Plan betrifft ausschließlich das AUDI-Climate-Cube-Projekt. Er unterscheidet zwischen bestätigten Projektinformationen, vorläufigen Entwürfen und noch offenen Entscheidungen. Die eigentliche Produktimplementierung beginnt erst, nachdem Lastenheft, Pflichtenheft und der technische Entwurf mit den zuständigen Beteiligten abgestimmt wurden. Bereits ausgeführte Hardware- und LoRa-Tests gelten als Bestandsaufnahme beziehungsweise reversible technische Voruntersuchungen.

## 1. Ausgangssituation

Mehrere Slave-ClimateCubes sollen Messdaten im vorgesehenen 15-Minuten-Rhythmus erfassen, lokal als Backup speichern und per LoRa Peer-to-Peer an einen Master-ClimateCube senden. Der genaue Uebertragungszeitpunkt und ein genauer absoluter Messzeitpunkt sind unkritisch; entscheidend sind der 15-Minuten-Messrhythmus und die chronologische Sequenznummer je Slave. Der Master soll die empfangenen Daten zentral auf einer SD-Karte speichern. Als nachzuweisende Zielgroesse wurden ungefaehr zehn Slaves je Master genannt; dies stellt keine softwareseitige Obergrenze dar. LoRaWAN soll aufgrund möglicher Einsatzorte ohne passende Infrastruktur, unter anderem in Peru, nicht vorausgesetzt werden.

Ein vorhandener CircuitPython-Prototyp liest den SEN66 und weitere im Code vorgesehene Sensoren aus, steuert ein OLED an und speichert Datensätze auf SD-Karte. Alle neun im Lastenheft aufgeführten SEN66-Messgrößen sind für das Kernsystem verbindlich; Bodensensoren bleiben optional. Wie Master, Slave und Kommunikationsprotokoll genau umgesetzt werden, wird in Pflichtenheft und Architekturentwurf festgelegt.

Am 14.08.2026 wurde ein hardwareunabhaengig getesteter Architektur-Prototyp mit hexagonaler Struktur angelegt. Er dient der Validierung von Modulgrenzen, FIFO-, ACK- und Persistenzlogik und ist noch keine freigegebene Produktimplementierung. Die Installation auf den beiden Einsatzgeraeten und verbindliche Hardwareintegration erfolgen weiterhin erst nach den vorgesehenen Freigabepunkten.

## 2. Verbindlicher Projektablauf

Die Projektarbeit folgt diesen aufeinander aufbauenden Schritten:

1. Ist-Stand, Stakeholder und Projektgrenzen erfassen.
2. Lastenheft erstellen und fachlich abstimmen: Was wird benötigt und warum?
3. Systemrollen, Anwendungsfälle und Abnahmekriterien festlegen.
4. Pflichtenheft erstellen und technisch abstimmen: Wie soll das System die Anforderungen erfüllen?
5. Architektur, Schnittstellen, Datenformat und Testkonzept konkretisieren.
6. Die abgestimmte Lösung implementieren.
7. Anforderungen durch dokumentierte Tests verifizieren und das System abnehmen.
8. Ergebnisse in technischer Dokumentation, Projekttagebuch und Abschluss-Paper festhalten.

### Freigabepunkte

| Gate | Erforderliches Ergebnis | Bedeutung |
|---|---|---|
| G1 Fachliche Grundlage | Lastenheft einschließlich Umfang, Rollen und Abnahmeszenarien geprüft | fachlicher Sollzustand ist abgestimmt |
| G2 Technische Grundlage | Pflichtenheft einschließlich Anwendungsfällen und Prüfkriterien geprüft | geplante technische Erfüllung ist abgestimmt |
| G3 Entwicklungsfreigabe | Architektur, Schnittstellen, Datenformat und Testkonzept geprüft | eigentliche Produktimplementierung kann beginnen |
| G4 Systemabnahme | Muss-Anforderungen anhand der vereinbarten Tests nachgewiesen | Projektstand kann abgeschlossen und ausgewertet werden |

Wer die Gates formal freigibt und wie die Freigabe dokumentiert wird, ist noch mit den Beteiligten zu klären.

## 3. Aktueller Technischer Stand

| Thema | Stand am 11.08.2026 |
|---|---|
| Mikrocontroller | zwei Raspberry Pi Pico 2 W vorhanden |
| Laufzeit | Adafruit CircuitPython 10.2.1 auf beiden Geräten bestätigt |
| vorhandene Software | CircuitPython-Prototyp für Sensorik, optionale OLED-Anzeige und SD-Speicherung vorhanden |
| bestätigte Sensorik | SEN66 wurde auf der vorhandenen Hardware ausgeführt |
| weitere Sensorik | im Code vorgesehen; tatsächlicher Umfang und Verschaltung noch nicht abschließend bestätigt |
| SD-Speicherung | auf beiden Geräten grundsätzlich funktionsfähig; Kapazität für mindestens ein Jahr Daten gefordert |
| LoRa-Hardware | Waveshare Pico-LoRa-SX1262-868M auf zwei Geräten vorhanden |
| LoRa-Treiber | Python-Treiberdateien `_sx126x.py`, `sx126x.py` und `sx1262.py` für den Test verwendet |
| LoRa-Voruntersuchung | bidirektionaler Ping-Pong-Test mit 21 dokumentierten PING/PONG-Paaren erfolgreich |
| Kommunikationsziel | LoRa Peer-to-Peer; genaue Topologie und Protokollregeln noch festzulegen |
| Zeitbezug | kein genauer absoluter Messzeitpunkt erforderlich; chronologische Ordnung ueber persistente Sequenznummer je Slave |
| Empfangsbestaetigung | ACK nach erfolgreicher zentraler Speicherung fachlich bestaetigt; Timeout und Wiederholungsparameter offen |
| Sicherungen | ursprünglicher Stand beider Geräte getrennt gesichert und nach dem Test wiederhergestellt |

Der erfolgreiche Ping-Pong-Test weist die grundsätzliche bidirektionale Kommunikation der zwei vorhandenen LoRa-Geräte nach. Er belegt noch nicht die Reichweite, Dauerstabilität, Kommunikation mit ungefaehr zehn Slaves oder die Eignung des späteren Anwendungsprotokolls.

## 4. Rollen Und Verantwortlichkeiten

### Projektbeteiligte Rollen

| Rolle | Derzeitiger Stand |
|---|---|
| Praktikant und Entwickler | Analyse, Entwurf, Implementierung, Tests und Dokumentation |
| fachlicher Ansprechpartner | Herr Schnabel für bisherige Projektanforderungen und Hardwareinformationen; genauer Freigabeumfang noch zu bestätigen |
| Hochschulbetreuer | Herr Heym; konkrete Abstimmungs- und Freigabepunkte noch zu klären |
| weitere Stakeholder | noch zu ermitteln |

### Systemrollen

| Systemrolle | Geplanter Verantwortungsbereich |
|---|---|
| Slave-ClimateCube | Messdaten erfassen, lokal sichern und zur Übertragung bereitstellen |
| Master-ClimateCube | Daten der Slaves empfangen, zeitlich referenzieren und zentral speichern |
| Bediener beziehungsweise Installateur | Geräte konfigurieren, starten und Betriebszustand prüfen |
| Datenauswerter | gespeicherte Daten eindeutig zuordnen und für eine spätere Auswertung verwenden |

Die detaillierten Fähigkeiten und Grenzen jeder Rolle werden im Lasten- und Pflichtenheft beschrieben und müssen noch abgestimmt werden.

## 5. Vorläufiges Systemkonzept

Als zu prüfende Basisvariante wird eine direkte Kommunikation der Slaves mit dem Master betrachtet:

```text
Slave 1  \
Slave 2   \
Slave 3    ---> LoRa Peer-to-Peer ---> Master ClimateCube ---> SD-Karte
...       /
Slave 10 /
```

Das Kernsystem verwendet eine direkte Sternkommunikation. Slaves erhalten die vorgesehene Master-ID ueber ihre lokale Konfiguration und kommunizieren unmittelbar mit diesem Master; sie leiten keine fremden Pakete weiter. Ein dynamisches Mesh mit automatischer Nachbar- und Routenerkennung ist nur eine Kann-Erweiterung bei verbleibender Projektzeit. Vor einer Umsetzung werden Anforderungen, Pflichtenheft, Architektur und Testkonzept erweitert.

## 6. Zeitplan

| Phase | Zeitraum | Schwerpunkt | Erwartetes Ergebnis |
|---|---|---|---|
| 1. Bestandsaufnahme und Voruntersuchung | 03.08.-16.08. | vorhandenen Code, Hardware, Anforderungen und technische Machbarkeit untersuchen | dokumentierter Ist-Stand, erste Hardwaretests und offene Punkte |
| 2. Lastenheft und Rollenklärung | 12.08.-23.08. | Stakeholder, Systemgrenzen, Rollen, fachliche Anforderungen und Abnahmeszenarien abstimmen | geprüfte fachliche Grundlage, Gate G1 |
| 3. Pflichtenheft und Anwendungsfälle | 24.08.-06.09. | technische Erfüllung, Abläufe, Schnittstellen und Prüfkriterien entwerfen | geprüfte technische Grundlage, Gate G2 |
| 4. Architektur und Testkonzept | 07.09.-20.09. | Komponenten, Protokoll, Datenformat, Fehlerbehandlung und Tests festlegen | umsetzbarer Entwurf, Gate G3 |
| 5. Slave-Implementierung | 21.09.-11.10. | Messung, lokale Sicherung, Identifikation und LoRa-Versand umsetzen | Slave erfüllt die freigegebenen Anforderungen |
| 6. Master-Implementierung | 12.10.-01.11. | Empfang, Prüfung, Zeitbezug und zentrale Speicherung umsetzen | Master erfüllt die freigegebenen Anforderungen |
| 7. Integration und Verifikation | 02.11.-22.11. | Mehrgerätebetrieb, Fehlerfälle, Reichweite und Dauerlauf prüfen | dokumentierte Nachweise und priorisierte Restfehler |
| 8. Abschluss und Paper | 23.11.-06.12. | Stabilisierung, Abnahme, Auswertung, Dokumentation und Paper abschließen | vorführbarer Projektstand und vollständige Abschlussunterlagen |

Die Phasen überlappen dort, wo Rückmeldungen ausstehen oder Dokumentation parallel gepflegt werden kann. Eine inhaltliche Produktimplementierung wird dadurch nicht vor Gate G3 vorgezogen.

## 7. Wöchentlicher Arbeitsplan

| Woche | Datum | Ziel |
|---|---|---|
| 1 | 03.08.-09.08. | Anforderungen und vorhandenen Quellcode analysieren; Projektdokumentation beginnen |
| 2 | 10.08.-16.08. | reale Hardware erfassen; SEN66, SD und LoRa als Voruntersuchung prüfen; Lastenheft beginnen |
| 3 | 17.08.-23.08. | Stakeholder, Rollen, Projektumfang, Muss-/Soll-/Kann-Anforderungen und Abnahmeszenarien abstimmen |
| 4 | 24.08.-30.08. | Anwendungsfälle und technische Lösungsanforderungen im Pflichtenheft ausarbeiten |
| 5 | 31.08.-06.09. | Pflichtenheft, Schnittstellen und Prüfkriterien abstimmen |
| 6 | 07.09.-13.09. | Systemarchitektur, Komponentenverantwortung und Kommunikationsabläufe festlegen |
| 7 | 14.09.-20.09. | Datenformat, Funkparameter, Zeitkonzept, Fehlerbehandlung und Testplan finalisieren |
| 8 | 21.09.-27.09. | freigegebenen Slave-Grundaufbau und Konfiguration implementieren |
| 9 | 28.09.-04.10. | Messablauf und lokale Slave-Speicherung gemäß Pflichtenheft umsetzen |
| 10 | 05.10.-11.10. | Slave-Identifikation, Paketbildung und LoRa-Versand integrieren und testen |
| 11 | 12.10.-18.10. | Master-Empfang und Paketvalidierung implementieren |
| 12 | 19.10.-25.10. | Zeitbezug und zentrale Speicherung implementieren |
| 13 | 26.10.-01.11. | Fehlerbehandlung sowie vereinbarte Empfangssicherung ergänzen |
| 14 | 02.11.-08.11. | Slave und Master integrieren; zwei vorhandene Geräte systematisch testen |
| 15 | 09.11.-15.11. | Wiederanlauf, Unterbrechungen, ungültige Daten und Speicherausfälle testen |
| 16 | 16.11.-22.11. | Reichweite, Dauerlauf und Mehrgeräte-Konzept prüfen; Anforderungsnachweise vervollständigen |
| 17 | 23.11.-29.11. | kritische Restfehler beheben; Abnahme vorbereiten; Paper-Ergebnisse und Diskussion schreiben |
| 18 | 30.11.-06.12. | Abnahme, Vorführung, Dokumentation und Paper finalisieren |

## 8. Meilensteine

| Meilenstein | Zieltermin | Messbares Ergebnis |
|---|---|---|
| M1 Ist-Stand dokumentiert | 16.08.2026 | Hardware, Softwarestand, ausgeführte Voruntersuchungen und offene Punkte sind nachvollziehbar festgehalten |
| M2 Lastenheft abgestimmt | 23.08.2026 | fachlicher Umfang, Rollen, Anforderungen und Abnahmeszenarien sind geprüft |
| M3 Pflichtenheft abgestimmt | 06.09.2026 | Anwendungsfälle, technische Erfüllung und Prüfkriterien sind geprüft |
| M4 Entwicklungsgrundlage freigegeben | 20.09.2026 | Architektur, Schnittstellen, Datenformat und Testkonzept sind umsetzbar beschrieben |
| M5 Slave-Stand fertig | 11.10.2026 | freigegebene Slave-Anforderungen sind implementiert und getestet |
| M6 Master-Stand fertig | 01.11.2026 | freigegebene Master-Anforderungen sind implementiert und getestet |
| M7 Systemverifikation abgeschlossen | 22.11.2026 | vereinbarte System- und Fehlerfalltests sind protokolliert |
| M8 Projektabschluss | 06.12.2026 | Abnahmeunterlagen, Demonstration, technische Dokumentation und Abschluss-Paper liegen vor |

Die Zieltermine M2 bis M8 sind interne Planwerte und müssen noch mit den Beteiligten abgestimmt werden.

## 9. Teststrategie

Tests werden aus den Anforderungen und Abnahmekriterien abgeleitet. Zu jedem Test gehören Ziel, Voraussetzungen, Aufbau, Schritte, erwartetes Ergebnis, tatsächliches Ergebnis und Nachweis.

| Teststufe | Ziel |
|---|---|
| technische Voruntersuchung | Machbarkeit und vorhandenen Hardwarestand erfassen, ohne eine Produktlösung vorwegzunehmen |
| Modultest | Sensorik, Speicherung, Paketbildung und Funkmodule einzeln prüfen |
| Schnittstellentest | Datenformat und Übergaben zwischen Slave, Funkstrecke, Master und SD prüfen |
| Integrationstest | vollständigen Ablauf von der Messung bis zur zentralen Speicherung prüfen |
| Fehlerfalltest | Funkabbruch, Neustart, ungültige Daten sowie Sensor- und SD-Ausfälle behandeln |
| Systemtest | abgestimmte Anforderungen im Gesamtsystem nachweisen |
| Abnahmetest | vereinbarte Abnahmeszenarien gemeinsam bewerten und dokumentieren |

Der Ping-Pong-Test vom 11.08.2026 ist ein Nachweis der technischen Grundfunktion der vorhandenen LoRa-Hardware. Weitere Testfälle werden nach Festlegung der Anforderungen geplant.

## 10. Dokumentation Und Paper

Folgende Dokumente werden gepflegt:

| Dokument | Zweck |
|---|---|
| Lastenheft | fachliche Anforderungen aus Auftraggebersicht |
| Pflichtenheft | technische Erfüllung, Rollenfähigkeiten, Anwendungsfälle und Prüfkriterien |
| Architektur- und Datenformatdokumente | konkrete, freigegebene Entwicklungsgrundlage |
| Projekttagebuch | tägliche Tätigkeiten, Entscheidungen, Probleme und Erkenntnisse |
| Testprotokolle und Rohdaten | reproduzierbare Nachweise für technische Aussagen |
| README und Betriebsanleitung | Projektübersicht sowie Inbetriebnahme und Bedienung |
| Abschluss-Paper | wissenschaftlich strukturierte Zusammenfassung von Problem, Methode, Umsetzung und Ergebnissen |

Das Paper wird bereits während des Projekts abschnittsweise vorbereitet. Die geplante Struktur ist in `docs/Paper_Struktur_AUDI_Climate_Cube.md` festgehalten. Formvorgaben wie Sprache, Vorlage, Seitenzahl und Zitierstil sind noch zu klären.

## 11. Risiken Und Gegenmaßnahmen

| Risiko | Auswirkung | Gegenmaßnahme |
|---|---|---|
| Anforderungen oder Rollen bleiben unklar | Umsetzung erfüllt möglicherweise nicht den tatsächlichen Bedarf | Lastenheft, Anwendungsfälle und Freigabepunkte vor der Implementierung abstimmen |
| Freigaben verzögern sich | Entwicklungszeit verkürzt sich | Entwürfe früh versenden, offene Entscheidungen kennzeichnen und Rückmeldetermine vereinbaren |
| Pinbelegung optionaler Bodensensoren ist unklar | bei optionaler Umsetzung sind elektrische Konflikte möglich | nur bei Aufnahme der optionalen Funktion Hardware und Belegung vor Gate G3 bestätigen |
| Funkparameter oder rechtliche Rahmenbedingungen sind offen | Test oder späterer Betrieb ungeeignet | gültige Parameter für Entwicklungs- und Einsatzort vor der Integration klären |
| LoRa-Reichweite reicht im Sternsystem nicht | Slaves erreichen den Master nicht zuverlässig | Reichweite testen und Platzierung anpassen; Mesh nur bei verbleibender Zeit als gesonderte Erweiterung prüfen |
| SD-Kapazität, SD- oder Sensorfehler führen zu Datenlücken | Messdaten gehen verloren oder sind unvollständig | Kapazität für mindestens ein Jahr mit Reserve auslegen; Erfolgs-ACK nur nach zentraler Speicherung senden; Fehlerverhalten testen |
| Messzeitstempel ist ungenau oder bezeichnet nur den Empfang | Daten lassen sich zeitlich falsch auswerten | Genauigkeit, Zeitquelle und Synchronisationskonzept vor der Implementierung festlegen |
| zu großer Funktionsumfang | Kernanforderungen werden nicht rechtzeitig fertig | Muss-/Soll-/Kann-Priorisierung und Änderungsverfahren verwenden |
| Paper wird erst am Ende begonnen | Ergebnisse und Entscheidungen müssen rückwirkend rekonstruiert werden | Kapitel, Quellen und Nachweise parallel zum Projekt pflegen |

## 12. Unmittelbare Nächste Schritte

| Nr. | Aufgabe | Ergebnis |
|---|---|---|
| 1 | Entwurf des Lastenhefts fachlich prüfen lassen | Umfang, Rollen, Anforderungen und offene Fragen erhalten Rückmeldung |
| 2 | Zuständigkeit und Form der Freigaben klären | es ist bekannt, wer G1 bis G4 bestätigt und wie dies dokumentiert wird |
| 3 | offene fachliche Punkte mit Herrn Schnabel priorisieren | Betriebsablauf, Topologie, Zeitbezug und Abnahme werden konkretisiert |
| 4 | Pflichtenheft nach der fachlichen Rückmeldung überarbeiten | technische Aussagen passen zum abgestimmten Lastenheft |
| 5 | Rollen und Anwendungsfälle gemeinsam prüfen | jede Rolle besitzt nachvollziehbare Aufgaben und Berechtigungen |
| 6 | formale Vorgaben für das Abschluss-Paper erfragen | Sprache, Vorlage, Umfang, Termin und Zitierstil sind bekannt |
| 7 | Projekttagebuch und Testnachweise fortlaufend pflegen | Entscheidungen und Ergebnisse bleiben für Abschluss und Paper nachvollziehbar |

Bis zur Abstimmung sind Lastenheft, Pflichtenheft, Architektur und Zeitplan Arbeitsentwürfe. Offene Punkte werden nicht als bereits beschlossene Anforderungen behandelt.
