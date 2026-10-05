#!/usr/bin/env python3
"""Check a master CSV produced by a 24-hour Climate Cube endurance test."""

import argparse
import csv
import math
import sys
from collections import Counter


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_rows(path, device_id):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"device_id", "sequence_number"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV must contain device_id and sequence_number")
        return [row for row in reader if row.get("device_id", "").strip() == device_id]


def analyse(rows, interval, tolerance, minimum_cycles):
    failures = []
    sequences = []
    usable_rows = []

    for row in rows:
        try:
            sequence = int(row.get("sequence_number", ""))
        except ValueError:
            continue
        sequences.append(sequence)
        usable_rows.append(row)

    if len(sequences) < minimum_cycles:
        failures.append("only {} measurement rows, expected at least {}".format(len(sequences), minimum_cycles))

    duplicates = sorted(sequence for sequence, count in Counter(sequences).items() if count > 1)
    if duplicates:
        failures.append("duplicate sequences: {}".format(", ".join(map(str, duplicates))))

    regressions = [(left, right) for left, right in zip(sequences, sequences[1:]) if right <= left]
    if regressions:
        failures.append("sequence order is not strictly increasing")

    gaps = []
    for left, right in zip(sequences, sequences[1:]):
        if right > left + 1:
            gaps.extend(range(left + 1, right))
    if gaps:
        failures.append("missing sequences: {}".format(", ".join(map(str, gaps))))

    uptime_key = None
    if usable_rows:
        for candidate in ("slave_uptime_s", "uptime_s"):
            if candidate in usable_rows[0]:
                uptime_key = candidate
                break

    deviations = []
    resets = []
    checked_intervals = 0
    if uptime_key:
        for previous, current in zip(usable_rows, usable_rows[1:]):
            previous_sequence = int(previous["sequence_number"])
            current_sequence = int(current["sequence_number"])
            previous_uptime = number(previous.get(uptime_key))
            current_uptime = number(current.get(uptime_key))
            if current_sequence != previous_sequence + 1 or previous_uptime is None or current_uptime is None:
                continue
            delta = current_uptime - previous_uptime
            if delta <= 0:
                resets.append((previous_sequence, current_sequence, delta))
                continue
            checked_intervals += 1
            if abs(delta - interval) > tolerance:
                deviations.append((previous_sequence, current_sequence, delta))

    if resets:
        failures.append("{} possible restart(s) detected from uptime".format(len(resets)))
    if deviations:
        failures.append("{} interval(s) outside {:.0f} +/- {:.0f} s".format(len(deviations), interval, tolerance))

    return {
        "sequences": sequences,
        "checked_intervals": checked_intervals,
        "deviations": deviations,
        "resets": resets,
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", help="master CSV copied from the SD card")
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--expected-interval", type=float, default=900.0)
    parser.add_argument("--tolerance", type=float, default=30.0)
    parser.add_argument("--minimum-hours", type=float, default=24.0)
    args = parser.parse_args()

    if args.expected_interval <= 0 or args.minimum_hours <= 0 or args.tolerance < 0:
        parser.error("interval and hours must be positive; tolerance must not be negative")
    minimum_cycles = math.ceil(args.minimum_hours * 3600 / args.expected_interval)

    try:
        rows = load_rows(args.csv_file, args.device_id)
        result = analyse(rows, args.expected_interval, args.tolerance, minimum_cycles)
    except (OSError, ValueError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 2

    sequences = result["sequences"]
    print("Device:                {}".format(args.device_id))
    print("Measurement rows:      {} (minimum {})".format(len(sequences), minimum_cycles))
    if sequences:
        print("Sequence range:        {} to {}".format(sequences[0], sequences[-1]))
    print("Intervals checked:     {}".format(result["checked_intervals"]))
    for left, right, delta in result["deviations"][:10]:
        print("  sequence {} -> {}: {:.1f} s".format(left, right, delta))

    if result["failures"]:
        print("Result:                FAIL")
        for failure in result["failures"]:
            print("  - {}".format(failure))
        return 1

    print("Result:                PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
