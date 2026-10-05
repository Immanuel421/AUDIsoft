# Isolierter SX1262-Ping-Pong-Test

Dieser Test prueft nur die direkte LoRa-Kommunikation zwischen zwei Raspberry Pi Picos mit Waveshare Pico-LoRa-SX1262-868M. Der vorhandene Messcode wird dabei nicht verwendet oder veraendert.

## Dateien

- `lora_sender_test.py`: sendet alle zehn Sekunden `PING` und wartet auf `PONG`
- `lora_receiver_test.py`: wartet auf `PING` und antwortet mit `PONG`
- `TESTPROTOKOLL_LoRa_Ping_Pong.md`: ausfuellbares Protokoll fuer Aufbau, Testfaelle, Messwerte, Abweichungen und Nachweise

## Bibliotheksquelle

Die verwendete Bibliothek stammt aus `ehong-tl/micropySX126X`:
https://github.com/ehong-tl/micropySX126X

Der zugehoerige MIT-Lizenztext liegt als `micropySX126X_LICENSE.txt` bei.

## Voraussetzungen

Auf beiden Picos muessen sich im Verzeichnis `lib/` dieselben Dateien befinden:

- `_sx126x.py`
- `sx126x.py`
- `sx1262.py`

Vor dem Einschalten muss an jedem LoRa-Modul eine passende Antenne angeschlossen sein.

## Vorlaeufige Pinbelegung

| SX1262-Signal | Pico-Pin |
|---|---|
| CLK | GP10 |
| MOSI | GP11 |
| MISO | GP12 |
| CS | GP3 |
| DIO1 / IRQ | GP20 |
| RESET | GP15 |
| BUSY | GP2 |

`BAT_AD` auf GP26 wird in diesem isolierten Test nicht verwendet.

## Testdurchfuehrung

1. Den bestehenden `code.py` des ersten Pico sichern.
2. `lora_sender_test.py` als `code.py` auf den ersten Pico kopieren.
3. Den bestehenden `code.py` des zweiten Pico sichern.
4. `lora_receiver_test.py` als `code.py` auf den zweiten Pico kopieren.
5. Auf beiden Picos die serielle Ausgabe oeffnen.
6. Zuerst den Empfaenger und danach den Sender starten.
7. Pruefen, ob zu jeder `PING`-Nachricht eine `PONG`-Antwort erscheint.
8. RSSI, SNR, Fehlermeldungen, Abstand und Testbedingungen dokumentieren.

Vor dem Test wird `TESTPROTOKOLL_LoRa_Ping_Pong.md` mit dem Softwarestand und den Geraetedaten ergaenzt. Waehrend des Tests werden dort die Testfaelle, Messreihen und Abweichungen festgehalten.

## Funkparameter

Die Testprogramme verwenden vorlaeufig:

- Frequenz: 868,1 MHz
- Bandbreite: 125 kHz
- Spreading Factor: 7
- Coding Rate: 4/5 (`cr=5`)
- Sendeleistung: 10 dBm
- privates Sync Word: `0x12`
- CRC: aktiviert

Diese Parameter sind nur fuer den ersten kurzen Funktionstest vorgesehen. Zulaessigkeit, Sendeleistung, Kanalbelegung und Duty Cycle muessen vor laengeren Tests beziehungsweise dem spaeteren Einsatz geprueft und mit dem fachlichen Ansprechpartner abgestimmt werden.

## Erfolgskriterium

Der Test gilt als technisch erfolgreich, wenn mehrere aufeinanderfolgende nummerierte `PING`-Pakete korrekt empfangen und jeweils mit dem passenden `PONG` beantwortet werden. Ein einzelnes erfolgreiches Paket reicht fuer den Stabilitaetsnachweis nicht aus.
