"""Slave-Anwendungsfall ohne direkte Hardwareabhaengigkeiten."""

import time

from domain.measurement import (
    MeasurementRecord,
    SLAVE_SD_UNAVAILABLE,
    SLAVE_SD_WRITE_ERROR,
)
from domain.plausibility import PlausibilityPolicy
from domain.protocol import (
    DiagnosticEvent, ProtocolError, SEQUENCE_RESPONSE_TYPE, SequenceQuery,
)
from ports.errors import StorageError


class SlaveController:
    def __init__(self, device_id, sensor, clock, storage, radio, codec,
                 diagnostics, ack_timeout_ms, master_id=None,
                 sequence_query_attempts=3, sequence_query_timeout_ms=3000,
                 sequence_query_pause_ms=2000, next_hop_id=None, hop_limit=1,
                 plausibility_limits=None, diagnostic_storage=None):
        self.device_id = device_id
        self.sensor = sensor
        self.clock = clock
        self.storage = storage
        self.diagnostic_storage = diagnostic_storage
        self.radio = radio
        self.codec = codec
        self.diagnostics = diagnostics
        self.ack_timeout_ms = ack_timeout_ms
        self.master_id = master_id
        self.next_hop_id = next_hop_id or master_id
        self.hop_limit = int(hop_limit)
        self.sequence_query_attempts = int(sequence_query_attempts)
        self.sequence_query_timeout_ms = int(sequence_query_timeout_ms)
        self.sequence_query_timeout_floor_ms = self.sequence_query_timeout_ms
        self.sequence_query_pause_ms = int(sequence_query_pause_ms)
        self._relay_service = None
        self.volatile_next_sequence = None
        self.volatile_held_measurement = None
        self._volatile_diagnostic_events = []
        self._active_diagnostic_events = set()
        self.plausibility = PlausibilityPolicy(plausibility_limits)

    def set_relay_service(self, relay):
        """Allows relay packets to be handled during local wait loops."""
        self._relay_service = relay
        set_service = getattr(self.sensor, "set_background_service", None)
        if set_service is not None:
            set_service(relay.service_pending)

    def _process_background_packet(self, payload):
        if self._relay_service is not None:
            self._relay_service.process_payload(payload)

    def _set_diagnostic_state(self, event_code, active, reference_sequence=0):
        is_active = event_code in self._active_diagnostic_events
        if active == is_active:
            return True
        state = "STARTED" if active else "ENDED"
        self._queue_diagnostic_event(event_code, state, 1)
        if active:
            self._active_diagnostic_events.add(event_code)
        else:
            self._active_diagnostic_events.remove(event_code)
        self.diagnostics.info(
            "diagnostic event {} {} queued".format(event_code, state)
        )
        return True

    def _clock_status_flags(self):
        status_flags = getattr(self.clock, "status_flags", None)
        return status_flags() if status_flags is not None else 0

    def report_device_restarted(self):
        """Meldet einen Neustart einmalig vor dem naechsten Messzyklus."""
        if self.master_id is None:
            return False
        reference_sequence = self.volatile_next_sequence
        if reference_sequence is None:
            reference_sequence = (
                self.storage.next_sequence() if self.storage is not None else 0
            )
        self._queue_diagnostic_event("I1", "OCCURRED", 1)
        self.diagnostics.info("diagnostic event I1 queued")
        return True

    def _queue_diagnostic_event(self, event_code, event_state, repeat_count):
        queue_owner = self.diagnostic_storage or self.storage
        queue_event = getattr(queue_owner, "queue_diagnostic_event", None)
        queued = False
        if queue_event is not None:
            try:
                queue_event(event_code, event_state, repeat_count)
                queued = True
            except StorageError as exc:
                self.diagnostics.error("local diagnostic queue failed: {}".format(exc))
        record_event = getattr(self.storage, "record_diagnostic_event", None)
        if record_event is not None and queue_owner is not self.storage:
            try:
                record_event(event_code, event_state, repeat_count)
            except StorageError as exc:
                self.diagnostics.error("SD diagnostic history failed: {}".format(exc))
        if queued:
            return
        self._volatile_diagnostic_events.append(
            (event_code, event_state, int(repeat_count))
        )

    def _pending_diagnostic_events(self, reference_sequence):
        if self.master_id is None:
            return []
        queue_owner = self.diagnostic_storage or self.storage
        pending_events = getattr(queue_owner, "pending_diagnostic_events", None)
        if pending_events is not None:
            return pending_events(
                self.device_id, reference_sequence, self.master_id,
                self.next_hop_id, self.hop_limit,
            )
        return [DiagnosticEvent(
            self.device_id, self.master_id, self.next_hop_id,
            reference_sequence, code, state, repeats, 0, self.hop_limit,
        ) for code, state, repeats in self._volatile_diagnostic_events]

    def _mark_diagnostic_events_transmitted(self, events):
        if not events:
            return
        queue_owner = self.diagnostic_storage or self.storage
        mark_events = getattr(queue_owner, "mark_diagnostic_events_transmitted", None)
        if mark_events is not None:
            mark_events(events)
        else:
            del self._volatile_diagnostic_events[:len(events)]

    def _send_diagnostics_for(self, record):
        events = self._pending_diagnostic_events(record.sequence_number)
        for event in events:
            if not self.radio.send(self.codec.encode_diagnostic_event(event)):
                self.diagnostics.error(
                    "diagnostic event send failed: {}".format(event.event_code)
                )
                # A diagnosis must not prevent the associated measurement
                # from being sent. Keep the complete batch queued for retry.
                return []
        return events

    def sequence_from_response(self, payload):
        try:
            if self.codec.message_type(payload) != SEQUENCE_RESPONSE_TYPE:
                return None
            response = self.codec.decode_sequence_response(payload)
        except ProtocolError as exc:
            self.diagnostics.error(
                "invalid sequence response: {}".format(exc)
            )
            return None
        if (self.master_id is None
                or response.origin_id != self.master_id
                or response.destination_id != self.device_id
                or response.next_hop_id != self.device_id):
            # LoRa is broadcast-like: a slave can hear an R packet while it
            # is still travelling through the configured return route.
            return None
        return response.next_sequence

    def request_sequence_from_master(self, report_timeout=True):
        if self.master_id is None:
            self.diagnostics.error("master_id required for sequence query")
            return None
        query = SequenceQuery(
            self.device_id, self.master_id, self.next_hop_id, 0, self.hop_limit
        )
        if not self.radio.send(self.codec.encode_sequence_query(query)):
            self.diagnostics.error("sequence query send failed")
            return None
        deadline = time.monotonic() + self.sequence_query_timeout_ms / 1000
        while time.monotonic() < deadline:
            remaining_ms = max(1, int((deadline - time.monotonic()) * 1000))
            payload, _metadata = self.radio.receive(remaining_ms)
            if payload is None:
                break
            sequence = self.sequence_from_response(payload)
            if sequence is not None:
                return sequence
            self._process_background_packet(payload)
        if report_timeout:
            self.diagnostics.error("sequence response timeout")
        return None

    def calibrate_sequence_query_timeout(self):
        """Measures one Q/R round trip without weakening the route baseline."""
        if self.master_id is None:
            return None
        started_at = time.monotonic()
        sequence = self.request_sequence_from_master(report_timeout=False)
        if sequence is None:
            self.diagnostics.info("sequence response startup probe unavailable")
            return None
        elapsed_ms = int((time.monotonic() - started_at) * 1000)
        measured_minimum_ms = elapsed_ms * 2 + 10000
        self.sequence_query_timeout_ms = max(
            self.sequence_query_timeout_floor_ms, measured_minimum_ms
        )
        if self.storage is None:
            self.volatile_next_sequence = sequence
        self.diagnostics.info(
            "sequence response startup probe {} ms; timeout {} ms".format(
                elapsed_ms, self.sequence_query_timeout_ms
            )
        )
        return sequence

    def request_sequence_round(self):
        for attempt in range(self.sequence_query_attempts):
            sequence = self.request_sequence_from_master()
            if sequence is not None:
                return sequence
            if attempt < self.sequence_query_attempts - 1:
                self.clock.sleep_ms(self.sequence_query_pause_ms)
        return None

    def _transmit_record_once(self, record):
        # Pending measurements can outlive a change of network topology.
        record.destination_id = self.master_id
        record.next_hop_id = self.next_hop_id
        record.hop_count = 0
        record.hop_limit = self.hop_limit
        events = self._send_diagnostics_for(record)
        payload = self.codec.encode_data(record)
        if not self.radio.send(payload):
            self.diagnostics.error(
                "send failed for sequence {}".format(record.sequence_number)
            )
            return False
        deadline = time.monotonic() + self.ack_timeout_ms / 1000
        while time.monotonic() < deadline:
            remaining_ms = max(1, int((deadline - time.monotonic()) * 1000))
            ack_payload, _metadata = self.radio.receive(remaining_ms)
            if self.codec.is_success_ack(
                   ack_payload, self.master_id, record.device_id,
                   record.sequence_number):
                self.diagnostics.info(
                    "sequence {} acknowledged".format(record.sequence_number)
                )
                self._mark_diagnostic_events_transmitted(events)
                return True
            if ack_payload is not None:
                self._process_background_packet(ack_payload)
        self.diagnostics.error(
            "ACK missing for sequence {}".format(record.sequence_number)
        )
        return False

    def run_measurement_cycle(self):
        sequence_number = self.storage.next_sequence()
        timestamp = self.clock.measurement_timestamp()
        values, status_flags = self.sensor.read_measurement()
        status_flags |= self._clock_status_flags()
        status_flags = self.plausibility.apply(values, status_flags)
        record = MeasurementRecord(
            self.device_id, sequence_number, timestamp,
            self.clock.uptime_s(), values, status_flags,
            self.master_id, self.next_hop_id, 0, self.hop_limit,
        )
        try:
            self.storage.save_local(record)
        except StorageError:
            self.diagnostics.error(
                "local SD write failed for sequence {}".format(sequence_number)
            )
            self._set_diagnostic_state(
                "F2", True, sequence_number
            )
            self.storage = None
            self.volatile_held_measurement = (
                timestamp, record.uptime_s, values,
                status_flags | SLAVE_SD_UNAVAILABLE | SLAVE_SD_WRITE_ERROR,
            )
            self.volatile_next_sequence = None
            return self.run_measurement_cycle_without_local_storage(False)
        self.diagnostics.info(
            "measurement {} stored locally".format(record.sequence_number)
        )
        return self.transmit_pending()

    def run_measurement_cycle_without_local_storage(self, refresh_measurement=True):
        self._set_diagnostic_state(
            "F1", True,
            self.volatile_next_sequence or 0,
        )
        if refresh_measurement or self.volatile_held_measurement is None:
            timestamp = self.clock.measurement_timestamp()
            values, status_flags = self.sensor.read_measurement()
            status_flags |= self._clock_status_flags()
            status_flags = self.plausibility.apply(values, status_flags)
            self.volatile_held_measurement = (
                timestamp, self.clock.uptime_s(), values,
                status_flags | SLAVE_SD_UNAVAILABLE,
            )
        if self.volatile_next_sequence is None:
            self.volatile_next_sequence = self.request_sequence_round()
        if self.volatile_next_sequence is None:
            self.diagnostics.error(
                "measurement not sent because sequence is unknown"
            )
            return 0
        timestamp, uptime_s, values, status_flags = self.volatile_held_measurement
        record = MeasurementRecord(
            self.device_id, self.volatile_next_sequence, timestamp,
            uptime_s, values, status_flags,
            self.master_id, self.next_hop_id, 0, self.hop_limit,
        )
        if not self._transmit_record_once(record):
            self.volatile_next_sequence = None
            self.volatile_held_measurement = None
            return 0
        self.volatile_next_sequence += 1
        self.volatile_held_measurement = None
        return 1

    def transmit_pending(self):
        transmitted = 0
        for record in self.storage.pending_records():
            if not self._transmit_record_once(record):
                break
            self.storage.mark_transmitted(record)
            transmitted += 1
        return transmitted
