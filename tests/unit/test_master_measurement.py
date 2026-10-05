from pathlib import Path
import tempfile
import unittest

from adapters.sd_storage import SdStorageAdapter
from application.master_controller import MasterController
from domain.protocol import AsciiProtocolCodec
from ports.errors import StorageError
from tests.unit.test_hexagonal_core import (
    FakeClock, FakeDiagnostics, FakeRadio, record, values,
)


class Clock(FakeClock):
    now = 0

    def uptime_s(self):
        return self.now


class Sensor:
    ready = False
    starts = 0
    flags = 0

    def start_measurement(self):
        self.starts += 1

    def poll_measurement(self):
        return (values(), self.flags) if self.ready else None


class MasterMeasurementTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.storage = SdStorageAdapter(self.directory.name)
        self.clock = Clock()
        self.sensor = Sensor()
        self.radio = FakeRadio()
        self.codec = AsciiProtocolCodec()
        self.controller = self.build()

    def build(self):
        return MasterController(
            'M01', self.clock, self.storage, self.radio, self.codec,
            FakeDiagnostics(), monitored_slaves=['C01'], sensor=self.sensor,
        )

    def test_master_stores_own_data_without_radio_or_slave_queue(self):
        self.sensor.ready = True
        self.assertTrue(self.controller.poll_measurement())
        files = list(Path(self.directory.name).glob('data/M01/*.csv'))
        self.assertEqual(len(files), 1)
        text = files[0].read_text()
        self.assertIn(',M01,1,M01,0,', text)
        self.assertTrue(text.strip().endswith(',,,0,0,0,0,'))
        self.assertEqual(self.storage.next_sequence_for('M01'), 1)
        self.assertEqual(self.storage.next_sequence_for('C01'), 0)
        self.assertEqual(self.radio.sent, [])
        self.assertFalse((Path(self.directory.name) / 'pending_records.jsonl').exists())

    def test_slave_ack_is_processed_while_master_sensor_warms_up(self):
        self.assertFalse(self.controller.poll_measurement())
        self.radio.receives.append((self.codec.encode_data(record(0)), {}))
        self.assertTrue(self.controller.process_next(100))
        self.assertTrue(self.codec.is_success_ack(self.radio.sent[0], 'M01', 'C01', 0))
        self.assertEqual(self.sensor.starts, 1)
        self.assertFalse(self.storage.has_received('M01', 0))

    def test_measurement_starts_every_900_seconds_without_repeat_poll_samples(self):
        self.controller.poll_measurement()
        self.clock.now = 65
        self.sensor.ready = True
        self.controller.poll_measurement()
        self.clock.now = 899
        self.assertFalse(self.controller.poll_measurement())
        self.clock.now = 900
        self.assertTrue(self.controller.poll_measurement())
        self.assertEqual(self.sensor.starts, 2)
        self.assertEqual(self.storage.next_sequence_for('M01'), 2)

    def test_master_sequence_survives_restart(self):
        self.sensor.ready = True
        self.controller.poll_measurement()
        self.storage = SdStorageAdapter(self.directory.name)
        self.controller = self.build()
        self.controller.poll_measurement()
        self.assertEqual(self.storage.next_sequence_for('M01'), 2)
        files = list(Path(self.directory.name).glob('data/M01/*.csv'))
        self.assertEqual(len(files[0].read_text().splitlines()), 3)

    def test_temporary_storage_failure_retains_sample_and_rate_limits_retry(self):
        self.sensor.ready = True
        original = self.storage.save_received
        calls = []

        def fail_once(item, metadata):
            calls.append(item)
            if len(calls) == 1:
                raise StorageError('temporary SD error')
            original(item, metadata)

        self.storage.save_received = fail_once
        with self.assertRaises(StorageError):
            self.controller.poll_measurement()
        self.clock.now = 1
        self.assertFalse(self.controller.poll_measurement())
        self.assertEqual(len(calls), 1)
        self.clock.now = 5
        self.assertTrue(self.controller.poll_measurement())
        self.assertIs(calls[0], calls[1])
        self.assertEqual(self.sensor.starts, 1)

    def test_sensor_status_is_preserved(self):
        self.sensor.ready = True
        self.sensor.flags = 0x0021
        self.controller.poll_measurement()
        csv = next(Path(self.directory.name).glob('data/M01/*.csv')).read_text()
        self.assertIn(',0021,', csv)

    def test_missing_slave_interval_is_recorded_and_late_record_replaces_it(self):
        self.clock.now = 900
        self.assertTrue(self.controller.poll_missing_intervals())
        path = next(Path(self.directory.name).glob('data/C01/*.csv'))
        self.assertIn('NO_PACKET,1', path.read_text())

        self.radio.receives.append((self.codec.encode_data(record(0)), {}))
        self.assertTrue(self.controller.process_next(100))
        text = path.read_text()
        self.assertNotIn('NO_PACKET', text)
        self.assertIn(',C01,0,', text)

    def test_received_packet_prevents_gap_for_current_interval(self):
        self.radio.receives.append((self.codec.encode_data(record(0)), {}))
        self.assertTrue(self.controller.process_next(100))
        self.clock.now = 900
        self.assertFalse(self.controller.poll_missing_intervals())
        path = next(Path(self.directory.name).glob('data/C01/*.csv'))
        self.assertNotIn('NO_PACKET', path.read_text())


if __name__ == '__main__':
    unittest.main()
