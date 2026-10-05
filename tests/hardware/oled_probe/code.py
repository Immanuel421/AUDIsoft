"""Reiner OLED-Test fuer den Climate Cube ohne SD, LoRa oder Sensoren."""

import time

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
try:
    display.sleep(False)
except Exception:
    pass
group = displayio.Group()
group.append(label.Label(terminalio.FONT, text="OLED OK", x=34, y=18))
group.append(label.Label(terminalio.FONT, text="M01 display test", x=8, y=40))
display.root_group = group

print("OLED probe started")
while True:
    time.sleep(30)
