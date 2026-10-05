# Schritt-fuer-Schritt-Anleitung Fuer Den Hardwaretermin Am 11.08.2026

Diese Anleitung ist fuer die praktische Durchfuehrung am 11.08.2026 gedacht. Sie erklaert nicht nur, **was** zu tun ist, sondern auch **warum**. Bei Unsicherheit gilt: nichts ueberschreiben oder neu installieren, sondern zuerst den vorhandenen Zustand sichern und Herrn Schnabel fragen.

## 1. Was Bereits Sicher Ist

- Herr Schnabel bringt zwei Geraete mit und ist ab 08:00 Uhr da.
- Der vorhandene `code.py` ist fuer CircuitPython geschrieben.
- Der vorhandene Code misst Sensordaten und speichert sie auf einer SD-Karte.
- Der produktive Code enthaelt noch keine LoRa-Kommunikation.
- Fuer einen getrennten LoRa-Test sind ein Sender- und ein Empfaengerprogramm vorbereitet.
- Die geplante LoRa-Hardware ist das Waveshare Pico-LoRa-SX1262-868M.

## 2. Was Noch Nicht Sicher Ist

- Ob auf beiden mitgebrachten Picos momentan CircuitPython installiert ist.
- Welche genaue Pico-Variante verwendet wird.
- Welche CircuitPython-Version installiert ist.
- Ob der vorhandene `code.py` auf beiden Geraeten identisch ist.
- Ob beide Geraete vollstaendig aufgebaut sind und funktionieren.
- Ob zwei SX1262-Module und zwei passende 868-MHz-Antennen vorhanden sind.
- Ob die reale Pinbelegung genau den bisherigen Unterlagen entspricht.
- Ob GP26 gleichzeitig vom Bodenfeuchtesensor und vom Anschluss `BAT_AD` des LoRa-Moduls betroffen ist.

Diese Punkte werden beim Termin geprueft. Sie duerfen vorher nicht als bestaetigte Tatsachen behandelt werden.

## 3. Die Wichtigsten Begriffe

### Pico

Der Raspberry Pi Pico ist ein Mikrocontroller. Er besitzt kein normales Betriebssystem wie Windows oder Linux.

### Firmware

Die Firmware ist die grundlegende Software auf dem Pico. Sie bestimmt, welche Programme der Pico ausfuehren kann. Ein Pico kann eine Python-Datei nicht allein aufgrund der Dateiendung ausfuehren.

### CircuitPython

CircuitPython ist eine moegliche Firmware fuer den Pico. Sie enthaelt den Python-Interpreter und fuehrt normalerweise automatisch die Datei `code.py` im Hauptverzeichnis aus.

Der vorhandene Projektcode verwendet typische CircuitPython-Module wie `board`, `busio`, `analogio`, `displayio`, `sdcardio` und `storage`. Deshalb benoetigt dieser Code eine passende CircuitPython-Firmware und die benoetigten Bibliotheken.

**Wichtig:** Daraus folgt nur, dass der Code fuer CircuitPython geschrieben wurde. Es beweist nicht, dass CircuitPython bereits auf den beiden mitgebrachten Picos installiert ist.

### CIRCUITPY

`CIRCUITPY` ist der Name des USB-Laufwerks, das normalerweise erscheint, wenn auf einem angeschlossenen Pico CircuitPython laeuft. Auf diesem Laufwerk liegen beispielsweise:

- `code.py`
- `boot_out.txt`
- der Ordner `lib/`
- eventuell `settings.toml`

`CIRCUITPY` ist weder das Git-Repository auf dem Laptop noch die externe SD-Karte des Climate Cubes.

### boot_out.txt

In `boot_out.txt` stehen Informationen ueber die installierte CircuitPython-Version und das erkannte Board. Die Datei dient nur zur Identifikation und soll nicht veraendert werden.

### Serielle Konsole

Die serielle Konsole zeigt Textausgaben und Fehlermeldungen des laufenden Programms an. Die Python-Datei wird nicht in der Konsole gestartet. Sie liegt als `code.py` auf `CIRCUITPY` und wird dort vom Pico ausgefuehrt.

## 4. Was Du Mitbringen Beziehungsweise Bereithalten Solltest

- Laptop und Ladegeraet
- das lokale Git-Repository mit dem aktuellen Stand
- VS Code mit installiertem Serial-Monitor
- nach Moeglichkeit ein Micro-USB-Datenkabel
- nach Moeglichkeit einen SD-Kartenleser
- ausreichend freien Speicher fuer Sicherungen, Fotos und Konsolenausgaben

Herr Schnabel bringt voraussichtlich die beiden Geraete und das benoetigte Zubehoer mit. Trotzdem vor Beginn klaeren, ob Datenkabel und passende Antennen vorhanden sind.

## 5. Grundregeln Vor Dem Start

1. Immer nur ein unbekanntes Geraet nach dem anderen anschliessen.
2. Noch keine Firmware installieren oder aktualisieren.
3. Noch keine Datei auf dem Pico ersetzen.
4. Zuerst den vorhandenen Stand sichern.
5. LoRa niemals ohne passende angeschlossene Antenne senden lassen.
6. Verkabelung nur veraendern, wenn das Geraet spannungsfrei ist.
7. Bei Hitze, Geruch, USB-Abbruechen oder unklarer Versorgung sofort trennen.

## 6. Ablauf Fuer Geraet 1

### Schritt 1: Geraet Kennzeichnen Und Fotografieren

1. Das erste Geraet vorlaeufig als `Geraet 1` kennzeichnen.
2. Ober- und Unterseite fotografieren.
3. Beschriftungen von Pico, LoRa-Modul und Antenne fotografieren.
4. Kabel und angeschlossene Sensoren fotografieren.
5. Herrn Schnabel fragen, welche Rolle das Geraet bisher hat oder spaeter haben soll.

Noch keine Kabel oder Module umstecken.

### Schritt 2: Geraet Per USB Anschliessen

1. Eine gegebenenfalls vorhandene LoRa-Antenne korrekt anschliessen, bevor spaeter gesendet wird.
2. Das Geraet mit einem **USB-Datenkabel** an den Laptop anschliessen.
3. Einige Sekunden warten.
4. Im Dateimanager nachsehen, ob ein neues Laufwerk erscheint.

Danach gibt es drei wichtige Faelle.

#### Fall A: Das Laufwerk `CIRCUITPY` Erscheint

Das ist ein starker Nachweis, dass aktuell CircuitPython laeuft.

Weiter mit Schritt 3. Noch nichts auf das Laufwerk kopieren.

#### Fall B: Das Laufwerk `RPI-RP2` Erscheint

Der Pico befindet sich im Bootloader-Modus. Das bedeutet nicht automatisch, dass CircuitPython defekt oder nicht installiert ist. Moeglicherweise wurde beim Anschliessen die BOOTSEL-Taste gedrueckt.

1. Geraet wieder trennen.
2. Darauf achten, dass BOOTSEL nicht gedrueckt ist.
3. Normal erneut anschliessen.
4. Falls wieder `RPI-RP2` erscheint: nichts auf das Laufwerk kopieren und den Zustand mit Herrn Schnabel besprechen.

#### Fall C: Kein Neues Laufwerk Erscheint

Das beweist ebenfalls noch nicht, dass der Pico defekt ist. Moegliche Ursachen sind beispielsweise ein reines Ladekabel, eine andere Firmware, ein USB-Problem oder eine fehlende Laufwerksfreigabe.

1. Pruefen, ob das Kabel Daten uebertragen kann.
2. Wenn vorhanden, einen anderen USB-Port oder ein anderes Kabel testen.
3. Im Serial-Monitor pruefen, ob trotzdem ein serieller Anschluss erscheint.
4. Keine Firmware installieren, solange der vorhandene Zustand nicht geklaert ist.

### Schritt 3: Vorhandenen Pico-Inhalt Sichern

Nur wenn `CIRCUITPY` sichtbar ist:

1. Auf dem Laptop einen Sicherungsordner fuer `Geraet 1` anlegen.
2. Den gesamten Inhalt von `CIRCUITPY` in diesen Ordner kopieren.
3. Pruefen, ob mindestens `code.py`, `boot_out.txt` und `lib/` in der Sicherung enthalten sind.
4. Die Sicherung nicht bearbeiten.
5. Falls eine externe SD-Karte vorhanden ist, auch deren bestehenden Inhalt sichern oder zumindest die Dateinamen dokumentieren.

Erst wenn diese Sicherung vorhanden ist, duerfen spaeter Testdateien kopiert werden.

### Schritt 4: Firmware Identifizieren

1. `boot_out.txt` auf `CIRCUITPY` oeffnen.
2. CircuitPython-Version notieren.
3. Board-ID beziehungsweise Board-Bezeichnung notieren.
4. Die Datei nicht veraendern.
5. Inhalt von `lib/` dokumentieren.

Wenn `boot_out.txt` fehlt oder kein `CIRCUITPY` vorhanden ist, wird die Firmware als **noch nicht geklaert** dokumentiert. Nicht raten.

### Schritt 5: Serielle Konsole Oeffnen

1. VS Code oeffnen.
2. Den Serial-Monitor oeffnen.
3. Den zum Pico gehoerenden Anschluss auswaehlen, unter Linux wahrscheinlich `/dev/ttyACM0`.
4. Falls eine Baudrate verlangt wird, `115200` einstellen.
5. Verbindung oeffnen und die Ausgabe beobachten.

Bei CircuitPython ist die eingestellte Baudrate fuer die USB-Konsole meist nicht entscheidend. `115200` ist fuer die Dokumentation und Kompatibilitaet trotzdem eine sinnvolle Einstellung.

Hilfreiche Tasten in einer CircuitPython-Konsole:

- `Strg+C`: laufenden Code unterbrechen und die Eingabeaufforderung `>>>` anzeigen
- `Strg+D`: CircuitPython neu starten und `code.py` erneut ausfuehren

Diese Tasten erst verwenden, nachdem die normale Startausgabe beobachtet wurde.

### Schritt 6: Vorhandenen Code Unveraendert Beobachten

1. Noch den urspruenglichen `code.py` auf dem Pico verwenden.
2. Startausgabe der seriellen Konsole speichern oder fotografieren.
3. Displaymeldungen beobachten.
4. Pruefen, ob der DS18B20 erkannt wird.
5. Pruefen, ob die SD-Karte erkannt wird.
6. Die etwa 60 Sekunden lange Aufwaermphase des SEN66 abwarten.
7. Messwerte und Fehlermeldungen dokumentieren.
8. Auf der SD-Karte pruefen, ob eine neue `log_NNNN.csv` angelegt und ein Datensatz geschrieben wurde.

Wenn der Code einen Fehler meldet, den genauen Fehlertext sichern. Nicht sofort Bibliotheken austauschen, weil der Fehler selbst ein wichtiges Ergebnis ist.

### Schritt 7: Reale Pinbelegung Pruefen

Die Pins nicht nur aus `code.py` ableiten. Kabelverlauf, Platinenbeschriftung und Herstellerunterlagen vergleichen.

Besonders pruefen:

- I2C: GP0 und GP1
- Bodenfeuchtesensor: GP26
- DS18B20: GP27
- SD-Karte: GP16, GP17, GP18 und GP19
- LoRa: GP2, GP3, GP10, GP11, GP12, GP15 und GP20
- `BAT_AD` des LoRa-Moduls: laut bisheriger Unterlage GP26

Der moegliche Konflikt an GP26 muss geklaert werden, bevor Bodenfeuchtesensor und LoRa-Modul gemeinsam betrieben werden.

## 7. Ablauf Fuer Geraet 2

1. Geraet 1 sauber trennen, sofern nicht zwei getrennte Konsolen benoetigt werden.
2. Geraet 2 kennzeichnen und fotografieren.
3. Alle Schritte aus Abschnitt 6 fuer Geraet 2 wiederholen.
4. Eine eigene Sicherung anlegen, auch wenn die Dateien gleich aussehen.
5. Firmware-Versionen, Bibliotheken, Pinbelegung und Fehler beider Geraete vergleichen.

Die Sicherungen duerfen nicht gegenseitig ueberschrieben werden.

## 8. Entscheidung: Darf Der Ping-Pong-Test Gestartet Werden?

Der Test darf nur gestartet werden, wenn alle folgenden Fragen mit Ja beantwortet sind:

- Sind zwei funktionsfaehige Picos vorhanden?
- Laeuft auf beiden eine mit den Testprogrammen kompatible CircuitPython-Version?
- Wurde der bisherige Inhalt beider Picos vollstaendig gesichert?
- Sind zwei SX1262-Module vorhanden und korrekt montiert?
- Ist an jedem sendenden Modul eine passende 868-MHz-Antenne angeschlossen?
- Ist die Pinbelegung bestaetigt?
- Ist der GP26-Konflikt fuer diesen Aufbau ausgeschlossen oder geklaert?
- Liegen `_sx126x.py`, `sx126x.py` und `sx1262.py` passend auf beiden Geraeten unter `lib/`?
- Sind die Funkparameter mit Herrn Schnabel abgestimmt?

Wenn eine Antwort Nein oder Unklar lautet, wird der Ping-Pong-Test verschoben. Die bis dahin gewonnenen Informationen sind trotzdem ein sinnvolles Ergebnis des Termins.

## 9. Ping-Pong-Test Schritt Fuer Schritt

### Empfaenger Vorbereiten

1. Noch einmal pruefen, ob seine Antenne angeschlossen ist.
2. Den urspruenglichen Inhalt des Pico sichern.
3. Die drei SX1262-Bibliotheken in `CIRCUITPY/lib/` kopieren, falls sie dort noch nicht vorhanden sind.
4. `tests/lora_ping_pong/lora_receiver_test.py` auf das Laufwerk `CIRCUITPY` kopieren.
5. Die kopierte Datei auf `CIRCUITPY` in `code.py` umbenennen. Dadurch wird der bisherige `code.py` ersetzt, weshalb die Sicherung zwingend erforderlich ist.
6. Serielle Konsole oeffnen.
7. Auf eine Meldung wie `Warte auf PING ...` achten.

### Sender Vorbereiten

1. Antenne pruefen.
2. Urspruenglichen Inhalt sichern.
3. Dieselben drei Bibliotheken in `CIRCUITPY/lib/` bereitstellen.
4. `tests/lora_ping_pong/lora_sender_test.py` auf dieses `CIRCUITPY` kopieren.
5. Die kopierte Datei dort in `code.py` umbenennen.
6. Eine zweite serielle Konsole fuer dieses Geraet oeffnen.

### Kommunikation Beobachten

1. Zuerst den Empfaenger starten beziehungsweise neu starten.
2. Danach den Sender starten.
3. Der Sender sollte beispielsweise `PING:0000` senden.
4. Der Empfaenger sollte genau dieses `PING:0000` empfangen.
5. Der Empfaenger sollte als Antwort `PONG:0000` senden.
6. Der Sender sollte genau dieses `PONG:0000` empfangen.
7. RSSI, SNR, Statusmeldungen und Fehler dokumentieren.
8. Wenn moeglich mindestens 20 passende Folgen beobachten.

Die Meldung `Gesendet` allein beweist nur, dass der Sender einen Sendeversuch ausgefuehrt hat. Erst das passende empfangene `PONG` weist die Kommunikation in beide Richtungen nach.

### Test Beenden Und Ursprungsstand Wiederherstellen

1. Serielle Ausgaben beider Geraete sichern.
2. Ergebnisse in `tests/lora_ping_pong/TESTPROTOKOLL_LoRa_Ping_Pong.md` eintragen.
3. Testgeraete trennen.
4. Urspruenglichen `code.py` und gegebenenfalls den gesamten gesicherten Inhalt wiederherstellen.
5. Nach dem Wiederherstellen einmal pruefen, ob der urspruengliche Code wieder startet.

## 10. Falls Der Ping-Pong-Test Nicht Moeglich Ist

Dann trotzdem folgende Ergebnisse sichern:

- Fotos und genaue Hardwarebezeichnungen
- sichtbares USB-Laufwerk oder dessen Fehlen
- CircuitPython-Version und Board-ID, sofern feststellbar
- vorhandene Dateien und Bibliotheken
- serielle Startausgabe und Fehler
- reale Pinbelegung
- Anzahl der Module, Antennen und Datenkabel
- offene technische Fragen
- Grund, weshalb der Funkversuch verschoben wurde

Ein nicht ausgefuehrter Test ist kein Fehlschlag, wenn die Voraussetzungen noch nicht sicher geklaert sind. Die dokumentierte Bestandsaufnahme ist die Grundlage fuer den naechsten Arbeitsschritt.

## 11. Kurze Abschlusskontrolle

Vor dem Ende des Termins pruefen:

- [ ] Beide Geraete wurden einzeln dokumentiert.
- [ ] Vorhandene Software wurde vor Aenderungen gesichert.
- [ ] Firmware wurde festgestellt oder als offen markiert.
- [ ] Serielle Ausgaben und Fehler wurden gespeichert.
- [ ] Reale Pinbelegung und GP26 wurden besprochen.
- [ ] Testergebnis oder Grund fuer die Verschiebung ist dokumentiert.
- [ ] Urspruenglicher Zustand wurde wiederhergestellt.
- [ ] Offene Fragen und naechste Schritte wurden mit Herrn Schnabel abgestimmt.
- [ ] Projekttagebuch und Testprotokoll koennen danach aktualisiert werden.

## 12. Wichtigster Merksatz

Der vorhandene Code ist fuer CircuitPython geschrieben. Ob CircuitPython auf einem konkreten mitgebrachten Pico bereits installiert ist, wird erst am Geraet geprueft. Vor dieser Pruefung und einer Sicherung wird keine Firmware installiert und keine bestehende Datei ersetzt.
