# Pflichtenheft AUDI Climate Cube

Projekt: Offline-Messdatenerfassung und LoRa-Uebertragung fuer Climate Cubes  
Bearbeiter: Immanuel Mauch  
Stand: 18.09.2026
Version: 0.5
Dokumentstatus: **Technischer Entwurf - basiert auf dem noch nicht freigegebenen Lastenheft 0.4**

## 1. Zweck Und Gueltigkeit

Dieses Pflichtenheft beschreibt, **wie** die im Lastenheft formulierten Anforderungen technisch erfuellt werden sollen. Es ist noch keine Implementierungsfreigabe.

Bei einem Widerspruch gilt:

1. freigegebene Fassung des Lastenhefts,
2. schriftlich dokumentierte fachliche Entscheidung,
3. freigegebene Fassung dieses Pflichtenhefts,
4. technische Detailentwuerfe.

Nicht entschiedene Punkte sind in diesem Dokument als offen oder vorlaeufig gekennzeichnet.

## 2. Bezugsdokumente

| Dokument | Bedeutung |
|---|---|
| docs/Lastenheft_AUDI_Climate_Cube.md | fachliche Anforderungen und Abnahmesicht |
| docs/Anforderungen_AUDI_Climate_Cube.md | Quellen- und Arbeitsdokument der bisherigen Anforderungen |
| docs/Datenformat_V1_Entwurf.md | technischer Entwurf fuer Datensatz, Funkpaket und CSV |
| tests/lora_ping_pong/TESTPROTOKOLL_LoRa_Ping_Pong.md | Nachweis der isolierten SX1262-Kommunikation |
| docs/Testprotokoll_Systemintegration_2026-08-21.md | Nachweis des produktiven Master-/Slave-Ablaufs, ACK-Fehlerfalls und Neustarts |
| docs/Projektplan_AUDI_Climate_Cube.md | Phasen, Termine und Meilensteine |
| docs/Projekttagebuch_Climate_Cube.md | Verlauf, Entscheidungen und Erkenntnisse |

## 3. Technische Ausgangsbasis

| Bereich | Nachgewiesener beziehungsweise geplanter Stand |
|---|---|
| Mikrocontroller | zwei Raspberry Pi Pico 2 W mit RP2350A |
| Laufzeit | CircuitPython 10.2.1 |
| Programmiersprache | Python |
| LoRa-Modul | Waveshare Pico-LoRa-SX1262-868M |
| LoRa-Treiber | angepasster CircuitPython-Pfad aus micropySX126X |
| Funkgrundlage | bidirektionaler Peer-to-Peer-Ping-Pong-Test mit 21 dokumentierten Folgen erfolgreich |
| Luftsensor | SEN66 auf der untersuchten Hardware |
| lokale Speicherung | SD-Karte im vorhandenen Messprototyp erfolgreich beschrieben |
| Bodensensoren | fachlich optional; im Bestandscode enthalten, am 11.08.2026 nicht angeschlossen nachgewiesen |
| konsolidierter Master-Start | am 20.08.2026 auf einem Pico 2 W mit OLED, /config.json, SD-Karte und SX1262 bis in die Empfangsschleife erfolgreich getestet |
| automatisierte Kernpruefung | 52 Unit-Tests fuer Architekturgrenzen, Composition Root, Fehlerbehandlung, Codec, FIFO, ACK-Reihenfolge, Duplikatbehandlung und SD-Wiederanlauf erfolgreich |

Der Ping-Pong-Test bestaetigt Treiber, Grundbelegung und direkte Funkkommunikation. Der Master-Starttest vom 20.08.2026 bestaetigt die gemeinsame Initialisierung von OLED, Konfiguration, SD-Karte und SX1262. Der Systemintegrationstest vom 21.08.2026 weist zusaetzlich den produktiven Datentransfer von Slave `C01` zu Master `M01`, lokale und zentrale Speicherung, ACK-Wiederholung, Duplikatvermeidung sowie den Wiederanlauf des Slaves nach. Mehrgeraeteverhalten mit mehr als einem Slave, Reichweite und laengerer Dauerbetrieb bleiben offen.

## 4. Loesungskonzept

### 4.1 Systemgrenze

Zum System gehoeren:

- Software eines Slave Climate Cubes,
- Software eines Master Climate Cubes,
- lokale SD-Speicherung,
- direkte LoRa-Kommunikation,
- direkte Sternkommunikation mit fester Zuordnung des Masters in der Slave-Konfiguration,
- Konfiguration fuer Rolle, Kennung, Funk und Zeit,
- Betriebs-, Test- und Datendokumentation.

Externe Datenauswertung nach Entnahme der Dateien gehoert nicht zur Laufzeitsoftware des Praktikumsprojekts.

### 4.2 Vorlaeufige Netzstruktur

Das Kernsystem verwendet eine direkte Sternkommunikation:

~~~text
Slave 01 ----\
Slave 02 -----\
...             >---- Master ---- Master-SD
Slave 10 -----/
~~~

Jeder Slave enthaelt in seiner lokalen `/config.json` die eindeutige `master_id` des vorgesehenen Masters. Die Konfiguration enthaelt ausserdem den verpflichtenden Schluessel `network_mode`. Damit ist die Topologie pro Geraet bewusst und nachvollziehbar auswaehlbar:

| `network_mode` | Bedeutung | Status |
|---|---|---|
| `star` | Der Slave sendet unmittelbar an `master_id`. `next_hop_id` entspricht dem Master. Fremde Pakete werden nicht weitergeleitet. | Kernsystem und Standardwert |
| `mesh` | Der Slave oder Relay-Knoten verwendet einen statisch konfigurierten naechsten Hop Richtung Master und kann Pakete anderer Slaves weiterleiten. | Kann-Erweiterung; erst nach gesonderter Implementierung aktivierbar |

Eine automatische Master-, Nachbar- oder Routenerkennung ist in beiden Modi nicht vorgesehen. Die Bezeichnung `mesh` steht hier fuer eine mehrstufige, statisch konfigurierte Weiterleitung; sie meint kein dynamisches Mesh mit selbststaendiger Routensuche.

Im Modus `mesh` muss jede beteiligte `/config.json` mindestens `master_id`, `next_hop_id` und `hop_limit` enthalten. Beispiel fuer die Kette `C03 -> C02 -> C01 -> M01`: `C03` verwendet `next_hop_id: "C02"`, `C02` verwendet `next_hop_id: "C01"`, `C01` verwendet `next_hop_id: "M01"`. Der Master muss alle erwarteten Ursprungs-Slaves in `monitored_slaves` enthalten. Eine Konfiguration darf keinen Knoten auf sich selbst verweisen lassen und muss einen Hop-Grenzwert von mindestens eins festlegen.

Ein Relay nimmt nur Pakete mit eigener `next_hop_id` an, erkennt Duplikate, ersetzt den naechsten Hop, erhoeht den Hop-Zaehler und verwaltet fremde ausstehende Pakete bis zur erfolgreichen Weitergabe. Der unmittelbare Empfaenger bestaetigt jeden Funkhop. Der Master bestaetigt erst nach erfolgreicher zentraler Speicherung; der Ursprungs-Slave behaelt seine lokale Sicherung. Bei geaenderter Aufstellung muss die Konfiguration angepasst werden. Ohne zweiten konfigurierten Weg besteht keine automatische Ausfallsicherheit.

Die Datenpaket-Weiterleitung und der ACK-Rueckweg einer statischen Kette sind implementiert. Fuer die Kette `C03 -> C02 -> C01 -> M01` muessen die vier aufeinander abgestimmten Beispielkonfigurationen `config.mesh.example.json`, `config.mesh.relay.example.json`, `config.mesh.relay-c01.example.json` und `config.mesh.master.example.json` verwendet werden. Vor einer Freigabe auf Einsatzgeraeten bleiben die persistente Relay-Warteschlange, Duplikatbehandlung im Relay, weitergehendes Fehlerverhalten und Hardwaretests offen.

### 4.3 Komponenten

| Komponente | Verantwortung |
|---|---|
| Configuration | Rolle, Geraete-ID, Funkparameter, Messintervall und optionale Einstellungen bereitstellen |
| MeasurementService | freigegebene Sensoren ansprechen und einen gemeinsamen Messdatensatz erzeugen |
| LocalStorage | Messdatensaetze auf Slave- und Master-SD sowie zentral empfangene Diagnoseereignisse auf der Master-SD schreiben |
| ProtocolCodec | logischen Datensatz validieren, serialisieren und deserialisieren |
| LoRaTransport | SX1262 initialisieren sowie Pakete senden und empfangen |
| SlaveController | Messzyklus, lokale Sicherung, Uebertragung und Wiederholungslogik koordinieren |
| MasterController | Empfang, Validierung, Zeitbezug, Zuordnung und zentrale Speicherung koordinieren |
| TimeService | 15-Minuten-Messrhythmus steuern und vorhandene Zeitinformationen als optionale Zusatzinformation bereitstellen |
| Diagnostics | Fehler, Status und relevante Betriebsereignisse seriell protokollieren und waehrend der Integration optional auf dem OLED spiegeln |

Die Namen beschreiben Verantwortungsbereiche. Master- und Slave-Software werden in einem gemeinsamen Git-Repository und einer gemeinsamen Codebasis gepflegt. Rollenbezogene Einstiegspunkte trennen die Programmablaeufe; gemeinsam benoetigte Funktionen werden wiederverwendet. Auf einem Geraet wird nur der konfigurierte Master- oder Slave-Ablauf gestartet. Die Datei- und Modulstruktur ist in Abschnitt 4.4 sowie in `docs/Architektur_Hexagonal.md` festgelegt.

### 4.4 Architekturprinzip

Die Software verwendet eine schlanke hexagonale Architektur. `domain/` und `application/` enthalten hardwareunabhaengige Fachobjekte und Anwendungsfaelle. `ports/` beschreibt die vom Anwendungskern benoetigten Schnittstellen. CircuitPython, SEN66, SD-Karte, SX1262, Zeitquelle und Diagnose werden ausschliesslich ueber Implementierungen in `adapters/` angebunden. `code.py` ist die Composition Root und startet anhand der validierten Konfiguration nur den Master- oder Slave-Ablauf. Auf eine Dependency-Injection-Bibliothek und schwere abstrakte Frameworks wird wegen der Zielplattform bewusst verzichtet.

## 5. Akteure Und Systemrollen

### 5.1 Systemrolle: Slave Climate Cube

Der Slave soll:

1. seine Konfiguration und eindeutige Kennung laden,
2. die vorhandenen Sensoren initialisieren,
3. im vorgesehenen 15-Minuten-Intervall genau einen logischen Messdatensatz mit eindeutiger Sequenznummer erzeugen; den Sequenzstand bei verfuegbarer Slave-SD persistent sichern,
4. fehlende Sensorwerte eindeutig kennzeichnen,
5. den Datensatz bei verfuegbarer Slave-SD vor dem Senden lokal speichern und bei einem SD-Fehler gemaess UC-13 direkt uebertragen,
6. denselben logischen Datensatz fuer die Funkuebertragung verwenden,
7. das Paket ohne harte Anforderung an den genauen Uebertragungszeitpunkt an den Master senden,
8. eine zur Geraete-ID und Sequenznummer passende Empfangsbestaetigung auswerten,
9. Datensaetze ohne passende Empfangsbestaetigung als ausstehend erhalten und spaeter erneut senden,
10. nach einem Neustart die naechste noch unbenutzte Sequenznummer aus der Slave-SD oder gemaess UC-15 vom Master beziehen, lokal vorhandene ausstehende Datensaetze wiedererkennen und ohne Ueberschreiben vorhandener Daten weiterarbeiten.

### 5.2 Systemrolle: Master Climate Cube

Der Master soll:

1. seine Master-Konfiguration laden,
2. seinen persistenten Sequenzstand je Slave laden beziehungsweise rekonstruieren,
3. dauerhaft beziehungsweise in geeigneten Empfangsfenstern auf LoRa-Pakete warten,
4. Paketversion und Datenstruktur pruefen,
5. Slave-ID und Sequenznummer auswerten,
6. ungueltige, doppelte oder nicht unterstuetzte Pakete definiert behandeln,
7. vorhandene Zeitinformationen unveraendert erhalten und gueltige Pakete optional mit Empfangszeitstempel sowie mit RSSI, SNR und Empfangsstatus ergaenzen,
8. Daten mehrerer Slaves zentral auf SD-Karte speichern,
9. erst nach erfolgreicher zentraler Speicherung eine Empfangsbestaetigung senden,
10. Fehler und Neustarts nachvollziehbar dokumentieren,
11. ausschliesslich die in `monitored_slaves` konfigurierten Slaves als regulaere Funk-Datenquellen und fuer die spaetere Intervallueberwachung verwenden,
12. gemaess Erweiterungsauftrag vom 18.09.2026 eigene Sensorwerte im konfigurierten 15-Minuten-Rhythmus erfassen und unter seiner eigenen Geraete-ID mit separater persistenter Sequenz speichern. Die Master-ID wird nicht in `monitored_slaves` eingetragen. Eigene Datensaetze werden weder per Funk versendet noch mit einem ACK bestaetigt. Waehrend der Sensor-Aufwaermzeit wird der Funkempfang weiter bedient.

Die Erweiterung ist lokal implementiert und getestet; ihre Hardwareabnahme steht noch aus. Zeitfuehrung, Update-Anleitung und Testkriterien sind in `docs/Master_Messung_und_Zeit.md` beschrieben. Eine vorhandene interne UTC-Uhr wird beim Software-Neustart weiterverwendet, sofern sie mindestens den konfigurierten Startwert erreicht hat. Ohne erhaltene Uhr nach Stromverlust ist eine neue Zeitreferenz erforderlich; eine ausgeschaltete Zeitspanne wird nicht geschaetzt.

### 5.3 Externer Akteur: Benutzer

Der Benutzer soll:

1. die physische Rolle eines Geraets feststellen koennen,
2. eine eindeutige Geraete-ID konfigurieren,
3. Funkparameter zwischen Master und Slaves abgleichen,
4. den vorgesehenen 15-Minuten-Messrhythmus konfigurieren beziehungsweise pruefen,
5. den Betriebszustand bei Einrichtung und Fehlersuche anhand serieller beziehungsweise gespeicherter Diagnoseausgaben kontrollieren,
6. SD-Karten sicher entnehmen und Dateien einem Master oder Slave zuordnen,
7. Datensaetze anhand von Version, Geraete-ID und Sequenznummer zuordnen,
8. Messfelder, Einheiten, fehlende Werte und Statusflags verstehen,
9. Sequenznummern, optionale Zeitstempel und Funkmetadaten interpretieren,
10. nach einer Stoerung den vorgesehenen Wiederanlauf ausfuehren.

Eine grafische Oberflaeche ist dafuer derzeit nicht vorgesehen. Das im Prototyp vorhandene OLED ist fuer den Ausseneinsatz nicht erforderlich und hoechstens eine optionale lokale Diagnoseausgabe. Messung, Speicherung und Funkuebertragung muessen ohne Display funktionieren. Es gibt keine Benutzerkonten, Anmeldung oder unterschiedlichen Berechtigungsstufen. Als technische Konfigurationsform wird eine geraetespezifische `/config.json` verwendet. Der Benutzer darf sie anhand der Betriebsanleitung bearbeiten oder ersetzen. Aenderungen werden nach einem Neustart wirksam. Eine automatische oder zentrale Verteilung der Konfiguration ist nicht Bestandteil des Kernsystems.

## 6. Use Cases

### UC-01 Geraet Konfigurieren

| Feld | Inhalt |
|---|---|
| Akteur | Benutzer |
| Vorbedingung | Hardware ist spannungsfrei korrekt aufgebaut; Softwarestand ist bekannt |
| Ausloeser | Geraet wird fuer einen Einsatz vorbereitet |
| Hauptablauf | rollenpassende `config.example.json` beziehungsweise `config.master.example.json` als Vorlage verwenden, Rolle und eindeutige ID vergeben, bei einem Slave die `master_id` und bei einem Master die Liste `monitored_slaves` mit mindestens einer eindeutigen Slave-ID; eine feste softwareseitige Obergrenze besteht nicht festlegen, Messintervall und Funkparameter festlegen, Datei als `/config.json` auf dem CIRCUITPY-Laufwerk speichern und Geraet neu starten |
| Ergebnis | Software hat alle Pflichtfelder validiert und das Geraet startet eindeutig als Master oder Slave |
| Fehlerfaelle | Datei fehlt, Pflichtfeld fehlt, ungueltige Rolle, fehlende oder ungueltige `master_id`, fehlende, leere, doppelte oder ungueltige `monitored_slaves`, ungueltiges Messintervall oder ungueltige Funkparameter: regulaerer Betrieb startet nicht und der Fehler wird diagnostiziert. Doppelte IDs zwischen mehreren Geraeten muessen durch den Benutzer vermieden werden. |
| Lastenbezug | LH-F-040, LH-F-041, LH-NF-008 |

### UC-02 Messdatensatz Erzeugen

| Feld | Inhalt |
|---|---|
| Akteur | Slave Climate Cube |
| Vorbedingung | Slave-Konfiguration ist gueltig |
| Ausloeser | Messintervall ist erreicht |
| Hauptablauf | Sensoren auslesen, Werte normalisieren, fehlende Werte markieren, Status setzen, Sequenznummer vergeben |
| Ergebnis | genau ein logischer, validierbarer Messdatensatz |
| Fehlerfaelle | Sensor fehlt, Timeout, unplausibler Wert |
| Lastenbezug | LH-F-001 bis LH-F-004 |

### UC-03 Lokal Am Slave Speichern

| Feld | Inhalt |
|---|---|
| Akteur | Slave Climate Cube |
| Vorbedingung | logischer Messdatensatz vorhanden |
| Ausloeser | Messdatensatz wurde erzeugt |
| Hauptablauf | Datei bestimmen, Kopfzeile pruefen, Datensatz schreiben, Schreiben abschliessen |
| Ergebnis | Datensatz ist bei verfuegbarer SD vor dem Funkversuch lokal gesichert; bei SD-Fehler bleibt er fuer die direkte Uebertragung verfuegbar |
| Fehlerfaelle | SD fehlt, Einhaengen fehlgeschlagen oder Schreibfehler: Speicherfehler im Datensatz kennzeichnen und mit UC-04 fortfahren |
| Lastenbezug | LH-F-010 bis LH-F-012, LH-NF-002 |

### UC-04 Messdatensatz Senden

| Feld | Inhalt |
|---|---|
| Akteur | Slave Climate Cube |
| Vorbedingung | Messdatensatz vorhanden; lokaler Speicherstatus ist im Datensatz festgehalten; SX1262 initialisiert; `master_id` ist konfiguriert |
| Ausloeser | lokale Speicherung ist abgeschlossen |
| Hauptablauf | Datensatz serialisieren, Laenge pruefen, Paket senden, ACK abwarten und bei fehlendem ACK als ausstehend erhalten |
| Ergebnis | Master kann denselben fachlichen Datensatz empfangen |
| Fehlerfaelle | LoRa nicht initialisierbar, Paket zu gross, Timeout, fehlendes ACK |
| Lastenbezug | LH-F-020 bis LH-F-023, LH-F-025 |

### UC-05 Paket Empfangen Und Validieren

| Feld | Inhalt |
|---|---|
| Akteur | Master Climate Cube |
| Vorbedingung | Master-Konfiguration und LoRa sind gueltig |
| Ausloeser | SX1262 meldet ein empfangenes Paket |
| Hauptablauf | Payload dekodieren, Version und Feldzahl pruefen, ID und Sequenz auswerten, Messwerte validieren |
| Ergebnis | Paket ist als gueltig, ungueltig oder doppelt klassifiziert |
| Fehlerfaelle | unbekannte Version, falsche Feldzahl, ungueltige Zeichen, unplausible Werte |
| Lastenbezug | LH-F-030 bis LH-F-032 |

### UC-06 Zentral Speichern

| Feld | Inhalt |
|---|---|
| Akteur | Master Climate Cube |
| Vorbedingung | Paket ist klassifiziert |
| Ausloeser | Validierung ist abgeschlossen |
| Hauptablauf | Sequenznummer je Slave pruefen, vorhandene Zeitinformation erhalten, optional Empfangszeitstempel sowie RSSI/SNR ergaenzen, Datei bestimmen und den Datensatz in nachvollziehbarer Sequenzreihenfolge speichern |
| Ergebnis | Empfang ist zentral und einem Slave zugeordnet dokumentiert |
| Fehlerfaelle | Sequenzluecke oder Duplikat, SD fehlt, Schreibfehler |
| Lastenbezug | LH-F-033 bis LH-F-035, LH-F-043 |

### UC-07 Empfang Bestaetigen

| Feld | Inhalt |
|---|---|
| Akteur | Master und Slave |
| Status | fachlich bestaetigte Muss-Funktion; FIFO-Reihenfolge und Wiederholung im 15-Minuten-Zyklus festgelegt; vorlaeufiger ACK-Timeout drei Sekunden, Hardwarevalidierung offen |
| Hauptablauf | Master speichert den gueltigen Datensatz zentral und sendet erst danach ein ACK mit Geraete-ID und Sequenznummer; Slave sendet ausstehende Datensaetze chronologisch, markiert einen Datensatz nach passendem ACK als uebertragen und faehrt dann mit dem naechsten fort; beim ersten fehlenden ACK endet der Sendedurchlauf bis zum naechsten 15-Minuten-Zyklus |
| Ergebnis | Slave kann bestaetigte und nicht bestaetigte Uebertragungen unterscheiden |
| Fehlerfaelle | ACK verloren, falsche Sequenz, Master-Speicherfehler |
| Lastenbezug | LH-F-023, LH-F-025, LZ-M-09 |

### UC-08 Daten Entnehmen

| Feld | Inhalt |
|---|---|
| Akteur | Benutzer |
| Vorbedingung | Geraet wurde ordnungsgemaess gestoppt beziehungsweise SD sicher entnommen |
| Hauptablauf | Dateien kopieren, Quelle und Softwarestand dokumentieren, Formatversion pruefen |
| Ergebnis | Daten stehen fuer die Auswertung eindeutig interpretierbar bereit |
| Fehlerfaelle | unvollstaendige Datei, unbekannte Version, fehlende Dokumentation |
| Lastenbezug | LH-F-042, LH-F-043, LH-NF-003 |

### UC-09 Slave Nach Neustart Fortsetzen

| Feld | Inhalt |
|---|---|
| Akteur | Slave Climate Cube |
| Vorbedingung | lokale SD-Karte mit vorhandenen Mess- und Uebertragungsinformationen ist lesbar |
| Ausloeser | Slave startet nach Stromunterbrechung, Wartung oder Programmneustart |
| Hauptablauf | Konfiguration laden, hoechste bereits verwendete Sequenznummer und ausstehende Datensaetze bestimmen, mit der naechsten freien Sequenznummer weiterarbeiten und ausstehende Datensaetze fuer spaetere Uebertragung vormerken |
| Ergebnis | keine vorhandenen Daten werden ueberschrieben; Sequenznummern werden nicht erneut vergeben; ausstehende Uebertragungen bleiben erhalten |
| Fehlerfaelle | Statusinformation beschaedigt, letzte Datei unvollstaendig, SD-Karte fehlt oder ist nicht lesbar |
| Lastenbezug | LH-F-011, LH-F-025, LH-NF-004 |

### UC-10 Master Nach Neustart Fortsetzen

| Feld | Inhalt |
|---|---|
| Akteur | Master Climate Cube |
| Vorbedingung | Master-SD mit vorhandenen Mess- und Diagnosedateien ist lesbar |
| Ausloeser | Master startet nach Stromunterbrechung, Wartung oder Programmneustart |
| Hauptablauf | Konfiguration laden, letzten gespeicherten Sequenzstand je Slave aus den Messdateien rekonstruieren, aktive Diagnosezustaende aus `events.csv` rekonstruieren und danach den Empfang fortsetzen |
| Ergebnis | Bereits gespeicherte Datensaetze werden weiterhin als Duplikate erkannt; bestehende Diagnosezustaende werden nicht erneut als neue Fehlerfaelle eroeffnet |
| Fehlerfaelle | Master-SD fehlt, Datei unvollstaendig, unbekannte Formatversion oder widerspruechlicher Sequenzstand |
| Lastenbezug | LH-F-011, LH-F-033, LH-NF-004 |

### UC-11 Mehrere Ausstehende Datensaetze Nachsenden

| Feld | Inhalt |
|---|---|
| Akteur | Slave und Master Climate Cube |
| Vorbedingung | Slave besitzt mehrere lokal gesicherte, nicht bestaetigte Datensaetze; Master ist wieder erreichbar |
| Ausloeser | regulaerer Sendedurchlauf im naechsten 15-Minuten-Zyklus beginnt |
| Hauptablauf | Slave sendet den aeltesten ausstehenden Datensatz; nach erfolgreichem ACK folgt jeweils der naechste Datensatz in aufsteigender Sequenzreihenfolge |
| Ergebnis | Alle erfolgreich bestaetigten Datensaetze sind beim Master genau einmal gespeichert und beim Slave als uebertragen markiert |
| Fehlerfaelle | Beim ersten fehlenden oder unpassenden ACK wird der Durchlauf beendet; der betroffene und alle neueren Datensaetze bleiben fuer den naechsten Zyklus ausstehend. Das fehlende ACK darf zur Inbetriebnahme seriell mit der Sequenznummer ausgegeben werden, erzeugt aber kein eigenes Diagnoseereignis und keinen zusaetzlichen SD-Eintrag. |
| Lastenbezug | LH-F-020, LH-F-023, LH-F-025 |

### UC-12 Duplikat Erkennen Und Bestaetigen

| Feld | Inhalt |
|---|---|
| Akteur | Master Climate Cube |
| Vorbedingung | Ein Datensatz mit gleicher `origin_id` und `sequence_number` ist bereits zentral gespeichert |
| Ausloeser | Derselbe Datensatz wird erneut empfangen, beispielsweise weil ein ACK verloren ging |
| Hauptablauf | Master validiert Adressierung und Format, erkennt das Duplikat anhand von Ursprung und Sequenznummer, schreibt keine zweite Messzeile und sendet ACK-Ergebniscode `2` |
| Ergebnis | Der Datensatz ist genau einmal zentral gespeichert; der Slave kann die Wiederholung als erfolgreich abschliessen |
| Fehlerfaelle | Gleiche Sequenznummer mit abweichendem Inhalt wird als Konflikt diagnostiziert und nicht still als normales Duplikat behandelt |
| Lastenbezug | LH-F-023, LH-F-025, LH-F-032 |

### UC-13 Ohne Slave-SD Weiterarbeiten

| Feld | Inhalt |
|---|---|
| Akteur | Slave Climate Cube |
| Vorbedingung | Sensorik und LoRa sind betriebsbereit; Slave-SD fehlt oder ist nicht beschreibbar |
| Ausloeser | SD-Mount oder lokaler Schreibvorgang schlaegt fehl |
| Hauptablauf | Slave setzt `SLAVE_SD_UNAVAILABLE` beziehungsweise `SLAVE_SD_WRITE_ERROR`, sendet ein begrenztes Diagnoseereignis und uebertraegt den Messdatensatz trotz fehlendem lokalen Backup an den konfigurierten Master |
| Ergebnis | Der Master kann den Messdatensatz und den fehlenden lokalen Speicherzustand zentral dokumentieren; der Slave bleibt im Messbetrieb |
| Fehlerfaelle | Ohne Slave-SD koennen Datensatz und Diagnose nicht lokal gepuffert werden. Bei Neustart ohne lesbaren Sequenzstand wird die naechste freie Sequenznummer nach UC-15 beim Master abgefragt. |
| Lastenbezug | LH-F-012, LH-F-020, LH-NF-004 |

### UC-14 Diagnoseereignis Zentral Verwalten

| Feld | Inhalt |
|---|---|
| Akteur | Slave und Master Climate Cube |
| Vorbedingung | Direkte Funkverbindung zum konfigurierten Master ist moeglich; Master-SD ist beschreibbar |
| Ausloeser | Zustandsbehafteter Fehler beginnt oder endet beziehungsweise ein einmaliges Ereignis tritt auf |
| Hauptablauf | Slave sendet ein `E`-Paket mit `STARTED`, `ENDED` oder `OCCURRED`; Master ordnet es ueber `origin_id + event_code` zu, aktualisiert den aktiven Zustand und speichert es unter `/diagnostics/<origin_id>/events.csv` |
| Ergebnis | Der Benutzer kann zentrale Diagnoseverlaeufe je Slave nachvollziehen, ohne die Slave-SD auszulesen |
| Fehlerfaelle | Wiederholtes `STARTED` eroeffnet keinen neuen Fehlerfall; verlorene Ereignispakete besitzen kein eigenes ACK; SD- und Sensorzustaende bleiben zusaetzlich ueber Messdaten-Statusflags sichtbar |
| Lastenbezug | LH-F-012, LH-F-032, LZ-K-03, LH-NF-004 |

### UC-15 Sequenznummer Ohne Slave-SD Vom Master Beziehen

| Feld | Inhalt |
|---|---|
| Akteur | Slave und Master Climate Cube |
| Vorbedingung | Slave kann beim Start keinen persistenten Sequenzstand von seiner SD rekonstruieren; Master ist konfiguriert, seine Erreichbarkeit ist jedoch nicht garantiert |
| Ausloeser | Slave startet ohne lesbare Slave-SD |
| Hauptablauf | Slave sendet bis zu drei routingfaehige `Q`-Pakete mit jeweils drei Sekunden Antwort-Timeout und zwei Sekunden Pause zwischen erfolglosen Versuchen; Master bestimmt die hoechste zentral gespeicherte Sequenznummer dieses Slaves und antwortet mit `R` und der naechsten freien Sequenznummer; Slave fuehrt den erhaltenen Stand im RAM fort. Ein Wechsel zur SD-gestuetzten Verwaltung erfolgt nicht per Hot-Plug im laufenden Betrieb, sondern erst nach spannungsfreiem Einsetzen oder Reparieren der SD und anschliessendem Neustart |
| Ergebnis | Der Slave vergibt keine bereits zentral verwendete Sequenznummer und kann trotz fehlender lokaler SD Messdaten senden |
| Fehlerfaelle | Ohne gueltige `R`-Antwort endet die Abfragerunde nach drei Versuchen. Nach 60 Sekunden beginnt eine neue Runde. Der Slave beginnt nicht bei `0` und sendet keine neuen Messdatensaetze. Er haelt hoechstens die neueste noch nicht nummerierte Messung im RAM; ein neuer Messzyklus ersetzt eine aeltere unnummerierte Messung. Der RAM-Inhalt geht bei Neustart verloren. |
| Lastenbezug | LH-F-011, LH-F-020, LH-F-025, LH-NF-004 |

## 7. Datenmodell Und Protokoll

### 7.1 Gemeinsamer Logischer Datensatz

Lokale Speicherung und Funkpayload werden aus demselben logischen Datenobjekt erzeugt. Dadurch werden abweichende Messwerte zwischen lokaler und zentraler Ablage vermieden.

Vorgesehene Kernfelder:

- format_version,
- message_type,
- `origin_id`, `destination_id` und `next_hop_id`,
- `sequence_number`, `hop_count` und `hop_limit`,
- optionale Laufzeit beziehungsweise Boot-Kennung,
- Lufttemperatur, relative Luftfeuchtigkeit, CO2, PM1, PM2.5, PM4, PM10, VOC-Index und NOx-Index,
- Status fuer fehlende oder fehlerhafte Werte.

Die chronologische Ordnung eines logischen Datensatzes wird pro Slave verbindlich durch die persistente `sequence_number` bestimmt. Ein `measurement_timestamp` kann als zusaetzliche Zeitinformation enthalten sein, ist ohne gueltige Zeitsynchronisation jedoch nicht fuer die Sortierung massgeblich. Der Master ergaenzt Master-ID, optionalen `received_timestamp`, RSSI, SNR und das Ergebnis der Validierung.

### 7.2 Serialisierung

Die V1-Zielspezifikation verwendet eine ASCII-Darstellung mit fester Feldreihenfolge. Datenpakete besitzen 22 Felder und einen routingfaehigen Kopf mit Ursprung, Endziel, naechstem Hop, Sequenznummer, Hop-Zaehler und Hop-Limit. ACKs besitzen neun Felder und denselben Kopf in Gegenrichtung. Fehlende Werte werden als `NA`, Statusflags als vierstellige Hexadezimalzahl uebertragen. Die maximale Payload-Laenge betraegt 160 Byte. Der aktuelle Codec-Prototyp verwendet noch das aeltere Format und muss auf die festgelegte V1-Zielspezifikation umgestellt und erneut getestet werden.

### 7.3 Dateiformate

- Slave-Ablage: Unter `/data/<device_id>/` werden die eigenen Messdatensaetze in Dateien mit jeweils 3.000 fortlaufenden Sequenznummern gespeichert.
- Master-Ablage: Unter `/data/<device_id>/` existiert fuer jeden Slave ein eigener Ordner mit demselben Sequenzblock-Schema; Master-Metadaten werden in den zentralen Zeilen ergaenzt.
- Master-Diagnoseablage: Unter `/diagnostics/<device_id>/events.csv` speichert ausschliesslich der Master die von Slaves empfangenen Diagnoseereignisse.

CSV wird als lesbares Zielformat vorgeschlagen. Dezimalpunkt, Zeichencodierung, Kopfzeile und Versionswechsel werden verbindlich dokumentiert.

Dateien werden nach dem Schema `measurements_<erste_sequence>-<letzte_sequence>.csv` benannt, beispielsweise `measurements_000000-002999.csv`. Der Dateiblock wird ausschliesslich aus `sequence_number / 3000` bestimmt. Dadurch bleibt die Aufteilung auch ohne gueltige Uhrzeit und ueber Neustarts hinweg reproduzierbar. Bei einem 15-Minuten-Rhythmus entsprechen 3.000 Datensaetze ungefaehr einem Monat.

Slaves speichern keine eigene Diagnosedatei. Sie senden Diagnoseereignisse beim ersten Auftreten und bei der Behebung per LoRa an den Master. Wiederholte identische Ereignisse werden nicht in jeder Programmschleife gesendet, sondern fluechtig gezaehlt und beim Zustandswechsel zusammengefasst. Der Master speichert empfangene Ereignisse getrennt von Messdaten; seine Messdatenspeicherung besitzt Vorrang.

### 7.4 Ueberwachte Slaves Und Empfangsintervalle

Ein Master besitzt in seiner lokalen Konfiguration das Pflichtfeld `monitored_slaves`. Die Liste enthaelt mindestens eine eindeutige Slave-ID und besitzt keine feste softwareseitige Obergrenze. Jede ID folgt den allgemeinen Kennungsregeln; die Master-ID selbst ist unzulaessig. Aenderungen werden nach einem Master-Neustart wirksam. Entfernte Slaves werden ab dann nicht weiter ueberwacht, ihre vorhandenen Dateien bleiben erhalten. Neue Slaves werden ab dem ersten vollstaendigen 15-Minuten-Intervall nach dem Neustart ueberwacht.

Der Master verarbeitet nur Pakete eingetragener Slaves als regulaere Messdaten. Pakete unbekannter Slaves werden nicht in der normalen Messablage gespeichert und seriell als Konfigurationsabweichung gemeldet. Fuer jeden eingetragenen Slave fuehrt der Master getrennt den letzten Empfang, die letzte bekannte Sequenznummer und die Anzahl aufeinanderfolgender Intervalle ohne Paket.

Die Intervallueberwachung erzeugt pro konfiguriertem Slave und 15-Minuten-Intervall entweder einen echten empfangenen Datensatz oder zunaechst eine eindeutig als `NO_PACKET` markierte vorlaeufige Lueckenzeile. In einer Lueckenzeile sind Messwerte, Slave-Sequenznummer und Slave-Zeitinformation `NA`; Master-ID, Slave-ID, Rasterzeit beziehungsweise Master-Laufzeit und Anzahl aufeinanderfolgender fehlender Intervalle bleiben gesetzt. Die Zeile bedeutet ausschliesslich, dass der Master in diesem Intervall noch kein Paket empfangen hat. Der Master merkt die zu diesem Zeitpunkt erwartete Sequenznummer intern persistent; wird ein Datensatz mit dieser Nummer spaeter empfangen, ersetzt er die vorlaeufige Luecke atomar durch den echten Datensatz. Nur nicht nachgelieferte Datensaetze verbleiben als dauerhafte `NO_PACKET`-Luecken.

## 8. Hardware- Und Softwareschnittstellen

### 8.1 Bestaetigte SX1262-Belegung

| Signal | Pico-Pin | Teststatus 11.08.2026 |
|---|---|---|
| BUSY | GP2 | funktional im Ping-Pong-Test |
| CS / NSS | GP3 | funktional im Ping-Pong-Test |
| SCK | GP10 | funktional im Ping-Pong-Test |
| MOSI | GP11 | funktional im Ping-Pong-Test |
| MISO | GP12 | funktional im Ping-Pong-Test |
| RESET | GP15 | funktional im Ping-Pong-Test |
| DIO1 / IRQ | GP20 | funktional im Ping-Pong-Test |
| BAT_AD | GP26 | im Funkversuch nicht verwendet und nicht bewertet |

### 8.2 Weitere Bestandsschnittstellen

| Funktion | Bestand | Status |
|---|---|---|
| I2C fuer SEN66 und vorhandenes OLED | GP0 / GP1 | SEN66 erforderlich; OLED im Kernbetrieb optional |
| SD-SPI | GP16 bis GP19 | Schreiben auf beiden Testgeraeten nachgewiesen |
| DS18B20 | GP27 im neueren Bestandscode | optionale Funktion; Sensor am 11.08. nicht angeschlossen nachgewiesen; Wiederholungsfehler vorhanden |
| Bodenfeuchte | GP26 im Repository-Code | optionale Funktion; reale Hardware und Konfliktlage bei Umsetzung zu klaeren |

Die endgueltige Pinbelegung ist vor produktiver Implementierung als eigenes freigegebenes Artefakt zu dokumentieren.

### 8.3 Laufzeit Und Bibliotheken

- Ziel ist CircuitPython fuer Raspberry Pi Pico 2 W.
- Getestet wurde CircuitPython 10.2.1.
- Der SX1262-Treiber besteht aus _sx126x.py, sx126x.py und sx1262.py.
- Drittanbieterquelle und Lizenz bleiben im Repository dokumentiert.
- Board-spezifische Firmware darf nicht zwischen Pico-Varianten verwechselt werden.
- Eigene Python-Module duerfen unter CircuitPython ausserhalb von `code.py` liegen und werden aus den Architekturordnern importiert.
- Der Name eines Python-Moduls darf auf dem CIRCUITPY-Dateisystem nicht mit einem Mount-Verzeichnis kollidieren. Der am 20.08.2026 nachgewiesene Konflikt zwischen `SD.py` und `/sd` wird durch `adapters/sd_card.py` vermieden.
- Der konsolidierte Master-Start wurde auf CircuitPython 10.2.1 mit `/config.json`, OLED, SD-Karte und SX1262 erfolgreich ausgefuehrt.

## 9. Ablaufsteuerung

### 9.1 Slave-Zustandsmodell

~~~text
START
  -> KONFIGURATION PRUEFEN
  -> HARDWARE INITIALISIEREN
  -> AUF MESSZEIT WARTEN
  -> MESSEN
  -> LOKAL SPEICHERN
  -> SENDEN
  -> ACK AUSWERTEN; OHNE ACK DATENSATZ AUSSTEHEND LASSEN
  -> STATUS PROTOKOLLIEREN
  -> AUF MESSZEIT WARTEN
~~~

Ein Sensorfehler darf den Datensatz nicht zwingend verwerfen, sofern die fachliche Spezifikation Teildatensaetze zulaesst. Ein lokaler Speicherfehler und das Senden eines nicht lokal gesicherten Datensatzes muessen fachlich entschieden werden.

### 9.2 Master-Zustandsmodell

~~~text
START
  -> KONFIGURATION UND ZEIT PRUEFEN
  -> HARDWARE INITIALISIEREN
  -> EMPFANGEN
  -> VALIDIEREN
  -> ZEIT UND FUNKMETADATEN ERGAENZEN
  -> SPEICHERN ODER FEHLER PROTOKOLLIEREN
  -> NACH ERFOLGREICHER SPEICHERUNG ACK SENDEN
  -> EMPFANGEN
~~~

## 10. Fehlerbehandlung

| Fehler | Vorgeschlagenes Verhalten | Entscheidung |
|---|---|---|
| Sensor nicht vorhanden | Wert als fehlend markieren; andere Messungen fortsetzen | fachlich bestaetigen |
| SD am Slave fehlt | Speicherfehler im Datensatz kennzeichnen und Messdatensatz trotzdem an den Master senden; regulaeren Betrieb nach Moeglichkeit fortsetzen | entschieden am 24.08.2026; lokales Backup fehlt bis zur Wiederherstellung der SD |
| LoRa-Initialisierung fehlgeschlagen | lokal weiter speichern; Diagnose ausgeben | vorgeschlagen |
| Master nicht erreichbar | lokal als ausstehend erhalten und spaeter erneut senden | Grundprinzip bestaetigt; Parameter offen |
| ungueltiges Paket | nicht als gueltige Messung speichern; Fehler dokumentieren | vorgeschlagen |
| Duplikat | nicht doppelt als neue Messung speichern; Empfang dokumentieren | vorgeschlagen |
| Master-SD fehlt | kein Erfolgs-ACK senden; Slave behaelt Datensatz als ausstehend | fachlich bestaetigt |
| Master-Zeit ungueltig | Datensatz weiterhin anhand von Slave-ID und Sequenznummer speichern; Zeitstempel als ungueltig beziehungsweise nicht synchronisiert kennzeichnen | entschieden am 24.08.2026; Zeitfehler blockiert die Speicherung nicht |
| Neustart | vorhandene Dateien erhalten, naechste freie Sequenznummer verwenden und ausstehende Datensaetze wiederherstellen; ohne lesbare Slave-SD Sequenzstand nach UC-15 beim Master abfragen | Wiederanlauf mit lesbarer Slave-SD bestaetigt; Master-Abfrage ohne Slave-SD implementiert und per Unit-Test geprueft; Hardwaretest offen |

Der Architektur-Prototyp verwendet eine gemeinsame Fehlerbasis `ClimateCubeError` mit spezialisierten Konfigurations-, Zeit-, Speicher- und Funkfehlern. Adapter uebersetzen technische Ausnahmen an der Port-Grenze. Erwartete Systemfehler und unerwartete Programmfehler werden in der Composition Root unterscheidbar diagnostiziert. Sensorfehler bleiben davon getrennt und werden als Statusflags im Messdatensatz behandelt. Die fachlichen Reaktionen fuer den Betrieb ohne Slave-SD sind in UC-13 und UC-15 festgelegt. Der Prototyp enthaelt inzwischen die Sequenzabfrage, den fluechtigen RAM-Betrieb und die Statuskennzeichnung fuer fehlende Slave-SD; Hardwaretests bleiben offen.

## 11. Technische Anforderungen

| ID | Umsetzungsvorgabe | Lastenbezug |
|---|---|---|
| PH-T-001 | Master und Slave werden in einer gemeinsamen Codebasis gepflegt. Getrennte Einstiegspunkte starten anhand einer validierten Rollen-Konfiguration ausschliesslich den jeweils vorgesehenen Programmablauf. | LH-F-040 |
| PH-T-002 | Ein Messzyklus erzeugt genau ein gemeinsames Datenobjekt fuer SD und Funk. | LH-F-001, LH-F-010, LH-F-020 |
| PH-T-003 | Die Ablaufsteuerung startet pro Slave im vorgesehenen Abstand von 15 Minuten genau einen Messzyklus; Sensor-Aufwaermzeit und Funkuebertragung duerfen keine unkontrollierte Intervallverschiebung verursachen. | LH-F-002 |
| PH-T-004 | Sensoradapter liefern Wert oder definierten Fehlerstatus statt unkontrolliertem Programmabbruch. | LH-F-004, LH-NF-004 |
| PH-T-005 | Dateinamen verhindern unbeabsichtigtes Ueberschreiben vorhandener Messdaten. | LH-F-011 |
| PH-T-006 | Das V1-Datenpaket besitzt genau 22 ASCII-Felder mit Version, Typ, Ursprung, Endziel, naechstem Hop, Sequenznummer, Hop-Zaehler, Hop-Limit, optionaler Zeitinformation, Laufzeit, elf Messfeldern und Statusflags. | LH-F-030, LH-F-040 |
| PH-T-007 | Der Codec prueft Feldzahl, Wertebereiche und maximale Payload-Laenge. | LH-F-032 |
| PH-T-008 | Master und Slave laden denselben dokumentierten Funkparametersatz. | LH-F-022 |
| PH-T-009 | Der Master fuehrt den letzten bekannten Sequenzstand je Slave. | LZ-S-03 |
| PH-T-010 | Die chronologische Ordnung wird je Slave anhand der persistenten Sequenznummer hergestellt. Vorhandene Mess- und Empfangszeitstempel sind optionale Zusatzinformationen und werden nicht zur Sortierung verwendet. | LH-F-034 |
| PH-T-011 | Zentrale Speicherung trennt gueltige Messdaten von Fehler- beziehungsweise Diagnoseinformationen. | LH-F-032, LH-F-033 |
| PH-T-012 | Konfigurationsfehler werden vor dem normalen Betrieb erkannt. | LH-F-040, LH-F-041 |
| PH-T-013 | Bibliotheks- und Firmwareversionen werden reproduzierbar dokumentiert. | LH-NF-008 |
| PH-T-014 | LoRa-Senden wird nur mit montierter passender Antenne getestet und betrieben. | LH-NF-009 |
| PH-T-015 | Jeder Slave laedt die Zielkennung `master_id` aus seiner `/config.json`. Datenpaket und ACK muessen die Zuordnung zum konfigurierten Master pruefbar machen; Pakete beziehungsweise ACKs eines anderen Masters werden nicht als erfolgreiche Uebertragung gewertet. Eine automatische Master-Erkennung findet nicht statt. | LH-F-020, LH-F-022, LH-F-040 |
| PH-T-016 | Die Speicherplanung weist mindestens 35.040 Datensaetze je Slave und 350.400 Datensaetze am Master fuer zehn Slaves zuzueglich Sicherheitsreserve nach. | LH-F-010, LH-F-033, LH-NF-010 |
| PH-T-017 | Der Master erzeugt ein Erfolgs-ACK erst nach abgeschlossenem SD-Schreibvorgang. Das neunfeldrige ACK wird ueber Master-Ursprung, Slave-Ziel und Sequenznummer eindeutig zugeordnet; nur Ergebniscodes `0` und `2` gelten als erfolgreich. | LH-F-023, LH-F-025 |
| PH-T-018 | Der regulaere Betrieb ist unabhaengig vom OLED; ein fehlendes oder defektes Display verhindert Messung, Speicherung und Funkkommunikation nicht. | LZ-K-03, LH-NF-004 |
| PH-T-019 | Sequenzstand und Status ausstehender Uebertragungen werden persistent gespeichert oder beim Start eindeutig aus der SD-Ablage rekonstruiert. | LH-F-011, LH-F-025, LH-NF-004 |
| PH-T-020 | Der Slave sendet ausstehende Datensaetze FIFO. Nach einem passenden ACK folgt der naechste Datensatz; beim ersten fehlenden ACK wird der Durchlauf beendet und im naechsten 15-Minuten-Zyklus beim aeltesten unbestaetigten Datensatz fortgesetzt. | LH-F-020, LH-F-025 |
| PH-T-021 | Slaves speichern keine eigene Diagnosedatei, sondern senden begrenzte Diagnoseereignisse per LoRa an den Master. Der Master speichert sie unter `/diagnostics/<device_id>/events.csv` mit Geraete-ID, Bezugssequenznummer, Ereigniscode, Zustand und Wiederholungsanzahl. Wiederholte identische Ereignisse werden zusammengefasst; Messdatenspeicherung hat Vorrang. | LH-F-012, LH-F-032, LH-NF-002, LH-NF-004 |
| PH-T-022 | Eine fehlende oder nicht beschreibbare Slave-SD blockiert die LoRa-Uebertragung nicht. Der Speicherfehler wird im Datensatzstatus gekennzeichnet; der Slave versucht den Datensatz direkt an den Master zu senden und setzt den Betrieb fort. | LH-F-012, LH-F-020, LH-NF-004 |
| PH-T-023 | Jedes Geraet laedt beim Start eine lokale `/config.json` vom CIRCUITPY-Laufwerk und validiert mindestens Rolle, Geraete-ID, Messintervall und Funkparameter. Fehlende oder ungueltige Pflichtangaben verhindern den regulaeren Betrieb und werden diagnostiziert; sie werden nicht unbemerkt durch Standardwerte ersetzt. Unbekannte Zusatzfelder duerfen ignoriert werden. Die Software kann die systemweite Eindeutigkeit einer ID nicht lokal pruefen. | LH-F-040, LH-F-041, LH-NF-008 |
| PH-T-024 | `config.example.json` fuer Slaves und `config.master.example.json` fuer Master dienen als versionierte Vorlagen; die geraetespezifische `config.json` wird nicht in Git gepflegt. Der Benutzer nimmt Aenderungen anhand der Betriebsanleitung vor und aktiviert sie durch einen Neustart. Eine automatische oder zentrale Konfigurationsverteilung gehoert nicht zum Kernsystem. | LH-F-040, LH-NF-008 |
| PH-T-025 | Messdateien werden je Geraet unter `/data/<device_id>/` in Bloecke zu hoechstens 3.000 Sequenznummern aufgeteilt. Der Dateiname enthaelt den inklusiven Sequenzbereich, zum Beispiel `measurements_000000-002999.csv`. Die Blockwahl erfolgt ohne Zeitbezug aus der Sequenznummer. | LH-F-010, LH-F-033, LH-F-040, LH-NF-003 |
| PH-T-026 | Der routingfaehige V1-Kopf wird im Kernsystem mit direktem `next_hop_id` und `hop_count=0` verwendet. Er bereitet technische Routinginformationen vor, implementiert aber weder statisches Relay noch das dynamische Mesh aus LH-F-024. Eine Mehrsprungimplementierung erfordert zuvor eine gesonderte Spezifikation. | LH-F-024, LH-NF-006 |
| PH-T-027 | Der Master fuehrt je `origin_id + event_code` einen aktiven Diagnosezustand. Wiederholtes `STARTED` eroeffnet keinen neuen Fehlerfall, `ENDED` beendet ihn und `OCCURRED` dokumentiert ein einmaliges Ereignis. Der Zustand wird nach Master-Neustart aus `events.csv` rekonstruiert. | LH-F-012, LH-F-032, LH-NF-004 |
| PH-T-028 | V1 verwendet die festgelegten Ereigniscodes fuer Slave-SD, SEN66, optionale Bodensensoren, Funk, Sequenzzustand, Neustart, Konfiguration und Payload. Nicht konfigurierte optionale Sensoren, `TIME_UNSYNCED`, `ACK_MISSING` und einzelne unplausible Messwerte erzeugen kein eigenes Ereignispaket. Ein fehlendes ACK darf seriell mit der betroffenen Sequenznummer ausgegeben werden; eine laenger anhaltende Verbindungsstoerung wird ueber die Anzahl ausstehender Datensaetze erkennbar. | LH-F-004, LH-F-012, LH-F-032 |
| PH-T-029 | Kann ein Slave beim Start keinen Sequenzstand von seiner SD rekonstruieren, fragt er die naechste freie Sequenznummer mit `Q` beim konfigurierten Master ab. Eine Abfragerunde umfasst hoechstens drei Versuche mit je drei Sekunden Timeout und zwei Sekunden Pause; nach einer erfolglosen Runde folgt nach 60 Sekunden die naechste. Der Master antwortet mit `R` und `maximal gespeicherte Sequenz + 1`, beziehungsweise `0`, wenn fuer den Slave noch kein Datensatz existiert. Ohne gueltige Antwort startet der Slave nicht eigenmaechtig bei `0`, sendet keine neuen Messdatensaetze und haelt hoechstens die neueste unnummerierte Messung im RAM. Nach einer gueltigen Antwort wird sie nummeriert und gesendet. Der Sequenzstand wird im RAM gefuehrt. Eine Rueckkehr zur SD-gestuetzten Verwaltung erfolgt nicht per Hot-Plug, sondern nach spannungsfreiem Einsetzen oder Reparieren der SD und anschliessendem Neustart; ist der lokale Sequenzstand dann nicht eindeutig, gilt erneut die Master-Abfrage nach UC-15. | LH-F-011, LH-F-020, LH-F-025, LH-NF-004 |
| PH-T-030 | Die Master-`/config.json` enthaelt `monitored_slaves` mit mindestens einer eindeutigen, gueltigen Slave-ID und ohne feste softwareseitige Obergrenze. Die Master-ID ist ausgeschlossen. Nur eingetragene Slaves werden als regulaere Datenquellen akzeptiert. Pro eingetragenem Slave und 15-Minuten-Intervall wird spaeter entweder ein empfangener Messdatensatz oder zunaechst eine vorlaeufige Lueckenzeile mit `NA`, `NO_PACKET`, Master-Rasterbezug und fortlaufendem Fehlintervallzaehler gespeichert. Ein eindeutig nachgelieferter echter Datensatz ersetzt die passende vorlaeufige Luecke; nur dauerhaft fehlende Daten verbleiben als `NO_PACKET`. | LH-F-002, LH-F-032 bis LH-F-034, LH-F-040, LH-NF-003, LH-NF-004 |
| PH-T-031 | Der vorlaeufige ACK-Timeout betraegt drei Sekunden. Nach einem fehlenden oder unpassenden ACK endet der aktuelle FIFO-Durchlauf; der Datensatz bleibt ausstehend und wird im naechsten 15-Minuten-Zyklus erneut versucht. Der Wert wird durch Reichweiten- und Stoerungstests validiert und darf danach konfigurierbar angepasst werden. | LH-F-023, LH-F-025, LH-NF-004 |
| PH-T-032 | Master und Slaves verwenden einen identischen, konfigurierbaren Funkparametersatz. Fuer Entwicklung gelten vorlaeufig 868,1 MHz, 125 kHz Bandbreite, Spreading Factor 7, Coding Rate 5, 10 dBm Sendeleistung und Sync Word 18. Einsatzparameter werden erst nach Reichweitentest und regulatorischer Freigabe fuer den konkreten Einsatzort freigegeben. | LH-F-021, LH-F-022, LH-NF-009 |
| PH-T-033 | Der Slave loest Messungen autonom im 15-Minuten-Rhythmus aus und haelt den LoRa-Empfang zwischen den Messzyklen nicht dauerhaft aktiv. Vor einem Energiesparzustand werden persistierbare Sequenz- und Uebertragungszustaende gesichert. Der Master bleibt empfangsbereit und wird energetisch getrennt dimensioniert. Vor Einsatzfreigabe sind eine rechnerische Energiebilanz und ein praktischer Laufzeitnachweis fuer das Einjahresziel erforderlich. | LH-F-002, LH-NF-007, LH-NF-010 |
| PH-T-034 | Plausibilitaetsgrenzen werden je Sensorfeld aus dem Datenblatt der tatsaechlich eingesetzten Sensorversion als versionierte Konfigurations- oder Testwerte gepflegt. Die implementierte Konfiguration `plausibility_limits` akzeptiert je bekanntem Messfeld ein numerisches `min` und `max`. Werte ausserhalb der Grenzen werden nicht verworfen, sondern gespeichert und mit `MEASUREMENT_IMPLAUSIBLE` markiert; fehlende Werte bleiben `NA`. Konkrete Einsatzgrenzen bleiben bis zur Sensorbestaetigung offen. | LH-F-004, LH-F-032, LH-NF-003 |

## 12. Test- Und Abnahmekonzept

### 12.1 Teststufen

| Stufe | Inhalt |
|---|---|
| Komponententest | Codec, Validierung, Sequenzlogik, Dateinamensbildung und Fehlerstatus ohne Funkhardware |
| Hardwaretest | Sensoren, SD, SX1262, Antenne und Pinbelegung |
| Integrationstest Slave | Messung, gemeinsames Datenobjekt, lokale Speicherung und Senden |
| Integrationstest Master | Empfang, Validierung, Zeit und zentrale Speicherung |
| Systemtest | durchgaengiger Ablauf mit mindestens zwei realen Geraeten |
| Fehlerfalltest | fehlende Sensoren, SD-Fehler, Funkunterbrechung, Neustarts und ungueltige Pakete |
| Dauer- und Reichweitentest | Messrhythmus, Speicherwachstum, Stabilitaet und Funkabdeckung |
| Master-Zuordnungstest | Slave verwendet ausschliesslich die konfigurierte `master_id`; eine Bestaetigung mit anderer Master-ID wird abgelehnt |
| fachliche Abnahme | freigegebene Szenarien aus dem Lastenheft |

### 12.2 Bisheriger Voruntersuchungsnachweis

Am 11.08.2026 wurden zwei SX1262-Module mit CircuitPython initialisiert. Insgesamt wurden 21 vollstaendige bidirektionale PING-/PONG-Folgen beidseitig dokumentiert. Dieser Nachweis deckt nur den isolierten Transport ab.

Am 20.08.2026 wurde der konsolidierte Stand auf einem als Master `M01` konfigurierten Raspberry Pi Pico 2 W mit CircuitPython 10.2.1 gestartet. `/config.json`, OLED, SD-Karte und SX1262 wurden erfolgreich initialisiert; der Master erreichte die Empfangsschleife und durchlief mindestens einen vollstaendigen Empfangs-Timeout ohne Laufzeitfehler.

Am 21.08.2026 wurde der produktive Ablauf mit Slave `C01` und Master `M01` auf zwei realen Pico-Geraeten getestet. Die Sequenzen 5 bis 16 wurden in zwoelf aufeinanderfolgenden 15-Minuten-Intervallen uebertragen und zentral gespeichert. Nach `ACK missing for sequence 21` wurde Sequenz 21 spaeter erfolgreich uebertragen und auf der Master-SD genau einmal gespeichert; Sequenz 22 wurde anschliessend bestaetigt. Damit sind Wiederholung nach fehlendem ACK und Duplikatvermeidung fuer diesen Fehlerfall nachgewiesen.

Ein kontrollierter Slave-Neustart bestaetigte den Wiederanlauf von Sequenzverwaltung, Uebertragung, Master-Speicherung und ACK. Die Slave-Zeit wurde dabei zurueckgesetzt; dies ist nach der aktuellen Anforderung unkritisch, da die chronologische Ordnung ueber Slave-ID und persistente Sequenznummer erfolgt. Der Nachweis ist in `docs/Testprotokoll_Systemintegration_2026-08-21.md` dokumentiert.

Auf dem Entwicklungsrechner wurden 52 Unit-Tests fuer Architektur- und Adaptervertraege, Abhaengigkeitsrichtung, Composition Root, Fehlerbehandlung, Codec-Rundlauf, Speichern vor Senden, FIFO-Abbruch nach fehlendem ACK, Speichern vor ACK, Duplikat-ACK sowie Persistenz und Rekonstruktion des SD-Zustands erfolgreich ausgefuehrt. Diese Tests sichern die hardwareunabhaengige Prototyplogik ab.

Die bisherigen Hardware-Systemtests verwenden noch das fruehere 18-Felder-Datenpaket und das fuenffeldrige ACK. Das routingfaehige V1-Datenpaket mit 22 Feldern und das neunfeldrige ACK sind seit dem 03.09.2026 implementiert und auf Unit-Ebene getestet. Das elffeldrige Diagnoseereignis und die zentrale Master-Ablage sind auf Unit-Ebene umgesetzt; der Hardwaretest des neuen Funkformats und der Diagnoseereignisse stehen noch aus.

### 12.3 Vorlaeufige Abnahmewerte Und Offene Nachweise

- zulaessige Abweichung des 15-Minuten-Messrhythmus: vorlaeufig hoechstens plus oder minus 30 Sekunden,
- Dauerlauf: zunaechst 24 Stunden, vor Einsatzfreigabe mindestens sieben Tage,
- Mehrgeraetetest: mindestens zwei reale Slaves und zusaetzlich zehn simulierte Slaves,
- erforderliche Funkreichweite und Hindernisse,
- erlaubter Paketverlust,
- vorlaeufiger ACK-Timeout von drei Sekunden unter realistischen Funkbedingungen bestaetigen,
- rechnerischer und praktischer Nachweis der einjaehrigen Speicherkapazitaet einschliesslich Sicherheitsreserve,
- Plausibilitaetsgrenzen aus den Datenblaettern der tatsaechlich eingesetzten Sensorversionen ableiten und versionieren,
- rechnerische Energiebilanz und praktischer Laufzeitnachweis fuer das Einjahresziel.

## 13. Rueckverfolgbarkeit

| Lastenheft | Pflichtenheft / Use Case | Vorgesehener Nachweis |
|---|---|---|
| LH-F-001 bis LH-F-004 | UC-02, PH-T-002 bis PH-T-004 | Mess- und Sensorfehler-Test |
| LH-F-010 bis LH-F-012, LH-NF-010 | UC-03, UC-09, UC-13, UC-15, PH-T-005, PH-T-016, PH-T-019, PH-T-022, PH-T-029 | Kapazitaets-, SD-, Neustart- und Schreibfehlertest |
| LH-F-020 bis LH-F-023, LH-F-025 | UC-04, UC-07, UC-09, UC-11 bis UC-13, UC-15, PH-T-006 bis PH-T-008, PH-T-017, PH-T-019, PH-T-020 | LoRa-, ACK-, Neustart-, Speicherfehler- und Timeout-Test |
| LH-F-024 | nicht Bestandteil der Kernumsetzung | bei Aufnahme der Kann-Erweiterung neue Spezifikation und Mesh-Testkonzept erforderlich |
| LH-F-030 bis LH-F-035 | UC-05, UC-06, UC-10, UC-12, UC-14, PH-T-007, PH-T-009 bis PH-T-011, PH-T-021, PH-T-027 | Master- und Mehrgeraetetest |
| LH-F-040 bis LH-F-043 | UC-01, UC-08, PH-T-012 | Konfigurations- und Datenentnahmetest |
| LH-NF-001 bis LH-NF-004 | Zustandsmodelle und Fehlerbehandlung | Offline-, Fehlerfall- und Dauerlauftest |
| LH-NF-005 bis LH-NF-008 | Komponentenstruktur, PH-T-013 | Review, reproduzierbarer Neuaufbau |
| LH-NF-009 | Funkkonfiguration, PH-T-014 | dokumentierte fachliche/regulatorische Freigabe |

## 14. Geplante Umsetzungsreihenfolge Nach Freigabe

1. freigegebene Anforderungen und Rollen in eine Traceability-Matrix uebernehmen,
2. Datenformat und Konfiguration finalisieren,
3. Codec und Validierung hardwareunabhaengig implementieren und testen,
4. bestehenden Slave-Messcode in klar getrennte Verantwortungsbereiche ueberfuehren,
5. lokale Speicherung mit ID, Sequenz und Status implementieren,
6. LoRa-Transport in den Slave integrieren,
7. Master-Empfang und Validierung implementieren,
8. persistente Sequenzordnung und zentrale Speicherung implementieren,
9. bestaetigte ACK-Semantik und FIFO-Wiederholung integrieren sowie ACK-Timeout technisch validieren,
10. Fehler-, Mehrgeraete-, Reichweiten- und Dauerlauftests durchfuehren,
11. Betriebsdokumentation und Paper vervollstaendigen.

## 15. Offene Technische Entscheidungen

| ID | Entscheidung | Abhaengigkeit |
|---|---|---|
| PO-01 | Konfigurationsformat, Ablage und Aenderungsablauf | entschieden am 24.08.2026: lokale `/config.json`, versionierte `config.example.json` als Vorlage, Bearbeitung durch Benutzer nach Anleitung, Validierung beim Start und Wirksamkeit nach Neustart; keine zentrale Verteilung |
| PO-02 | Modul- und Dateistruktur innerhalb des gemeinsamen Repository | hexagonale Struktur mit `domain/`, `application/`, `ports/`, `adapters/` und `code.py` als Composition Root umgesetzt; konsolidierter Master-Start am 20.08.2026 getestet |
| PO-03 | verbindliches Datenformat V1 | entschieden am 24.08.2026: routingfaehiger 22-Felder-Datenkopf, neunfeldriges ACK, achtfeldrige `Q`-/`R`-Sequenzabfrage, 160-Byte-Grenze, `NA`, festgelegte Statusbits, elffeldriges Diagnoseereignis und zentrale Master-Diagnose; Datenpaket, ACK und Sequenzabfrage implementiert und per Unit-Test geprueft, Diagnose und Hardwaretest offen |
| PO-04 | technische Ablage oder Rekonstruktion von Sequenzstand und ausstehenden Datensaetzen | lokale Rekonstruktion im bisherigen Speicherformat getestet; bei Start ohne lesbare Slave-SD wird die naechste freie Sequenz ueber `Q`/`R` vom Master bezogen; Master-Neustart, aufgelaufene Datensaetze, `Q`/`R` und neues V1-Dateischema bleiben zu testen |
| PO-05 | ACK-Format und Timeout | vorlaeufig drei Sekunden; FIFO-Reihenfolge, Abbruch beim ersten fehlenden ACK und erneuter Versuch im naechsten 15-Minuten-Zyklus festgelegt; Hardwarevalidierung offen |
| PO-06 | chronologische Ordnung und Verhalten bei ungueltiger Zeit | entschieden am 24.08.2026: Slave-ID und persistente Sequenznummer bestimmen die Reihenfolge; ungueltige Zeit blockiert Messung, Uebertragung und Speicherung nicht |
| PO-07 | Dateiaufteilung pro Master beziehungsweise Slave | entschieden am 24.08.2026: ein Ordner je Geraet und Messdateien in Bloecken zu 3.000 Sequenznummern; keine Abhaengigkeit von Kalenderzeit |
| PO-08 | Verhalten ohne Slave-SD | entschieden am 24.08.2026: Live-Uebertragung fortsetzen und fehlendes lokales Backup im Datensatzstatus kennzeichnen |
| PO-09 | konkrete Fehlerantwort bei fehlender Master-SD | kein Erfolgs-ACK fachlich bestaetigt |
| PO-10 | endgueltige Pinbelegung der optionalen Bodensensoren | nur bei Entscheidung zur Umsetzung erforderlich |
| PO-11 | Energie- und Schlafstrategie | entschieden am 01.09.2026: autonome Slave-Messung, kein dauerhafter Slave-Empfang zwischen Messzyklen, persistenter Zustand vor Energiesparphase; konkrete Pico-Schlaftechnik, Energiebilanz und Einjahresnachweis offen |
| PO-12 | Einsatzort-spezifische Funkparameter | Entwicklungswerte festgelegt; konkrete Einsatzwerte bleiben bis Reichweiten- und regulatorischer Pruefung offen |
| PO-13 | Zuordnung eines Slaves zu seinem Master | entschieden am 24.08.2026: feste `master_id` in der Slave-`/config.json`; keine automatische Erkennung und kein Erkennungssignal |
| PO-14 | optionale Mehrsprungkommunikation | V1 ist mit Ursprung, Endziel, naechstem Hop, Hop-Zaehler und Hop-Limit sowie routingfaehigem ACK vorbereitet; Kernsystem bleibt direkte Sternkommunikation, Relay-Implementierung nur bei verbleibender Zeit |
| PO-15 | zentrale Diagnoseablage | entschieden am 24.08.2026: Slaves senden festgelegte `STARTED`-, `ENDED`- und `OCCURRED`-Ereignisse ohne lokale Diagnosedatei; der Master verwaltet den Zustand je Geraet und Ereigniscode und speichert ihn geraeteweise auf seiner vorausgesetzten SD |
| PO-16 | ueberwachte Slaves und Empfangsluecken | entschieden am 01.09.2026: Pflichtfeld `monitored_slaves` mit mindestens einer ID und ohne feste softwareseitige Obergrenze; pro 15-Minuten-Intervall spaeter echter Datensatz oder eindeutig markierte `NO_PACKET`-Lueckenzeile; Implementierung und Hardwaretest offen |
| PO-17 | Plausibilitaetsgrenzen | Vorgehen entschieden am 01.09.2026: Datenblatt-basierte versionierte Grenzen; unplausible Werte speichern und markieren; konkrete Grenzwerte nach Bestaetigung der Sensorversionen offen |

## 16. Freigabevermerk

| Version | Datum | Entscheidung | Person / Rolle | Bemerkung |
|---|---|---|---|---|
| 0.1 | 11.08.2026 | technischer Entwurf erstellt | Immanuel Mauch | Lastenheft und technische Entscheidungen noch nicht freigegeben |
| 0.2 | 20.08.2026 | Prototyp-, Master-Test- und Relay-Arbeitsstand ergaenzt | Immanuel Mauch | weiterhin technischer Entwurf; Slave-Integration und offene Entscheidungen nicht freigegeben |
| 0.3 | 24.08.2026 | Sequenzordnung, optionale Zeitinformation, begrenzte zentrale Master-Diagnose, Weiterbetrieb ohne Slave-SD, lokaler Konfigurationsablauf, feste Master-Zuordnung und sequenzbasierte Dateiaufteilung und routingfaehiges Datenformat V1 und Sequenzabfrage ohne Slave-SD festgelegt | Immanuel Mauch | technischer Entwurf; Lastenheftquelle wurde entsprechend aktualisiert, formale Freigabe bleibt offen |
| 0.4 | 01.09.2026 | ueberwachte Slaves, rollenbezogene Konfigurationsvalidierung und `NO_PACKET`-Lueckenzeilen festgelegt | Immanuel Mauch | technischer Entwurf; Konfigurationsvalidierung umgesetzt und per Unit-Test abgesichert, Lueckenlogik noch nicht implementiert |
| 0.5 | 18.09.2026 | eigene Master-Messung und Weiterverwendung einer gueltigen internen UTC-Uhr ergaenzt | Immanuel Mauch | Erweiterungsauftrag; lokale Tests bestanden, Hardwareabnahme offen |
