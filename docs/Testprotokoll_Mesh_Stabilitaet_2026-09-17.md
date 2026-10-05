# Testprotokoll: Mesh-Kommunikation und Stabilitaet

**Datum:** 17.09.2026 bis 18.09.2026  
**Status:** Teiltest; kein bestandener 24-Stunden-Stabilitaetsnachweis  
**Aufbau:** `C03 -> C02 -> C01 -> M01`, statisch konfigurierte Mesh-Route

## Ziel

Mehrstufige Uebertragung von C03 ueber C02 und C01 zum Master M01 sowie den
ACK-Rueckweg pruefen. Zusaetzlich Laufzeit, Nachsenden und Standort-Einfluesse
beobachten.

## Voraussetzungen

- Vier Climate Cubes mit LoRa-Antennen.
- Konfigurationen passend zur statischen Kette.
- SD-Karten an den an der Datenweiterleitung beteiligten Geraeten.
- `measurement_interval_s = 900` Sekunden, ACK-Timeout im Versuch 15.000 ms.

## Durchfuehrung und Beobachtungen

| Zeitpunkt | Beobachtung |
|---|---|
| 17.09., 14:10 | Beobachtungszeitraum gestartet. Die Geraete wurden anschliessend in getrennten Raeumen aufgestellt. |
| waehrend des Tests | C02 sendete ueber C01 zum Master und erhielt ACKs auf dem Rueckweg. Nach einem Neustart von C01 wurden ausstehende C02-Datensaetze vollstaendig uebertragen. |
| waehrend des Tests | C03 meldete mindestens einmal `ACK missing for sequence 241`. Der Datensatz blieb ausstehend. |
| nach Standortwechsel C03 | Aufstellung: C03 Erdgeschoss, C02 erstes Obergeschoss, C01 zweites Obergeschoss, M01 erstes Obergeschoss. Sequenz 246 wurde zentral gespeichert; das ACK erreichte C03. |
| danach | C03 und C02 uebertrugen nach Nutzerbeobachtung ihre ausstehenden Datensaetze vollstaendig. |
| waehrend des Tests | C01 zeigte einen SD-bezogenen Fehler mit `Error 5`. Der genaue Volltext wurde nicht festgehalten; die Fehlerstelle ist offen. |
| waehrend des Tests | M01 meldete `master receive cycle failed: LoRa receive failed: LoRa receive setup failed: -1`. Der Empfang danach wurde nicht als dauerhaft wiederhergestellt nachgewiesen. |
| waehrend des Tests | Das OLED von C02 stellte keine neue sichtbare Ausgabe mehr bereit. Ob nur Display oder der gesamte Controller betroffen war, wurde nicht abschliessend festgestellt. |
| Auswertung | Die Masterdaten wirkten bei Sichtpruefung lueckenlos. Eine formale CSV-Auswertung steht aus. Nach Mitternacht erschien das Datum nicht fortlaufend; die Zeitursache ist separat zu pruefen. |

## Ergebnis

- Die statische Kette funktionierte mindestens fuer C03-Sequenz 246 samt
  End-to-End-ACK.
- Ausstehende Datensaetze von C02 und C03 konnten nach Nutzerbeobachtung
  nachgesendet werden.
- Die Platzierung beeinflusste die Verbindungsqualitaet. Eine bestimmte
  Ursache, etwa eine Metallflaeche, wurde nicht isoliert nachgewiesen.
- Der Versuch ist **kein abgeschlossener 24-Stunden-Stabilitaetstest**, weil
  die Aufstellung geaendert wurde und LoRa-, SD- sowie OLED-Fehler auftraten.

## Offene Punkte

1. Master-CSV je Geraet auf Anzahl, Sequenzluecken und Duplikate auswerten.
2. `Error 5` auf C01 mit vollstaendiger serieller Meldung und SD-Pruefung reproduzieren.
3. LoRa-Fehler `-1` auf M01 untersuchen und pruefen, ob der Empfang danach weiterlaeuft.
4. C02 mit serieller Ausgabe gegen das OLED-Verhalten abgrenzen.
5. Nach Fehlerbehebung einen neuen 24-Stunden-Test mit unveraenderter Aufstellung, Start- und Endzeit sowie CSV-Auswertung durchfuehren.
6. Zeitfuehrung am Tageswechsel auf der Hardware pruefen.
