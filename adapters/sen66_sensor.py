"""SEN66-Adapter fuer Luftmesswerte und optionale Bodentemperatur."""

import time

import adafruit_sen6x

from ports.contracts import SensorPort
from domain.measurement import (
    MEASUREMENT_MISSING,
    SOIL_MOISTURE_ERROR,
    SEN66_ERROR,
    SOIL_TEMPERATURE_ERROR,
)

class Sen66SensorAdapter(SensorPort):
    def __init__(self, i2c, warmup_s=60, soil_sensor=None,
                 soil_moisture_sensor=None):
        self._i2c = i2c
        self._warmup_s = warmup_s
        self._soil_sensor = soil_sensor
        self._soil_moisture_sensor = soil_moisture_sensor
        self._sensor = None
        self._phase = None
        self._start_error = False

    def read_measurement(self):
        self.start_measurement()
        while True:
            result = self.poll_measurement()
            if result is not None:
                return result
            time.sleep(0.05)

    def start_measurement(self):
        if self._phase is not None:
            raise RuntimeError("measurement already active")
        self._start_error = False
        self._phase = "warmup"
        try:
            self._sensor = adafruit_sen6x.SEN66(self._i2c)
            self._sensor.start_measurement()
            self._ready_at = time.monotonic() + self._warmup_s
        except Exception as exc:
            print("SEN66 start error:", exc)
            self._start_error = True

    def poll_measurement(self):
        if self._phase is None:
            raise RuntimeError("no active measurement")
        try:
            if self._start_error:
                raise RuntimeError("SEN66 could not start")
            now = time.monotonic()
            if now < self._ready_at:
                return None
            if not self._sensor.data_ready:
                if now >= self._ready_at + 30:
                    raise RuntimeError("timeout waiting for SEN66 data")
                return None
            data = self._sensor.all_measurements()
            if self._phase == "warmup":
                self._phase = "sample"
                self._ready_at = now + 5
                return None
            values = {
                "air_temperature_c": data.get("temperature"),
                "relative_humidity_pct": data.get("humidity"),
                "co2_ppm": data.get("co2"),
                "pm1_0_ug_m3": data.get("pm1_0"),
                "pm2_5_ug_m3": data.get("pm2_5"),
                "pm4_0_ug_m3": data.get("pm4_0"),
                "pm10_ug_m3": data.get("pm10"),
                "voc_index": data.get("voc_index"),
                "nox_index": data.get("nox_index"),
                "soil_moisture_pct": None,
                "soil_temperature_c": None,
            }
            flags = 0
            for name in tuple(values)[:9]:
                if values[name] is None:
                    flags |= MEASUREMENT_MISSING
                    break
            soil_temperature, soil_temperature_failed = (
                self._read_soil_temperature()
            )
            values["soil_temperature_c"] = soil_temperature
            if soil_temperature_failed:
                flags |= SOIL_TEMPERATURE_ERROR | MEASUREMENT_MISSING
            soil_moisture, soil_moisture_failed = self._read_soil_moisture()
            values["soil_moisture_pct"] = soil_moisture
            if soil_moisture_failed:
                flags |= SOIL_MOISTURE_ERROR | MEASUREMENT_MISSING
            result = values, flags
        except Exception as exc:
            print("SEN66 error:", exc)
            result = self._empty_values(), SEN66_ERROR | MEASUREMENT_MISSING
        if self._sensor is not None:
            try:
                self._sensor.stop_measurement()
            except Exception:
                pass
        self._sensor = None
        self._phase = None
        return result

    def _read_soil_temperature(self):
        if self._soil_sensor is None:
            return None, False
        try:
            return self._soil_sensor.read_temperature(), False
        except Exception as exc:
            print("DS18B20 error:", exc)
            return None, True

    def _read_soil_moisture(self):
        if self._soil_moisture_sensor is None:
            return None, False
        try:
            return self._soil_moisture_sensor.read_moisture(), False
        except Exception as exc:
            print("soil moisture error:", exc)
            return None, True

    @staticmethod
    def _empty_values():
        return {
            "air_temperature_c": None,
            "relative_humidity_pct": None,
            "co2_ppm": None,
            "pm1_0_ug_m3": None,
            "pm2_5_ug_m3": None,
            "pm4_0_ug_m3": None,
            "pm10_ug_m3": None,
            "voc_index": None,
            "nox_index": None,
            "soil_moisture_pct": None,
            "soil_temperature_c": None,
        }
