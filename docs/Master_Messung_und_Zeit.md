# Master-Messung und Zeitfuehrung

Stand: 18.09.2026. Implementiert und lokal getestet; noch nicht auf die Picos
uebertragen oder als Hardware-Dauerlauf bestaetigt.

## Master-Messung

Der Master verwendet denselben SEN66-Adapter wie die Slaves. Ein Messzyklus
startet direkt nach dem Softwarestart und dann jeweils nach
`measurement_interval_s` (Standard 900 Sekunden). Die erste Messung liegt nach
Aufwaermzeit und zweiter Sensorabfrage vor, normalerweise nach etwa 65 Sekunden.
Der Zeitstempel der eigenen Master-Messung bezeichnet die fertige Probe.

Die Aufwaermzeit wird schrittweise abgefragt; waehrenddessen verarbeitet der
Master weiter Datenpakete und ACKs. Einzelne Hardwarezugriffe und SD-Schreib-
vorgaenge bleiben synchron. Dies ist keine Garantie fuer verlustfreien Empfang.

Eigene Messungen stehen bei Geraete-ID M01 unter `/sd/data/M01/` in den
bestehenden sequenzbasierten CSV-Bloecken mit Master-Kopfzeile. Die eigene
Sequenz ist unabhaengig von C01, C02 und C03 und wird nach Neustart aus den
Dateien wiederhergestellt. `device_id` und `master_id` sind beide M01.
RSSI und SNR bleiben leer, da kein Funkempfang stattgefunden hat. Die bestehende
Spalte `slave_uptime_s` enthaelt auch hier die Laufzeit des messenden Geraets.
Es gibt keine eigene Funkuebertragung, kein Selbst-ACK und keine Slave-Pending-
Datei fuer Master-Messungen. M01 bleibt aus `monitored_slaves` ausgeschlossen.

Fehlende SEN66-Werte werden mit den bestehenden Fehlerflags gespeichert.
Bei einem temporaeren SD-Schreibfehler bleibt die fertige eigene Probe im RAM;
Speicherwiederholungen erfolgen fruehestens nach fuenf Sekunden. Solange die
Probe nicht gespeichert ist, startet keine neue eigene Messung. Ein Strom-
verlust kann diese noch ungesicherte Probe verlieren.

## Zeit und Tageswechsel

`time_epoch_utc` ist eine Unix-Zeitreferenz in UTC, keine taegliche Startzeit.
Die Ausgabe mit `Z` ist UTC, nicht deutsche Ortszeit. Die Uhrzeit laeuft mit
der monotonen Laufzeit weiter; Tages-, Monats-, Jahres- und Schaltjahreswechsel
werden ueber die Kalenderfunktionen der Laufzeit berechnet. Auf CPython wird
explizit `gmtime` verwendet; CircuitPython rechnet ohne lokale Zeitzonen.

Die alte Berechnung enthielt keinen taeglichen Reset. Ein wiederholter
konfigurierter Startwert konnte dagegen bei jedem Programmneustart entstehen.
Der gemeldete Hardwareverlauf wurde noch nicht anhand von CSV und Neustartlogs
rekonstruiert; eine ausschliessliche Ursache ist daher nicht nachgewiesen.

Auf CircuitPython wird nun die interne RTC aus der Konfiguration gesetzt,
wenn ihr Wert aelter ist. Eine bereits mindestens so weit fortgeschrittene
interne Uhr wird uebernommen, statt sie auf den Konfigurationswert zurueck-
zustellen. Das hilft bei Software-Neustarts, sofern die interne Uhr erhalten
bleibt. Es erfordert keine zusaetzliche Platine oder GPIO-Verbindung.

Nach Stromverlust oder einem Reset, der die interne Uhr loescht, liest die
Software die letzte gueltige Messzeit des eigenen Geraets aus dessen CSV und
setzt die Zeitbasis fuer die naechste Messung auf diesen Wert plus
`measurement_interval_s`. Damit bleiben Tageswechsel und die chronologische
15-Minuten-Folge ueber Neustarts erhalten. Die so fortgesetzte Zeit wird mit
`TIME_UNSYNCED` markiert: Sie ist fuer Reihenfolge und Diagramme nutzbar, aber
nach einer laengeren Ausschaltzeit keine nachweislich echte UTC-Zeit. Fehlt eine
gueltige CSV-Zeit, wird weiterhin `time_epoch_utc` aus der Konfiguration
verwendet.
Das unveraenderte Sekundenfeld bei 900-Sekunden-Abstaenden ist normal:
14:10:37, 14:25:37, 14:40:37 usw.

Grundlage: [CircuitPython RTC](https://docs.circuitpython.org/en/10.3.0/shared-bindings/rtc/index.html)
und [Zeitfunktionen](https://docs.circuitpython.org/en/latest/shared-bindings/time/).

## Update

Vorher Programmstand, Konfiguration und Messdaten sichern. Die bestehende
Hardwarebelegung und `config.json` bleiben unveraendert, abgesehen von einer
gegebenenfalls neu zu setzenden aktuellen UTC-Referenz.

Auf M01 und C01 mit CircuitPython 10.2.1 diese Dateien aus dem Projekt in die
gleichen Pfade unter CIRCUITPY uebertragen:

- `code.py`
- `adapters/clock.py`
- `adapters/sen66_sensor.py`
- `application/master_controller.py`
- `ports/contracts.py`

Auf C02 und C03 mit CircuitPython 10.3.0 dieselben Pfade aus
`firmware/rp2040/` verwenden: `code.py` und die vier entsprechenden `.mpy`-
Dateien. Keine gleichnamigen `.py`- und `.mpy`-Varianten mischen. Alle zusammen-
gehoerigen Dateien vor dem Neustart vollstaendig uebertragen. Keine SD-Messdaten
oder Konfigurationen durch Beispielwerte ersetzen.

## Nachweise und offene Hardwaretests

134 lokale Unit-Tests bestanden. Neue Tests pruefen Master-Speicherung,
unabhaengige Sequenzen, Neustart, Empfang waehrend der Aufwaermphase, SD-Retry,
Sensorfehler, Zeituebergaenge und die Wiederverwendung der internen Uhr.
Firmware fuer CircuitPython 10.3.0 neu kompiliert und Quellenhashes geprueft.

1. M01 starten und nach der Aufwaermzeit `master measurement ... stored`
   sowie einen neuen Datensatz unter `/sd/data/M01/` pruefen.
2. Mindestens drei 15-Minuten-Zyklen laufen lassen. Master-Sequenzfortsetzung
   und weiterhin bestaetigte Slave-Daten vergleichen.
3. Fuer den Tageswechsel einen separaten Test mit passender UTC-Referenz
   durchfuehren; reale Messdateien und kuenstlich datierte Tests getrennt halten.
4. Einen Neustart nach Stromunterbrechung pruefen: Der naechste Zeitstempel soll
   genau ein Messintervall nach der letzten CSV-Messzeit liegen und das Flag
   `TIME_UNSYNCED` tragen.
5. Speicher- und RAM-Verhalten auf beiden Pico-Generationen pruefen.

Der vorher beobachtete LoRa-Fehler -1 und der OLED-Ausfall sind durch diese
Erweiterung nicht als behoben nachgewiesen. Eine automatische Funk-Reinitiali-
sierung oder zentrale Zeitverteilung wurde nicht hinzugefuegt.
