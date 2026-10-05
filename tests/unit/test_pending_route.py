import tempfile
import unittest

from adapters.sd_storage import SdStorageAdapter
from application.slave_controller import SlaveController
from domain.protocol import AckMessage, AsciiProtocolCodec
from tests.unit.test_hexagonal_core import (
    FakeClock, FakeDiagnostics, FakeRadio, FakeSensor, record,
)


class PendingRouteTests(unittest.TestCase):
    def test_persisted_measurement_uses_current_route_after_restart(self):
        for old_hop, old_limit, new_hop, new_limit in (
                ('M01', 1, 'C02', 3),
                ('C02', 3, 'M01', 1)):
            with self.subTest(new_hop=new_hop), tempfile.TemporaryDirectory() as directory:
                item = record(97)
                item.device_id = 'C03'
                item.next_hop_id = old_hop
                item.hop_limit = old_limit
                item.hop_count = 1
                original = item.to_dict()
                storage = SdStorageAdapter(directory)
                storage.save_local(item)
                restarted = SdStorageAdapter(directory)
                codec = AsciiProtocolCodec()
                ack = codec.encode_ack(AckMessage('M01', 'C03', 'C03', 97, 2))
                radio = FakeRadio([(ack, {})])
                controller = SlaveController(
                    'C03', FakeSensor(), FakeClock(), restarted, radio,
                    codec, FakeDiagnostics(), 3000, master_id='M01',
                    next_hop_id=new_hop, hop_limit=new_limit,
                )
                self.assertEqual(controller.transmit_pending(), 1)
                sent = codec.decode_data(radio.sent[0])
                self.assertEqual(sent.destination_id, 'M01')
                self.assertEqual(sent.next_hop_id, new_hop)
                self.assertEqual(sent.hop_limit, new_limit)
                self.assertEqual(sent.hop_count, 0)
                expected = codec.decode_data(codec.encode_data(item))
                self.assertEqual(sent.device_id, expected.device_id)
                self.assertEqual(sent.sequence_number, 97)
                self.assertEqual(sent.measurement_timestamp, expected.measurement_timestamp)
                self.assertEqual(sent.uptime_s, expected.uptime_s)
                self.assertEqual(sent.values, expected.values)
                self.assertEqual(sent.status_flags, expected.status_flags)
                self.assertEqual(item.to_dict(), original)
                self.assertEqual(list(SdStorageAdapter(directory).pending_records()), [])


if __name__ == '__main__':
    unittest.main()
