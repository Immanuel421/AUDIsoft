"""Persistente Slave-Warteschlange und zentrale Master-CSV auf SD."""

import json
import os

from domain.measurement import MEASUREMENT_FIELDS, MeasurementRecord
from ports.contracts import MasterStoragePort, SlaveStoragePort
from ports.errors import StorageError, StorageMigrationError

SLAVE_HEADER = (
    "format_version,device_id,sequence_number,measurement_timestamp,slave_uptime_s,"
    + ",".join(MEASUREMENT_FIELDS)
    + ",status_flags\n"
)
PRE_SUMMARY_MASTER_HEADER = (
    "received_timestamp,master_uptime_s,master_id,"
    + SLAVE_HEADER.rstrip("\n")
    + ",rssi_dbm,snr_db,receive_status,missing_intervals\n"
)
MASTER_HEADER = (
    PRE_SUMMARY_MASTER_HEADER.rstrip("\n")
    + ",restart_count,sd_write_error_count,diagnostics\n"
)
DIAGNOSTIC_HEADER = (
    "device_id,reference_sequence,event_code,event_state,repeat_count\n"
)


class SdStorageAdapter(SlaveStoragePort, MasterStoragePort):
    def __init__(self, mount_path="/sd", scan_existing_data=True):
        self._data_path = mount_path + "/data"
        self._state_path = mount_path + "/climate_state.json"
        self._backup_state_path = self._state_path + ".bak"
        self._slave_path = mount_path + "/slave_measurements.csv"
        self._pending_path = mount_path + "/pending_records.jsonl"
        self._master_path = mount_path + "/master_measurements.csv"
        self._pending_offsets = {}
        self._scan_existing_data = scan_existing_data
        phase = "loading state"
        try:
            self._state = self._load_state()
            if scan_existing_data:
                phase = "migrating legacy CSV files"
                self._migrate_legacy_csv_files()
                phase = "recovering measurement state"
                self._recover_state()
            phase = "recovering diagnostic state"
            self._active_diagnostics = self._recover_diagnostic_state()
        except (OSError, ValueError, TypeError) as exc:
            raise StorageError(
                "SD state cannot be initialized during {}: {}".format(phase, exc)
            )

    def next_sequence(self):
        return int(self._state.get("next_sequence", 0))

    def _migrate_legacy_csv_files(self):
        if self._has_legacy_csv():
            try:
                from adapters.csv_migration import migrate_legacy_csv

                migrate_legacy_csv(self._slave_path, SLAVE_HEADER, self._block_path)
                migrate_legacy_csv(
                    self._master_path, MASTER_HEADER, self._block_path
                )
            except (OSError, ValueError, TypeError, KeyError) as exc:
                raise StorageMigrationError(
                    "legacy CSV migration stopped: {}".format(exc)
                )
        self._upgrade_master_csv_headers()

    def _upgrade_master_csv_headers(self):
        for path in self._measurement_files():
            try:
                with open(path, "r") as source:
                    header = source.readline()
                    if header != PRE_SUMMARY_MASTER_HEADER:
                        continue
                    temporary_path = path + ".summary.tmp"
                    with open(temporary_path, "w") as target:
                        target.write(MASTER_HEADER)
                        previous_columns = len(
                            PRE_SUMMARY_MASTER_HEADER.rstrip("\n").split(",")
                        )
                        for line in source:
                            if (not line.endswith("\n")
                                    or len(line.rstrip("\n").split(","))
                                    != previous_columns):
                                raise ValueError(
                                    "master CSV has partial row during upgrade"
                                )
                            target.write(line.rstrip("\n") + ",0,0,\n")
                        target.flush()
            except OSError as exc:
                if exc.args[0] == 2:
                    continue
                raise
            os.rename(temporary_path, path)

    def _has_legacy_csv(self):
        for path in (self._slave_path, self._master_path):
            try:
                os.stat(path)
                return True
            except OSError as exc:
                if exc.args[0] != 2:
                    raise
        return False

    def save_local(self, record):
        try:
            self._save_local(record)
        except (OSError, ValueError, TypeError) as exc:
            raise StorageError(
                "local measurement cannot be stored: {}".format(exc)
            )

    def _save_local(self, record):
        path = self._measurement_path(record)
        self._ensure_header(path, SLAVE_HEADER)
        self._append(path, self._csv_row(record))
        with open(self._pending_path, "a") as pending_file:
            pending_file.write(json.dumps(record.to_dict()) + "\n")
            pending_file.flush()
        self._state["next_sequence"] = record.sequence_number + 1
        self._write_state()

    def pending_records(self):
        try:
            for record in self._pending_records():
                yield record
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise StorageError(
                "pending records cannot be read: {}".format(exc)
            )

    def _pending_records(self):
        try:
            pending_file = open(self._pending_path, "r")
        except OSError:
            return
        with pending_file:
            pending_file.seek(int(self._state.get("pending_offset", 0)))
            while True:
                line = pending_file.readline()
                if not line:
                    break
                record = MeasurementRecord.from_dict(json.loads(line))
                self._pending_offsets[record.sequence_number] = pending_file.tell()
                yield record

    def mark_transmitted(self, record):
        try:
            if record.sequence_number not in self._pending_offsets:
                raise ValueError("record was not read from pending queue")
            self._state["pending_offset"] = self._pending_offsets.pop(
                record.sequence_number
            )
            self._write_state()
        except (OSError, ValueError, TypeError) as exc:
            raise StorageError(
                "transmission state cannot be stored: {}".format(exc)
            )

    def has_received(self, device_id, sequence_number):
        received = self._state.get("last_received", {})
        return int(sequence_number) <= int(received.get(device_id, -1))

    def next_sequence_for(self, device_id):
        received = self._state.get("last_received", {})
        return int(received.get(device_id, -1)) + 1

    def latest_measurement_timestamp(self, device_id):
        try:
            self._validate_device_id(device_id)
            if not self._scan_existing_data:
                timestamps = self._state.get("last_measurement_timestamps", {})
                return timestamps.get(device_id)
            latest_sequence = -1
            latest_timestamp = None
            for path in self._measurement_files():
                source = self._open_measurement_file(path)
                if source is None:
                    continue
                with source:
                    header = source.readline().rstrip("\n").split(",")
                    if header == [""] or "measurement_timestamp" not in header:
                        continue
                    device_column = header.index("device_id")
                    sequence_column = header.index("sequence_number")
                    timestamp_column = header.index("measurement_timestamp")
                    status_column = (
                        header.index("receive_status")
                        if "receive_status" in header else None
                    )
                    for line in source:
                        fields = line.rstrip("\n").split(",")
                        if not line.endswith("\n") or len(fields) != len(header):
                            continue
                        if fields[device_column] != device_id:
                            continue
                        if status_column is not None and fields[status_column] == "NO_PACKET":
                            continue
                        try:
                            sequence = int(fields[sequence_column])
                        except ValueError:
                            continue
                        timestamp = fields[timestamp_column]
                        if sequence > latest_sequence and timestamp not in ("", "NA"):
                            latest_sequence = sequence
                            latest_timestamp = timestamp
            return latest_timestamp
        except (OSError, ValueError, TypeError) as exc:
            raise StorageError(
                "latest measurement timestamp cannot be read: {}".format(exc)
            )

    @staticmethod
    def _open_measurement_file(path):
        try:
            return open(path, "r")
        except OSError as exc:
            if exc.args[0] == 2:
                return None
            raise

    def save_received(self, record, metadata):
        try:
            self._save_received(record, metadata)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise StorageError(
                "received measurement cannot be stored: {}".format(exc)
            )

    def save_missing_interval(self, device_id, metadata):
        try:
            return self._save_missing_interval(device_id, metadata)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise StorageError(
                "missing interval cannot be stored: {}".format(exc)
            )

    def save_diagnostic_event(self, event):
        try:
            return self._save_diagnostic_event(event)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise StorageError(
                "diagnostic event cannot be stored: {}".format(exc)
            )

    def _save_diagnostic_event(self, event):
        self._validate_device_id(event.origin_id)
        self._validate_diagnostic_event(event)
        key = (event.origin_id, event.event_code)
        active_repeat = self._active_diagnostics.get(key)
        if event.event_state == "STARTED":
            if active_repeat is not None and event.repeat_count <= active_repeat:
                return False
            self._active_diagnostics[key] = event.repeat_count
        elif event.event_state == "ENDED":
            if active_repeat is None:
                return False
            del self._active_diagnostics[key]
        path = self._diagnostic_path(event.origin_id)
        self._ensure_header(path, DIAGNOSTIC_HEADER)
        self._append(path, "{},{},{},{},{}\n".format(
            event.origin_id, event.reference_sequence, event.event_code,
            event.event_state, event.repeat_count,
        ))
        self._queue_event_summary(event)
        self._write_state()
        return True

    def _queue_event_summary(self, event):
        summaries = self._state.setdefault("event_summaries", {})
        device_summaries = summaries.setdefault(event.origin_id, {})
        sequence_key = str(event.reference_sequence)
        summary = device_summaries.setdefault(sequence_key, {
            "restart_count": 0,
            "sd_write_error_count": 0,
            "diagnostics": [],
        })
        if event.event_code == "DEVICE_RESTARTED":
            summary["restart_count"] += event.repeat_count
        elif event.event_code == "SLAVE_SD_WRITE_ERROR":
            summary["sd_write_error_count"] += event.repeat_count
        else:
            entry = "{}:{}".format(event.event_code, event.repeat_count)
            if event.event_state == "ENDED":
                entry = "{}:ENDED".format(event.event_code)
            if entry not in summary["diagnostics"]:
                summary["diagnostics"].append(entry)

    def _event_summary(self, device_id, sequence_number):
        summaries = self._state.setdefault("event_summaries", {})
        device_summaries = summaries.get(device_id, {})
        summary = device_summaries.get(str(sequence_number))
        return summary or {
            "restart_count": 0,
            "sd_write_error_count": 0,
            "diagnostics": [],
        }

    def _consume_event_summary(self, device_id, sequence_number):
        summaries = self._state.setdefault("event_summaries", {})
        device_summaries = summaries.get(device_id, {})
        device_summaries.pop(str(sequence_number), None)
        if not device_summaries and device_id in summaries:
            del summaries[device_id]

    def _save_received(self, record, metadata):
        path = self._measurement_path(record)
        self._ensure_header(path, MASTER_HEADER)
        row = "{},{},{}".format(
            metadata.get("received_timestamp") or "NA",
            metadata["master_uptime_s"], metadata["master_id"]
        )
        row += "," + self._csv_row(record).rstrip("\n")
        summary = self._event_summary(
            record.device_id, record.sequence_number
        )
        row += ",{},{},0,0,{},{},{}\n".format(
            self._csv_value(metadata.get("rssi_dbm")),
            self._csv_value(metadata.get("snr_db")),
            summary["restart_count"], summary["sd_write_error_count"],
            ";".join(summary["diagnostics"]),
        )
        if not self._replace_pending_gap(record, row):
            self._append(path, row)
        self._consume_event_summary(record.device_id, record.sequence_number)
        received = self._state.setdefault("last_received", {})
        received[record.device_id] = max(
            int(received.get(record.device_id, -1)), record.sequence_number
        )
        self._write_state()

    def _save_missing_interval(self, device_id, metadata):
        self._validate_device_id(device_id)
        pending = self._state.setdefault("pending_gaps", {})
        device_gaps = pending.setdefault(device_id, [])
        expected_sequence = self._next_expected_sequence(device_id, device_gaps)
        path = self._block_path(device_id, expected_sequence)
        self._ensure_header(path, MASTER_HEADER)
        missing_count = len(device_gaps) + 1
        row = self._missing_row(device_id, metadata, missing_count)
        self._append(path, row)
        device_gaps.append({
            "sequence": expected_sequence,
            "path": path,
            "master_uptime_s": int(metadata["master_uptime_s"]),
        })
        self._write_state()
        return expected_sequence

    def _next_expected_sequence(self, device_id, device_gaps):
        received = int(self._state.get("last_received", {}).get(device_id, -1))
        pending_sequences = [int(gap["sequence"]) for gap in device_gaps]
        return max([received] + pending_sequences) + 1

    def _replace_pending_gap(self, record, row):
        pending = self._state.setdefault("pending_gaps", {})
        device_gaps = pending.get(record.device_id, [])
        for index, gap in enumerate(device_gaps):
            if int(gap["sequence"]) != record.sequence_number:
                continue
            self._replace_missing_row(gap, row)
            del device_gaps[index]
            if not device_gaps:
                del pending[record.device_id]
            return True
        return False

    def _replace_missing_row(self, gap, replacement):
        path = gap["path"]
        expected_uptime = str(gap["master_uptime_s"])
        with open(path, "r") as source:
            header = source.readline()
            if header != MASTER_HEADER:
                raise ValueError("pending gap CSV header differs")
            replaced = False
            temporary_path = path + ".tmp"
            with open(temporary_path, "w") as target:
                target.write(header)
                for line in source:
                    fields = line.rstrip("\n").split(",")
                    if (not replaced
                            and len(fields) == len(MASTER_HEADER.rstrip("\n").split(","))
                            and fields[1] == expected_uptime
                            and fields[5] == "NA"
                            and fields[MASTER_HEADER.rstrip("\n").split(",").index("receive_status")] == "NO_PACKET"):
                        target.write(replacement)
                        replaced = True
                    else:
                        target.write(line)
                target.flush()
        if not replaced:
            raise ValueError("pending gap row is missing")
        os.rename(temporary_path, path)

    def _missing_row(self, device_id, metadata, missing_count):
        values = [
            metadata.get("received_timestamp") or "NA",
            metadata["master_uptime_s"], metadata["master_id"],
            "NA", device_id, "NA", "NA", "NA",
        ]
        values.extend(["NA"] * len(MEASUREMENT_FIELDS))
        values.extend([
            "NA", "NA", "NA", "NO_PACKET", missing_count, 0, 0, "",
        ])
        return ",".join(str(value) for value in values) + "\n"

    def _load_state(self):
        for path in (self._state_path, self._backup_state_path):
            try:
                with open(path, "r") as state_file:
                    return json.load(state_file)
            except (OSError, ValueError):
                pass
        return {"next_sequence": 0, "pending_offset": 0, "last_received": {}}

    def _recover_state(self):
        changed = False
        highest_local_sequence = -1
        try:
            with open(self._pending_path, "r") as pending_file:
                for line in pending_file:
                    try:
                        sequence = int(json.loads(line)["sequence_number"])
                        highest_local_sequence = max(highest_local_sequence, sequence)
                    except (KeyError, TypeError, ValueError):
                        pass
        except OSError:
            pass
        recovered_next = highest_local_sequence + 1
        if recovered_next > int(self._state.get("next_sequence", 0)):
            self._state["next_sequence"] = recovered_next
            changed = True

        try:
            pending_size = os.stat(self._pending_path)[6]
            if int(self._state.get("pending_offset", 0)) > pending_size:
                self._state["pending_offset"] = 0
                changed = True
        except OSError:
            if self._state.get("pending_offset", 0) != 0:
                self._state["pending_offset"] = 0
                changed = True

        received = self._state.setdefault("last_received", {})
        # Read both legacy files and V1 blocks without rewriting measurement data.
        for path in self._measurement_files():
            for is_master, device_id, sequence in self._stored_sequences(path):
                if is_master:
                    if sequence > int(received.get(device_id, -1)):
                        received[device_id] = sequence
                        changed = True
                elif sequence >= int(self._state.get("next_sequence", 0)):
                    self._state["next_sequence"] = sequence + 1
                    changed = True
        if changed:
            self._write_state()

    @staticmethod
    def _validate_device_id(device_id):
        if (not isinstance(device_id, str) or not 1 <= len(device_id) <= 8
                or any(char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
                       for char in device_id)):
            raise ValueError("invalid device ID for storage path")

    def _measurement_path(self, record):
        return self._block_path(record.device_id, record.sequence_number)

    def _block_path(self, device_id, sequence_number):
        self._validate_device_id(device_id)
        if sequence_number < 0:
            raise ValueError("negative sequence number")
        device_path = self._data_path + "/" + device_id
        for directory in (self._data_path, device_path):
            try:
                os.mkdir(directory)
            except OSError as exc:
                if exc.args[0] != 17:
                    raise
                if not os.stat(directory)[0] & 0x4000:
                    raise ValueError("measurement directory is not a directory")
        first = (sequence_number // 3000) * 3000
        return device_path + "/measurements_{:06d}-{:06d}.csv".format(
            first, first + 2999
        )

    def _measurement_files(self):
        # Legacy root CSVs are imported during initialization and then renamed
        # to .pre_v1. Runtime recovery only reads the V1 block structure.
        try:
            device_ids = os.listdir(self._data_path)
        except OSError as exc:
            if exc.args[0] != 2:
                raise
            return
        for device_id in device_ids:
            self._validate_device_id(device_id)
            directory = self._data_path + "/" + device_id
            for name in os.listdir(directory):
                if name.startswith("measurements_") and name.endswith(".csv"):
                    yield directory + "/" + name

    def _recover_diagnostic_state(self):
        active = {}
        diagnostics_path = self._diagnostics_path()
        try:
            device_ids = os.listdir(diagnostics_path)
        except OSError as exc:
            if exc.args[0] == 2:
                return active
            raise
        for device_id in device_ids:
            self._validate_device_id(device_id)
            path = diagnostics_path + "/" + device_id + "/events.csv"
            try:
                source = open(path, "r")
            except OSError as exc:
                if exc.args[0] == 2:
                    continue
                raise
            with source:
                if source.readline() != DIAGNOSTIC_HEADER:
                    raise ValueError("diagnostic CSV header differs")
                for line in source:
                    fields = line.rstrip("\n").split(",")
                    if not line.endswith("\n") or len(fields) != 5:
                        raise ValueError("diagnostic CSV has partial row")
                    origin_id, _reference, code, state, repeat = fields
                    self._validate_device_id(origin_id)
                    if origin_id != device_id:
                        raise ValueError("diagnostic device path differs from row")
                    self._validate_diagnostic_values(code, state, repeat)
                    key = (origin_id, code)
                    if state == "STARTED":
                        active[key] = int(repeat)
                    elif state == "ENDED":
                        active.pop(key, None)
        return active

    def _diagnostics_path(self):
        return self._data_path.rsplit("/data", 1)[0] + "/diagnostics"

    def _diagnostic_path(self, device_id):
        self._validate_device_id(device_id)
        diagnostics_path = self._diagnostics_path()
        device_path = diagnostics_path + "/" + device_id
        for directory in (diagnostics_path, device_path):
            try:
                os.mkdir(directory)
            except OSError as exc:
                if exc.args[0] != 17:
                    raise
                if not os.stat(directory)[0] & 0x4000:
                    raise ValueError("diagnostic path is not a directory")
        return device_path + "/events.csv"

    @staticmethod
    def _validate_diagnostic_values(code, state, repeat_count):
        if (not isinstance(code, str) or not 1 <= len(code) <= 32
                or any(char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
                       for char in code)):
            raise ValueError("invalid diagnostic event code")
        if state not in ("STARTED", "ENDED", "OCCURRED"):
            raise ValueError("invalid diagnostic event state")
        if int(repeat_count) < 1:
            raise ValueError("invalid diagnostic repeat count")

    @classmethod
    def _validate_diagnostic_event(cls, event):
        cls._validate_diagnostic_values(
            event.event_code, event.event_state, event.repeat_count
        )
        if int(event.reference_sequence) < 0:
            raise ValueError("negative diagnostic reference sequence")

    @staticmethod
    def _stored_sequences(path):
        try:
            source = open(path, "r")
        except OSError as exc:
            if exc.args[0] != 2:
                raise
            return
        with source:
            header = source.readline().rstrip("\n").split(",")
            if header == [""]:
                return
            device_column = header.index("device_id")
            sequence_column = header.index("sequence_number")
            is_master = "master_id" in header
            status_column = header.index("receive_status") if is_master else None
            for line in source:
                fields = line.rstrip("\n").split(",")
                if not line.endswith("\n") or len(fields) != len(header):
                    continue
                if is_master and fields[status_column] == "NO_PACKET":
                    continue
                try:
                    sequence = int(fields[sequence_column])
                except ValueError:
                    continue
                if sequence >= 0:
                    yield is_master, fields[device_column], sequence

    def _write_state(self):
        temporary_path = self._state_path + ".tmp"
        with open(temporary_path, "w") as state_file:
            json.dump(self._state, state_file)
            state_file.flush()
        try:
            os.remove(self._backup_state_path)
        except OSError:
            pass
        try:
            os.rename(self._state_path, self._backup_state_path)
        except OSError:
            pass
        os.rename(temporary_path, self._state_path)
        try:
            os.remove(self._backup_state_path)
        except OSError:
            pass

    @staticmethod
    def _append(path, value):
        with open(path, "a") as output_file:
            output_file.write(value)
            output_file.flush()

    @staticmethod
    def _ensure_header(path, header):
        try:
            size = os.stat(path)[6]
        except OSError as exc:
            if exc.args[0] != 2:
                raise
            size = 0
        if size == 0:
            with open(path, "w") as output_file:
                output_file.write(header)
                output_file.flush()
            return
        with open(path, "rb") as source:
            if source.readline() != header.encode("ascii"):
                raise ValueError("existing measurement CSV header differs")
            source.seek(size - 1)
            if source.read(1) != b"\n":
                raise ValueError("existing measurement CSV ends with partial row")

    @staticmethod
    def _csv_value(value):
        if value is None:
            return ""
        if isinstance(value, float):
            return "{:.1f}".format(value)
        return str(value)

    def _csv_row(self, record):
        fields = [
            record.format_version, record.device_id, record.sequence_number,
            record.measurement_timestamp or "NA", record.uptime_s,
        ]
        for name in MEASUREMENT_FIELDS:
            fields.append(record.values.get(name))
        fields.append("{:04X}".format(record.status_flags & 0xFFFF))
        return ",".join(self._csv_value(value) for value in fields) + "\n"
