"""Statisch konfiguriertes Weiterleiten von Datenpaketen im Mesh-Modus."""

import time

from domain.protocol import (
    ACK_TYPE, DATA_TYPE, SEQUENCE_QUERY_TYPE, SEQUENCE_RESPONSE_TYPE,
    ProtocolError,
)


class RelayController:
    """Leitet Datenpakete und deren End-to-End-ACK entlang fester Routen weiter."""

    def __init__(self, device_id, master_id, next_hop_id, reverse_next_hops,
                 radio, codec, diagnostics, forward_timeout_ms, storage=None):
        self.device_id = device_id
        self.master_id = master_id
        self.next_hop_id = next_hop_id
        self.reverse_next_hops = dict(reverse_next_hops or {})
        self.radio = radio
        self.codec = codec
        self.diagnostics = diagnostics
        self.forward_timeout_ms = int(forward_timeout_ms)
        self.storage = storage

    def _wait_for_response(self, message_type, destination_id, sequence=None):
        deadline = time.monotonic() + self.forward_timeout_ms / 1000
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            payload, _metadata = self.radio.receive(max(1, int(remaining * 1000)))
            if payload is None:
                return None
            try:
                if self.codec.message_type(payload) != message_type:
                    continue
                if message_type == ACK_TYPE:
                    response = self.codec.decode_ack(payload)
                else:
                    response = self.codec.decode_sequence_response(payload)
            except ProtocolError as exc:
                self.diagnostics.error("invalid relay response: {}".format(exc))
                continue
            if (response.origin_id != self.master_id
                    or response.destination_id != destination_id
                    or response.next_hop_id != self.device_id):
                continue
            if sequence is not None and response.sequence_number != sequence:
                continue
            return payload

    def retry_pending(self):
        if self.storage is None:
            return 0
        transmitted = 0
        for record in self.storage.pending_records():
            record.next_hop_id = self.next_hop_id
            if not self.radio.send(self.codec.encode_data(record)):
                break
            ack_payload = self._wait_for_response(
                ACK_TYPE, record.device_id, record.sequence_number
            )
            if ack_payload is None or not self._forward_ack(ack_payload):
                break
            if self.codec.decode_ack(ack_payload).result_code not in (0, 2):
                break
            self.storage.mark_delivered(record)
            transmitted += 1
        return transmitted

    def process_next(self, timeout_ms):
        payload, _metadata = self.radio.receive(timeout_ms)
        if payload is None:
            return False
        try:
            message_type = self.codec.message_type(payload)
            if message_type == DATA_TYPE:
                return self._forward_data(payload)
            if message_type == ACK_TYPE:
                return self._forward_ack(payload)
            if message_type == SEQUENCE_QUERY_TYPE:
                return self._forward_sequence_query(payload)
            if message_type == SEQUENCE_RESPONSE_TYPE:
                return self._forward_sequence_response(payload)
            raise ProtocolError("relay does not handle message type")
        except ProtocolError as exc:
            self.diagnostics.error("invalid relay packet: {}".format(exc))
            return False

    def _forward_data(self, payload):
        record = self.codec.decode_data(payload)
        if record.next_hop_id != self.device_id:
            return False
        if record.destination_id != self.master_id:
            raise ProtocolError("data packet destination differs from master")
        if record.hop_count >= record.hop_limit:
            raise ProtocolError("data packet hop limit reached")
        if self.storage is not None:
            self.storage.enqueue(record)
        record.next_hop_id = self.next_hop_id
        record.hop_count += 1
        if not self.radio.send(self.codec.encode_data(record)):
            self.diagnostics.error(
                "relay send failed for {}:{}".format(
                    record.device_id, record.sequence_number
                )
            )
            return False
        ack_payload = self._wait_for_response(
            ACK_TYPE, record.device_id, record.sequence_number
        )
        if ack_payload is None:
            self.diagnostics.error(
                "relay ACK missing for {}:{}".format(
                    record.device_id, record.sequence_number
                )
            )
            return False
        forwarded = self._forward_ack(ack_payload)
        if (forwarded and self.storage is not None
                and self.codec.decode_ack(ack_payload).result_code in (0, 2)):
            self.storage.mark_delivered(record)
        return forwarded

    def _forward_sequence_query(self, payload):
        query = self.codec.decode_sequence_query(payload)
        if query.next_hop_id != self.device_id:
            return False
        if query.destination_id != self.master_id:
            raise ProtocolError("sequence query destination differs from master")
        if query.hop_count >= query.hop_limit:
            raise ProtocolError("sequence query hop limit reached")
        query.next_hop_id = self.next_hop_id
        query.hop_count += 1
        if not self.radio.send(self.codec.encode_sequence_query(query)):
            self.diagnostics.error("relay sequence query send failed")
            return False
        response_payload = self._wait_for_response(
            SEQUENCE_RESPONSE_TYPE, query.origin_id
        )
        if response_payload is None:
            self.diagnostics.error("relay sequence response missing")
            return False
        return self._forward_sequence_response(response_payload)

    def _forward_sequence_response(self, payload):
        response = self.codec.decode_sequence_response(payload)
        if response.next_hop_id != self.device_id:
            return False
        if response.origin_id != self.master_id:
            raise ProtocolError("sequence response origin differs from master")
        if response.hop_count >= response.hop_limit:
            raise ProtocolError("sequence response hop limit reached")
        previous_hop_id = self.reverse_next_hops.get(response.destination_id)
        if previous_hop_id is None:
            raise ProtocolError("sequence response return route is not configured")
        response.next_hop_id = previous_hop_id
        response.hop_count += 1
        if not self.radio.send(self.codec.encode_sequence_response(response)):
            self.diagnostics.error("relay sequence response send failed")
            return False
        self.diagnostics.info(
            "relayed sequence response for {} to {}".format(
                response.destination_id, previous_hop_id
            )
        )
        return True

    def _forward_ack(self, payload):
        ack = self.codec.decode_ack(payload)
        if ack.next_hop_id != self.device_id:
            return False
        if ack.origin_id != self.master_id:
            raise ProtocolError("ACK origin differs from master")
        if ack.hop_count >= ack.hop_limit:
            raise ProtocolError("ACK hop limit reached")
        previous_hop_id = self.reverse_next_hops.get(ack.destination_id)
        if previous_hop_id is None:
            raise ProtocolError("ACK return route is not configured")
        ack.next_hop_id = previous_hop_id
        ack.hop_count += 1
        if not self.radio.send(self.codec.encode_ack(ack)):
            self.diagnostics.error(
                "relay ACK send failed for {}:{}".format(
                    ack.destination_id, ack.sequence_number
                )
            )
            return False
        self.diagnostics.info(
            "relayed ACK for {}:{} to {}".format(
                ack.destination_id, ack.sequence_number, previous_hop_id
            )
        )
        return True
