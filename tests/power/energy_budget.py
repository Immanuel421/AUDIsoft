#!/usr/bin/env python3
"""Calculate the annual energy budget from measured operating phases."""

import argparse
import csv
import sys


HOURS_PER_YEAR = 365 * 24


def read_phases(path, cycle_seconds):
    phases = []
    auto_phase = None
    fixed_duration = 0.0

    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"phase", "current_ma", "duration_s", "occurrences_per_cycle"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV header must contain: " + ", ".join(sorted(required)))

        for line_number, row in enumerate(reader, start=2):
            name = row["phase"].strip()
            if not name:
                raise ValueError("line {}: phase is empty".format(line_number))
            try:
                current = float(row["current_ma"])
                occurrences = float(row["occurrences_per_cycle"])
            except (TypeError, ValueError):
                raise ValueError(
                    "line {} ({}): current_ma and occurrences_per_cycle must be numbers"
                    .format(line_number, name)
                )
            if current < 0 or occurrences < 0:
                raise ValueError("line {} ({}): values must not be negative".format(line_number, name))

            duration_text = row["duration_s"].strip().upper()
            if duration_text == "AUTO":
                if auto_phase is not None or occurrences != 1:
                    raise ValueError("AUTO is allowed exactly once and requires one occurrence")
                auto_phase = len(phases)
                duration = None
            else:
                try:
                    duration = float(duration_text)
                except ValueError:
                    raise ValueError("line {} ({}): duration_s must be a number or AUTO".format(line_number, name))
                if duration < 0:
                    raise ValueError("line {} ({}): duration must not be negative".format(line_number, name))
                fixed_duration += duration * occurrences

            phases.append({"name": name, "current": current, "duration": duration, "occurrences": occurrences})

    if auto_phase is not None:
        remaining = cycle_seconds - fixed_duration
        if remaining < 0:
            raise ValueError("phase durations exceed the {:.1f}-second cycle".format(cycle_seconds))
        phases[auto_phase]["duration"] = remaining
    elif abs(fixed_duration - cycle_seconds) > 0.001:
        raise ValueError(
            "phase durations total {:.1f} s, expected {:.1f} s; add an AUTO sleep row"
            .format(fixed_duration, cycle_seconds)
        )

    return phases


def calculate(phases, cycle_seconds, reserve_percent):
    charge_ma_seconds = sum(
        phase["current"] * phase["duration"] * phase["occurrences"]
        for phase in phases
    )
    average_current_ma = charge_ma_seconds / cycle_seconds
    annual_mah = average_current_ma * HOURS_PER_YEAR
    annual_with_reserve_mah = annual_mah * (1 + reserve_percent / 100.0)
    return average_current_ma, annual_mah, annual_with_reserve_mah


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", help="CSV containing measured operating phases")
    parser.add_argument("--cycle-seconds", type=float, default=900.0)
    parser.add_argument("--reserve-percent", type=float, default=30.0)
    parser.add_argument("--battery-capacity-mah", type=float)
    args = parser.parse_args()

    if args.cycle_seconds <= 0 or args.reserve_percent < 0:
        parser.error("cycle-seconds must be positive and reserve-percent must not be negative")

    try:
        phases = read_phases(args.csv_file, args.cycle_seconds)
        average, annual, annual_reserved = calculate(phases, args.cycle_seconds, args.reserve_percent)
    except (OSError, ValueError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 2

    print("Cycle duration:        {:.1f} s".format(args.cycle_seconds))
    for phase in phases:
        print("  {:20s} {:8.3f} mA for {:8.2f} s x {:g}".format(
            phase["name"], phase["current"], phase["duration"], phase["occurrences"]
        ))
    print("Average current:       {:.3f} mA".format(average))
    print("Annual requirement:    {:.1f} mAh".format(annual))
    print("With {:.1f}% reserve:   {:.1f} mAh".format(args.reserve_percent, annual_reserved))

    if args.battery_capacity_mah is not None:
        if args.battery_capacity_mah <= 0:
            parser.error("battery-capacity-mah must be positive")
        runtime_days = args.battery_capacity_mah / average / 24 if average else float("inf")
        print("Estimated runtime:     {:.1f} days".format(runtime_days))
        print("One-year result:       {}".format(
            "PASS" if args.battery_capacity_mah >= annual_reserved else "FAIL"
        ))

    return 0


if __name__ == "__main__":
    sys.exit(main())
