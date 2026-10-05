import calendar
import sys
import time
import types
import unittest
from unittest.mock import patch

from adapters.clock import ConfiguredUtcClock


def epoch(year, month, day, hour=0, minute=0, second=0):
    return calendar.timegm((year, month, day, hour, minute, second))


class ClockRolloverTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.time = types.SimpleNamespace(
            monotonic=lambda: self.now, gmtime=time.gmtime,
            localtime=time.localtime, mktime=calendar.timegm,
        )
        self.patcher = patch('adapters.clock.time', self.time)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.rtc_patcher = patch.dict(sys.modules, {'rtc': None})
        self.rtc_patcher.start()
        self.addCleanup(self.rtc_patcher.stop)

    def test_day_month_year_and_leap_day_rollover(self):
        cases = [
            ((2026, 9, 18), '2026-09-19T00:00:01Z'),
            ((2026, 9, 30), '2026-10-01T00:00:01Z'),
            ((2026, 12, 31), '2027-01-01T00:00:01Z'),
            ((2028, 2, 28), '2028-02-29T00:00:01Z'),
            ((2028, 2, 29), '2028-03-01T00:00:01Z'),
        ]
        for date, expected in cases:
            with self.subTest(date=date):
                self.now = 0
                clock = ConfiguredUtcClock(epoch(*date, 23, 59, 59))
                self.now = 2
                self.assertEqual(clock.measurement_timestamp(), expected)

    def test_more_than_24_hours_does_not_reset_to_config(self):
        clock = ConfiguredUtcClock(epoch(2026, 9, 17, 14, 10, 37))
        self.now = 2 * 86400 + 900
        self.assertEqual(clock.measurement_timestamp(), '2026-09-19T14:25:37Z')
        self.assertEqual(clock.uptime_s(), self.now)

    def test_utc_output_does_not_use_host_local_timezone(self):
        self.time.localtime = lambda *_: self.fail('must use UTC on CPython')
        clock = ConfiguredUtcClock(epoch(2026, 9, 18))
        self.assertEqual(clock.measurement_timestamp(), '2026-09-18T00:00:00Z')

    def test_circuitpython_without_gmtime_uses_utc_localtime(self):
        del self.time.gmtime
        self.time.localtime = time.gmtime
        clock = ConfiguredUtcClock(epoch(2026, 9, 18, 23, 59, 59))
        self.now = 2
        self.assertEqual(clock.measurement_timestamp(), '2026-09-19T00:00:01Z')

    def test_valid_internal_clock_survives_software_restart(self):
        internal = types.SimpleNamespace(datetime=time.gmtime(epoch(2026, 9, 19)))
        with patch.dict(sys.modules, {'rtc': types.SimpleNamespace(RTC=lambda: internal)}):
            clock = ConfiguredUtcClock(epoch(2026, 9, 17))
            self.assertEqual(clock.measurement_timestamp(), '2026-09-19T00:00:00Z')
            self.now = 60
            self.assertEqual(clock.measurement_timestamp(), '2026-09-19T00:01:00Z')

    def test_unset_internal_clock_is_seeded_from_configuration(self):
        internal = types.SimpleNamespace(datetime=time.gmtime(epoch(2000, 1, 1)))
        with patch.dict(sys.modules, {'rtc': types.SimpleNamespace(RTC=lambda: internal)}):
            clock = ConfiguredUtcClock(epoch(2026, 9, 18, 14, 10))
            self.assertEqual(calendar.timegm(internal.datetime), epoch(2026, 9, 18, 14, 10))
            self.assertEqual(clock.measurement_timestamp(), '2026-09-18T14:10:00Z')

    def test_last_stored_timestamp_continues_by_one_interval(self):
        clock = ConfiguredUtcClock(
            epoch(2026, 9, 17), "2026-09-18T23:51:00Z", 900,
        )
        self.assertEqual(clock.measurement_timestamp(), "2026-09-19T00:06:00Z")
        self.assertEqual(clock.status_flags(), 0x0040)


if __name__ == '__main__':
    unittest.main()
