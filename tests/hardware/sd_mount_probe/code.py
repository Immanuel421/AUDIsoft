"""Isolierter SD-Mount-Test fuer CircuitPython auf dem Climate Cube.

Diese Datei nur voruebergehend als CIRCUITPY/code.py verwenden. Sie startet
weder die Projektsoftware noch SEN66 oder LoRa und schreibt nichts auf die SD.
"""

import gc
import time


def memory_text():
    if hasattr(gc, "mem_free"):
        return "free {} B".format(gc.mem_free())
    return "heap unknown"


def show_result(title, lines):
    print(title)
    for line in lines:
        print(line)

    try:
        import board
        import busio
        import displayio
        import i2cdisplaybus
        import terminalio
        from adafruit_display_text import label
        import adafruit_displayio_sh1106

        displayio.release_displays()
        i2c = busio.I2C(scl=board.GP1, sda=board.GP0, frequency=100000)
        display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
        display = adafruit_displayio_sh1106.SH1106(
            display_bus, width=128, height=64
        )
        group = displayio.Group()
        group.append(label.Label(terminalio.FONT, text=title[:21], x=2, y=8))
        for index, line in enumerate(lines[:4]):
            group.append(label.Label(
                terminalio.FONT, text=str(line)[:21], x=2, y=24 + index * 12
            ))
        display.root_group = group
    except Exception as exc:
        print("OLED unavailable:", exc)


def main():
    gc.collect()
    before = memory_text()
    try:
        import board
        import busio
        import sdcardio
        import storage

        gc.collect()
        spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16)
        card = sdcardio.SDCard(spi, board.GP17)
        vfs = storage.VfsFat(card)
        storage.mount(vfs, "/sd")
        show_result("SD mount OK", [before, memory_text(), "no data written"])
    except Exception as exc:
        gc.collect()
        show_result("SD mount failed", [type(exc).__name__, str(exc), before])

    while True:
        time.sleep(30)


main()
