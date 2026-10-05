"""One-time, restartable import of legacy measurement CSVs on CircuitPython."""

import os
import struct

BLOCK_SIZE = 3000


def _exists(path):
    try:
        os.stat(path)
        return True
    except OSError as exc:
        if exc.args[0] != 2:
            raise
        return False


def _remove_if_present(path):
    if _exists(path):
        os.remove(path)


def _header(source):
    line = source.readline()
    if not line.endswith("\n"):
        raise ValueError("legacy CSV has no complete header")
    names = line.rstrip("\r\n").split(",")
    if len(set(names)) != len(names):
        raise ValueError("duplicate CSV column")
    return names


def _row(source, names, target_names):
    line = source.readline()
    if not line:
        return None
    fields = line.rstrip("\r\n").split(",")
    if not line.endswith("\n") or len(fields) != len(names):
        raise ValueError("incomplete or malformed migration CSV row")
    values = dict(zip(names, fields))
    if "uptime_s" in values:
        values["slave_uptime_s"] = values.pop("uptime_s")
    values.setdefault("master_uptime_s", "NA")
    values.setdefault("missing_intervals", "0")
    values.setdefault("restart_count", "0")
    values.setdefault("sd_write_error_count", "0")
    values.setdefault("diagnostics", "")
    if values.get("receive_status") == "OK":
        values["receive_status"] = "0"
    if values["format_version"] != "1":
        raise ValueError("unsupported legacy measurement version")
    sequence = values["sequence_number"]
    if not sequence or any(char not in "0123456789" for char in sequence):
        raise ValueError("invalid legacy sequence")
    return [values[name] for name in target_names]


def _same_measurement(first, second, names):
    # Reception metadata may differ after a retransmission; keep the V1 copy.
    reception = ("received_timestamp", "master_uptime_s", "master_id",
                 "rssi_dbm", "snr_db", "receive_status", "missing_intervals",
                 "restart_count", "sd_write_error_count", "diagnostics")
    for name, left, right in zip(names, first, second):
        if name in reception or left == right:
            continue
        if left in ("", "NA") and right in ("", "NA"):
            continue
        if name in ("device_id", "measurement_timestamp"):
            return False
        try:
            equal = (int(left, 16) == int(right, 16) if name == "status_flags"
                     else float(left) == float(right))
        except ValueError:
            return False
        if not equal:
            return False
    return True


def _offset(index, slot):
    return struct.unpack_from("<I", index, slot * 4)[0]


def _index_rows(source, names, target_names, device_id, block, strict_block):
    # Two offset tables need 24 KB, independent of the total archive size.
    index = bytearray(BLOCK_SIZE * 4)
    device_column = target_names.index("device_id")
    sequence_column = target_names.index("sequence_number")
    while True:
        offset = source.tell()
        row = _row(source, names, target_names)
        if row is None:
            return index
        sequence = int(row[sequence_column])
        matches = (row[device_column] == device_id
                   and sequence // BLOCK_SIZE == block)
        if not matches:
            if strict_block:
                raise ValueError("record does not belong to migration target block")
            continue
        slot = sequence % BLOCK_SIZE
        previous = _offset(index, slot)
        if previous:
            position = source.tell()
            source.seek(previous)
            old_row = _row(source, names, target_names)
            source.seek(position)
            if not _same_measurement(old_row, row, target_names):
                raise ValueError("conflicting measurements for {}:{}".format(
                    device_id, sequence))
        else:
            struct.pack_into("<I", index, slot * 4, offset)


def _merge_block(source_path, path, target_header, device_id, block):
    temporary = path + ".migration.tmp"
    backup = path + ".migration.bak"
    # A reset between the two renames leaves the old complete block here.
    if _exists(backup) and not _exists(path):
        os.rename(backup, path)
    target_names = target_header.rstrip("\n").split(",")
    with open(source_path, "r") as legacy:
        names = _header(legacy)
        legacy_index = _index_rows(
            legacy, names, target_names, device_id, block, False
        )
        existing = None
        try:
            if _exists(path):
                existing = open(path, "r")
                if _header(existing) != target_names:
                    raise ValueError("migration target CSV header differs")
                existing_index = _index_rows(
                    existing, target_names, target_names, device_id, block, True
                )
            else:
                existing_index = bytearray(BLOCK_SIZE * 4)
            with open(temporary, "w") as output:
                output.write(target_header)
                for slot in range(BLOCK_SIZE):
                    old_offset = _offset(legacy_index, slot)
                    new_offset = _offset(existing_index, slot)
                    if not old_offset and not new_offset:
                        continue
                    old_row = None
                    if old_offset:
                        legacy.seek(old_offset)
                        old_row = _row(legacy, names, target_names)
                    if new_offset:
                        existing.seek(new_offset)
                        row = _row(existing, target_names, target_names)
                        if old_row is not None and not _same_measurement(
                                old_row, row, target_names):
                            raise ValueError(
                                "conflicting legacy and V1 measurement {}:{}".format(
                                    device_id, block * BLOCK_SIZE + slot))
                    else:
                        row = old_row
                    output.write(",".join(row) + "\n")
                output.flush()
        finally:
            if existing is not None:
                existing.close()
    _remove_if_present(backup)
    if _exists(path):
        os.rename(path, backup)
    os.rename(temporary, path)
    _remove_if_present(backup)


def migrate_legacy_csv(source_path, target_header, block_path):
    if not _exists(source_path):
        return
    archive = source_path + ".pre_v1"
    if _exists(archive):
        raise ValueError("legacy CSV and its pre_v1 backup both exist")
    target_names = target_header.rstrip("\n").split(",")
    legacy_names = [
        name.replace("slave_uptime_s", "uptime_s")
        for name in target_names
        if name not in (
            "master_uptime_s", "missing_intervals", "restart_count",
            "sd_write_error_count", "diagnostics",
        )
    ]
    previous_names = [
        name for name in target_names
        if name not in (
            "restart_count", "sd_write_error_count", "diagnostics",
        )
    ]
    previous_legacy_names = [
        name.replace("slave_uptime_s", "uptime_s")
        for name in previous_names
        if name not in ("master_uptime_s", "missing_intervals")
    ]
    blocks = set()
    with open(source_path, "r") as source:
        names = _header(source)
        if names not in (
                legacy_names, previous_legacy_names, previous_names,
                target_names):
            raise ValueError("unsupported legacy CSV header")
        device_column = target_names.index("device_id")
        sequence_column = target_names.index("sequence_number")
        while True:
            row = _row(source, names, target_names)
            if row is None:
                break
            device_id = row[device_column]
            if (not 1 <= len(device_id) <= 8
                    or any(char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
                           for char in device_id)):
                raise ValueError("invalid legacy device ID")
            blocks.add((device_id, int(row[sequence_column]) // BLOCK_SIZE))
    for device_id, block in sorted(blocks):
        path = block_path(device_id, block * BLOCK_SIZE)
        _merge_block(source_path, path, target_header, device_id, block)
    # Renaming only after all blocks commit makes an interrupted import retryable.
    os.rename(source_path, archive)
