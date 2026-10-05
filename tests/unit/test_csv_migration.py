import csv
import os
import tempfile
import unittest
from unittest.mock import patch

from adapters.csv_migration import migrate_legacy_csv
from adapters.sd_storage import (
    PRE_SUMMARY_MASTER_HEADER,
    MASTER_HEADER,
    SLAVE_HEADER,
    SdStorageAdapter,
)
from domain.measurement import MEASUREMENT_FIELDS, MeasurementRecord
from ports.errors import StorageMigrationError


def write_legacy(directory, records, master=False):
    header = PRE_SUMMARY_MASTER_HEADER if master else SLAVE_HEADER
    header = header.replace("master_uptime_s,", "").replace(
        "slave_uptime_s", "uptime_s"
    ).replace(",missing_intervals", "")
    path = directory + ("/master_measurements.csv" if master else "/slave_measurements.csv")
    with open(path, "w") as output:
        output.write(header)
        for device_id, sequence, co2 in records:
            row = ["1", device_id, str(sequence), "2026-09-09T08:00:00Z", "60"]
            row += [str(co2) if name == "co2_ppm" else "" for name in MEASUREMENT_FIELDS]
            row += ["0020"]
            if master:
                row = ["2026-09-09T08:00:05Z", "M01"] + row + ["-90", "7.5", "OK"]
            output.write(",".join(row) + "\n")
    return path


def block_rows(directory, device_id="C01", block=0):
    path = directory + "/data/" + device_id + "/measurements_{:06d}-{:06d}.csv".format(
        block * 3000, block * 3000 + 2999
    )
    with open(path) as source:
        return list(csv.DictReader(source))


def new_record(sequence, co2=430):
    values = {name: None for name in MEASUREMENT_FIELDS}
    values["co2_ppm"] = co2
    return MeasurementRecord("C01", sequence, "2026-09-09T08:00:00Z", 60, values, 0x20)


class CsvMigrationTests(unittest.TestCase):
    def test_imports_sorted_blocks_and_preserves_backup_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_legacy(directory, [
                ("C01", 3000, 430), ("C02", 4, 440), ("C01", 2999, 450),
                ("C01", 0, 460),
            ])
            with open(path, "rb") as source:
                original = source.read()
            storage = SdStorageAdapter(directory)
            self.assertFalse(os.path.exists(path))
            with open(path + ".pre_v1", "rb") as source:
                self.assertEqual(source.read(), original)
            self.assertEqual([row["sequence_number"] for row in block_rows(directory)],
                             ["0", "2999"])
            self.assertEqual(block_rows(directory, block=1)[0]["co2_ppm"], "430")
            self.assertEqual(block_rows(directory, "C02")[0]["co2_ppm"], "440")
            self.assertEqual(storage.next_sequence(), 3001)
            self.assertFalse(os.path.exists(directory + "/pending_records.jsonl"))

    def test_master_unknown_uptime_is_not_invented(self):
        with tempfile.TemporaryDirectory() as directory:
            write_legacy(directory, [("C01", 157, 430)], master=True)
            storage = SdStorageAdapter(directory)
            row = block_rows(directory)[0]
            self.assertEqual(row["master_uptime_s"], "NA")
            self.assertEqual(row["slave_uptime_s"], "60")
            self.assertEqual(row["receive_status"], "0")
            self.assertEqual(row["missing_intervals"], "0")
            self.assertEqual(row["rssi_dbm"], "-90")
            self.assertEqual(storage.next_sequence_for("C01"), 158)

    def test_restart_does_not_duplicate_and_new_data_share_same_block(self):
        with tempfile.TemporaryDirectory() as directory:
            write_legacy(directory, [("C01", 0, 430)])
            storage = SdStorageAdapter(directory)
            storage.save_local(new_record(1))
            SdStorageAdapter(directory)
            self.assertEqual([row["sequence_number"] for row in block_rows(directory)],
                             ["0", "1"])

    def test_existing_v1_rows_are_merged_in_sequence_order(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_local(new_record(2))
            write_legacy(directory, [("C01", 1, 430), ("C01", 0, 430)])
            SdStorageAdapter(directory)
            self.assertEqual([row["sequence_number"] for row in block_rows(directory)],
                             ["0", "1", "2"])

    def test_overlapping_rows_are_not_duplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_local(new_record(0))
            write_legacy(directory, [("C01", 0, 430), ("C01", 0, 430)])
            SdStorageAdapter(directory)
            self.assertEqual(len(block_rows(directory)), 1)

    def test_conflicting_values_stop_import_without_overwriting_target(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_local(new_record(0))
            path = write_legacy(directory, [("C01", 0, 999)])
            with self.assertRaises(StorageMigrationError):
                SdStorageAdapter(directory)
            self.assertTrue(os.path.exists(path))
            self.assertEqual(block_rows(directory)[0]["co2_ppm"], "430")

    def test_conflicting_legacy_duplicates_are_not_silently_dropped(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_legacy(directory, [("C01", 0, 430), ("C01", 0, 999)])
            with self.assertRaises(StorageMigrationError):
                SdStorageAdapter(directory)
            self.assertTrue(os.path.exists(path))
            self.assertFalse(os.path.exists(path + ".pre_v1"))

    def test_partial_source_is_not_archived(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_legacy(directory, [("C01", 0, 430)])
            with open(path, "a") as output:
                output.write("1,C01,1")
            with self.assertRaises(StorageMigrationError):
                SdStorageAdapter(directory)
            self.assertTrue(os.path.exists(path))
            self.assertFalse(os.path.exists(directory + "/data"))

    def test_interruption_between_block_renames_can_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_local(new_record(1))
            source = write_legacy(directory, [("C01", 0, 430)])
            rename = os.rename

            def interrupted(old, new):
                if old.endswith(".migration.tmp"):
                    raise OSError(5, "simulated power interruption")
                rename(old, new)

            with patch("adapters.csv_migration.os.rename", side_effect=interrupted):
                with self.assertRaises(StorageMigrationError):
                    SdStorageAdapter(directory)
            self.assertTrue(os.path.exists(source))
            SdStorageAdapter(directory)
            self.assertEqual([row["sequence_number"] for row in block_rows(directory)],
                             ["0", "1"])
            self.assertFalse(any("migration" in name for name in os.listdir(directory + "/data/C01")))

    def test_interruption_before_source_archive_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_legacy(directory, [("C01", 0, 430), ("C01", 3000, 440)])
            rename = os.rename

            def interrupted(old, new):
                if old == source:
                    raise OSError(5, "simulated power interruption")
                rename(old, new)

            with patch("adapters.csv_migration.os.rename", side_effect=interrupted):
                with self.assertRaises(StorageMigrationError):
                    SdStorageAdapter(directory)
            SdStorageAdapter(directory)
            self.assertEqual(len(block_rows(directory)), 1)
            self.assertEqual(len(block_rows(directory, block=1)), 1)

    def test_existing_backup_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_legacy(directory, [("C01", 0, 430)])
            with open(source + ".pre_v1", "w") as output:
                output.write("previous backup")
            with self.assertRaises(StorageMigrationError):
                SdStorageAdapter(directory)
            with open(source + ".pre_v1") as backup:
                self.assertEqual(backup.read(), "previous backup")

    def test_migration_preserves_pending_queue_and_ack_offset(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_local(new_record(0))
            storage.save_local(new_record(1))
            pending = storage.pending_records()
            storage.mark_transmitted(next(pending))
            pending.close()
            with open(directory + "/pending_records.jsonl", "rb") as source:
                original = source.read()
            write_legacy(directory, [("C01", 0, 430)])
            restarted = SdStorageAdapter(directory)
            self.assertEqual([item.sequence_number for item in restarted.pending_records()], [1])
            with open(directory + "/pending_records.jsonl", "rb") as source:
                self.assertEqual(source.read(), original)

    def test_write_failure_keeps_legacy_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = write_legacy(directory, [("C01", 0, 430)])
            original_open = open

            def no_space(path, mode="r", *args, **kwargs):
                if path.endswith(".migration.tmp") and mode == "w":
                    raise OSError(28, "SD full")
                return original_open(path, mode, *args, **kwargs)

            with patch("builtins.open", side_effect=no_space):
                with self.assertRaises(StorageMigrationError):
                    SdStorageAdapter(directory)
            self.assertTrue(os.path.exists(source))
            self.assertFalse(os.path.exists(source + ".pre_v1"))

    def test_header_mismatch_keeps_existing_block(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = SdStorageAdapter(directory)
            storage.save_local(new_record(0))
            path = write_legacy(directory, [("C01", 0, 430)], master=True)
            with self.assertRaises(StorageMigrationError):
                SdStorageAdapter(directory)
            self.assertTrue(os.path.exists(path))
            self.assertNotIn("master_id", block_rows(directory)[0])


if __name__ == "__main__":
    unittest.main()
