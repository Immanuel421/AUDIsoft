import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

from ports.errors import RadioError


class FakeChip:
    def __init__(self):
        self.receiving = False
        self.payload = None
        self.irq = 0
        self.starts = 0
        self.start_status = 0
        self.send_status = 0

    def startReceive(self, timeout):
        assert timeout == 0
        self.starts += 1
        self.payload = None
        self.irq = 0
        self.receiving = True
        return self.start_status

    def deliver(self, payload, irq=2):
        if self.receiving:
            self.payload = payload
            self.irq = irq
            self.receiving = False

    def send(self, payload):
        self.receiving = False
        return len(payload), self.send_status

    def standby(self):
        self.receiving = False
        return 0

    def getIrqStatus(self):
        return self.irq

    def getPacketLength(self):
        return len(self.payload)

    def readData(self, buffer, length):
        buffer[:] = self.payload[:length]
        self.irq = 0
        return 0

    def getRSSI(self):
        return -70

    def getSNR(self):
        return 8


class RadioReceiveWindowTests(unittest.TestCase):
    def setUp(self):
        driver = types.ModuleType('sx1262')
        driver.SX1262 = FakeChip
        constants = types.ModuleType('_sx126x')
        constants.ERR_RX_TIMEOUT = -6
        constants.SX126X_IRQ_RX_DONE = 2
        constants.SX126X_IRQ_CRC_ERR = 64
        constants.SX126X_IRQ_HEADER_ERR = 32
        path = Path(__file__).resolve().parents[2] / 'adapters/sx1262_radio.py'
        spec = importlib.util.spec_from_file_location('radio_under_test', path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {
            'board': types.ModuleType('board'), 'sx1262': driver,
            '_sx126x': constants,
        }):
            spec.loader.exec_module(self.module)
        self.now = 0
        self.on_sleep = None
        self.module.time = types.SimpleNamespace(
            monotonic=lambda: self.now, sleep=self.sleep,
        )
        self.chip = FakeChip()
        self.radio = self.module.Sx1262RadioAdapter.__new__(
            self.module.Sx1262RadioAdapter
        )
        self.radio._radio = self.chip
        self.radio._start_receive()

    def sleep(self, duration):
        self.now += duration
        if self.on_sleep:
            self.on_sleep()

    def test_ack_arriving_between_send_and_receive_is_preserved(self):
        self.assertTrue(self.radio.send(b'data'))
        self.chip.deliver(b'ack')
        payload, metadata = self.radio.receive(100)
        self.assertEqual(payload, b'ack')
        self.assertEqual(metadata['rssi_dbm'], -70)
        self.assertTrue(self.chip.receiving)

    def test_next_packet_arriving_during_application_work_is_preserved(self):
        self.chip.deliver(b'overheard data')
        self.assertEqual(self.radio.receive(100)[0], b'overheard data')
        self.chip.deliver(b'ack')
        self.assertEqual(self.radio.receive(100)[0], b'ack')

    def test_timeout_keeps_receiver_running_for_late_ack(self):
        starts = self.chip.starts
        self.assertIsNone(self.radio.receive(10)[0])
        self.assertEqual(self.chip.starts, starts)
        self.assertTrue(self.chip.receiving)
        self.chip.deliver(b'late ack')
        self.assertEqual(self.radio.receive(100)[0], b'late ack')

    def test_corrupt_packet_is_discarded_and_valid_ack_can_follow(self):
        for irq in (64, 32):
            with self.subTest(irq=irq):
                self.chip.deliver(b'corrupt', irq)
                self.on_sleep = lambda: self.chip.deliver(b'valid ack')
                self.assertEqual(self.radio.receive(100)[0], b'valid ack')
                self.on_sleep = None

    def test_failed_transmission_still_rearms_receiver(self):
        self.chip.send_status = -5
        self.assertFalse(self.radio.send(b'data'))
        self.assertTrue(self.chip.receiving)

    def test_receive_setup_failure_is_reported(self):
        self.chip.start_status = -1
        with self.assertRaises(RadioError):
            self.radio.send(b'data')


if __name__ == '__main__':
    unittest.main()
