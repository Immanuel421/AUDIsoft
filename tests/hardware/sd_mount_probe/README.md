# SD-Mount-Speichertest

Dieser Test trennt einen Speicher- oder Hardwarefehler beim SD-Mount von der
normalen Climate-Cube-Software. Er misst nicht, funkt nicht und veraendert
keine SD-Datei.

## Ausfuehren Auf M01

1. M01 ausschalten und `CIRCUITPY/code.py` sichern.
2. `tests/hardware/sd_mount_probe/code.py` voruebergehend als
   `CIRCUITPY/code.py` kopieren.
3. Alle Projektordner, `lib/`, `config.json` und die SD-Karte unveraendert
   lassen.
4. Laufwerk sicher auswerfen und M01 neu starten.
5. Ergebnis auf dem OLED ablesen.

`SD mount OK` bedeutet: SD-Hardware und CircuitPython koennen mit einem
minimalen Programm mounten. Dann belegt die normale Anwendung noch zu viel
RAM und wird weiter entlastet.

`SD mount failed` mit `MemoryError` bedeutet: Der Fehler besteht bereits ohne
die Projektschichten. Dann sind CircuitPython-Version, SD-Karte, ihre
Formatierung und der freie Speicher auf dem Geraet zu pruefen.

Danach die gesicherte produktive `code.py` wiederherstellen. Der Test wird
nicht zusammen mit der normalen Firmware installiert.
