"""Optionaler DS18B20-Adapter fuer die Bodentemperatur an GP27."""

import board
from adafruit_ds18x20 import DS18X20
from adafruit_onewire.bus import OneWireBus


class Ds18b20SensorAdapter:
    def __init__(self, pin=board.GP27):
        self._bus = OneWireBus(pin)
        devices = self._bus.scan()
        self._sensor = DS18X20(self._bus, devices[0]) if devices else None

    def read_temperature(self):
        if self._sensor is None:
            return None
        return self._sensor.temperature
