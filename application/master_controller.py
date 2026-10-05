"""Master-Anwendungsfall ohne direkte Hardwareabhaengigkeiten."""

from domain.measurement import MeasurementRecord
from domain.plausibility import PlausibilityPolicy
from domain.protocol import (
    AckMessage,
    DIAGNOSTIC_EVENT_TYPE,
    ProtocolError,
    SEQUENCE_QUERY_TYPE,
    SequenceResponse,
)


class MasterController:
    def __init__(self, master_id, clock, storage, radio, codec, diagnostics,
                 monitored_slaves=None, return_next_hops=None, sensor=None,
                 measurement_interval_s=900, plausibility_limits=None):
        self.master_id = master_id
        self.clock = clock
        self.storage = storage
        self.radio = radio
        self.codec = codec
        self.diagnostics = diagnostics
        self.monitored_slaves = (
            set(monitored_slaves) if monitored_slaves is not None else None
        )
        self.return_next_hops = dict(return_next_hops or {})
        self.sensor = sensor
        self.measurement_interval_s = int(measurement_interval_s)
        if self.measurement_interval_s <= 0:
            raise ValueError("measurement interval must be positive")
        self._next_measurement_at = 0
        self._measurement_active = False
        self._local_record = None
        self._storage_retry_at = 0
        self.plausibility = PlausibilityPolicy(plausibility_limits)
        self._next_missing_interval_check_at = self.measurement_interval_s
        self._received_in_interval = set()

    def poll_measurement(self):
        if self.sensor is None:
            return False
        now = self.clock.uptime_s()
        if self._local_record is not None:
            if now < self._storage_retry_at:
                return False
            # Retain the completed sample across temporary SD errors.
            self._storage_retry_at = now + 5
            self.storage.save_received(self._local_record, {
                "master_id": self.master_id,
                "received_timestamp": self.clock.measurement_timestamp(),
                "master_uptime_s": now,
            })
            sequence = self._local_record.sequence_number
            self._local_record = None
            self.diagnostics.info("master measurement {} stored".format(sequence))
            return True
        if not self._measurement_active:
            if now < self._next_measurement_at:
                return False
            self._next_measurement_at = now + self.measurement_interval_s
            self.sensor.start_measurement()
            self._measurement_active = True
        result = self.sensor.poll_measurement()
        if result is None:
            return False
        self._measurement_active = False
        values, flags = result
        status_flags = getattr(self.clock, "status_flags", None)
        if status_flags is not None:
            flags |= status_flags()
        flags = self.plausibility.apply(values, flags)
        self._local_record = MeasurementRecord(
            self.master_id, self.storage.next_sequence_for(self.master_id),
            self.clock.measurement_timestamp(), self.clock.uptime_s(),
            values, flags, self.master_id, self.master_id,
        )
        self._storage_retry_at = 0
        return self.poll_measurement()

    def poll_missing_intervals(self):
        """Erfasst je vollendetem Rasterintervall fehlende Slave-Pakete."""
        if self.monitored_slaves is None:
            return False
        now = self.clock.uptime_s()
        stored_gap = False
        while now >= self._next_missing_interval_check_at:
            for device_id in self.monitored_slaves:
                if device_id in self._received_in_interval:
                    continue
                self.storage.save_missing_interval(device_id, {
                    "master_id": self.master_id,
                    "master_uptime_s": self._next_missing_interval_check_at,
                    "received_timestamp": self.clock.measurement_timestamp(),
                })
                self.diagnostics.info(
                    "missing packet recorded for {}".format(device_id)
                )
                stored_gap = True
            self._received_in_interval = set()
            self._next_missing_interval_check_at += self.measurement_interval_s
        return stored_gap

    def _process_sequence_query(self, payload):
        query = self.codec.decode_sequence_query(payload)
        if query.next_hop_id != self.master_id:
            return False
        if (self.monitored_slaves is not None
                and query.origin_id not in self.monitored_slaves):
            raise ProtocolError("sequence query from unmonitored slave")
        if query.destination_id != self.master_id:
            raise ProtocolError("sequence query addressed to another master")
        next_sequence = self.storage.next_sequence_for(query.origin_id)
        response = SequenceResponse(
            self.master_id, query.origin_id,
            self._ack_next_hop(query.origin_id), next_sequence,
            0, query.hop_limit
        )
        if not self.radio.send(self.codec.encode_sequence_response(response)):
            self.diagnostics.error(
                "sequence response send failed for {}".format(query.origin_id)
            )
            return False
        self.diagnostics.info(
            "next sequence for {} is {}".format(
                query.origin_id, next_sequence
            )
        )
        return True

    def _ack_next_hop(self, origin_id):
        return self.return_next_hops.get(origin_id, origin_id)

    def _process_diagnostic_event(self, payload):
        event = self.codec.decode_diagnostic_event(payload)
        if event.next_hop_id != self.master_id:
            return False
        if event.destination_id != self.master_id:
            raise ProtocolError("diagnostic event addressed to another master")
        if (self.monitored_slaves is not None
                and event.origin_id not in self.monitored_slaves):
            raise ProtocolError("diagnostic event from unmonitored slave")
        if self.storage.save_diagnostic_event(event):
            self.diagnostics.info(
                "diagnostic {}:{} {} stored".format(
                    event.origin_id, event.event_code, event.event_state
                )
            )
        return True

    def process_next(self, timeout_ms):
        payload, metadata = self.radio.receive(timeout_ms)
        if not payload:
            return False
        try:
            message_type = self.codec.message_type(payload)
            if message_type in ("A", "R"):
                return False
            if message_type == SEQUENCE_QUERY_TYPE:
                return self._process_sequence_query(payload)
            if message_type == DIAGNOSTIC_EVENT_TYPE:
                return self._process_diagnostic_event(payload)
            record = self.codec.decode_data(payload)
            if record.next_hop_id != self.master_id:
                return False
            if record.destination_id != self.master_id:
                raise ProtocolError("data packet addressed to another master")
            if (self.monitored_slaves is not None
                    and record.device_id not in self.monitored_slaves):
                raise ProtocolError("data packet from unmonitored slave")
        except ProtocolError as exc:
            self.diagnostics.error("invalid packet: {}".format(exc))
            return False

        if self.storage.has_received(record.device_id, record.sequence_number):
            ack = self.codec.encode_ack(AckMessage(
                self.master_id, record.device_id,
                self._ack_next_hop(record.device_id),
                record.sequence_number, 2, 0, record.hop_limit,
            ))
            if not self.radio.send(ack):
                self.diagnostics.error(
                    "duplicate ACK send failed for {}:{}".format(
                        record.device_id, record.sequence_number
                    )
                )
                return False
            self.diagnostics.info(
                "duplicate {}:{} acknowledged".format(
                    record.device_id, record.sequence_number
                )
            )
            return True

        metadata["master_id"] = self.master_id
        metadata["received_timestamp"] = self.clock.measurement_timestamp()
        metadata["master_uptime_s"] = self.clock.uptime_s()
        self.storage.save_received(record, metadata)
        self._received_in_interval.add(record.device_id)
        ack = self.codec.encode_ack(AckMessage(
            self.master_id, record.device_id,
            self._ack_next_hop(record.device_id),
            record.sequence_number, 0, 0, record.hop_limit,
        ))
        if not self.radio.send(ack):
            self.diagnostics.error(
                "ACK send failed for {}:{}".format(
                    record.device_id, record.sequence_number
                )
            )
            return False
        self.diagnostics.info(
            "stored and acknowledged {}:{}".format(
                record.device_id, record.sequence_number
            )
        )
        return True
