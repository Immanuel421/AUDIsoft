# Testprotokoll SX1262 LoRa Ping-Pong

Dieses Protokoll dokumentiert den isolierten Peer-to-Peer-Funktionstest zwischen zwei Raspberry Pi Picos mit Waveshare Pico-LoRa-SX1262-868M. Der erste Hardwaretest wurde am 11.08.2026 durchgefuehrt.

## 1. Allgemeine Angaben

| Feld | Eintrag |
|---|---|
| Testdatum | 11.08.2026 |
| Testbeginn | ca. 18:50 Uhr |
| Testende | ca. 19:05 Uhr einschliesslich Wiederherstellung |
| Testort | Innenraum, genauer Ort nicht dokumentiert |
| Testperson | Immanuel Mauch |
| Wetter beziehungsweise Umgebung | Kurzer Tischtest bei geringem Abstand und ohne definierte Hindernisse |
| Git-Commit / Softwarestand | `ed18c8b` |

## 2. Testziel

Nachgewiesen werden soll, dass zwei Picos mit identischer LoRa-Konfiguration direkt miteinander kommunizieren koennen:

1. Der Sender uebertraegt ein nummeriertes `PING`-Paket.
2. Der Empfaenger erkennt das Paket und antwortet mit der gleichen Nummer als `PONG`.
3. Der Sender empfaengt die Antwort innerhalb des festgelegten Timeouts.
4. RSSI, SNR, Fehler und auffaellige Paketverluste werden dokumentiert.

Der Test prueft nur die isolierte Funkkommunikation. Sensorik, SD-Karte und produktiver Climate-Cube-Code sind nicht Bestandteil dieses Tests.

## 3. Voraussetzungen Und Sicherheitspruefung

Vor dem Einschalten beider Geraete pruefen:

- [x] An beiden LoRa-Modulen ist eine passende 868-MHz-Antenne angeschlossen.
- [x] Beide Module sind spannungsfrei auf den Picos montiert worden.
- [x] Die fuer den Test verwendete Pinbelegung wurde mit den Herstellerunterlagen verglichen und funktional bestaetigt.
- [x] Auf beiden Picos liegt dieselbe Version von `_sx126x.py`, `sx126x.py` und `sx1262.py` unter `lib/`.
- [x] Der bisherige `code.py` wurde je Geraet unmittelbar vor dem Test gesichert.
- [x] Sender- und Empfaengerprogramm wurden jeweils als `code.py` auf den richtigen Pico kopiert.
- [x] Die seriellen Ausgaben beider Picos wurden getrennt beobachtet und gespeichert.
- [x] Die Funkparameter sind auf beiden Geraeten identisch.
- [ ] Frequenz, Sendeleistung und Testdauer sind fuer den kurzen Test freigegeben beziehungsweise geprueft.

## 4. Testgeraete

### 4.1 Sender

| Eigenschaft | Eintrag |
|---|---|
| Pico-Modell / Board-ID | Raspberry Pi Pico 2 W / `raspberry_pi_pico2_w` |
| Inhalt beziehungsweise relevante Zeile aus `boot_out.txt` | RP2350A, Geraet 2, UID endet auf `84EE` |
| CircuitPython-Version | 10.2.1 vom 13.05.2026 |
| Waveshare-Modell / Revision | Pico-LoRa-SX1262-868M laut Projektvorgabe; Revision nicht erfasst |
| Antenne | 868-MHz-Antenne, genauer Typ nicht erfasst |
| Stromversorgung | USB |
| SX1262-Treiberversion / Quelle | `ehong-tl/micropySX126X`, Repository-Stand `ed18c8b` |
| Auffaelligkeiten | Als `/dev/ttyACM1` verwendet; Initialisierung mit `ERR_NONE` |

### 4.2 Empfaenger

| Eigenschaft | Eintrag |
|---|---|
| Pico-Modell / Board-ID | Raspberry Pi Pico 2 W / `raspberry_pi_pico2_w` |
| Inhalt beziehungsweise relevante Zeile aus `boot_out.txt` | RP2350A, Geraet 1, UID endet auf `A455` |
| CircuitPython-Version | 10.2.1 vom 13.05.2026 |
| Waveshare-Modell / Revision | Pico-LoRa-SX1262-868M laut Projektvorgabe; Revision nicht erfasst |
| Antenne | 868-MHz-Antenne, genauer Typ nicht erfasst |
| Stromversorgung | USB |
| SX1262-Treiberversion / Quelle | `ehong-tl/micropySX126X`, Repository-Stand `ed18c8b` |
| Auffaelligkeiten | Als `/dev/ttyACM0` verwendet; Initialisierung mit `ERR_NONE` |

## 5. Pinbelegung

| SX1262-Signal | Geplanter Pico-Pin | Sender bestaetigt | Empfaenger bestaetigt |
|---|---|---|---|
| BUSY | GP2 | [x] | [x] |
| CS / NSS | GP3 | [x] | [x] |
| CLK | GP10 | [x] | [x] |
| MOSI | GP11 | [x] | [x] |
| MISO | GP12 | [x] | [x] |
| RESET | GP15 | [x] | [x] |
| DIO1 / IRQ | GP20 | [x] | [x] |
| BAT_AD | GP26, im Test unbenutzt | nicht geprueft | nicht geprueft |

Abweichungen von der geplanten Pinbelegung:

```text
Keine Abweichung fuer die im Funkversuch verwendeten Signale festgestellt.
BAT_AD beziehungsweise GP26 war nicht Bestandteil des Funkversuchs.
```

## 6. Funkparameter

Die Werte in der Spalte `Vorbereitet` stammen aus den Testprogrammen und sind vorlaeufig.

| Parameter | Vorbereitet | Tatsaechlich verwendet |
|---|---:|---:|
| Frequenz | 868,1 MHz | 868,1 MHz |
| Bandbreite | 125 kHz | 125 kHz |
| Spreading Factor | 7 | 7 |
| Coding Rate | 4/5 (`cr=5`) | 4/5 (`cr=5`) |
| Sendeleistung | 10 dBm | 10 dBm |
| Praeambellaenge | 8 Symbole | 8 Symbole |
| Sync Word | `0x12` | `0x12` |
| CRC | aktiviert | aktiviert |
| TCXO-Spannung | 1,7 V | 1,7 V |
| Senderintervall | 10 s | 10 s |
| Antwort-Timeout | 3000 ms | 3000 ms |

Begruendung und Freigabe eventueller Abweichungen:

```text
Die Parameter wurden fuer den kurzen Funktionstest unveraendert aus den
vorbereiteten Testprogrammen uebernommen. Eine fachliche beziehungsweise
regulatorische Freigabe fuer den spaeteren Dauer- oder Feldeinsatz ist damit
nicht erfolgt.
```

## 7. Testfaelle

| ID | Testfall | Durchfuehrung | Erwartetes Ergebnis | Status |
|---|---|---|---|---|
| PP-01 | Initialisierung Sender | Sender starten und serielle Ausgabe pruefen | Initialisierung endet mit `ERR_NONE` | bestanden |
| PP-02 | Initialisierung Empfaenger | Empfaenger starten und serielle Ausgabe pruefen | Initialisierung endet mit `ERR_NONE` und wartet auf Pakete | bestanden |
| PP-03 | Einzelnes Ping-Pong | Beide Geraete bei kurzem Abstand betreiben | `PING:0000` wird mit `PONG:0000` beantwortet | bestanden |
| PP-04 | Folge von 20 Paketen | Mindestens 20 Sequenzen bei konstantem Aufbau abwarten | Nummern stimmen ueberein; kein Absturz oder Haengen | mit Dokumentationseinschraenkung bestanden; 21 Paare beidseitig nachgewiesen, verteilt auf mehrere Aufzeichnungen |
| PP-05 | Empfaenger nicht erreichbar | Empfaenger kurz ausschalten und danach wieder starten | Sender meldet Timeout und arbeitet danach weiter | nicht durchgefuehrt |
| PP-06 | Neustart Sender | Sender neu starten, Empfaenger weiterlaufen lassen | Kommunikation startet nach Initialisierung erneut | bestanden |
| PP-07 | Neustart Empfaenger | Empfaenger neu starten, Sender weiterlaufen lassen | Kommunikation wird nach Initialisierung wieder aufgenommen | nicht durchgefuehrt |
| PP-08 | Abstandstest | Abstand schrittweise vergroessern und Bedingungen notieren | Empfangsverhalten, RSSI und SNR sind nachvollziehbar dokumentiert | nicht durchgefuehrt |

## 8. Messreihen

Fuer jede wesentlich andere Entfernung oder Umgebung eine eigene Zeile verwenden.

| Lauf | Abstand | Umgebung / Hindernisse | PING gesendet | PONG empfangen | Verluste | RSSI-Bereich | SNR-Bereich | Fehler / Bemerkungen |
|---:|---:|---|---:|---:|---:|---|---|---|
| 1 | kurzer Tischabstand, nicht vermessen | Innenraum, keine definierten Hindernisse | 21 vollstaendig beidseitig dokumentierte Folgen | 21 | 0 in den vollstaendig dokumentierten Folgen | -35 bis -14 dBm | 11,75 bis 13,25 dB | Mehrere serielle Aufzeichnungslaeufe; Funkkommunikation blieb aktiv |
| 2 |  |  |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |  |  |
| 4 |  |  |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |  |  |

Paketverlust:

```text
Verlust in Prozent = (PING gesendet - PONG empfangen) / PING gesendet * 100
```

## 9. Vorlaeufige Erfolgskriterien

Der erste Funktionstest gilt als bestanden, wenn:

- beide Funkmodule mit `ERR_NONE` initialisiert werden,
- bei kurzem Abstand mindestens 20 aufeinanderfolgende `PING`-Pakete korrekt beantwortet werden,
- jede empfangene `PONG`-Nummer zur vorher gesendeten `PING`-Nummer passt,
- beide Programme ohne Absturz oder dauerhafte Blockierung weiterlaufen,
- ein voruebergehend nicht erreichbarer Empfaenger zu einem nachvollziehbaren Timeout fuehrt,
- Kommunikation nach einem Neustart wieder moeglich ist,
- verwendete Parameter, RSSI, SNR und Fehler im Protokoll festgehalten sind.

Diese Kriterien sind technische Arbeitskriterien fuer den ersten Nachweis und noch keine fachlich freigegebenen Abnahmekriterien.

## 10. Fehler Und Abweichungen

| Nr. | Zeitpunkt / Testfall | Beobachtung | Reproduzierbar | Vermutete Ursache | Weitere Massnahme |
|---:|---|---|---|---|---|
| 1 | PP-04 / serielle Aufzeichnung | In einem Teilaufzeichnungslauf fehlte die Senderausgabe, obwohl der Empfaenger weitere PINGs empfing und PONGs sendete. | ja | Problem der seriellen Aufzeichnung, nicht als Funkfehler bewertet | Weitere beidseitige Aufzeichnung durchgefuehrt; nur vollstaendig nachgewiesene Paare gezaehlt |
| 2 | Vorbereitung | Microsoft Serial Monitor in der VS-Code-Flatpak-Installation zeigte keine Ausgabe. | ja | Zunaechst fehlende `dialout`-Mitgliedschaft; Ansicht blieb danach unzuverlaessig | Benutzer zu `dialout` hinzugefuegt und serielle Ports direkt auf dem Host gelesen |
| 3 | Abschluss | LoRa-Testprogramme ersetzten temporaer den produktiven `code.py`. | nein | notwendiger Testaufbau | Beide produktiven Dateien aus UID-bezogenen Sicherungen wiederhergestellt und byteweise verglichen |
| 4 |  |  |  |  |  |

## 11. Nachweise

- [x] serielle Ausgabe des Senders gespeichert
- [x] serielle Ausgabe des Empfaengers gespeichert
- [x] verwendete `boot_out.txt`-Informationen dokumentiert
- [x] Foto des Senderaufbaus erstellt
- [x] Foto des Empfaengeraufbaus erstellt
- [x] Git-Commit beziehungsweise Softwarestand dokumentiert
- [x] Abweichungen von Pinbelegung oder Funkparametern festgehalten

Ablageorte beziehungsweise Dateinamen der Nachweise:

```text
tests/lora_ping_pong/results/2026-08-11/
Lokale, nicht versionierte Vollsicherungen:
/home/immanuel/Dokumente/ClimateCube_Sicherungen/Geraet1_vor_LoRa_2026-08-11
/home/immanuel/Dokumente/ClimateCube_Sicherungen/Geraet2_vor_LoRa_2026-08-11
```

## 12. Gesamtergebnis

| Bewertung | Auswahl |
|---|---|
| Test bestanden | [ ] |
| Test mit Einschraenkungen bestanden | [x] |
| Test nicht bestanden | [ ] |
| Wiederholung erforderlich | [ ] |

Zusammenfassung:

```text
Die direkte bidirektionale LoRa-Kommunikation zwischen beiden Pico 2 W mit
SX1262 wurde nachgewiesen. Sender und Empfaenger initialisierten mit ERR_NONE.
In mehreren Aufzeichnungen wurden insgesamt 21 vollstaendige PING-/PONG-Paare
mit passenden Sequenznummern und ohne dokumentierten Paketverlust bestaetigt.
Timeout-, Empfaengerneustart- und Abstandstest stehen noch aus.
```

Naechste technische Schritte:

```text
Timeout-Verhalten, Empfaengerneustart und verschiedene Entfernungen testen.
Funkparameter fuer den vorgesehenen Einsatz abstimmen. Danach das LoRa-Protokoll
schrittweise mit Slave-ID, Sequenzverwaltung, ACK und Messdaten integrieren.
```

## 13. Freigaben Und Offene Abstimmungen

| Punkt | Status / Rueckmeldung |
|---|---|
| Pinbelegung auf realer Hardware bestaetigt | Fuer die im Ping-Pong-Test verwendeten SX1262-Signale funktional bestaetigt |
| CircuitPython-Kompatibilitaet bestaetigt | Ja, mit CircuitPython 10.2.1 auf zwei Pico 2 W |
| Funkparameter fuer weitere Tests abgestimmt | Nur fuer kurzen Funktionstest verwendet; weitere Abstimmung offen |
| GP26- beziehungsweise BAT_AD-Konflikt geklaert | Nicht Bestandteil des Tests; offen |
| Integration in den Climate-Cube-Code freigegeben | Noch nicht abgestimmt |
