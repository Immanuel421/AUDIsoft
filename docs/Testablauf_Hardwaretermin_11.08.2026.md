# Testablauf Hardwaretermin Am 11.08.2026

Projekt: AUDI Climate Cube  
Dokumentstatus: Vorbereiteter Arbeitsablauf, noch ohne Testergebnisse  
Geplanter Termin: 11.08.2026

## 1. Ziel Des Termins

Der Termin dient dazu, den vorhandenen CircuitPython-Prototypen mit der realen Climate-Cube-Hardware abzugleichen. Am Ende sollen folgende Punkte entweder bestaetigt oder als konkrete Abweichung dokumentiert sein:

- genaue Pico-Variante und installierte CircuitPython-Version,
- reale Sensoren, Displays, SD-Kartenmodule und deren Verkabelung,
- tatsaechlich verwendete GPIOs und noch freie GPIOs,
- Verhalten des vorhandenen `code.py` auf der Hardware,
- Funktion von Display, DS18B20, Bodenfeuchtesensor, SD-Karte und SEN66,
- Loesung beziehungsweise weiterer Klaerungsbedarf fuer den Konflikt GP26 / `BAT_AD`,
- Verfuegbarkeit von zwei Picos, zwei SX1262-Modulen und passenden Antennen,
- Voraussetzungen fuer den spaeteren isolierten LoRa-Ping-Pong-Test.

Der Termin ist in erster Linie eine Bestands- und Funktionspruefung. Die produktive LoRa-Integration in `code.py` ist nicht Bestandteil dieses Termins.

## 2. Allgemeine Angaben

| Feld | Eintrag |
|---|---|
| Datum | 11.08.2026 |
| Beginn |  |
| Ende |  |
| Ort |  |
| Anwesende Personen |  |
| Gepruefter Git-Commit |  |
| Verwendeter Rechner |  |
| Ablageort der Nachweise |  |

## 3. Benoetigte Ausstattung

Vor dem Termin soweit moeglich bereitlegen:

- [ ] Climate Cube mit vorhandener Sensorik und SD-Karte
- [ ] USB-Datenkabel und geeignete Stromversorgung
- [ ] Rechner mit VS Code und serieller Konsole
- [ ] Zugriff auf das GitLab-Repository
- [ ] Kartenleser fuer die SD-Karte, sofern vorhanden
- [ ] Datenblatt beziehungsweise Herstellerseite des Waveshare Pico-LoRa-SX1262-868M
- [ ] mindestens eine passende 868-MHz-Antenne je eingeschaltetem LoRa-Modul
- [ ] fuer einen optionalen Ping-Pong-Test zwei Picos, zwei SX1262-Module und zwei Antennen
- [ ] Moeglichkeit fuer Fotos der Platinen, Steckverbindungen und Beschriftungen
- [ ] optional Multimeter fuer Spannungs- und Durchgangspruefungen

## 4. Sicherheits- Und Abbruchregeln

- Verkabelung nur im spannungsfreien Zustand veraendern.
- Vor dem Einschalten Sichtpruefung auf Kurzschluesse, lose Leitungen und vertauschte Versorgung durchfuehren.
- Ein SX1262-Modul nur mit angeschlossener passender Antenne in den Sendebetrieb nehmen.
- GP26 nicht gleichzeitig ungeprueft fuer Bodenfeuchtesensor und `BAT_AD` verwenden.
- Vor Firmware-, Bibliotheks- oder Codeaenderungen den vorhandenen Stand sichern.
- Bei ungewoehnlicher Erwaermung, Geruch, instabiler Versorgung oder wiederholten USB-Abbruechen sofort spannungsfrei schalten.
- Den LoRa-Sendetest auslassen, solange Pinbelegung, Antenne oder Funkparameter nicht ausreichend geklaert sind.

## 5. Geplanter Ablauf

Die Reihenfolge ist verbindlich, soweit die reale Hardware keinen begruendeten anderen Ablauf erfordert.

### Schritt 1: Ausgangsstand Sichern

Noch keine Firmware aktualisieren und keine Bibliotheken austauschen.

- [ ] Repository-Stand und Commit-ID notieren.
- [ ] Inhalt von `CIRCUITPY` sichern oder mindestens `code.py`, `boot_out.txt`, `settings.toml` und `lib/` kopieren.
- [ ] Inhalt der SD-Karte vor dem Test sichern beziehungsweise vorhandene Dateien auflisten.
- [ ] Vorhandene Fehlermeldungen aus der seriellen Konsole sichern.
- [ ] Gesamtaufbau vor Veraenderungen fotografieren.

| Pruefpunkt | Ergebnis / Ablageort |
|---|---|
| Git-Commit |  |
| Sicherung `CIRCUITPY` |  |
| Sicherung SD-Karte |  |
| serielle Startausgabe |  |
| Fotos Ausgangsaufbau |  |

**Abbruchkriterium:** Wenn der vorhandene Stand nicht gesichert werden kann, keine Firmware- oder Codeaenderung vornehmen.

### Schritt 2: Hardware Identifizieren

Hardware zunaechst spannungsfrei erfassen.

- [ ] genaue Pico-Bezeichnung und Board-Revision fotografieren und notieren.
- [ ] Waveshare-Modell und Revision bestaetigen.
- [ ] SEN66, DS18B20, Bodenfeuchtesensor, OLED und SD-Modul identifizieren.
- [ ] Stromversorgung und Akkukonfiguration dokumentieren.
- [ ] Anzahl verfuegbarer Picos, SX1262-Module und Antennen erfassen.
- [ ] weitere Peripherie wie Taster oder Status-LEDs dokumentieren.

| Komponente | Modell / Revision | Anzahl | Bemerkung |
|---|---|---:|---|
| Pico |  |  |  |
| SX1262-Modul |  |  |  |
| Antenne |  |  |  |
| SEN66 |  |  |  |
| DS18B20 |  |  |  |
| Bodenfeuchtesensor |  |  |  |
| OLED |  |  |  |
| SD-Kartenmodul |  |  |  |
| Akku / Versorgung |  |  |  |
| weitere Peripherie |  |  |  |

### Schritt 3: Firmware Und Bibliotheken Erfassen

Den Pico mit dem gesicherten Ausgangsstand verbinden.

- [ ] relevante Zeilen aus `boot_out.txt` uebernehmen.
- [ ] CircuitPython-Version und Board-ID notieren.
- [ ] Inhalt und erkennbare Versionen von `lib/` dokumentieren.
- [ ] freien Speicher auf `CIRCUITPY` feststellen.
- [ ] pruefen, ob der vorhandene Code beim Start Syntax-, Import- oder Speicherfehler meldet.

| Pruefpunkt | Ergebnis |
|---|---|
| CircuitPython-Version |  |
| Board-ID |  |
| Bibliotheksstand |  |
| freier Speicher |  |
| Startfehler |  |

### Schritt 4: Reale Pinbelegung Abgleichen

Jede Verbindung anhand von Platinenbeschriftung, Kabelverlauf und vorhandener Dokumentation bestaetigen. Nicht allein aus `code.py` ableiten.

| Funktion | Signal | Im Code Vorgesehen | Real Bestaetigt / Abweichung |
|---|---|---|---|
| I2C | SDA | GP0 |  |
| I2C | SCL | GP1 |  |
| Bodenfeuchte | Analog | GP26 |  |
| DS18B20 | OneWire | GP27 |  |
| SD-Karte | MISO | GP16 |  |
| SD-Karte | CS | GP17 |  |
| SD-Karte | SCK | GP18 |  |
| SD-Karte | MOSI | GP19 |  |
| SX1262 | BUSY | GP2 |  |
| SX1262 | CS / NSS | GP3 |  |
| SX1262 | CLK | GP10 |  |
| SX1262 | MOSI | GP11 |  |
| SX1262 | MISO | GP12 |  |
| SX1262 | RESET | GP15 |  |
| SX1262 | DIO1 / IRQ | GP20 |  |
| SX1262 | BAT_AD | GP26 laut Modulunterlagen |  |

Zusaetzlich dokumentieren:

- [ ] alle noch freien GPIOs
- [ ] Versorgungsspannungen der Module
- [ ] gemeinsame Masseverbindungen
- [ ] festgelegte Loesung fuer GP26 oder klaren offenen Klaerungspunkt
- [ ] moegliche weitere Pin- oder SPI-Konflikte

**Abbruchkriterium:** Bei ungeklaertem GP26-Konflikt oder widerspruechlicher Versorgung keine betroffenen Komponenten gemeinsam betreiben.

### Schritt 5: Vorhandenen `code.py` Unveraendert Starten

Zuerst den vorhandenen Prototypen ohne LoRa-Integration pruefen.

- [ ] gesicherten `code.py` verwenden.
- [ ] serielle Ausgabe vom Einschalten an mitschneiden.
- [ ] Startmeldungen auf Display pruefen.
- [ ] Meldung zur DS18B20-Erkennung festhalten.
- [ ] Meldung zur SD-Initialisierung festhalten.
- [ ] SEN66-Aufwaermphase und Messausgabe beobachten.
- [ ] Absturz, Neustart, Haengen oder Speicherfehler dokumentieren.

| Teilfunktion | Erwartete Beobachtung | Tatsaechliche Beobachtung | Status |
|---|---|---|---|
| OLED | Startmeldungen werden sichtbar |  | [ ] ok / [ ] Fehler |
| DS18B20 | `DS18B20 gefunden` oder nachvollziehbare Fehlermeldung |  | [ ] ok / [ ] Fehler |
| SD-Karte | `SD ok` und neuer CSV-Dateiname |  | [ ] ok / [ ] Fehler |
| SEN66 | Initialisierung, 60 s Aufwaermen und gueltige Messung |  | [ ] ok / [ ] Fehler |
| Gesamtablauf | kein unkontrollierter Neustart oder Stillstand |  | [ ] ok / [ ] Fehler |

### Schritt 6: Teilfunktionen Und Messwerte Pruefen

#### 6.1 Display

- [ ] Text ist lesbar und korrekt ausgerichtet.
- [ ] Display schaltet wie vorgesehen ein und aus.
- [ ] keine I2C-Fehler in der seriellen Ausgabe.

#### 6.2 DS18B20

- [ ] Sensor wird erkannt.
- [ ] Temperaturwert ist plausibel.
- [ ] Reaktion auf fehlenden Sensor wird nachvollziehbar gemeldet, sofern gefahrlos pruefbar.

#### 6.3 Bodenfeuchtesensor

- [ ] Rohwert beziehungsweise Prozentwert ist plausibel.
- [ ] trockener und feuchter Zustand veraendern den Messwert nachvollziehbar.
- [ ] Kalibrierwerte `DRY` und `WET` werden als vorlaeufig oder bestaetigt markiert.
- [ ] GP26-Konflikt ist vor Betrieb mit dem LoRa-Modul geklaert.

#### 6.4 SD-Karte

- [ ] SD-Karte wird unter `/sd` eingebunden.
- [ ] neue Datei `log_NNNN.csv` wird erstellt.
- [ ] CSV-Kopfzeile ist vollstaendig.
- [ ] mindestens ein Datensatz wird geschrieben und nach Neustart gelesen.
- [ ] vorhandene Daten werden nicht ueberschrieben.
- [ ] Verhalten ohne SD-Karte wird nur geprueft, wenn ein gefahrloses Entfernen im spannungsfreien Zustand moeglich ist.

#### 6.5 SEN66

- [ ] Sensor startet ohne I2C-Fehler.
- [ ] Dummy-Messung und gueltige Messung werden ausgegeben.
- [ ] Temperatur, Luftfeuchtigkeit, CO2, PM1, PM2.5, PM4, PM10, VOC und NOx werden auf Plausibilitaet geprueft.
- [ ] benoetigte Einheiten und tatsaechlich benoetigte Messgroessen werden mit Herrn Schnabel bestaetigt.
- [ ] Verhalten nach `stop_measurement()` wird beobachtet.

| Messwert | Wert / Bereich | Einheit Bestaetigt | Plausibel | Bemerkung |
|---|---|---|---|---|
| Lufttemperatur |  | [ ] | [ ] |  |
| Luftfeuchtigkeit |  | [ ] | [ ] |  |
| CO2 |  | [ ] | [ ] |  |
| PM1 |  | [ ] | [ ] |  |
| PM2.5 |  | [ ] | [ ] |  |
| PM4 |  | [ ] | [ ] |  |
| PM10 |  | [ ] | [ ] |  |
| VOC-Index |  | [ ] | [ ] |  |
| NOx-Index |  | [ ] | [ ] |  |
| Bodenfeuchte |  | [ ] | [ ] |  |
| Bodentemperatur |  | [ ] | [ ] |  |

### Schritt 7: Messintervall Bewerten

Ein vollstaendiger 15-Minuten-Dauerlauf ist nur durchzufuehren, wenn die Terminzeit reicht. Andernfalls das Verhalten aus dem Code und einem kuerzeren, klar gekennzeichneten Test bewerten.

- [ ] Startzeit einer Messung notieren.
- [ ] Ende der Messung notieren.
- [ ] Beginn der Wartezeit notieren.
- [ ] Startzeit der folgenden Messung notieren.
- [ ] pruefen, ob die 900 Sekunden nach Messende statt nach Messstart beginnen.
- [ ] mit Herrn Schnabel klaeren, ob exakt 15 Minuten zwischen Messstarts gefordert sind.

| Zeitpunkt | Uhrzeit / monotone Zeit |
|---|---|
| Start Messung 1 |  |
| Ende Messung 1 |  |
| Start Messung 2 |  |
| Abstand der Messstarts |  |

### Schritt 8: LoRa-Voraussetzungen Pruefen

Dieser Schritt veraendert den produktiven `code.py` noch nicht.

- [ ] Waveshare-Modell und 868-MHz-Ausfuehrung bestaetigt.
- [ ] dokumentierte SX1262-Pins mit realer Hardware abgeglichen.
- [ ] GP26- beziehungsweise `BAT_AD`-Konflikt geklaert.
- [ ] zwei vollstaendige Testgeraete vorhanden.
- [ ] an jedem eingeschalteten Modul passende Antenne angeschlossen.
- [ ] CircuitPython-Kompatibilitaet der Dateien `_sx126x.py`, `sx126x.py` und `sx1262.py` pruefbar.
- [ ] Testfrequenz, Sendeleistung und Testdauer fuer den kurzen Versuch abgestimmt.

### Schritt 9: Optionaler Isolierter Ping-Pong-Test

Nur durchfuehren, wenn alle Voraussetzungen aus Schritt 8 erfuellt sind und ausreichend Zeit bleibt.

1. Produktiven Stand beider Picos sichern.
2. Bibliotheksdateien auf beiden Picos unter `lib/` bereitstellen.
3. Empfaengerprogramm getrennt vom produktiven Code als `code.py` auf Testgeraet 1 einsetzen.
4. Senderprogramm als `code.py` auf Testgeraet 2 einsetzen.
5. Zuerst Empfaenger, danach Sender starten.
6. Testfaelle und Messwerte im separaten Protokoll dokumentieren.
7. Nach dem Test den zuvor gesicherten Stand wiederherstellen.

Verbindliches Detailprotokoll: `../tests/lora_ping_pong/TESTPROTOKOLL_LoRa_Ping_Pong.md`

**Abbruchkriterium:** Bei fehlender Antenne, ungeklaerter Pinbelegung, Initialisierungsfehlern oder ungewoehnlicher Erwaermung nicht senden beziehungsweise Test sofort beenden.

### Schritt 10: Abschluss Und Datensicherung

- [ ] geaenderten Code und geaenderte Bibliotheken eindeutig sichern.
- [ ] serielle Protokolle und Fotos sinnvoll benennen.
- [ ] erzeugte CSV-Dateien sichern.
- [ ] alle Abweichungen zur geplanten Pinbelegung dokumentieren.
- [ ] offene fachliche Entscheidungen Herrn Schnabel zuordnen.
- [ ] keine ungetestete Aenderung als bestaetigte Loesung dokumentieren.
- [ ] Repository nach dem Termin aktualisieren und Aenderungen committen.
- [ ] Projekttagebuch mit Ergebnissen, Problemen und naechsten Schritten ergaenzen.

Empfohlene Dateinamen:

```text
2026-08-11_hardware_uebersicht.jpg
2026-08-11_pinbelegung.jpg
2026-08-11_boot_out.txt
2026-08-11_seriell_bestand.txt
2026-08-11_sd_log_0001.csv
2026-08-11_ping_pong_sender.txt
2026-08-11_ping_pong_empfaenger.txt
```

## 6. Ergebnisbewertung

| Bereich | Bestaetigt | Teilweise Bestaetigt | Nicht Bestaetigt | Bemerkung |
|---|---|---|---|---|
| Board und Firmware | [ ] | [ ] | [ ] |  |
| reale Pinbelegung | [ ] | [ ] | [ ] |  |
| OLED | [ ] | [ ] | [ ] |  |
| DS18B20 | [ ] | [ ] | [ ] |  |
| Bodenfeuchtesensor | [ ] | [ ] | [ ] |  |
| SD-Karte / CSV | [ ] | [ ] | [ ] |  |
| SEN66 | [ ] | [ ] | [ ] |  |
| Messablauf | [ ] | [ ] | [ ] |  |
| LoRa-Voraussetzungen | [ ] | [ ] | [ ] |  |
| optionaler Ping-Pong-Test | [ ] | [ ] | [ ] |  |

Gesamtergebnis:

- [ ] Ausgangsbasis vollstaendig bestaetigt
- [ ] Ausgangsbasis mit dokumentierten Abweichungen nutzbar
- [ ] weitere Hardwareklaerung erforderlich
- [ ] Softwaretest wegen Hardwareproblem blockiert

## 7. Offene Entscheidungen Nach Dem Termin

| Nr. | Entscheidung / Frage | Verantwortlich | Termin | Status |
|---:|---|---|---|---|
| 1 | Loesung GP26 / `BAT_AD` |  |  |  |
| 2 | finale Pinbelegung |  |  |  |
| 3 | benoetigte Messwerte und Einheiten |  |  |  |
| 4 | exaktes Messintervall |  |  |  |
| 5 | Master-Zeitsetzung |  |  |  |
| 6 | freigegebene Funkparameter |  |  |  |
| 7 | Termin fuer Ping-Pong-Test |  |  |  |
| 8 | weitere offene Entscheidung |  |  |  |

## 8. Naechste Technische Schritte

Die naechsten Schritte werden erst nach Auswertung der tatsaechlichen Ergebnisse festgelegt. Voraussichtlich:

1. bestaetigte Pinbelegung und Hardwaredaten in Anforderungen und README uebernehmen,
2. Abweichungen im vorhandenen `code.py` korrigieren,
3. vorhandene Sensor-, Display- und SD-Funktionen stabilisieren,
4. isolierten LoRa-Ping-Pong-Test durchfuehren oder auswerten,
5. erst nach erfolgreichem Funknachweis LoRa in den produktiven Slave-Code integrieren.
