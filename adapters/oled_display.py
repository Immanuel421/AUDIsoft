"""SH1106-OLED-Adapter fuer Start- und Diagnosemeldungen."""

import time
import board
import busio
import displayio
import i2cdisplaybus
import terminalio
from adafruit_display_text import label
import adafruit_displayio_sh1106


class OledDisplayAdapter:
    WIDTH = 128
    MAX_CHARS = 21

    def __init__(self, i2c=None):
        displayio.release_displays()
        self.i2c = i2c or busio.I2C(
            scl=board.GP1, sda=board.GP0, frequency=100000
        )
        display_bus = i2cdisplaybus.I2CDisplayBus(
            self.i2c, device_address=0x3C
        )
        self.display = adafruit_displayio_sh1106.SH1106(
            display_bus, width=128, height=64
        )
        try:
            self.display.brightness = 0.15
        except Exception:
            pass

    def show_startup(self):
        self.show_message("", ["Hochschule", "Hof"], 2)
        self.show_message("", ["Audi", "Umweltstiftung"], 2)
        self.show_message("Climate Cube", ["Starte System ..."], 1)

    def show_message(self, title, lines, seconds=None):
        group = displayio.Group()
        title = self._trim(title)
        group.append(label.Label(
            terminalio.FONT, text=title, x=self._center_x(title), y=8
        ))
        wrapped = []
        for line in lines:
            wrapped.extend(self._wrap(str(line)))
        for index in range(4):
            text = wrapped[index] if index < len(wrapped) else ""
            group.append(label.Label(
                terminalio.FONT,
                text=text,
                x=self._center_x(text),
                y=(24, 36, 48, 60)[index],
            ))
        try:
            self.display.sleep(False)
        except Exception:
            try:
                self.display.wake()
            except Exception:
                pass
        self.display.root_group = group
        if seconds is not None:
            time.sleep(seconds)

    def _wrap(self, text):
        if not text:
            return [""]
        return [
            text[index:index + self.MAX_CHARS]
            for index in range(0, len(text), self.MAX_CHARS)
        ]

    def _trim(self, text):
        return str(text)[:self.MAX_CHARS]

    def _center_x(self, text):
        return max(0, (self.WIDTH - len(text) * 6) // 2)
