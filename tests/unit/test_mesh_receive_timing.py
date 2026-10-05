import unittest

from application.master_controller import MasterController
from application.relay_controller import RelayController
from domain.protocol import AsciiProtocolCodec, AckMessage, SequenceQuery, SequenceResponse
from tests.unit.test_hexagonal_core import (
    FakeClock, FakeDiagnostics, FakeMasterStorage, FakeRadio, record,
)


class MeshReceiveTimingTests(unittest.TestCase):
    def test_master_silently_ignores_overheard_packets(self):
        codec = AsciiProtocolCodec()
        data = record(0)
        data.next_hop_id = 'C01'
        packets = [codec.encode_data(data),
                   codec.encode_sequence_query(SequenceQuery('C02', 'M01', 'C01', 0, 3)),
                   codec.encode_ack(AckMessage('M01', 'C02', 'C02', 0)),
                   codec.encode_sequence_response(SequenceResponse('M01', 'C02', 'C02', 1))]
        radio = FakeRadio([(p, {}) for p in packets])
        diagnostics = FakeDiagnostics()
        storage = FakeMasterStorage()
        master = MasterController('M01', FakeClock(), storage, radio, codec, diagnostics)
        for p in packets:
            with self.subTest(packet=p):
                self.assertFalse(master.process_next(100))
        self.assertEqual(diagnostics.messages, [])
        self.assertEqual(storage.received, {})
        self.assertEqual(radio.sent, [])

    def test_no_display_update_between_relay_send_and_ack_receive(self):
        codec = AsciiProtocolCodec()
        events = []

        class Diagnostics(FakeDiagnostics):
            def info(self, message):
                events.append('display')

        class Radio(FakeRadio):
            def send(self, payload):
                events.append('send')
                return super().send(payload)

            def receive(self, timeout_ms):
                events.append('receive')
                return super().receive(timeout_ms)

        data = record(0)
        data.next_hop_id = 'C01'
        data.hop_limit = 3
        ack = codec.encode_ack(AckMessage('M01', data.device_id, 'C01', 0, 0, 0, 3))
        radio = Radio([(codec.encode_data(data), {}), (ack, {})])
        relay = RelayController('C01', 'M01', 'M01', {data.device_id: 'C02'},
                                radio, codec, Diagnostics(), 3000)
        self.assertTrue(relay.process_next(100))
        self.assertEqual(events[:4], ['receive', 'send', 'receive', 'send'])


if __name__ == '__main__':
    unittest.main()
