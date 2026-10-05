import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

from domain.measurement import MEASUREMENT_IMPLAUSIBLE
from domain.plausibility import PlausibilityPolicy


class SensorPollingTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.reads = 0
        self.stops = 0
        self.ready = True
        self.fail_start = False
        self.fail_read = False
        chip = types.SimpleNamespace(
            start_measurement=self.start, stop_measurement=self.stop,
            all_measurements=self.read,
        )
        self.chip = chip
        chip.data_ready = True
        path = Path(__file__).resolve().parents[2] / 'adapters/sen66_sensor.py'
        spec = importlib.util.spec_from_file_location('sensor_under_test', path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {
            'adafruit_sen6x': types.SimpleNamespace(SEN66=lambda i2c: chip),
        }):
            spec.loader.exec_module(self.module)
        self.module.time = types.SimpleNamespace(monotonic=lambda: self.now, sleep=self.sleep)
        self.sensor = self.module.Sen66SensorAdapter(object(), warmup_s=60)

    def sleep(self, seconds):
        self.now += seconds

    def start(self):
        if self.fail_start:
            raise OSError('sensor missing')

    def stop(self):
        self.stops += 1

    def read(self):
        self.reads += 1
        if self.fail_read:
            raise OSError('sensor read failed')
        return dict(temperature=20, humidity=50, co2=500, pm1_0=1,
                    pm2_5=2, pm4_0=3, pm10=4, voc_index=5, nox_index=6)

    def test_warmup_and_settling_are_nonblocking(self):
        self.sensor.start_measurement()
        self.assertIsNone(self.sensor.poll_measurement())
        self.assertEqual(self.now, 0)
        self.now = 60
        self.assertIsNone(self.sensor.poll_measurement())
        self.assertEqual(self.now, 60)
        self.assertEqual(self.reads, 1)
        self.now = 65
        values, flags = self.sensor.poll_measurement()
        self.assertEqual(values['co2_ppm'], 500)
        self.assertEqual(flags, 0)
        self.assertEqual(self.stops, 1)

    def test_timeout_returns_missing_values_and_allows_next_cycle(self):
        self.chip.data_ready = False
        self.sensor.start_measurement()
        self.now = 90
        values, flags = self.sensor.poll_measurement()
        self.assertIsNone(values['co2_ppm'])
        self.assertEqual(flags, 0x0021)
        self.assertEqual(self.stops, 1)
        self.sensor.start_measurement()
        self.assertIsNone(self.sensor.poll_measurement())

    def test_start_failure_is_reported_as_sensor_flags(self):
        self.fail_start = True
        self.sensor.start_measurement()
        values, flags = self.sensor.poll_measurement()
        self.assertEqual(flags, 0x0021)
        self.assertTrue(all(value is None for value in values.values()))

    def test_read_failure_stops_sensor_and_allows_next_cycle(self):
        self.fail_read = True
        self.sensor.start_measurement()
        self.now = 60
        self.assertEqual(self.sensor.poll_measurement()[1], 0x0021)
        self.assertEqual(self.stops, 1)
        self.sensor.start_measurement()

    def test_blocking_slave_api_still_produces_measurement(self):
        values, flags = self.sensor.read_measurement()
        self.assertEqual(values['air_temperature_c'], 20)
        self.assertEqual(flags, 0)
        self.assertGreaterEqual(self.now, 65)
        self.assertEqual(self.reads, 2)
        self.assertEqual(self.stops, 1)

    def test_failed_configured_soil_sensor_sets_specific_flags(self):
        self.sensor._soil_sensor = types.SimpleNamespace(
            read_temperature=lambda: (_ for _ in ()).throw(OSError('missing'))
        )
        values, flags = self.sensor.read_measurement()
        self.assertIsNone(values['soil_temperature_c'])
        self.assertEqual(flags, 0x0022)

    def test_plausibility_policy_marks_but_keeps_outlier(self):
        values = {"co2_ppm": 2500}
        policy = PlausibilityPolicy({"co2_ppm": {"min": 400, "max": 2000}})
        self.assertEqual(
            policy.apply(values, 0), MEASUREMENT_IMPLAUSIBLE
        )
        self.assertEqual(values["co2_ppm"], 2500)


if __name__ == '__main__':
    unittest.main()
