import unittest

from application.master_controller import MasterController
from application.relay_controller import RelayController
from application.slave_controller import SlaveController
from domain.measurement import (
    MEASUREMENT_FIELDS,
    MeasurementRecord,
    SLAVE_SD_UNAVAILABLE,
    SLAVE_SD_WRITE_ERROR,
)
from ports.errors import StorageError
from domain.protocol import (
    AckMessage,
    AsciiProtocolCodec,
    DiagnosticEvent,
    ProtocolError,
    SequenceQuery,
    SequenceResponse,
)


def values():
    result = {}
    for index, name in enumerate(MEASUREMENT_FIELDS):
        result[name] = index + 0.5
    result["co2_ppm"] = 430
    return result


def record(sequence):
    return MeasurementRecord(
        "C01", sequence, "2026-08-14T08:00:00Z", 60, values(), 0,
        "M01", "M01"
    )


class FakeDiagnostics:
    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(("info", message))

    def error(self, message):
        self.messages.append(("error", message))


class FakeSlaveStorage:
    def __init__(self, pending=None, events=None):
        self.pending = list(pending or [])
        self.marked = []
        self.events = events if events is not None else []

    def next_sequence(self):
        return len(self.pending)

    def save_local(self, item):
        self.events.append(("save", item.sequence_number))
        self.pending.append(item)

    def pending_records(self):
        return iter(self.pending)

    def mark_transmitted(self, item):
        self.events.append(("mark", item.sequence_number))
        self.marked.append(item.sequence_number)


class FailingSlaveStorage(FakeSlaveStorage):
    def save_local(self, _item):
        raise StorageError("simulated SD write failure")


class FakeSensor:
    def __init__(self):
        self.read_count = 0

    def read_measurement(self):
        self.read_count += 1
        return values(), 0


class FakeClock:
    def __init__(self):
        self.sleeps = []

    def measurement_timestamp(self):
        return "2026-08-14T08:00:00Z"

    def uptime_s(self):
        return 60

    def sleep_ms(self, milliseconds):
        self.sleeps.append(milliseconds)


class FakeRadio:
    def __init__(self, receives=None, events=None):
        self.receives = list(receives or [])
        self.sent = []
        self.events = events if events is not None else []

    def send(self, payload):
        self.sent.append(payload)
        self.events.append(("send", payload))
        return True

    def receive(self, _timeout_ms):
        if not self.receives:
            return None, {}
        return self.receives.pop(0)


class FakeMasterStorage:
    def __init__(self, events=None):
        self.received = {}
        self.diagnostic_events = []
        self.events = events if events is not None else []

    def has_received(self, device_id, sequence_number):
        return (device_id, sequence_number) in self.received

    def save_received(self, item, metadata):
        self.events.append(("store", item.sequence_number))
        self.received[(item.device_id, item.sequence_number)] = metadata

    def save_missing_interval(self, device_id, metadata):
        self.events.append(("gap", device_id, metadata["master_uptime_s"]))

    def next_sequence_for(self, device_id):
        sequences = [
            sequence for stored_device, sequence in self.received
            if stored_device == device_id
        ]
        return max(sequences) + 1 if sequences else 0

    def save_diagnostic_event(self, event):
        key = (event.origin_id, event.event_code, event.event_state)
        if key in [(item.origin_id, item.event_code, item.event_state)
                   for item in self.diagnostic_events]:
            return False
        self.diagnostic_events.append(event)
        return True


class HexagonalCoreTests(unittest.TestCase):
    def setUp(self):
        self.codec = AsciiProtocolCodec()
        self.diagnostics = FakeDiagnostics()

    def test_codec_round_trip_preserves_identity_and_timestamp(self):
        original = record(7)
        decoded = self.codec.decode_data(self.codec.encode_data(original))
        self.assertEqual(decoded.device_id, "C01")
        self.assertEqual(decoded.sequence_number, 7)
        self.assertEqual(decoded.measurement_timestamp, original.measurement_timestamp)
        self.assertEqual(decoded.values["co2_ppm"], 430)
        self.assertEqual(decoded.destination_id, "M01")
        self.assertEqual(decoded.next_hop_id, "M01")
        self.assertEqual(len(self.codec.encode_data(original).split(b";")), 22)

    def test_v1_data_packet_matches_specification(self):
        measurement_values = dict((name, None) for name in MEASUREMENT_FIELDS)
        measurement_values.update({
            "air_temperature_c": 22.4,
            "relative_humidity_pct": 58.1,
            "co2_ppm": 430,
            "pm1_0_ug_m3": 4.2,
            "pm2_5_ug_m3": 5.1,
            "pm4_0_ug_m3": 6.3,
            "pm10_ug_m3": 8.1,
            "voc_index": 10.4,
            "nox_index": 1.2,
        })
        item = MeasurementRecord(
            "C01", 125, None, 3720, measurement_values, 0x0040,
            "M01", "M01", 0, 1,
        )
        payload = self.codec.encode_data(item)
        self.assertEqual(
            payload,
            b"1;D;C01;M01;M01;125;0;1;NA;3720;224;581;430;42;51;63;81;104;12;NA;NA;0040",
        )
        self.assertEqual(self.codec.decode_data(payload).measurement_timestamp, "NA")

    def test_v1_ack_matches_specification_and_checks_master(self):
        payload = self.codec.encode_ack(
            AckMessage("M01", "C01", "C01", 125, 0)
        )
        self.assertEqual(payload, b"1;A;M01;C01;C01;125;0;1;0")
        self.assertTrue(self.codec.is_success_ack(payload, "M01", "C01", 125))
        self.assertFalse(self.codec.is_success_ack(payload, "M02", "C01", 125))
        self.assertFalse(self.codec.is_success_ack(payload, "M01", "C02", 125))
        rejected = self.codec.encode_ack(
            AckMessage("M01", "C01", "C01", 125, 1)
        )
        self.assertFalse(
            self.codec.is_success_ack(rejected, "M01", "C01", 125)
        )

    def test_diagnostic_event_round_trip(self):
        event = DiagnosticEvent(
            "C01", "M01", "M01", 125, "SLAVE_SD_UNAVAILABLE",
            "STARTED", 1,
        )
        payload = self.codec.encode_diagnostic_event(event)
        self.assertEqual(
            payload,
            b"1;E;C01;M01;M01;125;0;1;SLAVE_SD_UNAVAILABLE;STARTED;1",
        )
        decoded = self.codec.decode_diagnostic_event(payload)
        self.assertEqual(decoded.event_code, "SLAVE_SD_UNAVAILABLE")
        self.assertEqual(decoded.event_state, "STARTED")

    def test_v1_data_rejects_invalid_fields(self):
        fields = self.codec.encode_data(record(7)).decode("ascii").split(";")
        invalid_packets = []
        invalid = list(fields)
        invalid[11] = "-1"
        invalid_packets.append(";".join(invalid).encode("ascii"))
        invalid = list(fields)
        invalid[21] = "00000"
        invalid_packets.append(";".join(invalid).encode("ascii"))
        invalid = list(fields)
        invalid[3] = " M01"
        invalid_packets.append(";".join(invalid).encode("ascii"))
        invalid_packets.append(b";".join(part.encode("ascii") for part in fields[:-1]))
        for payload in invalid_packets:
            with self.subTest(payload=payload):
                with self.assertRaises(ProtocolError):
                    self.codec.decode_data(payload)

    def test_master_stores_diagnostic_event_once(self):
        event = DiagnosticEvent(
            "C01", "M01", "M01", 4, "SLAVE_SD_UNAVAILABLE", "STARTED"
        )
        payload = self.codec.encode_diagnostic_event(event)
        storage = FakeMasterStorage()
        radio = FakeRadio([(payload, {})])
        master = MasterController(
            "M01", FakeClock(), storage, radio, self.codec,
            self.diagnostics, monitored_slaves=["C01"],
        )
        self.assertTrue(master.process_next(100))
        self.assertEqual(len(storage.diagnostic_events), 1)
        self.assertEqual(radio.sent, [])

    def test_v1_payload_limit_is_enforced(self):
        item = record(10 ** 170)
        with self.assertRaises(ProtocolError):
            self.codec.encode_data(item)
        with self.assertRaises(ProtocolError):
            self.codec.decode_data(b"1" * 161)

    def test_sequence_query_round_trip(self):
        payload = self.codec.encode_sequence_query(
            SequenceQuery("C01", "M01", "M01")
        )
        decoded = self.codec.decode_sequence_query(payload)
        self.assertEqual(payload, b"1;Q;C01;M01;M01;0;0;1")
        self.assertEqual(decoded.origin_id, "C01")
        self.assertEqual(decoded.destination_id, "M01")
        self.assertEqual(decoded.next_hop_id, "M01")
        self.assertEqual(decoded.hop_count, 0)
        self.assertEqual(decoded.hop_limit, 1)

    def test_sequence_response_round_trip_for_known_slave(self):
        payload = self.codec.encode_sequence_response(
            SequenceResponse("M01", "C01", "C01", 126)
        )
        decoded = self.codec.decode_sequence_response(payload)
        self.assertEqual(payload, b"1;R;M01;C01;C01;126;0;1")
        self.assertEqual(decoded.next_sequence, 126)

    def test_sequence_response_allows_zero_for_new_slave(self):
        payload = self.codec.encode_sequence_response(
            SequenceResponse("M01", "C01", "C01", 0)
        )
        self.assertEqual(
            self.codec.decode_sequence_response(payload).next_sequence, 0
        )

    def test_sequence_query_rejects_nonzero_reserved_field(self):
        with self.assertRaises(ProtocolError):
            self.codec.decode_sequence_query(b"1;Q;C01;M01;M01;1;0;1")

    def test_sequence_messages_reject_wrong_type_or_field_count(self):
        with self.assertRaises(ProtocolError):
            self.codec.decode_sequence_response(b"1;R;M01;C01;C01;1;0")
        with self.assertRaises(ProtocolError):
            self.codec.decode_sequence_response(b"1;Q;M01;C01;C01;1;0;1")

    def test_sequence_response_rejects_invalid_sequence_and_hops(self):
        invalid_payloads = (
            b"1;R;M01;C01;C01;-1;0;1",
            b"1;R;M01;C01;C01;1;2;1",
            b"1;R;M01;C01;C01;abc;0;1",
        )
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ProtocolError):
                    self.codec.decode_sequence_response(payload)

    def test_master_returns_next_sequence_for_known_slave(self):
        storage = FakeMasterStorage()
        storage.received[("C01", 125)] = {}
        query = self.codec.encode_sequence_query(
            SequenceQuery("C01", "M01", "M01")
        )
        radio = FakeRadio([(query, {})])
        controller = MasterController(
            "M01", FakeClock(), storage, radio, self.codec, self.diagnostics
        )
        self.assertTrue(controller.process_next(30000))
        response = self.codec.decode_sequence_response(radio.sent[0])
        self.assertEqual(response.next_sequence, 126)

    def test_master_returns_zero_for_new_slave(self):
        query = self.codec.encode_sequence_query(
            SequenceQuery("C01", "M01", "M01")
        )
        radio = FakeRadio([(query, {})])
        controller = MasterController(
            "M01", FakeClock(), FakeMasterStorage(), radio,
            self.codec, self.diagnostics
        )
        self.assertTrue(controller.process_next(30000))
        self.assertEqual(
            self.codec.decode_sequence_response(radio.sent[0]).next_sequence, 0
        )

    def test_repeated_query_returns_same_free_sequence(self):
        storage = FakeMasterStorage()
        storage.received[("C01", 125)] = {}
        query = self.codec.encode_sequence_query(
            SequenceQuery("C01", "M01", "M01")
        )
        radio = FakeRadio([(query, {}), (query, {})])
        controller = MasterController(
            "M01", FakeClock(), storage, radio, self.codec, self.diagnostics
        )
        self.assertTrue(controller.process_next(30000))
        self.assertTrue(controller.process_next(30000))
        self.assertEqual(
            [self.codec.decode_sequence_response(item).next_sequence
             for item in radio.sent],
            [126, 126],
        )

    def test_seq_11_ack_lost_after_master_store_returns_next_sequence(self):
        storage = FakeMasterStorage()
        storage.received[("C01", 125)] = {}
        query = self.codec.encode_sequence_query(
            SequenceQuery("C01", "M01", "M01")
        )
        radio = FakeRadio([(query, {})])
        controller = MasterController(
            "M01", FakeClock(), storage, radio, self.codec, self.diagnostics
        )
        self.assertTrue(controller.process_next(30000))
        response = self.codec.decode_sequence_response(radio.sent[0])
        self.assertEqual(response.next_sequence, 126)

    def test_seq_12_unsaved_sequence_remains_free_after_restart_query(self):
        storage = FakeMasterStorage()
        storage.received[("C01", 124)] = {}
        query = self.codec.encode_sequence_query(
            SequenceQuery("C01", "M01", "M01")
        )
        radio = FakeRadio([(query, {})])
        controller = MasterController(
            "M01", FakeClock(), storage, radio, self.codec, self.diagnostics
        )
        self.assertTrue(controller.process_next(30000))
        response = self.codec.decode_sequence_response(radio.sent[0])
        self.assertEqual(response.next_sequence, 125)

    def test_slave_accepts_only_matching_sequence_response(self):
        controller = SlaveController(
            "C01", FakeSensor(), FakeClock(), FakeSlaveStorage(), FakeRadio(),
            self.codec, self.diagnostics, 3000, master_id="M01"
        )
        valid = self.codec.encode_sequence_response(
            SequenceResponse("M01", "C01", "C01", 126)
        )
        wrong_master = self.codec.encode_sequence_response(
            SequenceResponse("M02", "C01", "C01", 126)
        )
        wrong_slave = self.codec.encode_sequence_response(
            SequenceResponse("M01", "C02", "C02", 126)
        )
        self.assertEqual(controller.sequence_from_response(valid), 126)
        self.assertIsNone(controller.sequence_from_response(wrong_master))
        self.assertIsNone(controller.sequence_from_response(wrong_slave))
        self.assertIsNone(controller.sequence_from_response(b"invalid"))

    def test_slave_sequence_query_round_stops_after_success(self):
        response = self.codec.encode_sequence_response(
            SequenceResponse("M01", "C01", "C01", 126)
        )
        clock = FakeClock()
        radio = FakeRadio([(response, {})])
        controller = SlaveController(
            "C01", FakeSensor(), clock, FakeSlaveStorage(), radio,
            self.codec, self.diagnostics, 3000, master_id="M01"
        )
        self.assertEqual(controller.request_sequence_round(), 126)
        self.assertEqual(len(radio.sent), 1)
        self.assertEqual(clock.sleeps, [])
        query = self.codec.decode_sequence_query(radio.sent[0])
        self.assertEqual(query.origin_id, "C01")
        self.assertEqual(query.destination_id, "M01")
        self.assertEqual(query.next_hop_id, "M01")

    def test_seq_04_sequence_query_round_without_master_response(self):
        clock = FakeClock()
        radio = FakeRadio([(None, {}), (None, {}), (None, {})])
        controller = SlaveController(
            "C01", FakeSensor(), clock, FakeSlaveStorage(), radio,
            self.codec, self.diagnostics, 3000, master_id="M01"
        )
        self.assertIsNone(controller.request_sequence_round())
        self.assertEqual(len(radio.sent), 3)
        self.assertEqual(clock.sleeps, [2000, 2000])
        for payload in radio.sent:
            query = self.codec.decode_sequence_query(payload)
            self.assertEqual(query.origin_id, "C01")
            self.assertEqual(query.destination_id, "M01")
            self.assertEqual(query.next_hop_id, "M01")

    def test_no_sd_cycle_without_master_response_sends_no_measurement(self):
        clock = FakeClock()
        radio = FakeRadio([(None, {}), (None, {}), (None, {})])
        controller = SlaveController(
            "C01", FakeSensor(), clock, None, radio,
            self.codec, self.diagnostics, 3000, master_id="M01"
        )
        self.assertEqual(
            controller.run_measurement_cycle_without_local_storage(), 0
        )
        self.assertEqual(
            [self.codec.message_type(payload) for payload in radio.sent],
            ["E", "Q", "Q", "Q"],
        )

    def test_no_sd_retry_reuses_held_measurement_until_next_cycle(self):
        sensor = FakeSensor()
        response = self.codec.encode_sequence_response(
            SequenceResponse("M01", "C01", "C01", 126)
        )
        ack = self.codec.encode_ack(
            AckMessage("M01", "C01", "C01", 126)
        )
        radio = FakeRadio([
            (None, {}), (None, {}), (None, {}),
            (response, {}), (ack, {}),
        ])
        controller = SlaveController(
            "C01", sensor, FakeClock(), None, radio,
            self.codec, self.diagnostics, 3000, master_id="M01"
        )
        self.assertEqual(
            controller.run_measurement_cycle_without_local_storage(True), 0
        )
        self.assertEqual(
            controller.run_measurement_cycle_without_local_storage(False), 1
        )
        self.assertEqual(sensor.read_count, 1)
        self.assertIsNone(controller.volatile_held_measurement)
        self.assertEqual(
            [self.codec.message_type(payload) for payload in radio.sent],
            ["E", "Q", "Q", "Q", "Q", "D"],
        )

    def test_no_sd_cycle_sends_measurement_with_status_after_sequence_response(self):
        response = self.codec.encode_sequence_response(
            SequenceResponse("M01", "C01", "C01", 126)
        )
        ack = self.codec.encode_ack(
            AckMessage("M01", "C01", "C01", 126)
        )
        radio = FakeRadio([(response, {}), (ack, {})])
        controller = SlaveController(
            "C01", FakeSensor(), FakeClock(), None, radio,
            self.codec, self.diagnostics, 3000, master_id="M01"
        )
        self.assertEqual(
            controller.run_measurement_cycle_without_local_storage(), 1
        )
        self.assertEqual(
            [self.codec.message_type(payload) for payload in radio.sent],
            ["E", "Q", "D"],
        )
        event = self.codec.decode_diagnostic_event(radio.sent[0])
        self.assertEqual(event.event_code, "SLAVE_SD_UNAVAILABLE")
        sent_record = self.codec.decode_data(radio.sent[2])
        self.assertEqual(sent_record.sequence_number, 126)
        self.assertTrue(sent_record.status_flags & SLAVE_SD_UNAVAILABLE)
        self.assertEqual(controller.volatile_next_sequence, 127)

    def test_device_restart_event_references_next_local_sequence(self):
        storage = FakeSlaveStorage([record(0), record(1)])
        radio = FakeRadio()
        controller = SlaveController(
            "C01", FakeSensor(), FakeClock(), storage, radio,
            self.codec, self.diagnostics, 3000, master_id="M01"
        )
        self.assertTrue(controller.report_device_restarted())
        event = self.codec.decode_diagnostic_event(radio.sent[0])
        self.assertEqual(event.event_code, "DEVICE_RESTARTED")
        self.assertEqual(event.event_state, "OCCURRED")
        self.assertEqual(event.reference_sequence, 2)

    def test_sd_write_failure_sends_degraded_record_with_flags(self):
        response = self.codec.encode_sequence_response(
            SequenceResponse("M01", "C01", "C01", 0)
        )
        ack = self.codec.encode_ack(AckMessage("M01", "C01", "C01", 0))
        radio = FakeRadio([(response, {}), (ack, {})])
        controller = SlaveController(
            "C01", FakeSensor(), FakeClock(), FailingSlaveStorage(), radio,
            self.codec, self.diagnostics, 3000, master_id="M01"
        )
        self.assertEqual(controller.run_measurement_cycle(), 1)
        message_types = [self.codec.message_type(payload) for payload in radio.sent]
        self.assertEqual(message_types, ["E", "E", "Q", "D"])
        sent_record = self.codec.decode_data(radio.sent[-1])
        self.assertTrue(sent_record.status_flags & SLAVE_SD_UNAVAILABLE)
        self.assertTrue(sent_record.status_flags & SLAVE_SD_WRITE_ERROR)

    def test_no_sd_cycle_continues_ram_sequence_after_ack(self):
        response = self.codec.encode_sequence_response(
            SequenceResponse("M01", "C01", "C01", 126)
        )
        first_ack = self.codec.encode_ack(
            AckMessage("M01", "C01", "C01", 126)
        )
        second_ack = self.codec.encode_ack(
            AckMessage("M01", "C01", "C01", 127)
        )
        radio = FakeRadio([(response, {}), (first_ack, {}), (second_ack, {})])
        controller = SlaveController(
            "C01", FakeSensor(), FakeClock(), None, radio,
            self.codec, self.diagnostics, 3000, master_id="M01"
        )
        self.assertEqual(
            controller.run_measurement_cycle_without_local_storage(), 1
        )
        self.assertEqual(
            controller.run_measurement_cycle_without_local_storage(), 1
        )
        self.assertEqual(
            [self.codec.message_type(payload) for payload in radio.sent],
            ["E", "Q", "D", "D"],
        )
        self.assertEqual(self.codec.decode_data(radio.sent[2]).sequence_number, 126)
        self.assertEqual(self.codec.decode_data(radio.sent[3]).sequence_number, 127)

    def test_no_sd_cycle_forgets_ram_sequence_after_missing_ack(self):
        response = self.codec.encode_sequence_response(
            SequenceResponse("M01", "C01", "C01", 126)
        )
        radio = FakeRadio([(response, {}), (None, {})])
        controller = SlaveController(
            "C01", FakeSensor(), FakeClock(), None, radio,
            self.codec, self.diagnostics, 3000, master_id="M01"
        )
        self.assertEqual(
            controller.run_measurement_cycle_without_local_storage(), 0
        )
        self.assertIsNone(controller.volatile_next_sequence)

    def test_master_rejects_query_for_another_master(self):
        query = self.codec.encode_sequence_query(
            SequenceQuery("C01", "M02", "M02")
        )
        radio = FakeRadio([(query, {})])
        controller = MasterController(
            "M01", FakeClock(), FakeMasterStorage(), radio,
            self.codec, self.diagnostics
        )
        self.assertFalse(controller.process_next(30000))
        self.assertEqual(radio.sent, [])

    def test_master_rejects_data_for_another_master(self):
        item = record(1)
        item.destination_id = "M02"
        item.next_hop_id = "M02"
        radio = FakeRadio([(self.codec.encode_data(item), {})])
        storage = FakeMasterStorage()
        controller = MasterController(
            "M01", FakeClock(), storage, radio, self.codec, self.diagnostics
        )
        self.assertFalse(controller.process_next(30000))
        self.assertEqual(storage.received, {})
        self.assertEqual(radio.sent, [])

    def test_master_rejects_unmonitored_slave_packets(self):
        unknown_record = record(1)
        unknown_record.device_id = "C99"
        query = self.codec.encode_sequence_query(
            SequenceQuery("C99", "M01", "M01")
        )
        radio = FakeRadio([
            (self.codec.encode_data(unknown_record), {}),
            (query, {}),
        ])
        storage = FakeMasterStorage()
        controller = MasterController(
            "M01", FakeClock(), storage, radio, self.codec,
            self.diagnostics, monitored_slaves=["C01"]
        )
        self.assertFalse(controller.process_next(30000))
        self.assertFalse(controller.process_next(30000))
        self.assertEqual(storage.received, {})
        self.assertEqual(radio.sent, [])

    def test_relay_silently_ignores_other_recipients(self):
        item = record(7)
        payloads = [
            self.codec.encode_data(item),
            self.codec.encode_ack(AckMessage("M01", "C03", "C01", 7)),
            self.codec.encode_sequence_query(SequenceQuery("C03", "M01", "C01")),
            self.codec.encode_sequence_response(SequenceResponse("M01", "C03", "C01", 8)),
        ]
        radio = FakeRadio([(payload, {}) for payload in payloads])
        storage = FakeSlaveStorage()
        relay = RelayController(
            "C02", "M01", "C01", {"C03": "C03"}, radio,
            self.codec, self.diagnostics, 3000, storage,
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertFalse(relay.process_next(30000))
        self.assertEqual(radio.sent, [])
        self.assertEqual(self.diagnostics.messages, [])
        self.assertEqual(storage.events, [])

    def test_relay_still_reports_invalid_packet_for_itself(self):
        item = record(7)
        item.next_hop_id = "C02"
        item.destination_id = "M99"
        radio = FakeRadio([(self.codec.encode_data(item), {})])
        relay = RelayController(
            "C02", "M01", "C01", {}, radio,
            self.codec, self.diagnostics, 3000,
        )
        self.assertFalse(relay.process_next(30000))
        self.assertEqual(radio.sent, [])
        self.assertEqual(self.diagnostics.messages[0][0], "error")

    def test_relay_forwards_sequence_query_and_response(self):
        query = self.codec.encode_sequence_query(
            SequenceQuery("C03", "M01", "C02", 0, 3)
        )
        response = self.codec.encode_sequence_response(
            SequenceResponse("M01", "C03", "C02", 14, 0, 3)
        )
        radio = FakeRadio([(query, {}), (response, {})])
        relay = RelayController(
            "C02", "M01", "M01", {"C03": "C03"}, radio,
            self.codec, self.diagnostics, 3000,
        )
        self.assertTrue(relay.process_next(30000))
        forwarded_query = self.codec.decode_sequence_query(radio.sent[0])
        forwarded_response = self.codec.decode_sequence_response(radio.sent[1])
        self.assertEqual(forwarded_query.next_hop_id, "M01")
        self.assertEqual(forwarded_query.hop_count, 1)
        self.assertEqual(forwarded_response.next_hop_id, "C03")
        self.assertEqual(forwarded_response.next_sequence, 14)

    def test_relay_forwards_data_and_master_ack_along_static_route(self):
        item = record(7)
        item.device_id = "C03"
        item.next_hop_id = "C02"
        item.hop_limit = 3
        master_ack = self.codec.encode_ack(
            AckMessage("M01", "C03", "C02", 7, 0, 0, 3)
        )
        radio = FakeRadio([(self.codec.encode_data(item), {}), (master_ack, {})])
        relay = RelayController(
            "C02", "M01", "M01", {"C03": "C03"}, radio,
            self.codec, self.diagnostics, 3000,
        )
        self.assertTrue(relay.process_next(30000))
        forwarded = self.codec.decode_data(radio.sent[0])
        returned_ack = self.codec.decode_ack(radio.sent[1])
        self.assertEqual(forwarded.next_hop_id, "M01")
        self.assertEqual(forwarded.hop_count, 1)
        self.assertEqual(returned_ack.next_hop_id, "C03")
        self.assertEqual(returned_ack.hop_count, 1)

    def test_slave_ignores_foreign_ack_until_own_ack_arrives(self):
        pending = [record(0)]
        foreign_ack = self.codec.encode_ack(
            AckMessage("M01", "C02", "C02", 0)
        )
        own_ack = self.codec.encode_ack(
            AckMessage("M01", "C01", "C01", 0)
        )
        storage = FakeSlaveStorage(pending)
        radio = FakeRadio([(foreign_ack, {}), (own_ack, {})])
        controller = SlaveController(
            "C01", FakeSensor(), FakeClock(), storage, radio,
            self.codec, self.diagnostics, 3000, master_id="M01",
        )
        self.assertEqual(controller.transmit_pending(), 1)
        self.assertEqual(storage.marked, [0])
        self.assertEqual(self.diagnostics.messages,
                         [("info", "sequence 0 acknowledged")])

    def test_slave_stores_before_sending(self):
        events = []
        storage = FakeSlaveStorage(events=events)
        ack = self.codec.encode_ack(
            AckMessage("M01", "C01", "C01", 0)
        )
        radio = FakeRadio([(ack, {})], events)
        controller = SlaveController(
            "C01", FakeSensor(), FakeClock(), storage, radio,
            self.codec, self.diagnostics, 3000,
            master_id="M01",
        )
        controller.run_measurement_cycle()
        self.assertEqual(events[0], ("save", 0))
        self.assertEqual(events[1][0], "send")
        self.assertEqual(storage.marked, [0])

    def test_slave_stops_fifo_transfer_after_first_missing_ack(self):
        pending = [record(0), record(1), record(2)]
        first_ack = self.codec.encode_ack(
            AckMessage("M01", "C01", "C01", 0)
        )
        radio = FakeRadio([(first_ack, {}), (None, {})])
        storage = FakeSlaveStorage(pending)
        controller = SlaveController(
            "C01", FakeSensor(), FakeClock(), storage, radio,
            self.codec, self.diagnostics, 3000,
            master_id="M01",
        )
        self.assertEqual(controller.transmit_pending(), 1)
        self.assertEqual(storage.marked, [0])
        self.assertEqual(len(radio.sent), 2)

    def test_master_stores_before_ack(self):
        events = []
        incoming = self.codec.encode_data(record(5))
        radio = FakeRadio([(incoming, {"rssi_dbm": -90})], events)
        storage = FakeMasterStorage(events)
        controller = MasterController(
            "M01", FakeClock(), storage, radio, self.codec, self.diagnostics
        )
        self.assertTrue(controller.process_next(30000))
        self.assertEqual(events[0], ("store", 5))
        metadata = storage.received[("C01", 5)]
        self.assertEqual(metadata["master_id"], "M01")
        self.assertEqual(metadata["master_uptime_s"], 60)
        self.assertEqual(metadata["received_timestamp"], "2026-08-14T08:00:00Z")
        self.assertEqual(events[1][0], "send")
        self.assertTrue(self.codec.is_success_ack(radio.sent[0], "M01", "C01", 5))

    def test_master_uses_configured_relay_for_mesh_sequence_response(self):
        query = self.codec.encode_sequence_query(
            SequenceQuery("C03", "M01", "M01", 1, 3)
        )
        radio = FakeRadio([(query, {})])
        controller = MasterController(
            "M01", FakeClock(), FakeMasterStorage(), radio, self.codec,
            self.diagnostics, return_next_hops={"C03": "C02"},
        )
        self.assertTrue(controller.process_next(30000))
        response = self.codec.decode_sequence_response(radio.sent[0])
        self.assertEqual(response.next_hop_id, "C02")
        self.assertEqual(response.hop_limit, 3)

    def test_master_uses_configured_relay_for_mesh_ack(self):
        item = record(6)
        item.device_id = "C03"
        item.next_hop_id = "M01"
        item.hop_count = 1
        item.hop_limit = 3
        radio = FakeRadio([(self.codec.encode_data(item), {})])
        controller = MasterController(
            "M01", FakeClock(), FakeMasterStorage(), radio, self.codec,
            self.diagnostics, return_next_hops={"C03": "C02"},
        )
        self.assertTrue(controller.process_next(30000))
        ack = self.codec.decode_ack(radio.sent[0])
        self.assertEqual(ack.next_hop_id, "C02")
        self.assertEqual(ack.hop_limit, 3)

    def test_master_acknowledges_stored_duplicate_without_storing_again(self):
        item = record(9)
        incoming = self.codec.encode_data(item)
        radio = FakeRadio([(incoming, {})])
        storage = FakeMasterStorage()
        storage.received[("C01", 9)] = {}
        controller = MasterController(
            "M01", FakeClock(), storage, radio, self.codec, self.diagnostics
        )
        self.assertTrue(controller.process_next(30000))
        self.assertEqual(len(storage.received), 1)
        self.assertTrue(self.codec.is_success_ack(radio.sent[0], "M01", "C01", 9))


if __name__ == "__main__":
    unittest.main()
