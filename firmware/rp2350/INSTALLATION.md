# RP2350: CircuitPython 10.2.1

Dieses Paket ist ausschliesslich fuer C01 und M01 (Raspberry Pi Pico 2 W / RP2350A) bestimmt.

## Installation

1. Vollstaendige Sicherung von `CIRCUITPY`, `config.json` und SD-Karte erstellen.
2. Auf `CIRCUITPY` die Ordner `adapters`, `application`, `domain` und `ports` vollstaendig durch die gleichnamigen Ordner dieses Pakets ersetzen.
3. `code.py` aus diesem Paket nach `CIRCUITPY/code.py` kopieren.
4. `config.json`, den Ordner `lib/` und die SD-Daten unveraendert lassen.
5. Es duerfen keine gleichnamigen `.py`- und `.mpy`-Dateien in den vier Projektordnern verbleiben.
6. Laufwerk sicher auswerfen und den Pico neu starten.

Erzeugt mit: `CircuitPython 10.2.1 on 2026-05-12; mpy-cross emitting mpy v6.3`
