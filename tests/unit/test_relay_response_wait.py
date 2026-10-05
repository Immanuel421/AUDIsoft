import unittest
from unittest.mock import patch

from application.relay_controller import RelayController
from domain.protocol import AsciiProtocolCodec, AckMessage, SequenceQuery, SequenceResponse
from tests.unit.test_hexagonal_core import FakeRadio, FakeDiagnostics, record


class RelayResponseWaitTests(unittest.TestCase):
    def setUp(self):
        self.codec = AsciiProtocolCodec()
        self.diagnostics = FakeDiagnostics()

    def relay(self, packets):
        radio = FakeRadio([(packet, {}) for packet in packets])
        relay = RelayController('C01', 'M01', 'M01', {'C02': 'C02'},
                                radio, self.codec, self.diagnostics, 3000)
        return relay, radio

    def test_data_waits_past_overheard_query_and_wrong_ack(self):
        item = record(5)
        item.device_id = 'C02'
        item.next_hop_id = 'C01'
        item.hop_limit = 3
        foreign = self.codec.encode_sequence_query(SequenceQuery('C03', 'M01', 'C02', 0, 3))
        wrong_sequence = self.codec.encode_ack(AckMessage('M01', 'C02', 'C01', 4, 0, 0, 3))
        wrong_recipient = self.codec.encode_ack(AckMessage('M01', 'C03', 'C02', 5, 0, 0, 3))
        correct = self.codec.encode_ack(AckMessage('M01', 'C02', 'C01', 5, 0, 0, 3))
        relay, radio = self.relay([self.codec.encode_data(item), foreign,
                                   wrong_sequence, wrong_recipient, correct])
        self.assertTrue(relay.process_next(100))
        self.assertEqual(len(radio.sent), 2)
        ack = self.codec.decode_ack(radio.sent[1])
        self.assertEqual((ack.next_hop_id, ack.sequence_number), ('C02', 5))
        self.assertFalse(any(level == 'error' for level, _ in self.diagnostics.messages))

    def test_sequence_query_waits_past_overheard_forwarded_query(self):
        incoming = self.codec.encode_sequence_query(SequenceQuery('C02', 'M01', 'C01', 0, 3))
        overheard = self.codec.encode_sequence_query(SequenceQuery('C03', 'M01', 'C02', 0, 3))
        response = self.codec.encode_sequence_response(SequenceResponse('M01', 'C02', 'C01', 8, 0, 3))
        relay, radio = self.relay([incoming, overheard, response])
        self.assertTrue(relay.process_next(100))
        self.assertEqual(len(radio.sent), 2)
        self.assertEqual(self.codec.decode_sequence_response(radio.sent[1]).next_sequence, 8)

    def test_foreign_traffic_does_not_reset_timeout(self):
        foreign = self.codec.encode_ack(AckMessage('M01', 'C03', 'C02', 5))
        relay, radio = self.relay([foreign] * 5)
        with patch('application.relay_controller.time.monotonic', side_effect=[0, 0, 2, 4]):
            self.assertIsNone(relay._wait_for_response('A', 'C02', 5))
        self.assertEqual(len(radio.receives), 3)

    def test_timeout_does_not_forward_any_response(self):
        query = self.codec.encode_sequence_query(SequenceQuery('C02', 'M01', 'C01', 0, 3))
        relay, radio = self.relay([query, None])
        self.assertFalse(relay.process_next(100))
        self.assertEqual(len(radio.sent), 1)


if __name__ == '__main__':
    unittest.main()
