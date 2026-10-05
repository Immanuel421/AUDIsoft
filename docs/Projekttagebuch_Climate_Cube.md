# Projekttagebuch AUDI Climate Cube

Projekt: Pflichtpraktikum - Messdatenübertragung und Speicherung für Climate Cubes  
Bearbeiter: Immanuel Mauch  
Beginn: 03.08.2026  
Letzte Aktualisierung: 07.08.2026  
Dokumentstatus: **laufende Arbeitsdokumentation; unbestätigte Punkte sind als Projektinformation, Rechercheergebnis oder vorläufige Arbeitsentscheidung gekennzeichnet**

## Zweck Des Projekttagebuchs

Dieses Projekttagebuch dokumentiert fortlaufend Durchgeführte Arbeiten, gewonnene Erkenntnisse, vorläufige Arbeitsentscheidungen, offene Fragen und die jeweils Nächsten Schritte. Zeitaufwaendige oder unsichere Angaben werden nur eingetragen, wenn sie tatsächlich bekannt sind.

## Beteiligte Und Zuständigkeiten

Die folgende Zuordnung entspricht dem aktuellen Informationsstand:

| Person | Zuständigkeit |
|---|---|
| Herr Schnabel | fachlicher Ansprechpartner für Anforderungen, Hardware und technische Entscheidungen des AUDI-Climate-Cube-Projekts |
| Herr Heym | akademischer Betreuer des Pflichtpraktikums und Ansprechpartner für Hochschulvorgaben sowie die akademische Betreuung |

## 03.08.2026 - Erste Fachliche Rückmeldung Von Herrn Schnabel Ausgewertet

### Durchgeführte Arbeiten

- Rückmeldung von Herrn Schnabel zu den grundlegenden Systemanforderungen ausgewertet.
- Aufgaben von Master- und Slave-ClimateCubes voneinander abgegrenzt.
- Rahmenbedingungen für Kommunikation, Speicherung und Anzahl der Geräte festgehalten.
- Hinweis auf eine moegliche Weiterleitung über andere Slaves als offenen Architekturpunkt aufgenommen.
- Benötigte Dateninhalte und die Zeitreferenz betrachtet.

### Ergebnisse Und Erkenntnisse

#### Aus Der Rückmeldung Von Herrn Schnabel Bestätigt

- Jeder Slave soll alle 15 Minuten Messdaten erfassen.
- Die Slaves senden die Daten per LoRa Peer-to-Peer an einen Master-ClimateCube.
- Der Master speichert die Daten aller Slaves zentral auf seiner SD-Karte.
- Jeder Slave speichert seine eigenen Daten zusaetzlich auf einer lokalen SD-Karte als Backup.
- Ein Master soll ungefaehr zehn Slaves verwalten koennen.
- LoRaWAN ist nicht vorgesehen, da die Climate Cubes auch ohne vorhandene Infrastruktur, beispielsweise in Peru, eingesetzt werden sollen.
- Eine Weiterleitung über andere Slaves beziehungsweise ein Mesh wurde als moegliche Erweiterung genannt.

#### Weitere Projektinformationen Und vorläufige Schlussfolgerungen

- für die Auswertung werden alle relevanten Sensorwerte sowie ein Zeitbezug benoetigt.
- Ein Batteriewert ist aktuell weniger wichtig und daher kein Pflichtfeld.
- Als Zielhardware wird ein Raspberry Pi Pico beziehungsweise ein Pico-kompatibles Board angenommen.
- Die Slaves besitzen nach aktuellem Stand keine RTC.

### vorläufige Arbeitsentscheidungen

Die folgenden Punkte dienen als aktuelle Planungsgrundlage und sind fachlich noch mit Herrn Schnabel abzustimmen.

- Als vorläufige Basis wird eine direkte Sternstruktur geplant: Slaves kommunizieren unmittelbar mit dem Master.
- Mesh wird vorerst als moegliche Erweiterung betrachtet. Ob es erforderlich ist, wird mit Herrn Schnabel abgestimmt und nach Reichweitentests bewertet.
- Der Master soll beim Empfangen oder Schreiben einen Zeitstempel ergaenzen.
- Eine RTC wird vorerst nicht fest eingeplant. Die Master-Zeit soll beim Start eingestellt und anschliessend als Referenz verwendet werden.
- Slave-ID und Sequenznummer sollen später eine eindeutige Zuordnung sowie das Erkennen fehlender oder doppelter Datensätze ermoeglichen.

### Offene Punkte

- Genaue Hardware und Pico-Variante prüfen.
- Reale Sensoren und Messwerte feststellen.
- Pinbelegung und freie GPIOs prüfen.
- Methode zum Einstellen der Master-Zeit festlegen.
- Klären, ob ACK und Wiederholungsversuche verpflichtend sind.
- Reichweite testen und danach über Mesh entscheiden.

### Nächste Schritte

- Anforderungen in einem strukturierten Anforderungsdokument festhalten.
- Projektplan für das AUDI-Climate-Cube-Projekt erstellen.
- Hardwaretermin am 11.08.2026 vorbereiten.

## 04.08.2026 - Planung, Hardware-Recherche Und Bestandsanalyse

### Durchgeführte Arbeiten

- Projektplan für das AUDI-Climate-Cube-Projekt erstellt und später an den vorhandenen Entwicklungsstand angepasst.
- Vertragszeitraum des Pflichtpraktikums geprüft und den Projektplan auf den Zeitraum 03.08.2026 bis 06.12.2026 korrigiert.
- Anforderungsdokument für das AUDI-Climate-Cube-Projekt erstellt und erweitert.
- Vorgesehenes LoRa-Modul recherchiert: Waveshare Pico-LoRa-SX1262-868M mit SX1262-Funkchip.
- Waveshare-Wiki und Beispielprojekte hinsichtlich Pinbelegung und Peer-to-Peer-Kommunikation geprüft.
- C/C++-Ping-Pong-Beispiel im Repository `CodeUnit10X/lora_basics_modem_ports` gefunden und als Nachweis für direkte LoRa-Kommunikation bewertet.
- Python-Unterstützung für den SX1262 untersucht.
- Bibliothek `micropySX126X` als moeglichen Treiber für MicroPython und CircuitPython identifiziert.
- Python-Ping-Pong-, Sende- und Empfangsbeispiele der Bibliothek geprüft.
- Bestehenden Ordner `Audi Climate Cube/lib/` und den vorhandenen `code.py` analysiert.
- Entwicklungsmodell von CircuitPython geklaert: kein separates CMake- oder Pico-SDK-Projekt und kein klassischer Kompiliervorgang für `code.py` erforderlich.
- Sinnvolle VS-Code-Unterstützung für CircuitPython betrachtet.

### Ergebnisse Und Erkenntnisse

Die folgenden Punkte stammen aus bereitgestellten Projektinformationen, Hersteller-/Bibliotheksrecherche und der Analyse des vorhandenen Codes. Aussagen zur tatsaechlichen Funktion auf der Zielhardware bleiben bis zum Hardwaretest vorläufig.

- Der Praktikumszeitraum vom 03.08.2026 bis 06.12.2026 ist durch den Vertrag Bestätigt und umfasst 18 Wochen.
- Programmiersprache ist Python.
- Der vorhandene Climate-Cube-Prototyp nutzt CircuitPython und bringt bereits die Benötigten Adafruit-Bibliotheken als `.mpy`-Dateien mit.
- Das Waveshare-Modul nutzt für LoRa folgende Pins:

| Signal | Pico-GPIO |
|---|---|
| SCK / CLK | GP10 |
| MOSI | GP11 |
| MISO | GP12 |
| CS / NSS | GP3 |
| DIO1 / IRQ | GP20 |
| RESET | GP15 |
| BUSY | GP2 |

- `micropySX126X` unterstuetzt direktes Senden und Empfangen ohne LoRaWAN und enthaelt ein Python-Ping-Pong-Beispiel mit dieser Pinbelegung.
- Die Beispielkonfiguration verwendet 923 MHz und darf für das vorhandene 868-MHz-Modul nicht unveraendert übernommen werden.
- Die Bibliothek ist ein Drittanbieterprojekt und muss deshalb frueh mit zwei echten Picos getestet werden.
- Bei Speicherproblemen koennen Bibliotheksdateien als `.mpy` kompiliert werden.
- Der vorhandene `code.py` enthaelt bereits:
  - SEN66-Messung für Temperatur, Luftfeuchtigkeit, CO2, Feinstaub, VOC und NOx,
  - analoge Bodenfeuchtemessung,
  - DS18B20-Bodentemperatur,
  - OLED-Anzeige,
  - lokale CSV-Speicherung auf SD-Karte,
  - einen grundsaetzlichen 15-Minuten-Messablauf,
  - einfache Fehlerbehandlung.
- Noch nicht enthalten sind insbesondere LoRa-Kommunikation, Master-Software, Slave-ID, Sequenznummer, ACK/Wiederholung und zentrale Speicherung.
- Der aktuelle Messrhythmus kann sich durch die SEN66-Aufwaermzeit verschieben, weil das Nächste Intervall nach Abschluss der Messung beginnt.
- Bei einem Ausfall des SEN66 wird aktuell kein Datensatz mit den noch vorhandenen Bodenwerten gespeichert.
- Die SD- und Haupt-LoRa-Pins kollidieren nach aktuellem Stand nicht.
- Es besteht jedoch ein moeglicher Konflikt auf GP26: Der vorhandene Code nutzt GP26 für die Bodenfeuchte, während das Waveshare-Modul GP26 als `BAT_AD` verwendet.

### vorläufige Arbeitsentscheidungen

Die folgenden Punkte bilden den aktuellen Arbeitsstand ab und werden bei neuen Hardwareinformationen oder fachlichen Rückmeldungen von Herrn Schnabel angepasst.

- Das vorhandene CircuitPython-Projekt wird erweitert; es wird kein neues Pico-Projekt angelegt.
- CircuitPython bleibt die bevorzugte Python-Laufzeit, solange der SX1262-Treiber damit auf der realen Hardware funktioniert.
- Vor der Integration in den Climate-Cube-Code wird ein isolierter Ping-Pong-Test mit zwei Picos durchgeführt.
- Vorhandene Mess-, Display- und SD-Funktionen werden zuerst verifiziert und stabilisiert, nicht neu entwickelt.
- Der Projektplan wurde auf das AUDI-Climate-Cube-Projekt begrenzt. Die letzten beiden Praktikumswochen sind für Systemtest, Dauerlauf, Fehlerbehebung, Dokumentation und Demo vorgesehen.

### Erstellte Und Aktualisierte Dokumente

- `Anforderungen_AUDI_Climate_Cube.md`
- `Projektplan_AUDI_Climate_Cube.md`
- `Projekttagebuch_Climate_Cube.md`

### Offene Punkte

- Reale Hardware und Verkabelung am 11.08.2026 mit dem Code abgleichen.
- CircuitPython-Version aus `boot_out.txt` feststellen.
- Versionen der vorhandenen `.mpy`-Bibliotheken prüfen.
- GP26-Konflikt untersuchen und gegebenenfalls Bodenfeuchte auf einen freien ADC-Pin verschieben.
- `micropySX126X` unter CircuitPython auf zwei Picos testen.
- Geeignete und regulatorisch zulaessige 868-MHz-Funkparameter festlegen.
- Genaue Methode zur Einstellung der Master-Zeit bestimmen.
- ACK- und Wiederholungsstrategie festlegen.

### Nächste Schritte

- Checkliste für den Hardwaretermin am 11.08.2026 erstellen.
- Vorhandenen `code.py` auf der echten Hardware ausführen und Sensor-, Display- sowie SD-Funktionen prüfen.
- Danach `micropySX126X` vorbereiten und einen isolierten 868-MHz-Ping-Pong-Test durchfuehren.
- Datenformat Version 1 mit Slave-ID, Sequenznummer, Messwerten und Paketversion definieren.

## 05.08.2026 - SX1262-Bibliothek Und Ping-Pong-Test Vorbereitet

### Durchgeführte Arbeiten

- Die drei Kerndateien `_sx126x.py`, `sx126x.py` und `sx1262.py` aus dem Projekt `ehong-tl/micropySX126X` in `Audi Climate Cube/lib/` aufgenommen.
- Dateigrößen und interne Importabhängigkeiten geprüft.
- Alle drei Dateien mit `py_compile` auf Syntaxfehler geprüft.
- Die offiziellen Ping-Pong-Beispiele der Bibliothek analysiert und mit dem geplanten Waveshare-Aufbau verglichen.
- Die Beispielkonfiguration von 923 MHz und Integer-Pins auf einen vorlaeufigen 868,1-MHz-Test mit CircuitPython-`board.GP`-Pins angepasst.
- Fuer den ersten Funktionstest bewusst den blockierenden Bibliotheksmodus gewaehlt, um Sender und Empfaenger ohne zusaetzliche Callback- und Interruptlogik getrennt pruefen zu koennen.
- Einen isolierten Sender (`lora_sender_test.py`) und Empfaenger (`lora_receiver_test.py`) fuer einen nummerierten Ping-Pong-Test erstellt.
- Eine Testanleitung mit Pinbelegung, Durchfuehrung, Erfolgskriterium und Sicherheitshinweis erstellt.
- Den MIT-Lizenztext der verwendeten Drittanbieterbibliothek dem Testordner und dem Bibliotheksordner beigefuegt.
- Versucht, Herrn Schnabel ueber die genannte Hochschul-E-Mail-Adresse zum GitLab-Projekt einzuladen. GitLab hat die Adresse als ungueltig abgelehnt; Rueckfrage nach Benutzername beziehungsweise hinterlegter Adresse versendet.
- Eine zentrale `README.md` fuer das AUDI-Climate-Cube-Softwareprojekt erstellt. Darin sind Projektziel, aktueller Funktionsumfang, fehlende Funktionen, Hardware, vorlaeufige Pinbelegung, Softwareumgebung, Projektstruktur, LoRa-Test, offene Punkte und naechste Entwicklungsschritte dokumentiert.

### Ergebnisse Und Erkenntnisse

- Die Dateien bilden gemeinsam den benötigten SX1262-Treiber und enthalten einen eigenen CircuitPython-Pfad mit `busio` und `digitalio`.
- Die Bibliotheksdateien sind syntaktisch gültig.
- Sender und Empfaenger verwenden dieselbe vorlaeufige Konfiguration mit 868,1 MHz, 125 kHz Bandbreite, Spreading Factor 7, Coding Rate 4/5 und 10 dBm Sendeleistung.
- Der Test verwendet den blockierenden Bibliotheksmodus und prueft nummerierte `PING`-/`PONG`-Antworten sowie RSSI und SNR.
- Sender und Empfaenger liegen getrennt vom produktiven `code.py` unter `tests/lora_ping_pong/`; der vorhandene Messcode wurde nicht veraendert.
- Die neue README bildet einen zentralen Einstiegspunkt in das Softwareprojekt und verweist auf Anforderungsdokument, Projektplan und Projekttagebuch.
- Als Erfolgskriterium wurden mehrere aufeinanderfolgende, korrekt nummerierte `PING`-/`PONG`-Antworten festgelegt.
- Die Testprogramme sind syntaktisch gueltig.
- Die tatsaechliche Kompatibilitaet mit der installierten CircuitPython-Version und dem Waveshare-Modul ist erst nach einem Hardwaretest bestaetigt.

### Probleme Und Offene Punkte

- Zwei reale Picos mit Waveshare-Modulen stehen fuer die Ausfuehrung noch nicht zur Verfuegung.
- Pinbelegung, installierte CircuitPython-Version und Bibliothekskompatibilitaet muessen am 11.08.2026 auf der Hardware bestaetigt werden.
- Die vorlaeufigen Funkparameter sind vor laengeren Tests fachlich und regulatorisch zu bestaetigen.
- Die GitLab-Einladung fuer Herrn Schnabel ist bis zur Rueckmeldung zum korrekten Konto offen.

### Nächste Schritte

- CircuitPython-Version über `boot_out.txt` feststellen.
- Vorlaeufige Funkparameter vor dem Test fachlich und regulatorisch pruefen.
- Vorbereitete Programme in einem isolierten Ping-Pong-Test mit zwei Picos ausfuehren.
- Erst nach erfolgreichem Test in den vorhandenen Messcode integrieren.

## 06.08.2026 - Testprotokoll Fuer LoRa-Ping-Pong Vorbereitet

### Durchgeführte Arbeiten

- Ein ausfuellbares Testprotokoll fuer den isolierten SX1262-Ping-Pong-Test erstellt.
- Felder fuer Testdatum, Testort, Testperson, Git-Commit, Pico-Modell, CircuitPython-Version, LoRa-Modul, Antenne und Stromversorgung vorgesehen.
- Die vorlaeufige Pinbelegung und Funkkonfiguration aus den Testprogrammen in das Protokoll uebernommen.
- Acht Testfaelle fuer Initialisierung, einzelne und wiederholte Ping-Pong-Uebertragung, Timeout-Verhalten, Neustarts und Abstandstests definiert.
- Tabellen fuer Messreihen, Paketverluste, RSSI, SNR, Fehler, Abweichungen und Nachweise vorbereitet.
- Vorlaeufige technische Erfolgskriterien fuer den ersten Funktionstest dokumentiert.
- Das Testprotokoll in der Testanleitung und in der zentralen Projekt-README verlinkt.
- Das von VS Code verwendete lokale Git-Repository ermittelt.
- Branch, Remote, letzte Commits, Arbeitsbaum und den heutigen Dateistand geprueft.
- Vorhandene Git-Konfigurationsdateien wie `.gitignore` und `.gitattributes` geprueft.
- Eine projektbezogene `.gitignore` fuer Python-Caches, virtuelle Umgebungen, lokale Umgebungsdateien sowie Editor- und Betriebssystemartefakte erstellt.

### Ergebnisse Und Erkenntnisse

- Der geplante Hardwaretest kann jetzt einheitlich und nachvollziehbar dokumentiert werden.
- Testaufbau, Softwarestand, Parameter und Messergebnisse werden im selben Dokument erfasst.
- Die Erfolgskriterien sind vorlaeufige technische Arbeitskriterien und keine bereits fachlich freigegebenen Abnahmekriterien.
- Am 06.08.2026 wurde noch kein Funk- oder Hardwaretest durchgefuehrt; entsprechend wurden keine Messergebnisse eingetragen.
- Das AUDI-Projekt ist ein Git-Repository. Der Branch `main` verfolgt `origin/main`.
- Der Remote `origin` verweist auf das AUDI-Climate-Cube-Projekt im GitLab der Hochschule.
- Vor der abschliessenden Dokumentationskorrektur war das Projekttagebuch geaendert und das neue Testprotokoll noch unversioniert.
- Das Testprotokoll und der aktualisierte Tagebucheintrag entsprechen dem heute vorbereiteten Stand.
- Die fehlenden Verweise auf das Testprotokoll wurden in der Projekt-README und in der Ping-Pong-Testanleitung ergaenzt.
- CircuitPython-Bibliotheken (`.mpy`), die Pico-Firmware (`.uf2`) und Testnachweise werden von der `.gitignore` nicht ausgeschlossen und bleiben versionierbar.

### Probleme Und Offene Punkte

- Die reale Pinbelegung, Pico-Variante und installierte CircuitPython-Version muessen an der Hardware bestaetigt werden.
- Die vorbereiteten Funkparameter muessen vor der Durchfuehrung nochmals geprueft und gegebenenfalls abgestimmt werden.
- Sender, Empfaenger und passende Antennen stehen fuer die praktische Ausfuehrung noch nicht zur Verfuegung.
- Das neue Testprotokoll und die heutigen Dokumentationsaenderungen muessen noch gemeinsam committed und anschliessend gepusht werden.


### Nächste Schritte

- Beim Hardwaretermin die Geraete- und Firmwaredaten in das Testprotokoll eintragen.
- Sicherheitspruefung und Pinbelegung vor dem Einschalten abarbeiten.
- Die Testfaelle PP-01 bis PP-08 ausfuehren und serielle Ausgaben sowie Fotos als Nachweise sichern.
- Ergebnisse bewerten und Abweichungen als Grundlage fuer die Integration in den Messcode festhalten.
- Den abschliessenden Git-Diff pruefen und die heutigen Aenderungen gemeinsam committen.
- Den Commit anschliessend zu `origin/main` pushen.

## 07.08.2026 - Hardware-Testablauf Und Datenformat-V1-Entwurf Vorbereitet

### Durchgeführte Arbeiten

- Den vorhandenen `code.py`, die dokumentierte Pinbelegung und die offenen Hardwarefragen fuer den Termin am 11.08.2026 abgeglichen.
- Einen direkt abarbeitbaren Testablauf fuer den Hardwaretermin erstellt.
- Die Pruefreihenfolge vom Sichern des Ausgangsstands ueber Hardware-, Firmware-, Pin- und Funktionstests bis zur Abschlussdokumentation festgelegt.
- Prueftabellen fuer Pico, SX1262, Sensoren, Display, SD-Karte, Messwerte, Pinbelegung und offene Entscheidungen vorbereitet.
- Sicherheits- und Abbruchregeln fuer Verkabelung, GP26-Konflikt, Spannungsversorgung und LoRa-Sendebetrieb aufgenommen.
- Den isolierten Ping-Pong-Test als optionalen, nachgelagerten Schritt mit Verweis auf das eigene Testprotokoll eingeordnet.
- Den Testablauf in der zentralen Projekt-README verlinkt.
- Die im vorhandenen `code.py` erzeugten elf Messwerte und die bisherigen Anforderungen an Slave-ID, Sequenznummer, Master-Zeitstempel und Fehlerstatus abgeglichen.
- Einen separaten technischen Entwurf fuer Datenformat Version 1 erstellt.
- Eine feste ASCII-Funkdarstellung mit Formatversion, Nachrichtentyp, Slave-ID, Sequenznummer, Laufzeit, elf Messwerten und Statusflags definiert.
- Skalierungsregeln, Kennzeichnung fehlender Werte, Statusbits und Validierungsreihenfolge fuer den Master vorgeschlagen.
- Lesbare CSV-Strukturen fuer lokale Slave-Daten und zentral gespeicherte Master-Daten entworfen.
- Eine optionale ACK-Nachricht sowie offene Entscheidungen zu Neustarts, Duplikaten und Wiederholungen dokumentiert.
- Den V1-Entwurf in README und Anforderungen verlinkt.

### Ergebnisse Und Erkenntnisse

- Der Hardwaretermin kann nun in einer festen und nachvollziehbaren Reihenfolge durchgefuehrt werden.
- Der unveraenderte vorhandene Climate-Cube-Code wird zuerst gesichert und geprueft, bevor Firmware, Bibliotheken oder Verkabelung veraendert werden.
- Bestandspruefung und LoRa-Test sind klar getrennt. Der LoRa-Test erfolgt nur bei bestaetigter Pinbelegung, passenden Antennen, zwei vollstaendigen Testgeraeten und abgestimmten Funkparametern.
- Fuer serielle Ausgaben, Fotos, CSV-Dateien und Firmwareinformationen sind einheitliche Nachweise und Dateinamen vorgesehen.
- Am 07.08.2026 wurde noch kein Hardwaretest durchgefuehrt und es wurden keine Hardwarefunktionen als bestaetigt eingetragen.
- Lokale CSV-Zeile und Funkpaket sollen aus demselben logischen Messdatensatz erzeugt werden, damit keine voneinander abweichenden Werte entstehen.
- Der Slave sendet keinen Kalenderzeitstempel; der Master ergaenzt Zeitstempel, RSSI, SNR und Empfangsstatus.
- Das vollstaendige Beispielpaket umfasst 59 ASCII-Bytes und liegt damit unter dem vorlaeufigen Ziel von 120 Bytes.
- Der Entwurf ist noch nicht implementiert oder fachlich freigegeben und legt offene Punkte nicht als bestaetigte Anforderungen fest.

### Probleme Und Offene Punkte

- Pico-Variante, CircuitPython-Version, reale Verkabelung und freie GPIOs koennen erst an der Hardware bestaetigt werden.
- Der Konflikt zwischen Bodenfeuchtesensor und `BAT_AD` auf GP26 bleibt bis zur Sichtung der realen Verschaltung offen.
- Ob am 11.08. bereits zwei vollstaendige LoRa-Testgeraete und ausreichend Zeit fuer den Ping-Pong-Test verfuegbar sind, ist noch offen.
- Funkparameter und regulatorische Rahmenbedingungen muessen vor einem Sendetest ausreichend geklaert sein.
- Messwertumfang, Einheiten, Slave-ID-Schema, Sequenzverhalten nach Neustart, Umgang mit unvollstaendigen Messungen und ACK-Strategie sind noch abzustimmen.
- Zeitquelle, Zeitzone und Einstellverfahren des Masters sind weiterhin offen.

### Nächste Schritte

- Den Testablauf zum Termin bereithalten und zuerst den unveraenderten Ausgangsstand sichern.
- Alle bestaetigten Hardwaredaten, Abweichungen und Nachweise direkt im Ablauf dokumentieren.
- Nach dem Termin Anforderungen, README, Pinbelegung und Projekttagebuch mit den tatsaechlichen Ergebnissen aktualisieren.
- Sensorliste und Einheiten am 11.08. mit dem V1-Entwurf abgleichen.
- Serialisierung und Parser nach der Abstimmung unabhaengig von der Funkhardware implementieren und mit gueltigen, fehlenden und ungueltigen Werten testen.
- Den heutigen Dokumentationsstand pruefen, committen und zu GitLab pushen.

## 11.08.2026 - Hardware Geprueft Und LoRa-Ping-Pong Nachgewiesen

### Durchgeführte Arbeiten

- Zwei Geraete einzeln ueber `boot_out.txt` als Raspberry Pi Pico 2 W mit RP2350A und CircuitPython 10.2.1 identifiziert.
- Beide Geraete anhand ihrer unterschiedlichen UIDs eindeutig zugeordnet, ohne die vollstaendigen UIDs im Repository zu dokumentieren.
- Den Inhalt beider `CIRCUITPY`-Laufwerke vor Aenderungen lokal und getrennt gesichert.
- Den vorhandenen Messcode auf beiden Geraeten unveraendert gestartet und die seriellen Ausgaben direkt ueber `/dev/ttyACM0` beziehungsweise `/dev/ttyACM1` erfasst.
- SEN66-Messung und Schreiben einer CSV-Datei auf SD bei beiden Geraeten geprueft.
- Die vorbereiteten SX1262-Treiber auf ihre CircuitPython-Pfade mit `busio` und `digitalio` kontrolliert.
- Geraet 1 als LoRa-Empfaenger und Geraet 2 als LoRa-Sender eingerichtet.
- Die Initialisierung beider SX1262-Module sowie nummerierte PING-/PONG-Uebertragungen bei kurzem Tischabstand aufgezeichnet.
- Einen Senderneustart bei weiterlaufendem Empfaenger durchgefuehrt und die danach fortgesetzte Kommunikation bestaetigt.
- Nach Testende auf beiden Geraeten die jeweilige urspruengliche `code.py` aus der UID-bezogenen Sicherung wiederhergestellt und byteweise verglichen.
- Serielle Teilaufzeichnungen bereinigt unter `tests/lora_ping_pong/results/2026-08-11/` abgelegt und das Testprotokoll ausgefuellt.

### Ergebnisse Und Erkenntnisse

- Beide Picos verwenden `raspberry_pi_pico2_w` und CircuitPython 10.2.1 vom 13.05.2026.
- SEN66 und SD-Speicherung funktionieren auf beiden getesteten Geraeten grundsaetzlich.
- Bei beiden Geraeten war kein DS18B20 an GP27 erkennbar; nach Aussage zum aktuellen Aufbau war nur der SEN66 als Messsensor angeschlossen.
- Die wiederholte DS18B20-Initialisierung meldet anschliessend `GP27_A1 in Benutzung`. Dies ist ein zusaetzlicher Fehler in der Wiederholungslogik und kein Nachweis fuer zwei angeschlossene Sensoren.
- Beide SX1262-Module initialisierten mit `ERR_NONE`.
- Insgesamt wurden 21 vollstaendige bidirektionale PING-/PONG-Folgen mit passenden Sequenznummern beidseitig dokumentiert.
- In den vollstaendig dokumentierten Folgen trat kein Paketverlust auf. Die beobachteten Werte lagen insgesamt bei etwa -35 bis -14 dBm RSSI und 11,75 bis 13,25 dB SNR.
- Die vorbereitete CircuitPython-Anpassung von `micropySX126X` funktioniert im blockierenden Ping-Pong-Test auf dem Pico 2 W.
- Die produktiven Messprogramme wurden nach dem Funkversuch auf beiden Geraeten erfolgreich wiederhergestellt.

### vorläufige Arbeitsentscheidungen

- Die direkte LoRa-Peer-to-Peer-Kommunikation kann als technisch nachgewiesene Grundlage fuer die weitere Entwicklung verwendet werden.
- Die verwendeten Funkparameter bleiben Testwerte und gelten noch nicht als Freigabe fuer Dauer- oder Feldeinsatz.
- Nicht vorhandene Bodensensoren sollen den uebrigen Messablauf kuenftig ohne erneute Pinreservierung oder irrefuehrende Fehlermeldung weiterlaufen lassen.
- Vollstaendige Hardware-UIDs und lokale Pico-Sicherungen werden nicht in das Git-Repository aufgenommen.

### Probleme Und Offene Punkte

- Der Microsoft Serial Monitor in der VS-Code-Flatpak-Installation zeigte keine Ausgabe. Nach Aufnahme des Benutzers in `dialout` konnten die seriellen Ports direkt auf dem Host gelesen werden.
- In einzelnen seriellen Teilaufzeichnungen fehlte die Senderausgabe, obwohl der Funkverkehr am Empfaenger weiter sichtbar war. Deshalb wurden nur auf beiden Seiten vollstaendig nachgewiesene Paare fuer das Ergebnis gezaehlt.
- Timeout-Verhalten, Empfaengerneustart und Abstandstests wurden noch nicht durchgefuehrt.
- Reale Anschluesse fuer Bodenfeuchte und Bodentemperatur waren durch den Aufbau verdeckt und wurden nicht durch Demontage geprueft.
- Bodentemperatur- und Bodenfeuchtesensoren standen fuer einen Funktionstest nicht zur Verfuegung.
- Funkparameter fuer den spaeteren Einsatz und der Umgang mit GP26 beziehungsweise `BAT_AD` bleiben abzustimmen.

### Nächste Schritte

- Timeout-Test, Empfaengerneustart und Abstandstest nachholen.
- DS18B20-Initialisierung so korrigieren, dass GP27 nach einem erfolglosen Scan nicht erneut fehlerhaft reserviert wird.
- Klaeren, welche Bodensensoren spaeter eingesetzt und auf welche GPIOs sie tatsaechlich gefuehrt werden.
- Funkparameter sowie zulaessige Sendeintervalle und Sendeleistung fuer den vorgesehenen Einsatz abstimmen.
- Das bestaetigte LoRa-Grundgeruest mit Slave-ID, Sequenznummer, Messdatenformat, ACK und Wiederholungsstrategie verbinden.
- Dokumentations- und Testnachweise gemeinsam pruefen, committen und zu GitLab pushen.

## 11.08.2026 - Formales Projektvorgehen Und Abschluss-Paper Eingeplant

### Durchgeführte Arbeiten

- Die neue Vorgabe aufgenommen, das Praktikumsprojekt vor der eigentlichen Implementierung über Lastenheft, Pflichtenheft, Rollen und Anwendungsfälle zu spezifizieren.
- Einen Lastenheft-Entwurf mit Projektzielen, Stakeholdern, Systemrollen, fachlichen Anforderungen, Rahmenbedingungen, Abnahmeszenarien und offenen Entscheidungen erstellt.
- Einen Pflichtenheft-Entwurf mit Systemkomponenten, Rollenfähigkeiten, Anwendungsfällen, technischen Anforderungen, Teststufen und einer Rückverfolgbarkeitsmatrix erstellt.
- Den Projektplan um Freigabepunkte vor der Implementierung erweitert und die Phasen bis zum Vertragsende am 06.12.2026 neu eingeordnet.
- Die vorhandene PDF `ISEP_Gruppe5_LudoGame2.0_Dokumentation.pdf` aus dem lokalen Sicherungsordner als strukturelles Beispiel untersucht.
- Eine auf das Climate-Cube-Projekt zugeschnittene Gliederung für das spätere Abschluss-Paper sowie einen Plan für laufend zu sammelnde Nachweise erstellt.
- Die Projekt-README auf den verifizierten Hardwarestand, den erfolgreichen LoRa-Vorversuch und den neuen Projektablauf aktualisiert.

### Ergebnisse Und Erkenntnisse

- Lastenheft und Pflichtenheft sind getrennte Arbeitsdokumente: Das Lastenheft beschreibt den fachlichen Bedarf, das Pflichtenheft die geplante technische Erfüllung.
- Die Systemrollen Slave, Master, Bediener beziehungsweise Installateur und Datenauswerter sind als Entwurf beschrieben. Ihre genaue Ausgestaltung muss noch abgestimmt werden.
- Die bisherige Anforderungsdatei bleibt Informations- und Arbeitsgrundlage, ersetzt aber nicht die formale Trennung von Lasten- und Pflichtenheft.
- Hardware- und Ping-Pong-Test werden als Bestandsaufnahme und technische Voruntersuchung eingeordnet. Sie stellen keine Freigabe der späteren Produktarchitektur dar.
- Die untersuchte Beispiel-PDF enthält unter anderem Abstract, Projektorganisation, Anforderungen, Architektur, Implementierung, Tests, Projektverlauf, Fazit und Anhänge. Diese Gliederungsprinzipien wurden projektspezifisch übernommen, nicht deren Inhalte.
- Das Paper soll während des Projekts abschnittsweise gepflegt werden, damit Entscheidungen, Messdaten und Abweichungen später belegt werden können.
- Als fachliche Konkretisierung wurde bestätigt, dass die LoRa-Übertragung der Messdaten im 15-Minuten-Takt erfolgen soll. Die zulässige zeitliche Abweichung ist weiterhin offen.
- Die Weiterleitung von Messdaten über andere Slaves wurde als gewünschtes Soll-Ziel konkretisiert. Die technische Umsetzung und der tatsächlich erreichbare Umfang bleiben Gegenstand des Architekturentwurfs und späterer Tests.

### vorläufige Arbeitsentscheidungen

- Die eigentliche Produktimplementierung beginnt erst nach fachlicher und technischer Abstimmung sowie einem ausreichend konkreten Architektur- und Testentwurf.
- Lastenheft, Pflichtenheft, Projektplan und Paper-Struktur sind ausdrücklich als Entwürfe gekennzeichnet.
- Nicht bestätigte Punkte werden weiterhin als Vorschlag, Arbeitsannahme oder offene Entscheidung ausgewiesen.

### Probleme Und Offene Punkte

- Es ist noch nicht geklärt, wer Lastenheft, Pflichtenheft, Architektur und Abnahme formal freigibt und wie die Freigaben dokumentiert werden sollen.
- Rollen, Sensorumfang, Kommunikationsablauf, Zeitkonzept, Fehlerverhalten und Abnahmekriterien benötigen fachliche Rückmeldung.
- Für das Abschluss-Paper fehlen noch verbindliche Angaben zu Sprache, Vorlage, Seitenumfang, Zitierstil, Abgabeformat und Abgabetermin.
- Die internen Zieltermine des überarbeiteten Projektplans sind noch nicht mit den Beteiligten abgestimmt.

### Nächste Schritte

- Lastenheft zuerst fachlich prüfen lassen und Rückmeldungen nachvollziehbar einarbeiten.
- Zuständigkeiten und Form der Freigaben mit Herrn Schnabel und Herrn Heym klären, ohne ihre jeweilige Freigaberolle vorwegzunehmen.
- Pflichtenheft und Anwendungsfälle auf Grundlage des abgestimmten Lastenhefts überarbeiten.
- Formale Anforderungen an das Abschluss-Paper erfragen.
- Architektur, Datenformat und Testkonzept erst nach der fachlichen Klärung finalisieren.

## 12.08.2026 - Fachliche Anforderungen Konkretisiert

### Durchgeführte Arbeiten

- Herrn Schnabel gefragt, ob Bodenfeuchte und Bodentemperatur im Lastenheft als Muss- oder optionale Anforderungen einzuordnen sind.
- Die Rückmeldung erhalten, dass die Bodensensoren nur optional sind.
- Herrn Schnabel gefragt, ob alle neun verfügbaren SEN66-Messwerte verbindlich gespeichert und übertragen werden sollen.
- Die Bestätigung erhalten, dass alle aufgeführten SEN66-Messwerte verwendet werden sollen.
- Zur zeitlichen Toleranz die Rückmeldung erhalten, dass der genaue Übertragungszeitpunkt unkritisch ist und vor allem der Zeitstempel der Messung genau sein muss.
- Die Speicheranforderung konkretisiert: Das lokale Backup eines Slaves muss die im 15-Minuten-Rhythmus aufgenommenen Daten mindestens eines Jahres aufnehmen können.
- Herrn Schnabel gefragt, ob der Master nach erfolgreichem Empfang und Speichern eine Bestätigung senden soll und der Slave einen unbestätigten Datensatz später erneut übertragen soll.
- Die Rückmeldung `genau so` erhalten und damit den vorgeschlagenen ACK-Grundablauf fachlich bestätigt.
- Lastenheft, Pflichtenheft, Projektplan und README entsprechend aktualisiert.
- Das Lastenheft redaktionell auf Version 0.2 und den Status als versandfähiger Prüfentwurf gebracht.

### Ergebnisse Und Erkenntnisse

- Bodenfeuchte und Bodentemperatur gehören nicht zum verpflichtenden Kernumfang und sind keine Voraussetzung für dessen Abnahme.
- Sensorwahl, Pinbelegung, Kalibrierung und Fehlerbehandlung müssen nur festgelegt werden, falls die optionale Funktion umgesetzt wird.
- Lufttemperatur, relative Luftfeuchtigkeit, CO2, PM1, PM2.5, PM4, PM10, VOC-Index und NOx-Index gehören verbindlich in jeden Kern-Datensatz.
- Eine Übertragungsverzögerung ist fachlich zulässig. Messzeitpunkt und Empfangszeitpunkt dürfen jedoch nicht verwechselt werden.
- Ein Jahr umfasst bei vier Messungen pro Stunde mindestens 35.040 Datensätze je Slave; bei zehn Slaves entstehen am Master mindestens 350.400 Datensätze zuzüglich Reserve.
- Der Master sendet ein Erfolgs-ACK erst nach erfolgreicher zentraler Speicherung. Ohne ACK bleibt der Datensatz am Slave lokal als ausstehend erhalten und wird später erneut übertragen.
- Anzahl, zeitlicher Abstand und maximale Dauer der Wiederholungsversuche sind weiterhin offen.

### Nächste Schritte

- Die weiterhin offenen fachlichen Anforderungen priorisiert mit Herrn Schnabel abstimmen.
- Die geforderte Genauigkeit sowie Erzeugung und Synchronisation des Messzeitstempels klären.
- Als Nächstes die noch offenen Abnahmekriterien sowie Anzahl und Abstand der Wiederholungsversuche klären.

## 13.08.2026 - Lastenheft Als PDF Fuer Die Fachliche Pruefung Erstellt

### Durchgeführte Arbeiten

- Den Lastenheft-Pruefentwurf Version 0.2 in eine eigenstaendige A4-PDF ueberfuehrt.
- Titelblatt, Inhaltsuebersicht, Seitenzahlen, Ueberschriften und umgebrochene Tabelleninhalte fuer die Durchsicht aufbereitet.
- Die PDF im Dokumentationsordner neben der bearbeitbaren Markdown-Quelle abgelegt und in der README verlinkt.
- Die menschlichen Rollen Betreiber, Installateur und Datenauswerter im Pflichtenheft zur gemeinsamen Rolle Benutzer zusammengefasst; Master und Slave bleiben die einzigen Systemrollen.
- Festgelegt, dass Master und Slave nicht in getrennten Repositorys gepflegt werden: Eine gemeinsame Codebasis besitzt getrennte Rollenabläufe und startet je Gerät nur die konfigurierte Rolle.
- Das Kernsystem als Sternstruktur festgelegt: Slaves erkennen den Master über ein Erkennungssignal und kommunizieren direkt mit ihm; Slaves leiten im Kernsystem keine fremden Pakete weiter.
- Dynamisches Mesh mit automatischer Nachbar- und Routenerkennung auf eine Kann-Erweiterung bei verbleibender Projektzeit zurückgestuft. Vor einer möglichen Umsetzung muss das Pflichtenheft in einer neuen Version um Routing- und Mesh-Anwendungsfälle erweitert werden.
- Die bereits an Herrn Schnabel gesendete PDF-Version 0.2 bleibt als versendeter Prüfstand erhalten; die Markdown-Quelle führt die Änderung als Version 0.3 weiter.
- Das vorhandene OLED als optionale Diagnoseausgabe eingeordnet. Fuer den Ausseneinsatz ist es nicht erforderlich; der Kernbetrieb muss ohne Display funktionieren.
- Festgelegt, dass Sequenznummern und der Status ausstehender Uebertragungen einen Neustart ueberstehen muessen. Der Slave setzt mit der naechsten freien Sequenznummer fort und versucht unbestaetigte Datensaetze spaeter erneut zu senden.

### Ergebnisse Und Erkenntnisse

- `docs/Lastenheft_AUDI_Climate_Cube.md` bleibt die bearbeitbare Quelle.
- `docs/Lastenheft_AUDI_Climate_Cube.pdf` ist die Uebergabefassung fuer die fachliche Pruefung durch Herrn Schnabel.
- Die PDF ist weiterhin ausdruecklich als nicht freigegebener Pruefentwurf gekennzeichnet.

### Nächste Schritte

- PDF an Herrn Schnabel zur Durchsicht senden.
- Rueckmeldungen zunaechst in die Markdown-Quelle einarbeiten und anschliessend eine neue PDF-Version erzeugen.

## 14.08.2026 - Hexagonale Softwarearchitektur Umgesetzt

### Durchgeführte Arbeiten

- Den bisherigen monolithischen `code.py` in eine schlanke hexagonale Architektur überführt.
- Hardwareunabhängige Bereiche `domain/`, `application/` und `ports/` angelegt.
- CircuitPython-Adapter für Konfiguration, Zeitreferenz, SEN66, SD-Karte, SX1262 und serielle Diagnose ergänzt.
- Gemeinsame Codebasis mit rollenabhängigem Start von Master oder Slave über `config.json` umgesetzt.
- Slave-Ablauf mit lokaler Speicherung vor der Übertragung und chronologischer FIFO-Warteschlange implementiert.
- Festgelegt: Nach erfolgreichem ACK wird der nächste ausstehende Datensatz gesendet; beim ersten fehlenden ACK endet der Durchlauf bis zum nächsten 15-Minuten-Zyklus.
- Master-Ablauf mit Validierung, zentraler Speicherung und ACK erst nach erfolgreichem Schreiben implementiert.
- Behandlung verlorener ACKs vorbereitet: Bereits gespeicherte Duplikate werden erneut bestätigt, aber nicht nochmals als neue Messung gespeichert.
- Gerätespezifische `config.json` von Git ausgeschlossen und `config.example.json` als Vorlage ergänzt.
- Architekturentscheidungen in `docs/Architektur_Hexagonal.md`, README und Pflichtenheft dokumentiert.

### Prüfung

- Python-Syntax der hardwareunabhängigen Module und Adapter erfolgreich geprüft.
- Acht Unit-Tests für Codec, Speichern-vor-Senden, FIFO-Abbruch, Speichern-vor-ACK, Duplikat-ACK sowie SD-Zustand und Wiederanlauf erfolgreich ausgeführt.
- Die neue Gesamtsoftware wurde noch nicht auf den realen Pico-Geräten ausgeführt; Hardwareintegration, Zeitreferenz, Master-Erkennung und Dauerbetrieb bleiben nächste Prüfschritte.


## 17.08.2026 - Funktionsfaehigen Architekturprototyp Zusammengefuehrt

### Durchgefuehrte Arbeiten

- Den bisherigen Messcode mit der vorbereiteten hexagonalen Grundstruktur zu einem ausfuehrbaren Prototyp zusammengefuehrt.
- Adapter fuer Konfiguration, Zeitreferenz, Diagnose, SD-Speicherung, SEN66 und SX1262 eingebunden.
- Rollenabhaengige Master- und Slave-Ablaeufe mit einer gemeinsamen `code.py` verbunden.
- Gemeinsames Messdatenmodell und ASCII-Protokoll fuer Messdaten und ACK-Nachrichten integriert.
- Lokale Slave-Speicherung, FIFO-Warteschlange, ACK-Auswertung und zentrale Master-Speicherung in den Laufzeitpfad aufgenommen.
- `config.example.json` und Git-Ausschluss der geraetespezifischen `config.json` ergaenzt.

### Ergebnisse Und Erkenntnisse

- Die fachlichen Kernablaeufe sind in Domain, Anwendung, Ports und Hardwareadapter getrennt.
- Master und Slave koennen aus derselben Codebasis ueber die Geraetekonfiguration gestartet werden.
- Der Stand war als Integrationsprototyp vorhanden, aber noch nicht vollstaendig auf dem Pico getestet.
- Die vorhandene monolithische Messsoftware und die neue Architektur enthielten noch ueberschneidende Verantwortlichkeiten.

### Probleme Und Offene Punkte

- Die reale CircuitPython-Integration der Adapter und ihrer Importe war noch zu pruefen.
- OLED, SD-Karte, Sensoren und LoRa mussten im gemeinsamen Startpfad auf dem Pico getestet werden.
- Die Aufteilung des neueren Hardwarecodes auf die vorhandenen Adapter war noch nicht abgeschlossen.

### Naechste Schritte

- Hardwarebezogene Bestandteile weiter aus `code.py` auslagern.
- Import- und Initialisierungsreihenfolge direkt auf CircuitPython pruefen.
- Den Gesamtstart zunaechst in der Master-Rolle testen.

## 19.08.2026 - Komponenten Getrennt Und Hardwareintegration Untersucht

### Durchgefuehrte Arbeiten

- Den neueren Hardwarecode zunaechst in einzelne Root-Module fuer DS18B20, OLED, SD-Karte, SEN66, Diagnose, CSV-Ausgabe, Anzeige, Formatierung und Laufzeit zerlegt.
- Die Importreihenfolge in `code.py` mit fortlaufenden Diagnoseausgaben untersucht.
- Vorhandene Unit-Tests fuer Kernablaeufe und SD-Wiederanlauf in das Repository aufgenommen.
- Mit der Fehlersuche begonnen, weil der kombinierte Stand auf dem Pico nicht vollstaendig startete.
- Untersucht, ob CircuitPython eigene Module ausserhalb von `code.py` laden kann und welche Bibliotheken unter `lib/` benoetigt werden.
- Konzeptionell ueber einfache Erweiterungswege von der Sternstruktur zu einer spaeteren Mesh- beziehungsweise Relay-Funktion nachgedacht.

### Ergebnisse Und Erkenntnisse

- Eigene Python-Module duerfen unter CircuitPython ausserhalb von `code.py` liegen und normal importiert werden.
- Die zusaetzlichen Root-Module erleichterten die isolierte Fehlersuche, duplizierten jedoch teilweise bereits vorhandene Adapter.
- Fuer eine einfache spaetere Weiterleitung wurden Nachbarerkennung beziehungsweise bekannte Nachbarn, eindeutige Nachrichten-IDs, eine begrenzte Weiterleitungsanzahl und Duplikaterkennung als notwendige Aspekte erkannt.
- Eine unkontrollierte Weiterleitung an alle erreichbaren Slaves wuerde Schleifen, Duplikate und zusaetzlichen Energieverbrauch verursachen.
- Mesh bleibt eine optionale Erweiterung nach dem stabilen Sternsystem; es wurde weder als Kernfunktion festgelegt noch implementiert.

### Probleme Und Offene Punkte

- Der Pico brach beim Laden beziehungsweise Initialisieren der ausgelagerten Komponenten ab.
- Die genaue Ursache des SD-Importfehlers war am Ende des Arbeitstages noch nicht geloest.
- Alter Adapterstand und neuere Root-Module waren noch nicht konsistent zusammengefuehrt.
- Fuer Mesh waren weder Routingverfahren noch Paketfelder, Nachbarerkennung oder Abnahmekriterien festgelegt.

### Naechste Schritte

- Den konkreten CircuitPython-Traceback ueber die serielle Schnittstelle auslesen.
- Namenskonflikte und nachgelagerte Konstruktorfehler einzeln beheben.
- Neuere Hardwaredetails in die bestehende Adapterstruktur uebernehmen und Root-Duplikate danach entfernen.
- Mesh erst nach einem stabilen Sternbetrieb genauer spezifizieren und gegen Energie-, Speicher- und Zuverlaessigkeitsziele bewerten.

## 20.08.2026 - Importfehler Behoben Und Master-Pico Integriert Getestet

### Durchgefuehrte Arbeiten

- Den CircuitPython-Traceback direkt ueber `/dev/ttyACM0` ausgelesen.
- Als Ursache des vermeintlichen Importproblems eine Namenskollision zwischen `SD.py` und dem Mount-Verzeichnis `/sd` auf dem nicht case-sensitiven CIRCUITPY-Dateisystem identifiziert.
- Das SD-Hardwaremodul eindeutig benannt und anschliessend in `adapters/sd_card.py` ueberfuehrt.
- Weitere sichtbar gewordene Fehler bei SD-Methodensignatur, OLED-Aufrufen und gemeinsamem I2C-Bus behoben.
- Neuere Hardwarelogik fuer OLED und optionalen DS18B20 in Adapter ueberfuehrt.
- SEN66-, Diagnose- und Konfigurationsadapter bereinigt und die getesteten Controller- sowie SD-Speichervertraege beibehalten.
- `code.py` auf eine Composition Root fuer Initialisierung und Rollenstart reduziert.
- Nicht mehr verwendete Root-Duplikate lokal und auf dem Pico entfernt.
- Den konsolidierten Stand auf den als Master konfigurierten Pico uebertragen und neu gestartet.
- README auf die bereinigte Struktur und den tatsaechlichen Hardwaretest aktualisiert.

### Ergebnisse Und Erkenntnisse

- Der Importfehler lag nicht an ausgelagerten Python-Modulen, sondern an der Kollision von `SD.py` mit `/sd`.
- Der Master-Pico startet mit CircuitPython 10.2.1 erfolgreich bis in die Empfangsschleife.
- OLED, `config.json`, SD-Karte und SX1262 werden erfolgreich initialisiert.
- Der Start meldet nacheinander `SD card ready`, `LoRa ready` und `master M01 started`.
- Ein vollstaendiger LoRa-Empfangs-Timeout wurde ohne Laufzeitfehler durchlaufen.
- Python-Syntax, Diff-Pruefung und alle acht vorhandenen Unit-Tests waren erfolgreich.

### Probleme Und Offene Punkte

- Der vollstaendige Slave-Ablauf mit SEN66-Messung, lokaler Speicherung, LoRa-Uebertragung und ACK wurde mit dem konsolidierten Stand noch nicht auf dem zweiten Pico getestet.
- Der Master-Hardwaretest weist noch keinen realen Empfang eines produktiven Slave-Datensatzes nach.
- Zeitreferenz, SD-Wiederanlauf auf realer Hardware, Reichweite und Dauerbetrieb bleiben zu pruefen.
- Die optionale Mesh-Erweiterung ist weiterhin nur eine konzeptionelle Ueberlegung.

### Naechste Schritte

- Zweiten Pico als Slave konfigurieren und den vollstaendigen Mess-, Speicher-, Sende- und ACK-Ablauf testen.
- Auf Master und Slave Neustart- und Wiederholungsverhalten mit ausstehenden Datensaetzen pruefen.
- Erst nach stabilem Sternbetrieb entscheiden, ob Zeit fuer einen spezifizierten Relay- oder Mesh-Prototyp verbleibt.

## 21.08.2026 - Produktiven LoRa-Ablauf Und Fehlerfaelle Getestet

### Durchgeführte Arbeiten

- Den produktiven Master-/Slave-Ablauf ueber mehrere Stunden im vorgesehenen 15-Minuten-Intervall beobachtet.
- Die auf Master- und Slave-Seite erzeugten CSV-Datensaetze anhand von Sequenznummern, Messzeitpunkten, Empfangsstatus, RSSI und SNR ausgewertet.
- Das Verhalten bei einem fehlenden ACK mit Sequenz 21 untersucht.
- Geprueft, ob der spaeter erfolgreich uebertragene Datensatz 21 beim Master nur einmal gespeichert wurde.
- Einen kontrollierten Neustart des Slaves bei weiterlaufendem Master durchgefuehrt.
- Die Ergebnisse in `docs/Testprotokoll_Systemintegration_2026-08-21.md` dokumentiert.

### Ergebnisse Und Erkenntnisse

- Die Sequenzen 5 bis 16 wurden in zwoelf aufeinanderfolgenden 15-Minuten-Intervallen erfolgreich uebertragen.
- Nach `ACK missing for sequence 21` blieb der Datensatz erhalten und wurde spaeter erfolgreich zum Master uebertragen.
- Sequenz 21 war in der Master-CSV genau einmal vorhanden; fuer diesen Testfall wurden weder Datenverlust noch doppelte Speicherung festgestellt.
- Sequenz 22 wurde anschliessend erfolgreich bestaetigt.
- Nach dem kontrollierten Slave-Neustart funktionierten Sequenzverwaltung, Uebertragung, Speicherung und ACK weiter.
- Die absolute Slave-Zeit wird nach einem Neustart zurueckgesetzt. Die zeitliche Reihenfolge bleibt ueber Sequenznummer, 15-Minuten-Intervall und Empfangszeit des Masters nachvollziehbar.

### Probleme Und Offene Punkte

- Die bereits vor dem kontrollierten Neustart erzeugten Sequenzen 17 und 18 besitzen trotz unterschiedlicher Messwerte denselben Messzeitstempel. Die Ursache beziehungsweise fachliche Bedeutung dieses Feldes muss noch eindeutig festgelegt werden.
- Die Anforderungen muessen klarstellen, ob der Slave eine gueltige absolute Uhrzeit benoetigt oder ob Intervall, Sequenznummer und Master-Empfangszeit ausreichen.
- Master-Neustart, mehrere bei ausgeschaltetem Master aufgelaufene Datensaetze, Reichweite und Dauerbetrieb sind noch nicht getestet.

### Nächste Schritte

- Master-Neustart separat testen.
- Master fuer mehrere Messintervalle ausschalten und danach die chronologische Nachuebertragung aller ausstehenden Datensaetze pruefen.
- Bedeutung und Gueltigkeit von `measurement_timestamp` und `received_timestamp` im Datenformat und Pflichtenheft praezisieren.
- Reichweiten- und laengeren Dauerbetriebstest vorbereiten.

## 25.08.2026 - Sequenzverhalten Praezisiert Und Neustart Geprueft

### Durchgefuehrte Arbeiten

- Verhalten bei einem Slave-Neustart mit und ohne lesbare Slave-SD im Pflichtenheft und Datenformat praezisiert.
- Achtfeldrige `Q`- und `R`-Nachrichten fuer die Abfrage der naechsten freien Sequenznummer spezifiziert.
- Verhalten ohne gueltige Master-Antwort, RAM-Fortfuehrung und Rueckkehr zur SD-gestuetzten Verwaltung festgelegt.
- ACK-Diagnose vereinheitlicht: Ein fehlendes ACK erzeugt kein eigenes Diagnoseereignis und keinen zusaetzlichen SD-Eintrag.
- `docs/Testplan_Sequenzabfrage.md` mit den Testfaellen `SEQ-01` bis `SEQ-14` erstellt.
- Den SD-basierten Neustarttest `SEQ-01` mit Slave `C01` und Master `M01` durchgefuehrt.

### Ergebnisse Und Erkenntnisse

- Vor dem Neustart war Sequenz 40 erfolgreich bestaetigt.
- Nach dem Slave-Neustart wurde Sequenz 41 erfolgreich bestaetigt.
- Die Master-CSV enthaelt die Sequenzen 40 und 41 jeweils genau einmal.
- `SEQ-01` ist fuer den bestehenden SD-basierten Neustart bestanden.
- Die neue `Q`-/`R`-Abfrage war zu diesem Zeitpunkt noch nicht implementiert.

### Probleme Und Offene Punkte

- `Q`-/`R`-Codec, Master-Antwort und Slave-Abfragelogik mussten noch implementiert werden.
- Tests ohne Slave-SD sowie Integrations- und Hardwaretests waren noch offen.

### Naechste Schritte

- Wiederholungs- und Timeoutparameter fuer die Sequenzabfrage festlegen.
- `Q`-/`R`-Codec und erste Unit-Tests umsetzen.

## 26.08.2026 - Sequenzabfrage Implementiert Und Mit Unit-Tests Abgesichert

### Durchgefuehrte Arbeiten

- Parameter fuer die Sequenzabfrage festgelegt: drei Versuche je Runde, drei Sekunden Timeout, zwei Sekunden Pause und eine neue Runde nach 60 Sekunden.
- Festgelegt, dass hoechstens die neueste unnummerierte Messung im RAM gehalten wird und ohne gueltige `R`-Antwort keine neuen Messdatensaetze gesendet werden.
- Domain-Nachrichten `SequenceQuery` und `SequenceResponse` sowie Kodierung und Dekodierung der achtfeldrigen `Q`- und `R`-Pakete implementiert.
- Validierung fuer Formatversion, Nachrichtentyp, Feldzahl, IDs, reserviertes Anfragefeld, Sequenzwert, Hop-Werte und maximale Payload-Laenge ergaenzt.
- `MasterStoragePort` und SD-Adapter um die Ermittlung der naechsten freien Sequenz je Slave erweitert.
- Master-Controller um Verarbeitung von `Q` und Versand von `R` erweitert.
- Slave-Controller um die Pruefung korrekt adressierter `R`-Antworten des konfigurierten Masters erweitert.
- Testplan an die festgelegten Parameter und bestandenen Unit-Anteile angepasst.

### Ergebnisse Und Erkenntnisse

- `SEQ-02` und `SEQ-03` bestehen auf Unit-Ebene: Ein bekannter Slave erhaelt den letzten Masterstand plus eins, ein neuer Slave erhaelt Sequenz 0.
- `SEQ-05` bis `SEQ-07` bestehen: Antworten eines falschen Masters, fuer einen falschen Slave und syntaktisch ungueltige Antworten werden abgelehnt.
- `SEQ-08` besteht auf Unit-Ebene: Eine wiederholte Anfrage liefert ohne zwischenzeitliche Speicherung dieselbe freie Sequenznummer.
- Alle 33 Unit-Tests fuer Architektur, Ports, Fehlerbehandlung, Codec, Master-/Slave-Ablauf und SD-Speicherung wurden erfolgreich ausgefuehrt.
- Python-Syntax und Diff-Pruefung waren erfolgreich.

### Probleme Und Offene Punkte

- Die zeitgesteuerte Slave-Abfragerunde mit drei Versuchen, Pausen und 60-Sekunden-Wiederholung ist noch nicht in den Laufzeitablauf integriert.
- Betrieb ohne Slave-SD und die fluechtige RAM-Messung sind noch nicht implementiert.
- `SEQ-09` bis `SEQ-14` sowie die Hardwareanteile von `SEQ-02`, `SEQ-04` und `SEQ-08` bleiben offen.
- Das bisherige Messdaten- und ACK-Format ist noch nicht vollstaendig auf das routingfaehige V1-Zielformat umgestellt.

### Naechste Schritte

- Slave-Abfragerunde und Verhalten ohne lesbare SD implementieren.
- `SEQ-04` automatisieren und danach Integrationsfaelle `SEQ-09` bis `SEQ-14` bearbeiten.
- Nach bestandenen Softwaretests `Q`-/`R` auf beiden Pico-Geraeten testen.

## 27.08.2026 - Weiterbetrieb Ohne Slave-SD Implementiert

### Durchgefuehrte Arbeiten

- Die Slave-Sequenzabfrage um eine Laufzeitrunde mit bis zu drei `Q`-Versuchen, drei Sekunden Timeout und zwei Sekunden Pause ergaenzt.
- Den Clock-Port um testbares `sleep_ms` erweitert.
- Einen degradierten Slave-Betrieb ohne lokale SD umgesetzt: Messung wird im RAM gehalten, `SLAVE_SD_UNAVAILABLE` im Datensatzstatus gesetzt und erst nach gueltiger `R`-Antwort gesendet.
- Bei fehlender Slave-SD laeuft der Slave weiter; beim Master bleibt die SD fuer zentrale Speicherung verpflichtend.
- Nach fehlender Masterantwort wird keine Sequenz vergeben und kein Messdatensatz gesendet. Die gehaltene unnummerierte Messung kann nach 60 Sekunden erneut abgefragt werden.
- Nach fehlendem ACK im No-SD-Modus wird der fluechtige Sequenzstand verworfen, damit der naechste Versuch erneut am Masterstand ausgerichtet wird.

### Ergebnisse Und Erkenntnisse

- `SEQ-04` ist auf Unit-Ebene bestanden und deckt drei erfolglose `Q`-Versuche ohne Messdatenversand ab.
- `SEQ-11`, `SEQ-12` und der Unit-Anteil von `SEQ-14` sind automatisiert: gespeicherte, nicht gespeicherte und aus mehreren Master-CSV-Staenden rekonstruierte Sequenzen liefern die erwartete naechste freie Nummer.
- Der No-SD-Betrieb ist weiterhin kein vollstaendig anforderungskonformer Normalbetrieb, weil das lokale Backup fehlt; dieser Zustand wird im Statusflag sichtbar.
- Alle 40 Unit-Tests fuer Architektur, Ports, Fehlerbehandlung, Codec, Sequenzabfrage, No-SD-Verhalten, Master-/Slave-Ablauf und SD-Speicherung wurden erfolgreich ausgefuehrt.

### Probleme Und Offene Punkte

- Hardwaretests fuer `SEQ-02`, `SEQ-04` und `SEQ-08` bleiben offen.
- Die Integrationsfaelle `SEQ-09` bis `SEQ-14` bleiben offen.
- Das bisherige Messdaten- und ACK-Format ist noch nicht vollstaendig auf das routingfaehige V1-Zielformat umgestellt.

### Naechste Schritte

- No-SD-Verhalten auf zwei Pico-Geraeten testen.
- Integrationsfaelle `SEQ-09` bis `SEQ-14` schrittweise automatisieren beziehungsweise hardwareseitig vorbereiten.

## 28.08.2026 - No-SD-Hardwaretest Vorbereitet

### Durchgefuehrte Arbeiten

- Den Testplan fuer die Sequenzabfrage ohne Slave-SD um konkrete Hardwareablaeufe fuer `SEQ-02`, `SEQ-04` und `SEQ-08` erweitert.
- `SEQ-09` als Integrationstest konkret geplant: Ausgangszustand, Neustartablauf, erwartete erste und zweite `R`-Antwort, Abbruchkriterien und Nachweistabelle ergaenzt.
- `SEQ-10` fachlich geklaert: keine Hot-Plug-Rueckkehr zur Slave-SD im laufenden Betrieb; SD wird nur spannungsfrei eingesetzt oder repariert und danach per Neustart neu bewertet.
- Voraussetzungen, Sicherheitsregeln, Testkonfiguration, erwartete serielle Beobachtungen und CSV-Nachweise beschrieben.
- Eine sichere Methode fuer `SEQ-04` festgelegt: Master ausgeschaltet lassen beziehungsweise nicht starten, statt Funkhardware im laufenden Betrieb zu veraendern.
- Fuer `SEQ-08` eine sichere Simulation vorbereitet: erste Abfragerunde ohne laufenden Master, danach Master vor der naechsten Retry-Runde starten.

### Ergebnisse Und Erkenntnisse

- Der No-SD-Hardwaretest ist als abarbeitbarer Tischtest vorbereitet.
- `SEQ-09` ist nun so beschrieben, dass der Neustart ohne Slave-SD gegen den zentralen Masterstand ausgewertet werden kann.
- `SEQ-10` ist fachlich vereinfacht: Der Neustart bildet die Grenze zwischen RAM-Fehlerbetrieb und moeglicher Rueckkehr zur SD-gestuetzten Verwaltung.
- Die lokale Backup-Anforderung gilt ohne Slave-SD weiterhin als nicht erfuellt; der Test prueft nur das definierte Fehlerverhalten.
- Fuer jeden Teiltest sind serielle Logs, Master-CSV und SD-Zustand als Nachweise vorgesehen.

### Probleme Und Offene Punkte

- Die Hardwaretests sind noch nicht ausgefuehrt.
- Fuer `SEQ-08` wird der Verlust der ersten Antwort praktisch ueber einen zunaechst ausgeschalteten Master simuliert; ein gezielter Einzelpaketverlust bleibt ein spaeterer Spezialtest.

### Naechste Schritte

- `SEQ-02`, `SEQ-04`, `SEQ-08` und anschliessend `SEQ-09` auf zwei Pico-Geraeten ausfuehren.
- Danach den konkreten Hardwareablauf fuer `SEQ-10` auf Basis der `SEQ-09`-Ergebnisse vorbereiten.
- Danach Ergebnisse im Testplan beziehungsweise in einem Testprotokoll dokumentieren.


## 01.09.2026 - Ueberwachte Slaves Und Empfangsluecken Festgelegt

### Durchgefuehrte Arbeiten

- `monitored_slaves` zunaechst mit einer bis zehn eindeutigen Slave-IDs als Pflichtfeld der Master-Konfiguration festgelegt; diese irrtuemliche Obergrenze wurde am 03.09.2026 korrigiert.
- Rollenabhaengige Validierung fuer Master- und Slave-Konfiguration implementiert.
- Separate Master-Vorlage `config.master.example.json` erstellt.
- Master-Controller so erweitert, dass Messdaten und Sequenzanfragen unbekannter Slaves abgelehnt werden.
- `NO_PACKET`-Lueckenzeilen mit `NA`, Master-Laufzeit und Fehlintervallzaehler in Pflichtenheft und Datenformat spezifiziert.
- Vorlaeufigen ACK-Timeout, Entwicklungsfunkparameter, Energie- und Schlafstrategie, Plausibilitaetsvorgehen sowie erste Abnahmewerte festgelegt.
- README und Architekturdokument an den aktuellen Konfigurationsstand angepasst.

### Ergebnisse Und Erkenntnisse

- Ungueltige, leere, doppelte oder zu lange Slave-Listen sowie die Master-ID in der eigenen Liste werden beim Start abgelehnt.
- Spaeter nachgesendete echte Messdaten sollen Lueckenzeilen nicht ueberschreiben.
- Alle 47 Unit-Tests wurden erfolgreich ausgefuehrt.

### Probleme Und Offene Punkte

- Die Erzeugung der 15-minuetigen `NO_PACKET`-Lueckenzeilen ist noch nicht implementiert.
- ACK-Timeout, Intervalltoleranz und Entwicklungsfunkparameter muessen durch reale Hardwaretests bestaetigt werden.
- Konkrete Plausibilitaetsgrenzen, Pico-Schlaftechnik, Energiebilanz und Einjahresnachweis bleiben offen.
- Bestehende Master-`config.json` muss vor dem naechsten Hardwarestart um `monitored_slaves` ergaenzt werden.
- Hardwaretests fuer Sequenzabfrage und No-SD-Betrieb bleiben offen.

### Naechste Schritte

- Master-Intervallueberwachung und Speicherung der Lueckenzeilen implementieren.
- Danach Unit-, Integrations- und Hardwaretests fuer echte und fehlende Empfangsintervalle durchfuehren.

## 01.09.2026 - 24-Stunden-Schlaf- Und Energietest Vorbereitet

### Durchgefuehrte Arbeiten

- Eigenstaendig ausfuehrbaren 24-Stunden-Test fuer einen Master und einen Slave beschrieben.
- CSV-Vorlage fuer die Strommessung der Betriebsphasen angelegt.
- Desktop-Auswertung fuer mittleren Strom, Jahresbedarf, 30 Prozent Reserve und rechnerische Akkulaufzeit erstellt.
- Automatische Pruefung der Master-CSV auf Mindestanzahl, Sequenzfolge, Duplikate, Luecken und 15-Minuten-Intervalle erstellt.
- Testauswertungen mit Beispieldaten und alle 47 bestehenden Unit-Tests erfolgreich ausgefuehrt.

### Ergebnisse Und Erkenntnisse

- Der 24-Stunden-Test kann selbststaendig durchgefuehrt und anschliessend reproduzierbar ausgewertet werden.
- Die reale Stromaufnahme kann nicht durch Software allein bestimmt werden; dafuer bleibt ein externes Strommessgeraet erforderlich.
- Fuer die Strommessung darf keine aktive USB-Datenverbindung den CircuitPython-Schlafzustand beeinflussen.

### Probleme Und Offene Punkte

- Reale Stromwerte der Hardwarephasen liegen noch nicht vor.
- Der 24-Stunden-Test und der spaetere mindestens siebentaegige Dauertest sind noch auszufuehren.
- Die konkrete Schlafimplementierung muss vor dem Energienachweis auf der Hardware geprueft werden.

### Naechste Schritte

- Betriebsphasen mit einem externen Strommessgeraet erfassen.
- 24-Stunden-Test starten und danach Master-CSV sowie Energiebilanz auswerten.
- Bei erfolgreichem Kurztest einen mindestens siebentaegigen Dauertest durchfuehren.


## 02.09.2026 - Projektzwischenstand Fuer Abstimmung Vorbereitet

### Durchgefuehrte Arbeiten

- Einen kompakten Projektzwischenstand als Gespraechsleitfaden fuer Herrn Schnabel erstellt.
- Projektziel, aktueller Entwicklungsstand, Systemablauf, technische Entscheidungen, Teststand und offene Punkte zusammengefasst.
- Aussagen mit dem aktuellen Implementierungsstand abgeglichen und korrigiert: 47 Unit-Tests, aktuelles fuenffeldriges ACK, offene Hardwarevalidierung des Master-Neustarts sowie Stand der Dokumentenfreigabe.
- Fragen fuer die technische Abstimmung und die weitere Priorisierung vorbereitet.
- Termin zur Vorstellung und Abstimmung des Projektzwischenstands fuer Dienstag, den 08.09.2026, vereinbart.

### Ergebnisse Und Erkenntnisse

- Der Projektzwischenstand ist als Grundlage fuer den Abstimmungstermin vorbereitet.
- Das Lastenheft 0.4 wurde bereits fachlich positiv rueckgemeldet; beim Pflichtenheft stehen Durchsicht, Rueckmeldung und die Klaerung des formalen Freigabewegs noch aus.
- Die technische Darstellung unterscheidet zwischen nachgewiesener aktueller Funktionalitaet und noch nicht implementiertem V1-Zielformat.

### Probleme Und Offene Punkte

- Zur Verfuegbarkeit der zwei zusaetzlichen Raspberry Pi Picos liegt noch keine Rueckmeldung vor.
- Verfuegbarkeit und Eignung des Strommessgeraets fuer den Energienachweis sind beim Termin zu klaeren.
- Die Hardwaredemonstration fuer den Termin ist noch vorzubereiten und vorab zu pruefen.

### Naechste Schritte

- Projektzwischenstand und Pflichtenheft fuer den Termin bereithalten.
- Fragen zu technischem Ansatz, Freigabeweg, Priorisierung, zusaetzlichen Picos und Strommessung am 08.09.2026 klaeren.
- Hardwaredemonstration am Tag vor dem Termin testen und anschliessend das Messintervall wieder auf 900 Sekunden setzen.


## 03.09.2026 - V1-Datenformat Implementiert

### Durchgefuehrte Arbeiten

- Funkcodec vom bisherigen 18-Felder-Datenpaket auf das festgelegte 22-Felder-V1-Datenpaket umgestellt.
- Routingfelder fuer Ursprung, Endziel, naechsten Hop, Hop-Zaehler und Hop-Limit in Messdatensatz und Controller integriert.
- Neunfeldriges V1-ACK mit Master-Ursprung, Slave-Ziel, Sequenznummer und Ergebniscode implementiert.
- Slave prueft ACKs jetzt gegen konfigurierte Master-ID, eigene Slave-ID und Sequenznummer.
- `NA`, 160-Byte-Grenze, Feldzahl, Kennungen, Hop-Werte, Statusflags und nichtnegative Messgroessen validiert.
- Bestehende Tests auf V1 umgestellt und vier gezielte V1-Codec-Tests ergaenzt.
- Den Demonstrationsablauf fuer den Abstimmungstermin als Checkliste mit Hardwarevorbereitung, Konfiguration, Vorabtest, Live-Ablauf, Ersatznachweis und Rueckstellung auf 900 Sekunden ausgearbeitet.
- Die irrtuemlich aus der Zielgroesse von zehn Slaves abgeleitete Obergrenze aus Konfigurationsvalidierung, Tests und aktuellen Dokumenten entfernt.

### Ergebnisse Und Erkenntnisse

- Exaktes Beispieldatenpaket und ACK aus der V1-Spezifikation werden erzeugt und dekodiert.
- Direkte Pakete an einen anderen Master werden abgelehnt.
- Alle 52 Unit-Tests wurden erfolgreich ausgefuehrt.
- Zehn Slaves sind eine nachzuweisende Zielgroesse, aber keine feste Maximalanzahl.

### Probleme Und Offene Punkte

- V1-Datenpaket und ACK sind noch auf den beiden Pico-Geraeten zu testen.
- Elffeldriges Diagnoseereignis, V1-Speicherformat und `NO_PACKET`-Lueckenlogik sind noch nicht implementiert.
- Alte Pending-Dateien bleiben lesbar; ihre fehlende Route wird beim Senden aus der Slave-Konfiguration ergaenzt.

### Naechste Schritte

- V1-Funkformat auf zwei Pico-Geraeten testen.
- Danach V1-Speicherformat und Diagnoseereignisse implementieren.


## 04.09.2026 - V1-Funkformat Auf Hardware Bestaetigt

### Durchgefuehrte Arbeiten

- Aktuellen V1-Softwarestand auf Master `M01` und Slave `C01` getestet.
- Drei aufeinanderfolgende Messdatensaetze im 60-Sekunden-Testintervall uebertragen.
- Fuer alle drei Uebertragungen ein erfolgreiches ACK am Slave beobachtet.
- Zentrale Master-Speicherung, einmaliges Vorkommen und fortlaufende Sequenznummern kontrolliert.
- Slave kontrolliert neu gestartet und korrekte Sequenzfortsetzung mit ACK geprueft.
- `measurement_interval_s` danach auf beiden Geraeten wieder auf 900 Sekunden gesetzt und Konfiguration kontrolliert.
- Eigenes Testprotokoll `Testprotokoll_V1_Hardwaretest_2026-09-04.md` erstellt.

### Ergebnisse Und Erkenntnisse

- Das 22-feldrige V1-Datenpaket und das neunfeldrige V1-ACK funktionieren auf den beiden Pico-Geraeten im direkten Sternbetrieb.
- Die geprueften Datensaetze wurden zentral genau einmal gespeichert.
- Die Sequenzverwaltung wurde nach dem Slave-Neustart korrekt fortgesetzt.

### Probleme Und Offene Punkte

- Konkrete Sequenznummern und Dateinamen wurden waehrend des Tests nicht separat notiert.
- Mehrgeraete-, Reichweiten-, Stoerungs-, Dauer- und Energietests bleiben offen.
- V1-Speicherformat, Diagnoseereignisse und `NO_PACKET`-Lueckenlogik sind noch nicht implementiert.

### Naechste Schritte

- Testergebnis beim Abstimmungstermin am 08.09.2026 vorstellen.
- Nach der Abstimmung V1-Speicherformat oder `NO_PACKET` entsprechend der vereinbarten Prioritaet umsetzen.


## 07.09.2026 - Vorbereitung des Abstimmungstermins

### Durchgeführte Arbeiten

- Fragen für den Termin am 08.09. priorisiert: technischer Ansatz, Pflichtenheft, nächste Arbeiten, Hardware und Abnahmekriterien.
- Projektzwischenstand um den erfolgreichen V1-Hardwaretest vom 04.09. und den Verweis auf das Testprotokoll aktualisiert.
- Notizvorlage für Antworten, Entscheidungen, Zuständigkeiten und Termine erstellt.
- Codeablauf anhand von `code.py`, Slave- und Master-Controller nachvollzogen.
- Rollenwahl über Konfiguration, Messintervall, lokale Speicherung, FIFO-Wiederholung und ACK-Prüfung besprochen.
- Aufbau der Master-CSV anhand des aktuellen Codes und ihre Bedeutung für Herkunft, Reihenfolge und Nachvollziehbarkeit der Messdaten geprüft.

### Ergebnisse und Erkenntnisse

- Gesprächsunterlagen und Notizvorlage sind vorbereitet.
- Geräte-ID und Sequenznummer ermöglichen die Zuordnung und chronologische Ordnung je Slave.
- Zeitstempel beruhen derzeit auf einer manuell gesetzten Startzeit.
- Fehlende Messwerte bleiben in der CSV leer; automatische Empfangslückenzeilen sind noch nicht implementiert.

### Offene Punkte und nächste Schritte

- Master-CSV als lokale Kopie für die Demonstration sichern; Durchführung noch nicht bestätigt.
- Hardware und Kabel für den Termin bereitlegen.
- Rückmeldungen und vereinbarte Prioritäten beim Termin dokumentieren.


## 08.09.2026 - Gespräch zum Projektzwischenstand

### Durchgeführte Arbeiten

- Projektzwischenstand mit Herrn Schnabel besprochen und den allgemeinen Softwareaufbau erläutert.
- Zwei zusätzliche Raspberry Pi Picos übernommen.
- Gesprächsergebnisse in den Notizen und im Projekttagebuch dokumentiert.
- Gerätecheck am bisherigen Slave durchgeführt: Gerät mit UID `3E9B03325907A455` seriell erkannt; beim passiven Mitlesen über 15 Sekunden keine Ausgabe empfangen.
- Am Slave-OLED `ACK missing for sequence 157` beobachtet, während der Master ausgeschaltet war.
- Master anschließend eingeschaltet. Danach eine höhere Sequenznummer mit `acknowledged` am Slave bestätigt; die konkrete Nummer wurde nicht notiert.

### Ergebnisse und Erkenntnisse

- Positive Rückmeldung zum allgemeinen Softwareaufbau erhalten. Eine detaillierte technische Prüfung oder ausdrückliche Freigabe des Pflichtenhefts wurde damit nicht bestätigt.
- Das Strommessgerät ist bestellt; Herr Schnabel gibt Bescheid, sobald es verfügbar ist.
- Die Reichweite wurde nicht besprochen. Eine verbindliche Mindestreichweite wurde nicht festgelegt.
- Die Slave-Anwendung lief bis zum Sendeversuch. Das fehlende ACK bei ausgeschaltetem Master war erwartbar; nach dessen Einschalten wurde wieder eine Übertragung bestätigt.
- Der zuvor beobachtete Fehler `Failed to start CYW43` wurde bei diesem Check nicht erneut beobachtet. Ursache und dauerhafte Behebung sind damit nicht nachgewiesen.

### Offene Punkte und nächste Schritte

- Ausstattung und Firmware der neuen Picos prüfen und vorhandene Dateien vor Änderungen sichern.
- Verfügbarkeit des Strommessgeräts abwarten; Strommessung steht noch aus.
- Praktisch erreichbare Funkreichweite durch Tests untersuchen.
- Prüfen, ob Sequenz 157 genau einmal in der Master-CSV steht. Diese Kontrolle wurde nicht eindeutig bestätigt; der vollständige Nachsendetest ist deshalb noch nicht als bestanden dokumentiert.
- Die zuvor nicht abgeschlossene CSV-Sicherung bleibt offen.


## 09.09.2026 - V1-Speicherstruktur und Datenübernahme

### Durchgeführte Arbeiten

- V1-Speicherstruktur mit Geräteordnern und CSV-Blöcken zu je 3.000 Sequenznummern implementiert.
- Master-CSV um `master_uptime_s` und `missing_intervals` ergänzt; normale empfangene Messungen verwenden die Werte `0` und `0`.
- Automatische, wiederholbare Übernahme vorhandener Slave- und Master-CSV-Dateien in die V1-Blockstruktur implementiert.
- Bestehende CSVs werden erst nach vollständiger Übernahme als unveränderte `.pre_v1`-Sicherung archiviert.
- Unit-Tests für Blockwechsel, Altdateien, Duplikate, widersprüchliche Datensätze, Schreibfehler und Unterbrechungen ergänzt.

### Ergebnisse und Erkenntnisse

- Die Unit-Testsuite umfasst 79 Tests und lief erfolgreich durch.
- Bei einem Migrationsfehler wird auch ein Slave nicht im degradierten Betrieb ohne SD gestartet; der Fehler muss zuerst behoben werden.
- Die Implementierung wurde noch nicht auf einem Pico oder einer realen SD-Karte getestet.

### Nächste Schritte

- Vor einem Geräteupdate vollständige Sicherungen der beiden SD-Karten und des aktuellen Softwarestands erstellen.
- V1-Speicherstruktur zunächst mit einer gesicherten Test-SD auf beiden Rollen prüfen.
- Im Hardwaretest Pfade, Kopfzeilen, einmalige Speicherung, ACK und Sequenzfortsetzung kontrollieren.


## 10.09.2026 - Neue Pico-Hardware und RAM-Optimierung

### Durchgeführte Arbeiten

- Zwei neue Geräte mit CircuitPython eingerichtet und die Hardwarekennungen geprüft.
- Die Geräte melden sich als Raspberry Pi Pico mit RP2040, nicht als Pico 2 W.
- OLED-Startanzeige auf einem neuen Gerät bestätigt.
- Beim anschließenden Softwarestart auf dem RP2040 einen `MemoryError` beobachtet.
- CSV-Migrationscode im Speicheradapter verzögert geladen: Er wird nur bei tatsächlich vorhandenen Altdateien importiert.
- Unit-Test ergänzt, der den Verzicht auf den Migrationsimport bei einer leeren neuen SD prüft.

### Ergebnisse und Erkenntnisse

- Der sichtbare OLED-Start bestätigt Treiber, Grundverkabelung und CircuitPython-Start für mindestens ein neues Gerät.
- Die Speicheroptimierung ist per Unit-Test geprüft, aber noch nicht auf dem RP2040-Pico validiert.
- Die im Projekt bisher eingesetzten Geräte sind Pico 2 W; die Kompatibilität des vollständigen Systems mit RP2040-Picos bleibt durch Hardwaretests nachzuweisen.

### Nächste Schritte

- Aktualisierten `adapters/sd_storage.py` auf einem neuen Pico übertragen und erneut starten.
- Vor dem vollständigen Funktionstest `time_epoch_utc` in der jeweiligen `config.json` setzen.
- Bei erneutem `MemoryError` den genauen Startabschnitt über serielle Diagnose bestimmen und weitere Module bedarfsgerecht laden.



## 10.09.2026 - RP2040-LoRa-Speicheranalyse

### Durchgeführte Arbeiten

- Startdiagnose ergänzt und den MemoryError beim Import des LoRa-Adapters eingegrenzt.
- Größe der SX1262-Quelltreiber geprüft: insgesamt 76.555 Byte.
- _sx126x.py, sx126x.py und sx1262.py mit dem offiziellen, zu CircuitPython 10.3.0 passenden mpy-cross kompiliert.
- Kompakte RP2040-Treiber unter firmware/rp2040/lib/ abgelegt.

### Ergebnisse und Erkenntnisse

- Der OLED-Start und die Startdiagnose funktionieren auf mindestens einem RP2040-Pico.
- Der RP2040 scheitert beim Laden des SX1262-Quelltreibers mit einem MemoryError.
- Die kompilierten Treiber umfassen zusammen 34.751 Byte. Die tatsächliche Speicherwirkung ist noch auf Hardware zu prüfen.

### Nächste Schritte

- Auf einem neuen RP2040-Pico die drei LoRa-.py-Treiber durch die passenden .mpy-Dateien ersetzen.
- Mit gültiger Zeitreferenz erneut starten und den LoRa-Adaptertest dokumentieren.
- Bei erfolgreichem Start LoRa-Senden und -Empfangen erst mit einem gesicherten Testaufbau prüfen.

## 17.09.2026 - Mesh-Test, Standorteinfluss und erste Dauerlaufbeobachtung

### Durchgeführte Arbeiten

- Statische Mesh-Kette `C03 -> C02 -> C01 -> M01` mit vier Geraeten in getrennten Raeumen betrieben.
- Beobachtungszeitraum um 14:10 Uhr begonnen und ACK- sowie Nachsendeverhalten verfolgt.
- Den Standort von C03 nach einem fehlenden ACK geaendert. Die abschliessende Anordnung lautete: C03 Erdgeschoss, C02 erstes Obergeschoss, C01 zweites Obergeschoss und M01 erstes Obergeschoss.
- ACK-Timeout fuer die Hardwarebeobachtung zuvor auf 15.000 ms gesetzt.
- Neues Testprotokoll fuer Mesh-Kommunikation und Stabilitaet angelegt.

### Ergebnisse und Erkenntnisse

- C02 konnte seine ausstehenden Datensaetze nach Neustart von C01 vollstaendig nachsenden.
- C03 meldete mindestens einmal ein fehlendes ACK fuer Sequenz 241. Nach dem Standortwechsel wurde Sequenz 246 entlang der gesamten Kette gesendet, zentral gespeichert und bei C03 bestaetigt.
- C02 und C03 uebertrugen nach Nutzerbeobachtung anschliessend alle ausstehenden Datensaetze.
- Die Funkqualitaet haengt sichtbar von der Platzierung ab. Metall, Decken und weitere Hindernisse wurden nicht einzeln als Ursache nachgewiesen.
- Die sichtbare Master-CSV wirkte lueckenlos. Die formale Auswertung steht noch aus. Das Datum schien nach Mitternacht nicht fortzulaufen; dieses Verhalten ist noch nicht anhand der Rohdaten rekonstruiert.

### Probleme und offene Punkte

- C01 meldete einen SD-bezogenen `Error 5`; der vollstaendige Fehlertext und damit die genaue Fehlerquelle wurden nicht gesichert.
- M01 meldete `LoRa receive setup failed: -1`. Der weitere Empfang nach dem Fehler ist nicht bestaetigt.
- Das OLED von C02 gab keine neue sichtbare Ausgabe mehr aus. Ein reiner Displayfehler und ein Controllerstillstand sind noch nicht unterschieden.
- Der Beobachtungszeitraum ist wegen Standortwechseln und Fehlern kein bestandener 24-Stunden-Stabilitaetsnachweis.

### Nächste Schritte

- Master-CSV formell auf Anzahl, Luecken und Duplikate je Geraet auswerten.
- SD-Fehler auf C01, LoRa-Fehler auf M01 und OLED-Verhalten von C02 getrennt untersuchen.
- Nach den Korrekturen einen neuen, unveraenderten 24-Stunden-Test starten.

## 18.09.2026 - Eigene Master-Messung und Zeitfuehrung vorbereitet

### Durchgeführte Arbeiten

- Master-Controller um die eigene SEN66-Messung im konfigurierten 15-Minuten-Rhythmus erweitert.
- Sensoransteuerung in einen nicht blockierenden Start- und Abfrageablauf aufgeteilt, damit M01 waehrend der SEN66-Aufwaermzeit weiter Funkpakete bearbeiten kann.
- Eigene Masterdaten mit getrenntem Sequenzstand unter Geraete-ID M01 in der vorhandenen Speicherstruktur vorgesehen.
- Zeitadapter fuer UTC-Ausgabe, Kalenderuebergaenge und Weiterverwendung der internen CircuitPython-Uhr nach Software-Neustarts erweitert.
- Firmware fuer CircuitPython 10.3.0 neu kompiliert; Update- und Testanleitung erstellt.

### Ergebnisse und Erkenntnisse

- 120 lokale Unit-Tests waren erfolgreich, darunter Tests fuer Tages-/Monats-/Jahreswechsel, Master-Speicherung, Sequenzfortsetzung, Empfang waehrend der Sensoraufwaermzeit, Speicherwiederholung und Sensorfehler.
- Die Implementierung ist noch nicht auf den Picos installiert und nicht auf Hardware bestaetigt.
- Ohne erhaltene interne Uhr oder externe Zeitquelle kann nach vollstaendigem Stromverlust keine reale ausgeschaltete Zeit rekonstruiert werden.

### Nächste Schritte

- Zusammengehoerige Dateien auf M01 und den betroffenen Relay-Geraeten installieren und den Masterstart kontrollieren.
- Eigene M01-Messung, gleichzeitigen Slave-Empfang und Tageswechsel auf Hardware testen.
- Die noch offenen LoRa-, SD- und OLED-Fehler vor einem neuen Dauerlauf untersuchen.

## 21.09.2026 - Bodenfeuchtesensor angeschlossen und ADC-Signal untersucht

### Durchgeführte Arbeiten

- Den DFRobot Waterproof Capacitive Soil Moisture Sensor V2.0 identifiziert.
- Einen isolierten ADC-Test fuer `GP26`, `GP27` und `GP28` vorbereitet und auf
  dem betreffenden Pico ausgefuehrt.
- Anschlussbelegung mit Herrn Schnabel abgestimmt: Rot an `+3.3V`, Gelb an
  `ADC`, ein schwarzer Leiter an `GND`; der zweite schwarze Leiter ist eine
  Abschirmung und bleibt frei.
- Messungen sowohl mit dem Sensor in Luft als auch im Wasser wiederholt.
- Den normalen Start nach direkter serieller Testausfuehrung durch Neustart
  wiederhergestellt; die OLED-Anzeige erschien anschliessend wieder.

### Ergebnisse Und Erkenntnisse

- Laut Herrn Schnabel ist der ADC-Anschluss der Tragerplatine mit `GP27`
  verbunden. Derselbe Pin wird auch vom optionalen DS18B20 verwendet.
- Die Messwerte auf `GP27` lagen in den bisherigen Vergleichsmessungen nur
  bei etwa 0 bis 0,02 V und unterschieden sich nicht reproduzierbar zwischen
  Luft und Wasser.
- Ein belastbarer Bodenfeuchtewert und eine Kalibrierung in Prozent liegen
  daher noch nicht vor.

### Probleme Und Offene Punkte

- Es ist nicht geklaert, warum trotz der abgestimmten Anschlussbelegung kein
  verwertbares ADC-Signal ankommt. Daraus wird kein Hardwaredefekt abgeleitet.
- Die produktive Bodenfeuchteintegration bleibt bis zu einem reproduzierbaren
  Hardwarewert offen.

### Nächste Schritte

- Signalweg und Versorgung bei einem weiteren Hardwaretermin gezielt pruefen.
- Nach erfolgreicher Luft-/Wasser-Messung Trocken- und Nassreferenz erfassen
  und die Prozentkalibrierung implementieren.

## 22.09.2026 - Zentrale Diagnoseereignisse implementiert

### Durchgeführte Arbeiten

- Das elffeldrige routingfaehige V1-Diagnosepaket `E` mit Ereigniscode,
  Zustand und Wiederholungsanzahl implementiert.
- Master-Empfang fuer Diagnoseereignisse ergaenzt und die zentrale Ablage unter
  `/diagnostics/<device_id>/events.csv` umgesetzt.
- Aktive Diagnosezustaende werden beim Masterstart aus vorhandenen
  Ereignisdateien rekonstruiert; identische `STARTED`-Pakete werden nicht
  erneut gespeichert.
- Den vorhandenen No-SD-Betrieb des Slaves um ein einmaliges
  `SLAVE_SD_UNAVAILABLE`-Ereignis erweitert.
- Unit-Tests fuer Codec, Master-Empfang, Deduplizierung, Speicherung und
  Wiederanlaufzustand ergaenzt.

### Ergebnisse Und Erkenntnisse

- 123 lokale Unit-Tests waren erfolgreich.
- Messdaten und Diagnoseereignisse werden getrennt gespeichert; ein
  Diagnoseereignis erhaelt bewusst kein eigenes ACK.
- Die Ereignisinfrastruktur akzeptiert die spezifizierten Codes. Als erster
  konkreter Ausloeser ist der bereits vorhandene No-SD-Pfad angeschlossen.

### Probleme Und Offene Punkte

- Sensor-, Funk- und Schreibfehler muessen schrittweise als weitere
  Ereignisausloeser an die neue Infrastruktur angebunden werden.
- Der Hardwaretest von `E`-Paketen steht aus.
- Fuer die RP2040-Geraete C02 und C03 muessen die geaenderten Quellen vor der
  Installation noch mit passendem `mpy-cross` kompiliert werden.

### Nächste Schritte

- `SLAVE_SD_UNAVAILABLE` im direkten Master-Slave-Aufbau auf Hardware testen.
- Danach den Fehlerpfad fuer fehlgeschlagenes lokales Schreiben anbinden.
- `NO_PACKET`-Lueckenlogik auf den Pico-Geraeten mit einer absichtlich
  unterbrochenen Verbindung nachweisen.

### vorläufige Arbeitsentscheidungen

- `NO_PACKET`-Luecken sind fuer die fachliche Datenauswertung vorlaeufig. Ein
  spaeter eindeutig zuordenbarer nachgesendeter Messdatensatz ersetzt die
  Luecke; nur dauerhaft nicht gelieferte Daten bleiben als Luecke sichtbar.
- Die Zuordnung erfolgt intern ueber die beim Lueckenzeitpunkt erwartete
  Sequenznummer. Die CSV-Zeile selbst bleibt fachlich als `NA`/`NO_PACKET`
  markiert, bis der echte Datensatz sie ersetzt.

## 23.09.2026 - Statusflags Fuer Fehlerfaelle Ergaenzt

### Durchgeführte Arbeiten

- Die Statusflag-Konstanten zentral im Messdatenmodell zusammengefuehrt.
- DS18B20-Lesefehler so erweitert, dass sie `SOIL_TEMPERATURE_ERROR` und
  `MEASUREMENT_MISSING` im Datensatz setzen.
- Lokalen Slave-SD-Schreibfehler an den sicheren No-SD-Betrieb angebunden;
  der weitergesendete Datensatz enthaelt `SLAVE_SD_WRITE_ERROR` und
  `SLAVE_SD_UNAVAILABLE`.
- Unit-Tests fuer beide Fehlerpfade ergänzt.

### Ergebnisse Und Erkenntnisse

- 129 lokale Unit-Tests erfolgreich ausgefuehrt.
- Nicht konfigurierte optionale Bodensensoren bleiben weiterhin ohne Fehlerbit
  als `NA` sichtbar.

### Probleme Und Offene Punkte

- Die Bodenfeuchtemessung ist noch nicht integriert; daher kann
  `SOIL_MOISTURE_ERROR` noch nicht produktiv gesetzt werden.
- Plausibilitaetsgrenzen und eine verbindliche Zeitsynchronisation fehlen noch.

### Nächste Schritte

- Neue Statusflags zusammen mit dem V1-Diagnoseformat auf Hardware testen.

## 23.09.2026 - Excel-Auswertung Fuer Diagnoseereignisse Ergaenzt

### Durchgeführte Arbeiten

- Die Master-CSV um feste Auswertungsspalten `restart_count`,
  `sd_write_error_count` und `diagnostics` erweitert.
- Diagnoseereignisse mit einer Bezugssequenz werden beim Speichern des
  zugehoerigen Messdatensatzes in diese Spalten zusammengefasst.
- Bestehende Master-Dateibloecke werden beim Start atomar auf die neue
  Kopfzeile erweitert; alte Messzeilen erhalten die Standardwerte `0`, `0`
  und leer.
- Einmaliges `DEVICE_RESTARTED`-Ereignis beim Slave-Start implementiert.

### Ergebnisse Und Erkenntnisse

- Messwerte bleiben eine feste Zeile pro Sequenz und eignen sich dadurch
  direkt fuer Excel-Diagramme.
- Die vollstaendige, nicht zusammengefasste Ereignishistorie bleibt getrennt
  in `/diagnostics/<device_id>/events.csv` erhalten.
- 131 lokale Unit-Tests erfolgreich ausgefuehrt.

### Nächste Schritte

- Diagnoseuebertragung und die drei Auswertungsspalten auf Master und Slave
  auf realer Hardware pruefen.

## 23.09.2026 - Zeitfortsetzung Aus Der Lokalen CSV Implementiert

### Durchgeführte Arbeiten

- Beim Start die letzte gueltige Messzeit des eigenen Geraets aus der
  sequenzbasierten CSV ermitteln.
- Die naechste Zeitbasis als letzte Messzeit plus Messintervall erzeugen.
- Fortgesetzte Zeitwerte mit `TIME_UNSYNCED` markieren, aber weiterhin in der
  CSV speichern, damit Excel die Zeitreihe ohne Neustart-Rueckspruenge
  darstellen kann.
- Unit-Tests fuer Tageswechsel, Speicherabfrage und Zeitfortsetzung ergänzt.

### Ergebnisse Und Erkenntnisse

- Aus `2026-09-18T23:51:00Z` wird nach Neustart bei 15 Minuten Intervall
  `2026-09-19T00:06:00Z`.
- 134 lokale Unit-Tests erfolgreich ausgefuehrt.

### Probleme Und Offene Punkte

- Die ausgeschaltete reale Zeit bleibt ohne RTC oder Synchronisation
  unbekannt; der fortgesetzte Zeitwert ist daher nur chronologisch belastbar.

### Nächste Schritte

- Zeitfortsetzung mit einem realen Pico-Neustart und einem Tageswechsel testen.

## 23.09.2026 - Konfigurierbare Plausibilitaetspruefung Implementiert

### Durchgeführte Arbeiten

- Hardwareunabhaengige Plausibilitaetsregel im Domain-Kern ergänzt.
- `plausibility_limits` in der Konfiguration validiert: bekannte Messfelder
  sowie genau ein numerisches Minimum und Maximum je Feld.
- Master und Slave markieren Werte ausserhalb der konfigurierten Grenzen mit
  `MEASUREMENT_IMPLAUSIBLE`, ohne den Messwert zu verändern oder zu verwerfen.
- Alle Konfigurationsvorlagen um einen leeren vorbereiteten
  `plausibility_limits`-Block ergänzt.

### Ergebnisse Und Erkenntnisse

- 136 lokale Unit-Tests erfolgreich ausgefuehrt.
- Konkrete Grenzwerte wurden bewusst nicht erfunden; bis zur Bestaetigung der
  Sensorversionen bleibt die Standardkonfiguration leer.

### Nächste Schritte

- Datenblattwerte mit Herrn Schnabel abstimmen und anschliessend als
  versionskontrollierte Grenzen in die jeweiligen Geraetekonfigurationen
  eintragen.

## 24.09.2026 - Resetablauf Fuer Stabilitaetstests Dokumentiert

### Durchgeführte Arbeiten

- Anleitung fuer Dauerlauf ohne Reset und fuer einen bewusst neuen Testlauf
  ab Sequenz `0` erstellt.
- Konsistente Behandlung von Messdaten, Diagnoseereignissen, Sequenzzustand,
  Warteschlange und CSV-basierter Zeitfortsetzung dokumentiert.

### Ergebnisse Und Erkenntnisse

- Ein Teilreset nur des Masters oder eines einzelnen Slaves ist fuer einen
  sauber abgegrenzten Testlauf ungeeignet.
- Ein automatisches Reset-Skript auf den Picos wurde bewusst nicht angelegt,
  damit produktive Daten nicht versehentlich geloescht werden.

### Nächste Schritte

- Vor dem 24-Stunden-Test Variante A oder B der Reset-Anleitung festlegen und
  die Startwerte im Testprotokoll dokumentieren.

## 24.09.2026 - Betriebsanleitung Fuer Pico Und Software Erstellt

### Durchgeführte Arbeiten

- Betriebsanleitung fuer Softwareuebertragung, Konfiguration, Startreihenfolge,
  Datenablage, Auswertung, Neustart, Stabilitaetstest und Fehlersuche erstellt.
- Rollen von Master, Slave und optionalem statischem Relay fuer den praktischen
  Betrieb zusammengefasst.

### Ergebnisse Und Erkenntnisse

- Die Betriebsanleitung trennt den normalen Betrieb, Fehlerdiagnose und den
  bewusst destruktiven Reset eines neuen Testlaufs.
- Die Anleitung verweist auf Datenformat, Zeitfuehrung, Resetablauf und
  vorhandenes Mesh-Testprotokoll statt deren Inhalte zu duplizieren.

### Nächste Schritte

- Anleitung beim naechsten Pico-Update neben die Geraete legen und gegen den
  echten Installationsablauf pruefen.

## 25.09.2026 - Getrennte MPY-Firmwarepakete Und Integritaetspruefung

### Durchgeführte Arbeiten

- Reproduzierbaren Build fuer vorkompilierte CircuitPython-Module erstellt.
- Zwei getrennte Firmwarepakete aufgebaut: `firmware/rp2040/` fuer C02/C03
  mit CircuitPython 10.3.0 und `firmware/rp2350/` fuer C01/M01 mit
  CircuitPython 10.2.1.
- Die Firmwarepakete enthalten den aktuellen Stand von `code.py` sowie der
  Ordner `adapters/`, `application/`, `domain/` und `ports/` als `.mpy`.
- Die jeweilige `sources.json` dokumentiert Profil, Compiler-Version und
  SHA-256-Pruefsummen der Ausgangsdateien.
- Unit-Test `test_firmware_packages.py` ergänzt. Er erkennt, wenn Quellcode
  und eines der Firmwarepakete nicht mehr denselben Stand haben.
- OLED-Start an das Verhalten des zuvor funktionierenden Programms angepasst:
  Der SH1106 wird mit `display.sleep(False)` aktiviert.

### Ergebnisse Und Erkenntnisse

- 137 lokale Unit-Tests erfolgreich ausgefuehrt.
- Die Pakete sind versionsgetrennt und duerfen nicht zwischen RP2040 und
  RP2350 ausgetauscht werden.
- `code.py` bleibt als Python-Datei auf CIRCUITPY; nur die importierten
  Projektmodule werden als `.mpy` installiert.

### Probleme Und Offene Punkte

- Beim Master M01 trat weiterhin ein `MemoryError` bei der SD-Initialisierung
  auf (Zuweisung von 4096 Bytes). Der Hardwaretest mit der zuletzt gebauten
  RP2350-Firmware steht noch aus.
- Die serielle Ausgabe von M01 ist aktuell nicht lesbar. Die Anzeige des
  OLED-Tests und des angepassten OLED-Starts muss noch auf Hardware bestaetigt
  werden.

### Nächste Schritte

- RP2350-Firmware auf M01 mit gesicherter Konfiguration erneut installieren.
- OLED-Start, SD-Mount und anschliessend LoRa-Initialisierung auf M01 testen.
- Bei erneutem Speicherfehler den Startpfad weiter reduzieren und den genauen
  Fehlerzeitpunkt dokumentieren.

## 01.10.2026 - Masterstart Nach SD-I/O-Fehler Abgesichert

### Durchgeführte Arbeiten

- Den Startfehler von M01 per serieller Ausgabe bis zum SD-Speicheradapter und
  zur Zeitinitialisierung eingegrenzt.
- Fehlerhafte bzw. nicht lesbare Bestandsdateien im bisherigen CSV-Archiv als
  Ursache fuer den blockierten Start identifiziert.
- Den normalen Startpfad so angepasst, dass vorhandene Archivdaten nicht mehr
  vollstaendig durchsucht oder migriert werden. Der persistierte
  Geraetezustand wird weiterhin geladen.
- Den Zugriff auf den letzten Messzeitstempel fehlertolerant gestaltet: Bei
  nicht lesbaren Altdaten wird die konfigurierte Zeitbasis verwendet.
- RP2040- und RP2350-Firmwarepaket neu erzeugt und den RP2350-Stand auf M01
  getestet.

### Ergebnisse Und Erkenntnisse

- M01 startete im Hardwaretest erfolgreich bis `master M01 started`.
- SD-Karte, LoRa, OLED, DS18B20 und SEN66 wurden dabei initialisiert.
- Die 137 lokalen Unit-Tests waren nach der Anpassung erfolgreich.
- Eine fehlerhafte historische CSV-Datei blockiert den laufenden Messbetrieb
  nicht mehr.

### Probleme Und Offene Punkte

- Die betroffene alte CSV-Datei auf der SD-Karte wurde nicht veraendert. Sie
  muss vor einer separaten Analyse oder Bereinigung gesichert werden.
- Die vollstaendige Archivpruefung ist kein Teil des normalen Geraetestarts
  mehr und soll nur als geplanter Wartungsvorgang erfolgen.

### Nächste Schritte

- Stabilitaetstest fortsetzen und pruefen, ob neue Messdaten in der aktuellen
  Monatsdatei abgelegt werden.
- Historische CSV-Datei getrennt sichern und untersuchen.

## 02.10.2026 - ADC-Test Abgeschlossen Und Energiemessung Vorbereitet

### Durchgeführte Arbeiten

- ADC-Test auf M01 so korrigiert, dass GP27 als ADC1 nicht mehrfach belegt
  wird und der berechnete Wert ausgegeben wird.
- Ausgabe des ADC1-Tests auf Hardware verifiziert. Anschliessend die normale
  RP2350-Mastersoftware wiederhergestellt und den Start bis
  `master M01 started` geprueft.
- Strommessgeraet fuer den anstehenden Energie- und Akkulaufzeittest
  bereitgestellt.
- Einen weiteren Pico mit Gehaeuse und Akku erhalten.
- Datierte Messwertvorlage fuer die Strommessung angelegt.

### Ergebnisse Und Erkenntnisse

- ADC1 wird im Testprogramm ausgegeben; auf GP27 lagen Werte von etwa
  0,001 bis 0,015 V vor.
- Der berechnete Prozentwert ist mit den aktuellen Grenzwerten dauerhaft
  100 Prozent und noch keine belastbare Bodenfeuchte-Kalibrierung.
- M01 befindet sich nach dem Test wieder im normalen Masterbetrieb.

### Probleme Und Offene Punkte

- Der niedrige GP27-Wert weist weiterhin auf einen offenen Signalweg- oder
  Versorgungsbefund beim Bodenfeuchtesensor hin.
- Konkrete Strom- und Leistungswerte sowie die Akkukapazitaet sind noch zu
  messen beziehungsweise zu erfassen.

### Nächste Schritte

- Strom in den Betriebsphasen Start, Warten, Messung, SD-Schreiben und
  LoRa-Uebertragung messen und in die vorbereitete CSV eintragen.
- Neuen Pico mit `boot_out.txt`, Hardwarezustand und geplanter Verwendung
  erfassen, bevor eine Rolle oder Geraete-ID vergeben wird.

## Vorlage für Weitere Einträge

## TT.MM.JJJJ - Kurzer Titel

### Durchgeführte Arbeiten

- 

### Ergebnisse Und Erkenntnisse

- 

### vorläufige Arbeitsentscheidungen

- 

### Probleme Und Offene Punkte

- 

### Nächste Schritte

-
