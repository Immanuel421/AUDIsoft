# Testplan Sequenzabfrage Ohne Slave-SD

Projekt: AUDI Climate Cube  
Stand: 28.08.2026  
Status: Unit-Tests fuer `Q`/`R`, `SEQ-04`, `SEQ-11`, `SEQ-12` und `SEQ-14` vorhanden; Hardwareablaeufe fuer `SEQ-02`, `SEQ-04`, `SEQ-08` und `SEQ-09` vorbereitet

## 1. Ziel

Geprueft wird, dass ein Slave nach einem Neustart keine bereits verwendete Sequenznummer erneut vergibt. Mit lesbarer Slave-SD rekonstruiert er den lokalen Zustand. Ohne lesbare Slave-SD bezieht er die naechste freie Nummer mit `Q` und `R` vom konfigurierten Master. Ohne gueltige Antwort sendet er keine neuen Messdatensaetze.

## 2. Testfaelle

| ID | Ausgangslage und Durchfuehrung | Erwartetes Ergebnis | Ebene | Status |
|---|---|---|---|---|
| SEQ-01 | Slave-SD enthaelt zuletzt Sequenz `40`; Slave neu starten. | Keine `Q`-Anfrage; Slave verwendet `41`; Sequenz `40` wird nicht ueberschrieben. | Hardware | bestanden am 25.08.2026 |
| SEQ-02 | Slave-SD fehlt; Master hat zuletzt Sequenz `125`; `Q` verarbeiten. | Master antwortet mit `R` und `126`; Slave verwendet `126`. | Unit/Hardware | Unit bestanden am 26.08.2026; Hardware offen |
| SEQ-03 | Slave-SD fehlt; Master kennt den Slave noch nicht. | Master antwortet mit `R` und `0`; Slave darf mit `0` beginnen. | Unit | bestanden am 26.08.2026 |
| SEQ-04 | Slave-SD fehlt und Master antwortet nicht. | Drei `Q`-Versuche mit je drei Sekunden Timeout und zwei Sekunden Pause; danach 60 Sekunden bis zur naechsten Runde; keine Sequenzvergabe und kein neuer Messdatensatz. | Unit/Hardware | Unit bestanden am 27.08.2026; Hardware offen |
| SEQ-05 | `C01` erwartet `M01`; `R` kommt von `M02`. | Slave verwirft die Antwort. | Unit | bestanden am 26.08.2026 |
| SEQ-06 | `R` ist an `C02` statt `C01` adressiert. | Slave verwirft die Antwort. | Unit | bestanden am 26.08.2026 |
| SEQ-07 | `R` besitzt falsche Version, Feldzahl, ID oder Sequenz. | Kontrollierte Ablehnung; kein neuer Messdatensatz. | Unit | bestanden am 26.08.2026 |
| SEQ-08 | Erste `R`-Antwort geht verloren; `Q` wird wiederholt. | Master liefert erneut dieselbe freie Sequenznummer. | Unit/Hardware | Unit bestanden am 26.08.2026; Hardware offen |
| SEQ-09 | Slave sendet ohne SD nach gueltigem `R` und wird neu gestartet. | Erneute Abfrage liefert die naechste zentral freie Nummer. | Integration/Hardware | Ablauf vorbereitet am 28.08.2026 |
| SEQ-10 | Slave arbeitet ohne SD im RAM; danach wird die SD spannungsfrei eingesetzt und der Slave neu gestartet. | Nach Neustart nutzt der Slave die wieder verfuegbare SD. Ist kein eindeutiger lokaler Sequenzstand vorhanden, fragt er die naechste freie Sequenz beim Master ab. | Integration/Hardware | fachlich geklaert am 28.08.2026; Ablauf noch vorzubereiten |
| SEQ-11 | Sequenz `125` wurde gespeichert, ihr ACK ging verloren; Neustart ohne SD. | Master liefert `126`; `125` wird nicht neu vergeben. | Unit | bestanden am 27.08.2026 |
| SEQ-12 | Sequenz `125` wurde nicht beim Master gespeichert; Neustart ohne SD. | Master liefert weiterhin `125`. | Unit | bestanden am 27.08.2026 |
| SEQ-13 | SD ist lesbar, Sequenzstand aber nicht eindeutig rekonstruierbar. | Slave verwendet keinen unsicheren Wert und wechselt zur `Q`-Abfrage. | Unit | vorbereitet |
| SEQ-14 | Master startet mit vorhandenen Daten mehrerer Slaves neu. | Master rekonstruiert jeden Stand getrennt und beantwortet `Q` korrekt. | Unit/Integration | Unit bestanden am 27.08.2026; Integration offen |

## 3. Nachweis SEQ-01

| Feld | Ergebnis |
|---|---|
| Datum | 25.08.2026 |
| Slave | `C01` |
| Master | `M01` |
| Ausgangssequenz | `40`, erfolgreich bestaetigt |
| Sequenz nach Neustart | `41`, laut Bedienerbeobachtung erfolgreich bestaetigt |
| Master-SD | Sequenz `40` genau einmal; Sequenz `41` genau einmal in `master_measurements.csv` |
| `Q`-Anfrage | fuer den bestehenden Prototyp nicht implementiert; lokale SD-Rekonstruktion wurde verwendet |
| Bewertung | bestanden fuer den bestehenden SD-basierten Neustart; V1-`Q`/`R` ist nicht Bestandteil dieses Testfalls |

## 4. Abnahmekriterien

1. Keine bereits zentral verwendete Sequenznummer wird als neuer Datensatz vergeben.
2. Nur korrekt adressierte `R`-Antworten des konfigurierten Masters werden akzeptiert.
3. Ohne gueltige Antwort werden keine neuen Messdatensaetze gesendet.
4. Ein neuer Slave ohne Masterdaten kann mit Sequenz `0` beginnen.
5. Nach spannungsfreiem Einsetzen der SD und Neustart wird ein eindeutiger Sequenzstand aus SD oder Master-Abfrage verwendet.
6. Master- und Slave-Neustarts erzeugen keine Duplikate und ueberschreiben keine Daten.

## 5. Festgelegte Testparameter

- drei `Q`-Versuche je Abfragerunde,
- drei Sekunden Antwort-Timeout je Versuch,
- zwei Sekunden Pause zwischen erfolglosen Versuchen,
- 60 Sekunden Pause zwischen zwei Abfragerunden,
- hoechstens eine unnummerierte Messung im RAM; eine neuere ersetzt die aeltere,
- keine Uebertragung neuer Messdatensaetze ohne gueltige `R`-Antwort.

Noch fuer den Hardwaretest festzulegen ist die Methode zum gezielten Unterdruecken einer `R`-Antwort.

## 6. Vorbereitung Der Noch Offenen Testfaelle

| ID | Vorbereitung | Naechster Umsetzungsschritt |
|---|---|---|
| SEQ-09 | Master mit bekanntem zentralem Stand starten, Slave ohne SD mit gueltigem `R` senden lassen, danach Slave ohne SD neu starten. | Detailablauf, Erwartung, Abbruchkriterien und Nachweistabelle sind in Abschnitt 12 vorbereitet. |
| SEQ-10 | No-SD-RAM-Betrieb laufen lassen, Slave spannungsfrei schalten, SD einsetzen oder reparieren und Slave neu starten. | Detailablauf vorbereiten: Startpfad muss SD nutzen, wenn sie eindeutig lesbar ist; andernfalls `Q`/`R` verwenden. Kein Hot-Plug im laufenden Betrieb. |
| SEQ-13 | Fehlerhafte oder widerspruechliche lokale Slave-Zustandsdateien erzeugen, ohne gueltige ausstehende Warteschlange vorauszusetzen. | Eindeutigkeitsregel fuer lokale Rekonstruktion festlegen; danach Unit-Test fuer Wechsel in die `Q`-Abfrage ergaenzen. |
| SEQ-14 | Master-CSV mit mehreren Slaves und geloeschtem State verwenden. | Unit-Anteil ist automatisiert; Integrationstest mit realer Master-SD und anschliessender `Q`-Antwort je Slave vorbereiten. |


## 7. Hardwaretest-Vorbereitung Fuer SEQ-02, SEQ-04 Und SEQ-08

### 7.1 Ziel Und Testgrenze

Dieser Hardwaretest prueft den degradierten Slave-Betrieb ohne lesbare Slave-SD. Der Test weist nicht nach, dass die lokale Backup-Anforderung erfuellt ist. Er prueft nur, dass der Slave im Fehlerfall keine unsichere Sequenznummer vergibt, gueltige Masterantworten verwendet und fehlende Masterantworten kontrolliert behandelt.

Geprueft werden zunaechst die Hardwareanteile von `SEQ-02`, `SEQ-04` und `SEQ-08` mit einem Slave `C01` und einem Master `M01`.

### 7.2 Voraussetzungen

- Zwei Pico-Geraete mit SX1262-Modulen und passenden 868-MHz-Antennen sind vorhanden.
- Master `M01` besitzt eine eingesetzte, beschreibbare SD-Karte.
- Slave `C01` wird fuer den Test ohne lesbare Slave-SD gestartet.
- Beide Geraete verwenden denselben Softwarestand und kompatible Funkparameter.
- `C01` besitzt in `/config.json` eine gueltige `master_id` mit Wert `M01`.
- Fuer den Test darf das Messintervall voruebergehend reduziert werden, zum Beispiel `measurement_interval_s = 60` und `sequence_query_retry_s = 60`.
- Serielle Ausgaben von Master und Slave werden vollstaendig mitgeschnitten.
- Master-SD wird vor und nach dem Test gesichert oder mindestens die relevante CSV-Datei dokumentiert.

### 7.3 Sicherheitsregeln

- Slave-SD nur im spannungsfreien Zustand entfernen oder wieder einsetzen.
- SX1262 nie ohne passende Antenne in den Sendebetrieb nehmen.
- Master-SD waehrend eines Schreibvorgangs nicht entfernen.
- Fuer `SEQ-04` wird die Masterantwort bevorzugt dadurch verhindert, dass der Master ausgeschaltet bleibt oder noch nicht gestartet wird. Keine Funkhardware im laufenden Betrieb abstecken.
- Nach jedem Teiltest die erzeugten Master-CSV-Zeilen und seriellen Logs sichern, bevor der naechste Teiltest beginnt.

### 7.4 Vorbereitende Konfiguration

| Geraet | Rolle | Erwartete Konfiguration |
|---|---|---|
| Master | `master` | `device_id = M01`, SD eingesetzt, `receive_timeout_ms` passend fuer Dauerschleife |
| Slave | `slave` | `device_id = C01`, `master_id = M01`, Slave-SD entfernt oder nicht mountbar |

Empfohlene Testwerte fuer kurze Tischtests:

```json
{
  "measurement_interval_s": 60,
  "ack_timeout_ms": 3000,
  "sequence_query_retry_s": 60
}
```

## 8. Hardwareablauf SEQ-02

Ziel: Slave ohne SD fragt den Master nach der naechsten freien Sequenz und sendet danach einen Messdatensatz mit dieser Sequenz.

| Schritt | Aktion | Erwartete Beobachtung |
|---:|---|---|
| 1 | Master mit eingesetzter SD starten. | Serielle Meldung zeigt Masterstart und Empfangsschleife. |
| 2 | Sicherstellen, dass Master fuer `C01` bereits einen bekannten Stand besitzt, zum Beispiel letzte Sequenz `125`; alternativ tatsaechlichen letzten Stand notieren. | Letzte bekannte Sequenz ist dokumentiert. |
| 3 | Slave spannungsfrei schalten, Slave-SD entfernen oder gezielt unlesbar machen, danach Slave starten. | Slave meldet degradierten Betrieb ohne SD. |
| 4 | Slave bis zur Sequenzabfrage laufen lassen. | Slave sendet `Q`; Master antwortet mit `R`. |
| 5 | Auf den anschliessenden Messdatensatz und ACK warten. | Master speichert Datensatz; Slave erhaelt ACK. |
| 6 | Master-CSV auswerten. | Neue Sequenz ist `letzte Sequenz + 1`; `status_flags` enthaelt `0008` beziehungsweise das Bit `SLAVE_SD_UNAVAILABLE`. |

Bestanden, wenn genau ein neuer Master-Datensatz mit der erwarteten Sequenz vorhanden ist und der Datensatz den fehlenden Slave-SD-Status markiert.

## 9. Hardwareablauf SEQ-04

Ziel: Slave ohne SD sendet bei nicht antwortendem Master keine Messdaten und vergibt keine Sequenznummer.

| Schritt | Aktion | Erwartete Beobachtung |
|---:|---|---|
| 1 | Master ausgeschaltet lassen oder Master-Code nicht starten. | Es gibt keine `R`-Antwort. |
| 2 | Slave spannungsfrei schalten, Slave-SD entfernen oder gezielt unlesbar machen, danach Slave starten. | Slave meldet degradierten Betrieb ohne SD. |
| 3 | Erste Abfragerunde beobachten. | Drei `Q`-Versuche; je Versuch Timeout, zwischen den ersten beiden Fehlversuchen Pause. |
| 4 | Danach mindestens bis zum naechsten 60-Sekunden-Retry weiter beobachten. | Keine Datenpakete `D`; erneute `Q`-Runde nach Retry-Zeit. |
| 5 | Master danach weiterhin ausgeschaltet lassen und Slave-Log sichern. | Kein Messdatensatz wurde bestaetigt oder gespeichert. |

Bestanden, wenn ohne gueltige `R`-Antwort keine Datenuebertragung eines neuen Messdatensatzes erfolgt und im Slave-Log keine vergebene Sequenz fuer die gehaltene Messung erscheint.

## 10. Hardwareablauf SEQ-08

Ziel: Wenn eine erste Antwort beziehungsweise erste Abfragerunde verloren geht, liefert der Master bei wiederholter Anfrage dieselbe freie Sequenznummer, solange zwischenzeitlich kein Datensatz gespeichert wurde.

Praktische, sichere Simulation: Den Master fuer die erste Abfragerunde ausgeschaltet lassen und erst vor der zweiten Runde starten. Dadurch geht nicht technisch genau ein einzelnes `R`-Paket verloren, aber der Hardwaretest prueft das relevante Wiederholungsverhalten ohne riskante Funkmanipulation.

| Schritt | Aktion | Erwartete Beobachtung |
|---:|---|---|
| 1 | Master ausgeschaltet lassen. | Slave kann keine `R`-Antwort erhalten. |
| 2 | Slave ohne lesbare SD starten und erste Abfragerunde beobachten. | Drei erfolglose `Q`-Versuche; kein Datenpaket `D`. |
| 3 | Vor der naechsten Retry-Runde Master mit eingesetzter SD starten. | Master geht in Empfangsschleife. |
| 4 | Zweite Abfragerunde des Slaves beobachten. | Master antwortet mit derselben naechsten freien Sequenz wie vor dem Test dokumentiert. |
| 5 | Auf Messdatenversand und ACK warten. | Master speichert genau einen neuen Datensatz; Slave setzt RAM-Sequenz danach fort. |
| 6 | Master-CSV auswerten. | Keine doppelte Sequenz; neue Sequenz entspricht dem vor dem Test freien Wert. |

Bestanden, wenn die erste erfolglose Abfragerunde keine Messdaten erzeugt und die spaetere erfolgreiche Abfrage dieselbe freie Sequenznummer verwendet.

## 11. Nachweise Fuer Den Hardwaretest

| Nachweis | Ablage / Ergebnis |
|---|---|
| Git-Commit des getesteten Softwarestands |  |
| Master-`config.json` ohne geheime oder lokale Sonderwerte |  |
| Slave-`config.json` ohne geheime oder lokale Sonderwerte |  |
| Serielles Master-Log fuer SEQ-02 |  |
| Serielles Slave-Log fuer SEQ-02 |  |
| Master-CSV vor und nach SEQ-02 |  |
| Serielles Slave-Log fuer SEQ-04 |  |
| Nachweis, dass Master waehrend SEQ-04 nicht antworten konnte |  |
| Serielles Master- und Slave-Log fuer SEQ-08 |  |
| Master-CSV vor und nach SEQ-08 |  |
| Fotos oder Notizen zum SD-Zustand des Slaves |  |
| Bewertung bestanden / mit Hinweis bestanden / nicht bestanden |  |

## 12. Detailplanung SEQ-09

Ziel: Ein Slave ohne lesbare SD sendet nach einer gueltigen `R`-Antwort einen Messdatensatz, wird danach neu gestartet und fragt erneut beim Master an. Die zweite Masterantwort muss die naechste zentral freie Sequenznummer liefern. Dadurch wird geprueft, dass der fluechtige RAM-Sequenzstand nach einem Neustart nicht blind wiederverwendet wird und keine bereits zentral gespeicherte Sequenz erneut vergeben wird.

### 12.1 Voraussetzungen

- Master `M01` laeuft mit eingesetzter und beschreibbarer SD-Karte.
- Slave `C01` wird ohne lesbare Slave-SD betrieben.
- Beide Geraete verwenden denselben getesteten Softwarestand.
- Slave-Konfiguration enthaelt `device_id = C01`, `master_id = M01`, ein kurzes Testintervall und `sequence_query_retry_s = 60`.
- Master-CSV ist vor Testbeginn gesichert oder ihr letzter Stand fuer `C01` ist notiert.
- Serielle Ausgaben von Master und Slave werden ab Start mitgeschnitten.

### 12.2 Ausgangszustand Festlegen

| Feld | Eintrag |
|---|---|
| letzter zentral gespeicherter Datensatz fuer `C01` vor Test |  |
| erwartete erste `R`-Antwort | letzter Stand + 1 oder `0`, falls kein Datensatz vorhanden |
| erwartete zweite `R`-Antwort nach Slave-Neustart | erste gesendete und zentral gespeicherte Sequenz + 1 |
| Master-CSV vor Test gesichert | [ ] ja / [ ] nein |
| Slave-SD entfernt beziehungsweise nicht mountbar | [ ] ja / [ ] nein |

### 12.3 Ablauf

| Schritt | Aktion | Erwartete Beobachtung |
|---:|---|---|
| 1 | Master `M01` mit SD starten und Empfangsschleife abwarten. | Master meldet Start und wartet auf Pakete. |
| 2 | Slave `C01` ohne lesbare SD starten. | Slave meldet degradierten Betrieb ohne SD. |
| 3 | Erste Sequenzabfrage beobachten. | Slave sendet `Q`; Master antwortet mit `R` und der erwarteten ersten freien Sequenz. |
| 4 | Ersten Messdatensatz abwarten. | Slave sendet genau einen Datensatz mit `SLAVE_SD_UNAVAILABLE`; Master speichert ihn und sendet ACK. |
| 5 | Master-CSV direkt nach dem ersten ACK sichern oder relevante Zeile notieren. | Die erste gesendete Sequenz ist genau einmal vorhanden. |
| 6 | Slave kontrolliert neu starten, Master weiterlaufen lassen. | RAM-Zustand des Slaves geht verloren; Master behält zentralen Stand. |
| 7 | Zweite Sequenzabfrage nach Neustart beobachten. | Slave sendet erneut `Q`; Master antwortet mit erster Sequenz + 1. |
| 8 | Zweiten Messdatensatz abwarten. | Master speichert die zweite Sequenz genau einmal und sendet ACK. |
| 9 | Master-CSV nach Test sichern und auswerten. | Beide Sequenzen sind lueckenlos, chronologisch und ohne Duplikat vorhanden. |

### 12.4 Erwartetes Ergebnis

`SEQ-09` ist bestanden, wenn:

- der Slave nach Neustart ohne SD erneut `Q` sendet,
- die zweite `R`-Antwort dem zentralen Masterstand plus eins entspricht,
- die erste Sequenz nicht erneut vergeben wird,
- beide Messdatensaetze in der Master-CSV genau einmal vorhanden sind,
- beide Messdatensaetze das Statusflag `SLAVE_SD_UNAVAILABLE` enthalten,
- der Master nur nach erfolgreicher Speicherung ACK sendet.

### 12.5 Abbruch- Und Fehlerkriterien

Der Test wird abgebrochen oder als nicht bestanden markiert, wenn:

- der Slave ohne gueltige `R`-Antwort einen Messdatensatz sendet,
- nach dem Neustart dieselbe Sequenz erneut als neuer Datensatz gesendet wird,
- der Master eine Sequenz doppelt als neue Messung speichert,
- der Master ohne erfolgreiche SD-Speicherung ein ACK sendet,
- die Slave-SD versehentlich doch eingebunden ist und deshalb kein No-SD-Betrieb getestet wird.

### 12.6 Nachweistabelle

| Nachweis | Ergebnis / Ablage |
|---|---|
| Git-Commit des getesteten Stands |  |
| Master-Log erste Abfrage und erstes ACK |  |
| Slave-Log erste Abfrage und erstes ACK |  |
| Master-CSV-Zeile erster Datensatz |  |
| Zeitpunkt und Art des Slave-Neustarts |  |
| Master-Log zweite Abfrage und zweites ACK |  |
| Slave-Log zweite Abfrage und zweites ACK |  |
| Master-CSV-Zeile zweiter Datensatz |  |
| Bewertung | [ ] bestanden / [ ] mit Hinweis bestanden / [ ] nicht bestanden |

## 13. Fachliche Klaerung SEQ-10

`SEQ-10` wird nicht als Hot-Plug-Funktion im laufenden Betrieb umgesetzt. Eine Slave-SD wird nur im spannungsfreien Zustand wieder eingesetzt oder repariert. Die Rueckkehr vom degradierten No-SD-Betrieb in die SD-gestuetzte Verwaltung erfolgt deshalb ueber einen kontrollierten Neustart.

### 13.1 Begruendung

- Das Entfernen oder Einsetzen der SD im laufenden Betrieb ist fuer den Hardwaretest und den spaeteren Betrieb unnoetig riskant.
- Der No-SD-Modus ist ein degradierter Fehlerbetrieb und kein gleichwertiger Normalbetrieb.
- Ein Neustart erzeugt eine klare technische Grenze: RAM-Zustand ist verloren, SD-Zustand wird neu bewertet, und bei unklarem lokalen Sequenzstand greift die Master-Abfrage.
- Dadurch bleibt die Sequenzentscheidung nachvollziehbar und testbar.

### 13.2 Geaenderter Erwartungswert

| Situation | Erwartetes Verhalten |
|---|---|
| Slave laeuft ohne SD im RAM-Modus | Live-Uebertragung mit `SLAVE_SD_UNAVAILABLE`, solange Master erreichbar ist |
| SD soll wieder verwendet werden | Slave spannungsfrei schalten, SD einsetzen oder reparieren, Slave neu starten |
| SD nach Neustart eindeutig lesbar | Slave nutzt die normale SD-gestuetzte Sequenz- und FIFO-Verwaltung |
| SD nach Neustart leer oder uneindeutig | Slave fragt die naechste freie Sequenz per `Q`/`R` beim Master ab |
| SD weiterhin nicht lesbar | Slave bleibt im degradierten No-SD-Modus |

### 13.3 Naechster Testschritt

Der konkrete Hardwareablauf fuer `SEQ-10` wird erst nach `SEQ-09` vorbereitet. Dabei muss entschieden werden, ob die wieder eingesetzte SD einen eindeutigen lokalen Stand enthaelt oder bewusst als leer beziehungsweise uneindeutig getestet wird.
