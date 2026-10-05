# Struktur des Abschluss-Papers: AUDI Climate Cube

**Stand:** 11.08.2026  
**Status:** Planungsentwurf  
**Grundlage:** `ISEP_Gruppe5_LudoGame2.0_Dokumentation.pdf` aus dem Sicherungsordner

## 1. Zweck

Am Ende des Pflichtpraktikums soll neben der technischen Projektdokumentation ein wissenschaftlich aufgebautes Paper entstehen. Die vorhandene ISEP-Dokumentation dient als strukturelle Orientierung. Inhalte werden nicht übernommen; Aufbau und Umfang werden an das Climate-Cube-Projekt angepasst.

Lastenheft, Pflichtenheft und Paper erfüllen unterschiedliche Aufgaben:

- Das Lastenheft beschreibt, was aus Sicht des Auftraggebers benötigt wird.
- Das Pflichtenheft beschreibt, wie diese Anforderungen technisch umgesetzt und geprüft werden sollen.
- Das Paper dokumentiert Fragestellung, Vorgehen, Entscheidungen, Umsetzung, Ergebnisse und Grenzen in zusammengefasster wissenschaftlicher Form.

## 2. Vorgesehene Gliederung

### Titel, Autor und Zugehörigkeit

- Projekttitel
- Autor
- Hochschule, Studiengang und betreuende Personen
- Bearbeitungszeitraum

### Abstract und Keywords

Kurze Zusammenfassung von Ausgangsproblem, Ziel, Methode, Umsetzung und wichtigsten Ergebnissen. Das Abstract wird nach Abschluss der Auswertung finalisiert.

### I. Einleitung

- Einsatzkontext der Climate Cubes
- Problemstellung bei autarken Messstationen ohne LoRaWAN
- Ziel des Projekts
- Abgrenzung des Projektumfangs
- Aufbau des Papers

### II. Projektorganisation und Vorgehensmodell

- Beteiligte Rollen und Verantwortlichkeiten
- Abstimmungs- und Freigabeprozess
- Dokumentations- und Versionsverwaltung
- Vorgehen von Lastenheft und Pflichtenheft über Architektur und Tests bis zur Abnahme

### III. Anforderungen und Analysemethode

- Erhebung und Einordnung der Anforderungen
- Systemrollen und Anwendungsfälle
- Funktionale und nichtfunktionale Anforderungen
- Abnahmekriterien
- Offene Punkte und Umgang mit Änderungen

### IV. Ausgangssystem und Hardwareanalyse

- Raspberry Pi Pico 2 W und CircuitPython
- LoRa-Erweiterung Waveshare Pico-LoRa-SX1262
- vorhandene Sensorik und SD-Speicherung
- analysierter Ausgangscode
- festgestellte Hardware- und Pinbelegungsfragen

### V. Systemarchitektur und Entwurfsentscheidungen

- Rollen von Slave und Master
- Kommunikationsstruktur und betrachtete Alternativen
- LoRa-Peer-to-Peer-Protokoll
- Datenformat, Zeitbezug und Identifikation
- lokale Datensicherung
- Fehlerbehandlung und Wiederholungsstrategie
- Begründung wichtiger technischer Entscheidungen

### VI. Implementierung

- Slave-Software
- Master-Software
- Konfiguration und Inbetriebnahme
- Speicherung und Export
- wesentliche Änderungen gegenüber dem Ausgangssystem

### VII. Verifikation und Testmethodik

- Testaufbau und verwendete Hardware
- Modultests und Schnittstellentests
- LoRa-Ping-Pong- und Reichweitentests
- Integrations- und Dauertests
- Prüfung von Datenvollständigkeit, Zeitbezug und Fehlerfällen
- Zuordnung der Tests zu Anforderungen und Abnahmekriterien

### VIII. Ergebnisse

- erreichte Funktionen
- Messergebnisse und Kommunikationsqualität
- Speicher- und Laufzeitverhalten, soweit erhoben
- Ergebnisse der Abnahmeszenarien
- Abweichungen von den geplanten Anforderungen

### IX. Diskussion

- Einordnung der Ergebnisse
- technische Grenzen
- Aussagekraft und Grenzen der Tests
- Risiken für den Einsatz unter realen Bedingungen
- nicht umgesetzte oder zurückgestellte Anforderungen

### X. Projektverlauf

- wesentliche Meilensteine
- Änderungen an Anforderungen oder Architektur
- aufgetretene Probleme und gewählte Lösungen
- Reflexion des Vorgehens

### XI. Fazit und Ausblick

- Zusammenfassung des Projektergebnisses
- Erfüllungsgrad der Projektziele
- sinnvolle nächste Entwicklungsschritte

### Literaturverzeichnis

Herstellerdokumentation, technische Standards, verwendete Bibliotheken und gegebenenfalls wissenschaftliche Quellen werden einheitlich zitiert.

### Anhang

- Anforderungs- und Rückverfolgbarkeitsmatrizen
- relevante Diagramme
- Testprotokolle und ausgewählte Logauszüge
- Bedien- oder Inbetriebnahmeanleitung
- zusätzliche technische Tabellen

## 3. Laufende Nachweise

Während des Projekts werden folgende Nachweise fortlaufend gepflegt, damit das Paper am Ende nicht rückwirkend rekonstruiert werden muss:

| Nachweis | Ablage | Verwendung im Paper |
|---|---|---|
| Anforderungen und Änderungen | Lasten- und Pflichtenheft | Kapitel III und X |
| Rollen und Anwendungsfälle | Pflichtenheft | Kapitel II und III |
| Architekturentscheidungen | Architekturunterlagen und Projekttagebuch | Kapitel V und X |
| Implementierungsstand | Git-Historie und Projekttagebuch | Kapitel VI und X |
| Testaufbau und Rohdaten | `tests/` | Kapitel VII und VIII |
| Abweichungen und Grenzen | Projekttagebuch und Testprotokolle | Kapitel VIII und IX |

## 4. Schreibplan

- **Anforderungsphase:** Kapitel I bis III als Entwurf beginnen.
- **Architekturphase:** Kapitel IV und V ergänzen.
- **Implementierungsphase:** Kapitel VI parallel zur Entwicklung pflegen.
- **Testphase:** Testmethodik vor den Tests festhalten; Ergebnisse anschließend eintragen.
- **Abschlussphase:** Diskussion, Projektverlauf, Fazit und Abstract finalisieren.

## 5. Noch Zu Klaerende Formale Vorgaben

Vor der endgültigen Ausarbeitung müssen mit den zuständigen Betreuenden geklärt werden:

- gewünschte Sprache des Papers
- verbindliche Formatvorlage, beispielsweise IEEEtran
- erwarteter Seitenumfang
- Abgabedatum und Abgabeformat
- Angaben zu Autor, Hochschule, Unternehmen und Betreuung
- gewünschter Zitierstil
- zulässiger Umfang des Anhangs
- Verhältnis zwischen Paper und weiterer Projektdokumentation

## 6. Fertigstellungskriterien

Das Paper gilt als fertig, wenn:

- alle finalen Anforderungen und wesentlichen Entscheidungen nachvollziehbar dargestellt sind,
- Vorgehen, Implementierung und Tests reproduzierbar beschrieben sind,
- Aussagen zu Ergebnissen durch Protokolle oder Messdaten belegt sind,
- Abweichungen und Grenzen offen benannt sind,
- alle verwendeten Quellen korrekt angegeben sind,
- die formalen Vorgaben der betreuenden Stelle eingehalten und geprüft wurden.
