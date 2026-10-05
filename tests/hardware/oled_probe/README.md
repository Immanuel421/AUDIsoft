# OLED-Test

1. Die aktuelle `CIRCUITPY/code.py` sichern.
2. `code.py` aus diesem Ordner voruebergehend nach `CIRCUITPY/code.py` kopieren.
3. Pico sicher auswerfen und neu starten.

Das OLED muss `OLED OK` und `M01 display test` zeigen. Der Test verwendet
keine SD-Karte, kein LoRa und keine Projektmodule. Danach die produktive
`firmware/rp2350/code.py` wiederherstellen.
