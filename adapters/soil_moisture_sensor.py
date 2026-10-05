"""Kalibrierter Analogadapter fuer den kapazitiven Bodenfeuchtesensor."""

import analogio
import board


class SoilMoistureSensorAdapter:
    def __init__(self, dry_raw, wet_raw, pin=board.GP27):
        self._dry_raw = int(dry_raw)
        self._wet_raw = int(wet_raw)
        if self._dry_raw == self._wet_raw:
            raise ValueError("soil moisture calibration values must differ")
        self._input = analogio.AnalogIn(pin)

    def read_moisture(self):
        raw_value = self._input.value
        percent = (raw_value - self._dry_raw) * 100 / (
            self._wet_raw - self._dry_raw
        )
        return max(0, min(100, round(percent)))
