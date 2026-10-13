# Diagnosecodes

Diagnoseereignisse werden bei verfuegbarem beschreibbarem internen Speicher
unter `/diagnostics/pending.json` dauerhaft vorgemerkt. Im normalen
USB-Dateiuebertragungsbetrieb ist `CIRCUITPY` jedoch schreibgeschuetzt fuer den
laufenden Pico; dann verwendet die Software automatisch die Slave-SD und sonst
den Arbeitsspeicher. Ist eine Slave-SD vorhanden, werden sie zusaetzlich in
`slave_diagnostics.csv` dokumentiert. Sie werden nicht unmittelbar per LoRa gesendet: Beim naechsten regulaeren
15-Minuten-Messvorgang werden alle wartenden Ereignisse unmittelbar vor dem
Messpaket an den Master uebertragen. Erst nach dem erfolgreichen ACK fuer den
Messdatensatz werden sie aus der Warteschlange entfernt.

| Code | Bedeutung | Empfohlene Pruefung |
| --- | --- | --- |
| `F1` | Slave-SD nicht verfuegbar | SD-Karte, Kartenleser, Versorgung und Dateisystem pruefen. |
| `F2` | Schreiben auf Slave-SD fehlgeschlagen | SD-Karte nicht im Betrieb entfernen; freien Speicher und Dateisystem pruefen. |
| `I1` | Geraet wurde neu gestartet | Stromversorgung und vorherige Diagnoseereignisse pruefen, falls Neustarts unerwartet sind. |

Die interne Warteschlange ist auf 32 kompakte Ereignisse begrenzt, damit weder
Messdaten noch der Programmspeicher den Flash fuellen. Sie steht nur zur
Verfuegung, wenn `CIRCUITPY` vor dem Start fuer CircuitPython beschreibbar
eingebunden wurde.
