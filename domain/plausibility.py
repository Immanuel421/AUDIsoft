"""Konfigurierbare Kennzeichnung unplausibler Messwerte."""

from domain.measurement import MEASUREMENT_FIELDS, MEASUREMENT_IMPLAUSIBLE


class PlausibilityPolicy:
    def __init__(self, limits=None):
        self._limits = dict(limits or {})

    def apply(self, values, status_flags):
        for field, bounds in self._limits.items():
            value = values.get(field)
            if value is None:
                continue
            if value < bounds["min"] or value > bounds["max"]:
                return int(status_flags) | MEASUREMENT_IMPLAUSIBLE
        return int(status_flags)


def validate_limits(limits):
    if not isinstance(limits, dict):
        raise ValueError("plausibility_limits must be an object")
    normalized = {}
    for field, bounds in limits.items():
        if field not in MEASUREMENT_FIELDS:
            raise ValueError("unknown plausibility field: {}".format(field))
        if not isinstance(bounds, dict) or set(bounds) != {"min", "max"}:
            raise ValueError("plausibility limit needs min and max")
        minimum = bounds["min"]
        maximum = bounds["max"]
        if (isinstance(minimum, bool) or isinstance(maximum, bool)
                or not isinstance(minimum, (int, float))
                or not isinstance(maximum, (int, float)) or minimum > maximum):
            raise ValueError("invalid plausibility range for {}".format(field))
        normalized[field] = {"min": minimum, "max": maximum}
    return normalized
