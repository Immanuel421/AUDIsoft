# Testprotokoll Systemintegration Master/Slave

Dieses Protokoll dokumentiert den Test des produktiven Master-/Slave-Ablaufs des AUDI Climate Cube am 21.08.2026. Geprueft wurden die regelmaessige Messdatenuebertragung, Speicherung, Bestaetigung, Wiederholung nach fehlendem ACK und das Verhalten nach einem Slave-Neustart.

## 1. Testaufbau

| Feld | Eintrag |
|---|---|
| Testdatum | 21.08.2026 |
| Testperson | Immanuel Mauch |
| Slave | `C01`, Raspberry Pi Pico 2 W mit SX1262 |
| Master | `M01`, Raspberry Pi Pico 2 W mit SX1262 |
| Messintervall | 15 Minuten |
| Funkstruktur | Direkte Punkt-zu-Punkt-Verbindung Slave zu Master |
| Stromversorgung | USB ueber Laptop |
| Auswertung | Serielle Meldungen und CSV-Dateien auf den SD-Karten |

## 2. Testfaelle Und Ergebnisse

| ID | Testfall | Erwartetes Ergebnis | Beobachtung | Status |
|---|---|---|---|---|
| SI-01 | Uebertragung im 15-Minuten-Takt | Messdaten werden fortlaufend im vorgesehenen Intervall uebertragen und gespeichert | Die Sequenzen 5 bis 16 wurden ueber zwoelf aufeinanderfolgende Intervalle uebertragen. Messzeitpunkte und `uptime_s` stiegen jeweils um 900 Sekunden. | bestanden |
| SI-02 | Speicherung und ACK | Der Master speichert einen Datensatz und bestaetigt ihn anschliessend | Empfangene Datensaetze wurden in der Master-CSV gespeichert und ACKs wurden beobachtet. | bestanden |
| SI-03 | Fehlendes ACK | Ein nicht bestaetigter Datensatz bleibt erhalten und wird spaeter erneut uebertragen | Fuer Sequenz 21 erschien `ACK missing for sequence 21`. Sequenz 21 war anschliessend in der Master-CSV vorhanden; Sequenz 22 wurde danach bestaetigt. | bestanden |
| SI-04 | Duplikatvermeidung nach Wiederholung | Ein erneut uebertragener Datensatz wird beim Master nicht doppelt gespeichert | Sequenz 21 ist in der Master-CSV genau einmal enthalten. | bestanden |
| SI-05 | Neustart des Slaves | Sequenzverwaltung, Uebertragung, Speicherung und ACK funktionieren nach dem Neustart weiter | Der Ablauf funktionierte nach dem kontrollierten Slave-Neustart weiter. Die absolute Slave-Zeit wurde dabei zurueckgesetzt. | mit Hinweis bestanden |

## 3. Auswertung Der Messreihe

- Die Sequenzen 5 bis 16 bilden eine zusammenhaengende Messreihe mit dem geforderten Abstand von 15 Minuten.
- Die dokumentierten Empfangswerte lagen ungefaehr zwischen -14 und -35 dBm RSSI sowie zwischen 11,8 und 13,5 dB SNR.
- `receive_status` war bei den betrachteten Datensaetzen `0`.
- Nicht vorhandene optionale Bodenmesswerte blieben leer.
- Sequenz 21 ging trotz zunaechst fehlendem ACK nicht verloren und wurde nicht doppelt gespeichert.

## 4. Auffaelligkeiten Und Offene Punkte

| Nr. | Beobachtung | Bewertung | Weitere Massnahme |
|---:|---|---|---|
| 1 | Die Sequenzen 17 und 18 besitzen trotz unterschiedlicher Messwerte denselben `measurement_timestamp`. | Die Beobachtung stammt aus einem frueheren Lauf vor dem kontrollierten Neustart. Die Datensaetze bleiben ueber ihre Sequenznummer unterscheidbar. | Bedeutung und Gueltigkeit des Slave-Zeitstempels im Datenformat eindeutig festlegen. |
| 2 | Nach einem Slave-Neustart wird dessen absolute Zeit zurueckgesetzt. | Fuer den getesteten Kernablauf nicht blockierend, sofern 15-Minuten-Intervall, Sequenznummer und Master-Empfangszeit die geforderte Nachvollziehbarkeit herstellen. | Fachliche Auslegung im Lasten- beziehungsweise Pflichtenheft festhalten. |
| 3 | Ein Langzeittest bei groesserer Entfernung und unter realen Einsatzbedingungen wurde noch nicht durchgefuehrt. | Fuer den Tischtest nicht erforderlich, fuer den spaeteren Feldeinsatz weiterhin offen. | Reichweiten- und Dauerbetriebstest planen. |

## 5. Gesamtergebnis

Der produktive Ablauf von der Messdatenerfassung ueber lokale Slave-Speicherung und LoRa-Uebertragung bis zur Master-Speicherung und ACK-Bestaetigung wurde erfolgreich nachgewiesen. Auch die Wiederholung nach einem fehlenden ACK und die Vermeidung einer doppelten Master-Speicherung funktionierten im beobachteten Testfall.

Der Neustarttest war fuer Sequenzverwaltung, Uebertragung, Speicherung und ACK erfolgreich. Die zurueckgesetzte absolute Slave-Zeit wird als dokumentierter Hinweis gefuehrt. Noch zu pruefen sind insbesondere Master-Neustart, mehrere waehrend eines Master-Ausfalls aufgelaufene Datensaetze, Reichweite und Dauerbetrieb.
