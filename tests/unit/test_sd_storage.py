import csv
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from adapters.sd_storage import (
    DIAGNOSTIC_HEADER,
    MASTER_HEADER,
    PRE_SUMMARY_MASTER_HEADER,
    SLAVE_HEADER,
    SdStorageAdapter,
)
from ports.errors import StorageError
from domain.measurement import MEASUREMENT_FIELDS, MeasurementRecord
from domain.protocol import DiagnosticEvent


def record_for(device_id, sequence):
    values = {name: None for name in MEASUREMENT_FIELDS}
    values["co2_ppm"] = 430
    return MeasurementRecord(
        device_id, sequence, "2026-08-14T08:00:00Z", 60, values, 0x20
    )


def record(sequence):
    return record_for("C01", sequence)


class SdStorageTests(unittest.TestCase):
    def test_late_record_replaces_matching_pending_gap(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_missing_interval("C01", {
                "master_id": "M01", "master_uptime_s": 900,
                "received_timestamp": "2026-08-14T08:15:00Z",
            })
            path = directory + "/data/C01/measurements_000000-002999.csv"
            with open(path) as source:
                self.assertIn("NO_PACKET,1", source.read())

            storage.save_received(record(0), {
                "master_id": "M01", "master_uptime_s": 905,
                "received_timestamp": "2026-08-14T08:15:05Z",
            })
            with open(path) as source:
                rows = list(csv.DictReader(source))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["sequence_number"], "0")
            self.assertEqual(rows[0]["receive_status"], "0")

    def test_pending_gap_assignment_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_missing_interval("C01", {
                "master_id": "M01", "master_uptime_s": 900,
            })
            restarted = SdStorageAdapter(directory)
            restarted.save_received(record(0), {
                "master_id": "M01", "master_uptime_s": 905,
            })
            path = directory + "/data/C01/measurements_000000-002999.csv"
            with open(path) as source:
                self.assertNotIn("NO_PACKET", source.read())

    def test_diagnostic_events_are_central_and_active_state_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            started = DiagnosticEvent(
                "C01", "M01", "M01", 4, "SLAVE_SD_UNAVAILABLE", "STARTED"
            )
            self.assertTrue(storage.save_diagnostic_event(started))
            self.assertFalse(storage.save_diagnostic_event(started))
            path = directory + "/diagnostics/C01/events.csv"
            with open(path) as source:
                self.assertEqual(source.readline(), DIAGNOSTIC_HEADER)
                self.assertIn("C01,4,SLAVE_SD_UNAVAILABLE,STARTED,1", source.read())

            restarted = SdStorageAdapter(directory)
            self.assertFalse(restarted.save_diagnostic_event(started))
            ended = DiagnosticEvent(
                "C01", "M01", "M01", 4, "SLAVE_SD_UNAVAILABLE", "ENDED"
            )
            self.assertTrue(restarted.save_diagnostic_event(ended))

    def test_master_row_contains_event_summary_for_its_sequence(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            for event in (
                DiagnosticEvent("C01", "M01", "M01", 5, "DEVICE_RESTARTED", "OCCURRED", 2),
                DiagnosticEvent("C01", "M01", "M01", 5, "SLAVE_SD_WRITE_ERROR", "STARTED"),
                DiagnosticEvent("C01", "M01", "M01", 5, "SEN66_ERROR", "STARTED"),
            ):
                self.assertTrue(storage.save_diagnostic_event(event))
            storage.save_received(record(5), {
                "master_id": "M01", "master_uptime_s": 60,
            })
            path = directory + "/data/C01/measurements_000000-002999.csv"
            with open(path) as source:
                row = next(csv.DictReader(source))
            self.assertEqual(row["restart_count"], "2")
            self.assertEqual(row["sd_write_error_count"], "1")
            self.assertEqual(row["diagnostics"], "SEN66_ERROR:1")

    def test_existing_master_block_is_upgraded_with_empty_summaries(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_received(record(0), {
                "master_id": "M01", "master_uptime_s": 60,
            })
            path = directory + "/data/C01/measurements_000000-002999.csv"
            with open(path) as source:
                lines = source.readlines()
            with open(path, "w") as target:
                target.write(PRE_SUMMARY_MASTER_HEADER)
                target.write(",".join(lines[1].rstrip("\n").split(",")[:-3]) + "\n")

            restarted = SdStorageAdapter(directory)
            with open(path) as source:
                row = next(csv.DictReader(source))
            self.assertEqual(row["restart_count"], "0")
            self.assertEqual(row["sd_write_error_count"], "0")
            self.assertEqual(row["diagnostics"], "")
            self.assertTrue(restarted.has_received("C01", 0))
    def test_pending_offset_and_sequence_survive_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_local(record(0))
            storage.save_local(record(1))
            pending = storage.pending_records()
            first = next(pending)
            storage.mark_transmitted(first)

            restarted = SdStorageAdapter(directory)
            self.assertEqual(restarted.next_sequence(), 2)
            self.assertEqual(
                [item.sequence_number for item in restarted.pending_records()], [1]
            )

    def test_latest_measurement_timestamp_uses_latest_valid_sequence(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            first = record(0)
            first.measurement_timestamp = "2026-09-18T23:51:00Z"
            second = record(1)
            second.measurement_timestamp = "NA"
            storage.save_local(first)
            storage.save_local(second)
            self.assertEqual(
                storage.latest_measurement_timestamp("C01"),
                "2026-09-18T23:51:00Z",
            )

    def test_sequence_is_recovered_when_state_file_is_lost(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_local(record(4))
            os.remove(directory + "/climate_state.json")

            restarted = SdStorageAdapter(directory)
            self.assertEqual(restarted.next_sequence(), 5)

    def test_seq_14_master_recovers_multiple_slave_sequence_states(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            for item in (record_for("C01", 3), record_for("C02", 7)):
                storage.save_received(
                    item,
                    {
                        "received_timestamp": "2026-08-14T08:00:05Z",
                        "master_id": "M01",
                        "master_uptime_s": 65,
                        "rssi_dbm": -90,
                        "snr_db": 7,
                    },
                )
            os.remove(directory + "/climate_state.json")

            restarted = SdStorageAdapter(directory)
            self.assertEqual(restarted.next_sequence_for("C01"), 4)
            self.assertEqual(restarted.next_sequence_for("C02"), 8)

    def test_master_duplicate_state_is_recovered_from_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_received(
                record(3),
                {
                    "received_timestamp": "2026-08-14T08:00:05Z",
                    "master_id": "M01",
                    "master_uptime_s": 65,
                    "rssi_dbm": -90,
                    "snr_db": 7,
                },
            )
            os.remove(directory + "/climate_state.json")

            restarted = SdStorageAdapter(directory)
            self.assertTrue(restarted.has_received("C01", 3))

    def test_v1_block_boundaries_and_device_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            for sequence in (0, 2999, 3000, 5999, 6000):
                storage.save_local(record(sequence))
            base = directory + "/data/C01/"
            expected = {
                "measurements_000000-002999.csv": [0, 2999],
                "measurements_003000-005999.csv": [3000, 5999],
                "measurements_006000-008999.csv": [6000],
            }
            self.assertEqual(set(os.listdir(base)), set(expected))
            for name, sequences in expected.items():
                with open(base + name) as source:
                    reader = csv.DictReader(source)
                    self.assertEqual(reader.fieldnames, SLAVE_HEADER.strip().split(","))
                    self.assertEqual(
                        [int(row["sequence_number"]) for row in reader], sequences
                    )
            self.assertFalse(os.path.exists(directory + "/slave_measurements.csv"))

    def test_master_v1_columns_and_per_slave_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            for device_id in ("C01", "C02"):
                item = record_for(device_id, 3000)
                item.status_flags = 0x0040
                storage.save_received(item, {
                    "master_id": "M01", "master_uptime_s": 123,
                    "received_timestamp": None, "rssi_dbm": -90, "snr_db": 7.5,
                })
                path = directory + "/data/" + device_id + "/measurements_003000-005999.csv"
                with open(path) as source:
                    reader = csv.DictReader(source)
                    self.assertEqual(reader.fieldnames, MASTER_HEADER.strip().split(","))
                    rows = list(reader)
                self.assertEqual(len(rows), 1)
                row = rows[0]
                self.assertNotIn(None, row)
                self.assertEqual(row["device_id"], device_id)
                self.assertEqual(row["master_uptime_s"], "123")
                self.assertEqual(row["slave_uptime_s"], "60")
                self.assertEqual(row["measurement_timestamp"], "2026-08-14T08:00:00Z")
                self.assertEqual(row["received_timestamp"], "NA")
                self.assertEqual(row["soil_temperature_c"], "")
                self.assertEqual(row["co2_ppm"], "430")
                self.assertEqual(row["status_flags"], "0040")
                self.assertEqual(row["receive_status"], "0")
                self.assertEqual(row["missing_intervals"], "0")
            self.assertFalse(os.path.exists(directory + "/master_measurements.csv"))

    def test_block_rollover_preserves_fifo_after_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_local(record(2999))
            storage.save_local(record(3000))
            pending = storage.pending_records()
            storage.mark_transmitted(next(pending))
            pending.close()
            restarted = SdStorageAdapter(directory)
            self.assertEqual(restarted.next_sequence(), 3001)
            self.assertEqual(
                [item.sequence_number for item in restarted.pending_records()], [3000]
            )

    def test_local_sequence_recovers_from_csv_without_state_or_queue(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_local(record(6000))
            os.remove(directory + "/climate_state.json")
            os.remove(directory + "/pending_records.jsonl")
            restarted = SdStorageAdapter(directory)
            self.assertEqual(restarted.next_sequence(), 6001)

    def test_legacy_master_csv_is_unchanged_and_used_for_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            legacy_header = PRE_SUMMARY_MASTER_HEADER.replace("master_uptime_s,", "").replace(
                "slave_uptime_s", "uptime_s"
            ).replace(",missing_intervals", "")
            row = ["2026-08-14T08:00:05Z", "M01", "1", "C01", "2999",
                   "2026-08-14T08:00:00Z", "60"]
            row += [""] * len(MEASUREMENT_FIELDS)
            row += ["0020", "-90", "7.5", "0"]
            original = legacy_header + ",".join(row) + "\n"
            path = directory + "/master_measurements.csv"
            with open(path, "w") as output:
                output.write(original)
            storage = SdStorageAdapter(directory)
            self.assertEqual(storage.next_sequence_for("C01"), 3000)
            storage.save_received(record(3000), {
                "received_timestamp": None, "master_id": "M01", "master_uptime_s": 5,
            })
            with open(path + ".pre_v1" if path.endswith("_measurements.csv") else path) as source:
                self.assertEqual(source.read(), original)
            os.remove(directory + "/climate_state.json")
            restarted = SdStorageAdapter(directory)
            self.assertEqual(restarted.next_sequence_for("C01"), 3001)
            self.assertTrue(restarted.has_received("C01", 2999))

    def test_legacy_pending_records_remain_transmittable(self):
        with tempfile.TemporaryDirectory() as directory:
            with open(directory + "/pending_records.jsonl", "w") as output:
                output.write(json.dumps(record(7).to_dict()) + "\n")
            storage = SdStorageAdapter(directory)
            self.assertEqual(storage.next_sequence(), 8)
            self.assertEqual(
                [item.sequence_number for item in storage.pending_records()], [7]
            )
            storage.save_local(record(8))
            self.assertEqual(
                [item.sequence_number for item in storage.pending_records()], [7, 8]
            )

    def test_mismatched_header_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_local(record(0))
            path = directory + "/data/C01/measurements_000000-002999.csv"
            with open(path) as source:
                original = source.read()
            with self.assertRaises(StorageError):
                storage.save_received(record(1), {
                    "master_id": "M01", "master_uptime_s": 5,
                })
            with open(path + ".pre_v1" if path.endswith("_measurements.csv") else path) as source:
                self.assertEqual(source.read(), original)

    def test_partial_csv_tail_is_not_appended_or_counted(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_received(record(0), {
                "master_id": "M01", "master_uptime_s": 5,
            })
            path = directory + "/data/C01/measurements_000000-002999.csv"
            with open(path, "a") as output:
                output.write("NA,10,M01,1,C01,99")
            os.remove(directory + "/climate_state.json")
            restarted = SdStorageAdapter(directory)
            self.assertEqual(restarted.next_sequence_for("C01"), 1)
            with self.assertRaises(StorageError):
                restarted.save_received(record(1), {
                    "master_id": "M01", "master_uptime_s": 10,
                })

    def test_empty_block_gets_header(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            os.mkdir(directory + "/data")
            os.mkdir(directory + "/data/C01")
            path = directory + "/data/C01/measurements_000000-002999.csv"
            with open(path, "w"):
                pass
            storage.save_local(record(0))
            with open(path) as source:
                self.assertEqual(source.readline(), SLAVE_HEADER)

    def test_invalid_path_ids_and_negative_sequences_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            for device_id, sequence in (("../C01", 0), ("C/01", 0), ("C01", -1)):
                with self.subTest(device_id=device_id, sequence=sequence):
                    with self.assertRaises(StorageError):
                        storage.save_local(record_for(device_id, sequence))
            self.assertFalse(os.path.exists(directory + "/data"))

    def test_master_recovery_scans_all_blocks_not_directory_order(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            for device_id, sequence in (("C01", 6000), ("C02", 3000), ("C01", 2999)):
                storage.save_received(record_for(device_id, sequence), {
                    "master_id": "M01", "master_uptime_s": 5,
                })
            os.remove(directory + "/climate_state.json")
            restarted = SdStorageAdapter(directory)
            self.assertEqual(restarted.next_sequence_for("C01"), 6001)
            self.assertEqual(restarted.next_sequence_for("C02"), 3001)


    def test_legacy_slave_csv_preserves_sequence_and_original_file(self):
        with tempfile.TemporaryDirectory() as directory:
            header = SLAVE_HEADER.replace("slave_uptime_s", "uptime_s")
            row = ["1", "C01", "2999", "2026-08-14T08:00:00Z", "60"]
            row += [""] * len(MEASUREMENT_FIELDS) + ["0020"]
            original = header + ",".join(row) + "\n"
            path = directory + "/slave_measurements.csv"
            with open(path, "w") as output:
                output.write(original)
            storage = SdStorageAdapter(directory)
            self.assertEqual(storage.next_sequence(), 3000)
            storage.save_local(record(3000))
            with open(path + ".pre_v1" if path.endswith("_measurements.csv") else path) as source:
                self.assertEqual(source.read(), original)

    def test_unreadable_measurement_directory_is_not_treated_as_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("adapters.sd_storage.os.listdir", side_effect=OSError(5, "I/O error")):
                with self.assertRaises(StorageError):
                    SdStorageAdapter(directory)

    def test_empty_storage_does_not_import_csv_migration(self):
        with tempfile.TemporaryDirectory() as directory:
            original_import = __import__

            def guarded_import(name, *args, **kwargs):
                if name == "adapters.csv_migration":
                    raise AssertionError("migration must stay unloaded")
                return original_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=guarded_import):
                SdStorageAdapter(directory)


if __name__ == "__main__":
    unittest.main()
