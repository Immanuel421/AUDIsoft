"""UTC-Referenz mit monotoner Laufzeit und interner RTC fuer Soft-Neustarts."""

import time

from domain.measurement import TIME_UNSYNCED
from ports.contracts import ClockPort
from ports.errors import ClockError


class ConfiguredUtcClock(ClockPort):
    def __init__(self, epoch_at_boot, last_measurement_timestamp=None,
                 measurement_interval_s=900):
        if epoch_at_boot is None:
            raise ClockError(
                "time_epoch_utc must be configured before operation"
            )
        try:
            self._epoch_at_boot = int(epoch_at_boot)
        except (TypeError, ValueError):
            raise ClockError("time_epoch_utc must be an integer")
        self._time_unsynced = False
        try:
            interval_s = int(measurement_interval_s)
        except (TypeError, ValueError):
            raise ClockError("measurement interval must be an integer")
        if interval_s <= 0:
            raise ClockError("measurement interval must be positive")
        if last_measurement_timestamp not in (None, "", "NA"):
            continued_epoch = self._timestamp_epoch(last_measurement_timestamp)
            continued_epoch += interval_s
            if continued_epoch > self._epoch_at_boot:
                self._epoch_at_boot = continued_epoch
                self._time_unsynced = True
        self._utc_tuple = getattr(time, "gmtime", time.localtime)
        try:
            import rtc
        except ImportError:
            rtc = None
        if rtc is not None:
            try:
                internal_clock = rtc.RTC()
                current_epoch = int(time.mktime(internal_clock.datetime))
                if current_epoch < self._epoch_at_boot:
                    internal_clock.datetime = self._utc_tuple(self._epoch_at_boot)
                else:
                    self._epoch_at_boot = current_epoch
                    self._time_unsynced = False
            except (OSError, OverflowError, ValueError, RuntimeError) as exc:
                raise ClockError("internal UTC clock cannot be initialized: {}".format(exc))
        self._monotonic_at_boot = time.monotonic()

    def uptime_s(self):
        return int(time.monotonic() - self._monotonic_at_boot)

    def status_flags(self):
        return TIME_UNSYNCED if self._time_unsynced else 0

    def sleep_ms(self, milliseconds):
        time.sleep(float(milliseconds) / 1000)

    def measurement_timestamp(self):
        current_epoch = self._epoch_at_boot + self.uptime_s()
        try:
            value = self._utc_tuple(current_epoch)
        except (OverflowError, ValueError) as exc:
            raise ClockError("timestamp cannot be generated: {}".format(exc))
        return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(
            value.tm_year, value.tm_mon, value.tm_mday,
            value.tm_hour, value.tm_min, value.tm_sec,
        )

    @staticmethod
    def _timestamp_epoch(timestamp):
        if (not isinstance(timestamp, str) or len(timestamp) != 20
                or timestamp[4] != "-" or timestamp[7] != "-"
                or timestamp[10] != "T" or timestamp[13] != ":"
                or timestamp[16] != ":" or timestamp[19] != "Z"):
            raise ClockError("stored measurement timestamp is invalid")
        try:
            year = int(timestamp[0:4])
            month = int(timestamp[5:7])
            day = int(timestamp[8:10])
            hour = int(timestamp[11:13])
            minute = int(timestamp[14:16])
            second = int(timestamp[17:19])
        except ValueError:
            raise ClockError("stored measurement timestamp is invalid")
        if (year < 1970 or not 1 <= month <= 12 or not 0 <= hour < 24
                or not 0 <= minute < 60 or not 0 <= second < 60):
            raise ClockError("stored measurement timestamp is invalid")
        days = 0
        for current_year in range(1970, year):
            days += 366 if ConfiguredUtcClock._is_leap_year(current_year) else 365
        month_days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        for current_month in range(1, month):
            days += month_days[current_month - 1]
            if current_month == 2 and ConfiguredUtcClock._is_leap_year(year):
                days += 1
        maximum_day = month_days[month - 1]
        if month == 2 and ConfiguredUtcClock._is_leap_year(year):
            maximum_day += 1
        if not 1 <= day <= maximum_day:
            raise ClockError("stored measurement timestamp is invalid")
        return days * 86400 + (day - 1) * 86400 + hour * 3600 + minute * 60 + second

    @staticmethod
    def _is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
