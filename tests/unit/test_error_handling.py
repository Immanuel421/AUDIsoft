import json
from pathlib import Path
import tempfile
import unittest

from adapters.clock import ConfiguredUtcClock
from adapters.configuration import load_configuration
from adapters.sd_storage import SdStorageAdapter
from domain.measurement import MEASUREMENT_FIELDS, MeasurementRecord
from ports.errors import (
    ClimateCubeError,
    ClockError,
    ConfigurationError,
    RadioError,
    StorageError,
)


class ErrorHandlingTests(unittest.TestCase):
    def test_specialized_errors_share_one_base_class(self):
        for error_type in (
            ClockError,
            ConfigurationError,
            RadioError,
            StorageError,
        ):
            self.assertTrue(issubclass(error_type, ClimateCubeError))

    def test_missing_configuration_raises_configuration_error(self):
        with self.assertRaises(ConfigurationError):
            load_configuration("/path/that/does/not/exist.json")

    def test_invalid_configuration_raises_configuration_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(
                json.dumps({"role": "invalid", "device_id": "C01"}),
                encoding="utf-8",
            )
            with self.assertRaises(ConfigurationError):
                load_configuration(str(path))

    def test_master_configuration_accepts_more_than_ten_unique_slaves(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(
                json.dumps({
                    "role": "master",
                    "device_id": "M01",
                    "monitored_slaves": [
                        "C{:02d}".format(index) for index in range(1, 13)
                    ],
                }),
                encoding="utf-8",
            )
            config = load_configuration(str(path))
            self.assertEqual(len(config["monitored_slaves"]), 12)

    def test_master_configuration_requires_monitored_slaves(self):
        invalid_lists = (
            None,
            [],
            ["C01", "C01"],
            ["M01"],
            ["bad id"],
        )
        for monitored_slaves in invalid_lists:
            with self.subTest(monitored_slaves=monitored_slaves):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "config.json"
                    config = {"role": "master", "device_id": "M01"}
                    if monitored_slaves is not None:
                        config["monitored_slaves"] = monitored_slaves
                    path.write_text(json.dumps(config), encoding="utf-8")
                    with self.assertRaises(ConfigurationError):
                        load_configuration(str(path))

    def test_slave_configuration_requires_distinct_master_id(self):
        invalid_master_ids = (None, "C01", "invalid id")
        for master_id in invalid_master_ids:
            with self.subTest(master_id=master_id):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "config.json"
                    config = {"role": "slave", "device_id": "C01"}
                    if master_id is not None:
                        config["master_id"] = master_id
                    path.write_text(json.dumps(config), encoding="utf-8")
                    with self.assertRaises(ConfigurationError):
                        load_configuration(str(path))

    def test_network_mode_defaults_to_star(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps({
                "role": "slave", "device_id": "C01", "master_id": "M01"
            }), encoding="utf-8")
            self.assertEqual(load_configuration(str(path))["network_mode"], "star")

    def test_plausibility_limits_require_known_numeric_ranges(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps({
                "role": "slave", "device_id": "C01", "master_id": "M01",
                "plausibility_limits": {
                    "co2_ppm": {"min": 400, "max": 2000},
                },
            }), encoding="utf-8")
            config = load_configuration(str(path))
            self.assertEqual(config["plausibility_limits"]["co2_ppm"]["max"], 2000)
            path.write_text(json.dumps({
                "role": "slave", "device_id": "C01", "master_id": "M01",
                "plausibility_limits": {"unknown": {"min": 0, "max": 1}},
            }), encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                load_configuration(str(path))

    def test_mesh_slave_requires_route_and_positive_hop_limit(self):
        invalid_mesh_configs = (
            {"role": "slave", "device_id": "C01", "master_id": "M01", "network_mode": "mesh"},
            {"role": "slave", "device_id": "C01", "master_id": "M01", "network_mode": "mesh", "next_hop_id": "C01", "hop_limit": 2},
            {"role": "slave", "device_id": "C01", "master_id": "M01", "network_mode": "mesh", "next_hop_id": "C02", "hop_limit": 0},
        )
        for config in invalid_mesh_configs:
            with self.subTest(config=config), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "config.json"
                path.write_text(json.dumps(config), encoding="utf-8")
                with self.assertRaises(ConfigurationError):
                    load_configuration(str(path))

    def test_mesh_slave_configuration_accepts_static_next_hop(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps({
                "role": "slave", "device_id": "C03", "master_id": "M01",
                "network_mode": "mesh", "next_hop_id": "C02", "hop_limit": 3,
            }), encoding="utf-8")
            config = load_configuration(str(path))
            self.assertEqual(config["next_hop_id"], "C02")
            self.assertEqual(config["hop_limit"], 3)

    def test_missing_time_reference_raises_clock_error(self):
        with self.assertRaises(ClockError):
            ConfiguredUtcClock(None)

    def test_invalid_time_reference_raises_clock_error(self):
        with self.assertRaises(ClockError):
            ConfiguredUtcClock("not-an-epoch")

    def test_storage_write_failure_raises_storage_error(self):
        with tempfile.TemporaryDirectory() as directory:
            missing_mount = str(Path(directory) / "missing" / "sd")
            storage = SdStorageAdapter(missing_mount)
            values = {name: None for name in MEASUREMENT_FIELDS}
            record = MeasurementRecord(
                "C01", 0, "2026-08-20T12:00:00Z", 1, values, 0
            )
            with self.assertRaises(StorageError):
                storage.save_local(record)


if __name__ == "__main__":
    unittest.main()
