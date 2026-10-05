# Hexagonale Architektur - AUDI Climate Cube

Stand: 20.08.2026
Status: Technischer Architekturentwurf

## Ziel

Die Produktsoftware trennt die fachlichen Master- und Slave-Ablaeufe von
CircuitPython, GPIOs, Sensoren, SD-Karte und SX1262. Hardwareunabhaengige
Anwendungsfaelle koennen dadurch auf einem Entwicklungsrechner getestet werden.

## Bausteine

```text
                 +---------------------------+
                 |      Anwendungskern       |
                 | SlaveController           |
                 | MasterController          |
                 | MeasurementRecord / Codec |
                 +-------------+-------------+
                               |
                     Ports / Vertraege
                               |
        +----------------------+----------------------+
        |             |              |                |
      SEN66        SD-Karte        SX1262       Zeit / Diagnose
      Adapter       Adapter         Adapter          Adapter
```

- `domain/` enthaelt Messdatensatz und Protokollregeln.
- `application/` koordiniert die Master- und Slave-Anwendungsfaelle.
- `ports/` definiert die vom Kern benoetigten Schnittstellen. Die Hardwareadapter implementieren diese Port-Klassen explizit.
- `adapters/` bindet CircuitPython-Hardware und Konfiguration an.
- `code.py` ist die Composition Root und startet nur die konfigurierte Rolle. `build_diagnostics()` und `build_shared_components()` erzeugen gemeinsame Infrastruktur; `build_master()` und `build_slave()` verdrahten die rollenbezogenen Controller; `run_master()` und `run_slave()` enthalten nur die jeweilige Laufzeitschleife.
- Ein hardwareunabhaengiger Vertragstest prueft fuer jeden Kernadapter die erwartete Port-Basisklasse und die erforderlichen Methoden.
- Ein AST-basierter Architekturtest erzwingt die Abhaengigkeitsrichtung: Domain und Ports bleiben unabhaengig, Application importiert keine Adapter oder Hardwaremodule und Adapter importieren keine Application-Module.

## Bestaetigte Ablaufregeln

Der Slave speichert einen neuen Messdatensatz vor jedem Funkversuch lokal. Alle
ausstehenden Datensaetze werden beim 15-Minuten-Zyklus chronologisch gesendet.
Nach einem passenden ACK folgt der naechste Datensatz. Beim ersten fehlenden ACK
wird der Sendedurchlauf beendet und im naechsten Zyklus beim aeltesten noch
ausstehenden Datensatz fortgesetzt.

Der Master validiert einen Datensatz und schreibt ihn auf seine SD-Karte. Erst
danach sendet er ein Erfolgs-ACK. Ein bereits gespeichertes Duplikat wird erneut
bestaetigt, damit ein zuvor verlorenes ACK die Slave-Warteschlange nicht dauerhaft
blockiert.

Seit der Erweiterung vom 18.09.2026 misst der Master auch selbst. Der
SensorPort bietet dafuer `start_measurement()` und `poll_measurement()`.
Der SEN66-Adapter verwaltet Aufwaerm- und Wartephasen ohne lange Sleep-Aufrufe
im Master-Pfad. Die Composition Root wechselt zwischen Messfortschritt und
Funkempfang mit maximal 100 ms Empfangswartezeit pro Schleifendurchlauf.
Kurze Sensor-, SD- und Displayzugriffe bleiben synchron. Der MasterController
speichert eigene Datensaetze ueber den MasterStoragePort unter seiner ID;
die naechste lokale Sequenz wird aus denselben persistenten Messdateien
rekonstruiert wie bei empfangenen Daten. Ein lokaler Speicherfehler verhindert
nicht den anschliessenden Aufruf der Funkverarbeitung. Einzelheiten und
Hardware-Pruefschritte stehen in `Master_Messung_und_Zeit.md`.

## Fehlerbehandlung

`ports/errors.py` definiert mit `ClimateCubeError` eine gemeinsame Basis fuer erwartete technische Systemfehler. Konfigurations-, Zeit-, Speicher- und Funkadapter uebersetzen ihre Datei-, JSON-, Hardware- und Treiberfehler an der Port-Grenze in `ConfigurationError`, `ClockError`, `StorageError` beziehungsweise `RadioError`. Die Composition Root protokolliert diese erwarteten Fehler getrennt von unerwarteten Programmfehlern.

Einzelne fehlende oder fehlerhafte Sensorwerte werden nicht als Ausnahme durch den Anwendungskern gereicht, sondern durch definierte Statusflags im Messdatensatz dargestellt. Dadurch koennen verbleibende Messwerte gespeichert und uebertragen werden. Die konkrete Systemreaktion auf fehlende SD-Karten und dauerhaft ausgefallene Funkkommunikation bleibt fachlich beziehungsweise im Integrationstest zu klaeren.

## Bewusst offene Punkte

- Genauigkeit und Synchronisation der UTC-Zeitreferenz sind noch freizugeben.
- Das ASCII-Protokoll bleibt bis zur Freigabe des Datenformats ein Entwurf.
- Die feste Master-Zuordnung ueber `master_id` und die Master-Liste `monitored_slaves` werden beim Start validiert. `Q`- und `R`-Nachrichten pruefen diese Zuordnung; das vollstaendige V1-Daten- und ACK-Format bleibt umzusetzen.
- Der definierte RAM-Betrieb ohne Slave-SD ist implementiert und per Unit-Test abgesichert, aber noch auf Hardware zu testen. Bei defekter Master-SD bleibt ein Erfolgs-ACK unzulaessig. Die `NO_PACKET`-Lueckenzeilen fuer ueberwachte Slaves sind spezifiziert, aber noch nicht implementiert.
- Die optionale Bodenmessung und das OLED gehoeren nicht zum Kernpfad.
- Dynamisches Mesh und statisch konfiguriertes Relay-Routing sind nicht Bestandteil der Kernarchitektur; beide bleiben optionale, vor Umsetzung gesondert zu spezifizierende Erweiterungen.

Die Adapter enthalten keine Freigabe der Funkparameter fuer einen spaeteren
Einsatzort. Die Funkwerte aus den Konfigurationsvorlagen entsprechen nur dem bisherigen
lokalen Ping-Pong-Test.
