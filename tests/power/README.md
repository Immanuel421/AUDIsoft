# 24-Stunden-Schlaf- und Energietest

Dieser Test prueft, ob ein Slave ueber 24 Stunden im 15-Minuten-Takt arbeitet und ob die gemessene Stromaufnahme rechnerisch eine Laufzeit von einem Jahr ermoeglicht.

## Wichtige Abgrenzung

Die Python-Skripte koennen ohne Messhardware keinen Strom messen. Fuer die Stromwerte wird ein USB-Leistungsmesser, ein Multimeter mit Strommessung oder ein Labornetzteil mit Stromanzeige benoetigt. Die Skripte werten die eingetragenen Messwerte und die erzeugte Master-CSV aus.

Bei angeschlossener USB-Datenverbindung kann CircuitPython einen Schlafzustand nur simulieren. Fuer die eigentliche Strommessung deshalb eine reine Stromversorgung, ein Power-only-Kabel oder einen USB-Datenblocker verwenden. Vorher muss das Programm mit normaler USB-Datenverbindung auf den Pico kopiert und getestet werden.

## Voraussetzungen

- ein fertig konfigurierter Master und ein Slave
- LoRa-Antennen an beiden Geraeten
- SD-Karten im Master und moeglichst auch im Slave
- stabile Stromversorgung fuer mindestens 24 Stunden
- Strommessgeraet zwischen Versorgung und Slave
- aktuelle Sicherung der Pico-Dateien
- korrekte `config.json` auf beiden Geraeten

## Teil A: Strom pro Betriebsphase messen

1. `measurements.template.csv` als neue Ergebnisdatei kopieren, zum Beispiel `measurements_2026-09-01.csv`.
2. Slave mit dem Strommessgeraet verbinden. Fuer die Messung keine USB-Datenverbindung verwenden.
3. Mindestens drei vollstaendige 15-Minuten-Zyklen beobachten.
4. Fuer jede Phase den typischen Strom in mA und die Dauer in Sekunden eintragen.
5. Bei `sleep` fuer `duration_s` den Wert `AUTO` stehen lassen. Das Skript berechnet die Restzeit des 900-Sekunden-Zyklus.
6. Nicht auftretende Phasen mit Dauer `0` eintragen. Leere Felder sind nicht erlaubt.
7. Energiebilanz berechnen:

```sh
python3 tests/power/energy_budget.py tests/power/measurements_2026-09-01.csv --battery-capacity-mah 10000
```

Die Batteriekapazitaet durch die Kapazitaet des spaeter eingesetzten Akkus ersetzen. Ohne bekannte Kapazitaet den Parameter weglassen.

## Teil B: 24-Stunden-Funktionstest

1. Master und Slave auf den freigegebenen Projektstand bringen.
2. `config.json` pruefen: Rollen, IDs, Ziel-Master, Funkparameter und 900 Sekunden Messintervall.
3. Beide Geraete einschalten und eine erfolgreiche Messung mit ACK abwarten.
4. Startzeit, erste Sequenznummer und Dateinamen im Abschnitt "Testprotokoll" notieren.
5. Beide Geraete 24 Stunden ununterbrochen laufen lassen. Nicht zwischendurch Dateien auf `CIRCUITPY` bearbeiten, weil dies einen Neustart ausloesen kann.
6. Nach mindestens 24 Stunden die Master-CSV sichern.
7. CSV auswerten:

```sh
python3 tests/power/verify_endurance_log.py /pfad/zur/master.csv --device-id C01
```

Bei einem anderen Slave `C01` entsprechend ersetzen.

## Abnahmekriterien

- mindestens 96 Messdatensaetze des getesteten Slaves
- keine doppelte oder rueckwaerts laufende Sequenznummer
- keine unerwarteten Sequenzluecken
- aufeinanderfolgende Messungen liegen im Bereich 900 +/- 30 Sekunden, soweit die Laufzeitdaten dies pruefbar machen
- kein unkontrollierter Neustart
- Energiebilanz einschliesslich 30 Prozent Reserve deckt ein Jahr ab

Der 24-Stunden-Test ist ein erster Nachweis. Fuer die spaetere Abnahme sollte zusaetzlich ein mindestens siebentaegiger Dauertest folgen.

## Testprotokoll

| Feld | Eintrag |
|---|---|
| Datum und Startzeit | |
| Datum und Endzeit | |
| Master-ID | |
| Slave-ID | |
| erste Sequenznummer | |
| letzte Sequenznummer | |
| verwendete Softwareversion/Commit | |
| Stromversorgung | |
| Strommessgeraet | |
| CSV-Datei | |
| Ergebnis Energiebilanz | |
| Ergebnis Logpruefung | |
| Auffaelligkeiten | |

## Quellen zur Schlaftechnik

- CircuitPython `alarm`: https://docs.circuitpython.org/en/latest/shared-bindings/alarm/
- Adafruit-Hinweise zu Light Sleep und Deep Sleep: https://learn.adafruit.com/deep-sleep-with-circuitpython/alarms-and-sleep
