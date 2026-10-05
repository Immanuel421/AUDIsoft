"""Kompakter ASCII-Codec fuer Climate-Cube-Protokollnachrichten."""

from domain.measurement import MEASUREMENT_FIELDS, MeasurementRecord

FORMAT_VERSION = "1"
DATA_TYPE = "D"
ACK_TYPE = "A"
SEQUENCE_QUERY_TYPE = "Q"
SEQUENCE_RESPONSE_TYPE = "R"
DIAGNOSTIC_EVENT_TYPE = "E"
MAX_PAYLOAD_BYTES = 160

_SCALES = {
    "air_temperature_c": 10,
    "relative_humidity_pct": 10,
    "co2_ppm": 1,
    "pm1_0_ug_m3": 10,
    "pm2_5_ug_m3": 10,
    "pm4_0_ug_m3": 10,
    "pm10_ug_m3": 10,
    "voc_index": 10,
    "nox_index": 10,
    "soil_moisture_pct": 1,
    "soil_temperature_c": 10,
}

_NEGATIVE_ALLOWED = ("air_temperature_c", "soil_temperature_c")


class ProtocolError(ValueError):
    pass


class SequenceQuery:
    def __init__(self, origin_id, destination_id, next_hop_id,
                 hop_count=0, hop_limit=1):
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.next_hop_id = next_hop_id
        self.hop_count = int(hop_count)
        self.hop_limit = int(hop_limit)


class SequenceResponse:
    def __init__(self, origin_id, destination_id, next_hop_id,
                 next_sequence, hop_count=0, hop_limit=1):
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.next_hop_id = next_hop_id
        self.next_sequence = int(next_sequence)
        self.hop_count = int(hop_count)
        self.hop_limit = int(hop_limit)


class AckMessage:
    def __init__(self, origin_id, destination_id, next_hop_id,
                 sequence_number, result_code=0, hop_count=0, hop_limit=1):
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.next_hop_id = next_hop_id
        self.sequence_number = int(sequence_number)
        self.result_code = int(result_code)
        self.hop_count = int(hop_count)
        self.hop_limit = int(hop_limit)


class DiagnosticEvent:
    def __init__(self, origin_id, destination_id, next_hop_id,
                 reference_sequence, event_code, event_state, repeat_count=1,
                 hop_count=0, hop_limit=1):
        self.origin_id = origin_id
        self.destination_id = destination_id
        self.next_hop_id = next_hop_id
        self.reference_sequence = int(reference_sequence)
        self.event_code = event_code
        self.event_state = event_state
        self.repeat_count = int(repeat_count)
        self.hop_count = int(hop_count)
        self.hop_limit = int(hop_limit)


class AsciiProtocolCodec:
    """Kodiert und validiert die unterstuetzten ASCII-Nachrichten."""

    def encode_data(self, record):
        self._validate_routing_message(record)
        self._validate_nonnegative(record.sequence_number, "sequence number")
        self._validate_nonnegative(record.uptime_s, "slave uptime")
        fields = [
            FORMAT_VERSION, DATA_TYPE, record.origin_id,
            record.destination_id, record.next_hop_id,
            str(record.sequence_number), str(record.hop_count),
            str(record.hop_limit),
            self._validate_timestamp(record.measurement_timestamp),
            str(record.uptime_s),
        ]
        for name in MEASUREMENT_FIELDS:
            fields.append(self._encode_value(
                record.values.get(name), _SCALES[name],
                name in _NEGATIVE_ALLOWED,
            ))
        if not 0 <= record.status_flags <= 0xFFFF:
            raise ProtocolError("status flags outside 16-bit range")
        fields.append("{:04X}".format(record.status_flags))
        return self._encode_fields(fields)

    def decode_data(self, payload):
        fields = self._decode_fields(payload, DATA_TYPE, 22)
        for device_id in fields[2:5]:
            self._validate_device_id(device_id)
        try:
            sequence_number = int(fields[5])
            hop_count = int(fields[6])
            hop_limit = int(fields[7])
            uptime_s = int(fields[9])
            status_flags = int(fields[21], 16)
        except ValueError:
            raise ProtocolError("invalid integer field")
        self._validate_hops(hop_count, hop_limit)
        self._validate_nonnegative(sequence_number, "sequence number")
        self._validate_nonnegative(uptime_s, "slave uptime")
        if len(fields[21]) != 4 or not 0 <= status_flags <= 0xFFFF:
            raise ProtocolError("invalid status flags")
        values = {}
        for index, name in enumerate(MEASUREMENT_FIELDS, start=10):
            values[name] = self._decode_value(
                fields[index], _SCALES[name], name in _NEGATIVE_ALLOWED,
            )
        return MeasurementRecord(
            fields[2], sequence_number, self._validate_timestamp(fields[8]),
            uptime_s, values, status_flags, fields[3], fields[4],
            hop_count, hop_limit,
        )

    def encode_ack(self, ack):
        self._validate_routing_message(ack)
        self._validate_nonnegative(ack.sequence_number, "sequence number")
        if ack.result_code not in (0, 1, 2, 3):
            raise ProtocolError("invalid ACK result code")
        return self._encode_fields([
            FORMAT_VERSION, ACK_TYPE, ack.origin_id, ack.destination_id,
            ack.next_hop_id, str(ack.sequence_number), str(ack.hop_count),
            str(ack.hop_limit), str(ack.result_code),
        ])

    def decode_ack(self, payload):
        fields = self._decode_routing_fields(payload, ACK_TYPE, 9)
        try:
            sequence_number = int(fields[5])
            result_code = int(fields[8])
        except ValueError:
            raise ProtocolError("invalid ACK integer field")
        self._validate_nonnegative(sequence_number, "sequence number")
        if result_code not in (0, 1, 2, 3):
            raise ProtocolError("invalid ACK result code")
        hop_count, hop_limit = self._decode_hops(fields)
        return AckMessage(
            fields[2], fields[3], fields[4], sequence_number,
            result_code, hop_count, hop_limit,
        )

    def encode_diagnostic_event(self, event):
        self._validate_routing_message(event)
        self._validate_nonnegative(event.reference_sequence, "reference sequence")
        self._validate_nonnegative(event.repeat_count, "repeat count")
        self._validate_event_code(event.event_code)
        self._validate_event_state(event.event_state)
        if event.repeat_count < 1:
            raise ProtocolError("repeat count must be positive")
        return self._encode_fields([
            FORMAT_VERSION, DIAGNOSTIC_EVENT_TYPE, event.origin_id,
            event.destination_id, event.next_hop_id,
            str(event.reference_sequence), str(event.hop_count),
            str(event.hop_limit), event.event_code, event.event_state,
            str(event.repeat_count),
        ])

    def decode_diagnostic_event(self, payload):
        fields = self._decode_routing_fields(
            payload, DIAGNOSTIC_EVENT_TYPE, 11
        )
        try:
            reference_sequence = int(fields[5])
            repeat_count = int(fields[10])
        except ValueError:
            raise ProtocolError("invalid diagnostic event integer")
        self._validate_nonnegative(reference_sequence, "reference sequence")
        if repeat_count < 1:
            raise ProtocolError("repeat count must be positive")
        self._validate_event_code(fields[8])
        self._validate_event_state(fields[9])
        hop_count, hop_limit = self._decode_hops(fields)
        return DiagnosticEvent(
            fields[2], fields[3], fields[4], reference_sequence,
            fields[8], fields[9], repeat_count, hop_count, hop_limit,
        )

    def is_success_ack(self, payload, master_id, device_id, sequence_number):
        try:
            ack = self.decode_ack(payload)
        except ProtocolError:
            return False
        return (
            ack.origin_id == master_id
            and ack.destination_id == device_id
            and ack.next_hop_id == device_id
            and ack.sequence_number == int(sequence_number)
            and ack.result_code in (0, 2)
        )

    def message_type(self, payload):
        try:
            fields = payload.decode("ascii").split(";")
        except (AttributeError, TypeError, UnicodeError):
            raise ProtocolError("payload is not ASCII bytes")
        if len(fields) < 2 or fields[0] != FORMAT_VERSION:
            raise ProtocolError("unsupported version or missing message type")
        return fields[1]

    def encode_sequence_query(self, query):
        self._validate_routing_message(query)
        return self._encode_fields([
            FORMAT_VERSION, SEQUENCE_QUERY_TYPE, query.origin_id,
            query.destination_id, query.next_hop_id, "0",
            str(query.hop_count), str(query.hop_limit),
        ])

    def decode_sequence_query(self, payload):
        fields = self._decode_routing_fields(payload, SEQUENCE_QUERY_TYPE)
        if fields[5] != "0":
            raise ProtocolError("sequence query field 6 must be 0")
        hop_count, hop_limit = self._decode_hops(fields)
        return SequenceQuery(
            fields[2], fields[3], fields[4], hop_count, hop_limit
        )

    def encode_sequence_response(self, response):
        self._validate_routing_message(response)
        if response.next_sequence < 0:
            raise ProtocolError("negative next sequence")
        return self._encode_fields([
            FORMAT_VERSION, SEQUENCE_RESPONSE_TYPE, response.origin_id,
            response.destination_id, response.next_hop_id,
            str(response.next_sequence), str(response.hop_count),
            str(response.hop_limit),
        ])

    def decode_sequence_response(self, payload):
        fields = self._decode_routing_fields(payload, SEQUENCE_RESPONSE_TYPE)
        hop_count, hop_limit = self._decode_hops(fields)
        try:
            next_sequence = int(fields[5])
        except ValueError:
            raise ProtocolError("invalid next sequence")
        if next_sequence < 0:
            raise ProtocolError("negative next sequence")
        return SequenceResponse(
            fields[2], fields[3], fields[4], next_sequence,
            hop_count, hop_limit,
        )

    def _decode_routing_fields(self, payload, expected_type, field_count=8):
        fields = self._decode_fields(payload, expected_type, field_count)
        for device_id in fields[2:5]:
            self._validate_device_id(device_id)
        return fields

    def _decode_fields(self, payload, expected_type, field_count):
        try:
            if len(payload) > MAX_PAYLOAD_BYTES:
                raise ProtocolError(
                    "payload exceeds {} bytes".format(MAX_PAYLOAD_BYTES)
                )
            fields = payload.decode("ascii").split(";")
        except (AttributeError, TypeError, UnicodeError):
            raise ProtocolError("payload is not ASCII bytes")
        if len(fields) != field_count:
            raise ProtocolError("unexpected field count")
        if fields[0] != FORMAT_VERSION or fields[1] != expected_type:
            raise ProtocolError("unsupported version or message type")
        if any(not field or field.strip() != field for field in fields):
            raise ProtocolError("empty or whitespace-padded field")
        return fields

    def _validate_routing_message(self, message):
        for device_id in (
                message.origin_id, message.destination_id,
                message.next_hop_id):
            self._validate_device_id(device_id)
        self._validate_hops(message.hop_count, message.hop_limit)

    @staticmethod
    def _validate_hops(hop_count, hop_limit):
        if hop_count < 0 or hop_limit < 0:
            raise ProtocolError("negative hop field")
        if hop_count > hop_limit:
            raise ProtocolError("hop count exceeds hop limit")

    @staticmethod
    def _decode_hops(fields):
        try:
            hop_count = int(fields[6])
            hop_limit = int(fields[7])
        except ValueError:
            raise ProtocolError("invalid hop field")
        AsciiProtocolCodec._validate_hops(hop_count, hop_limit)
        return hop_count, hop_limit

    @staticmethod
    def _encode_fields(fields):
        try:
            payload = ";".join(fields).encode("ascii")
        except (TypeError, UnicodeError):
            raise ProtocolError("payload fields must be ASCII strings")
        if len(payload) > MAX_PAYLOAD_BYTES:
            raise ProtocolError(
                "payload exceeds {} bytes".format(MAX_PAYLOAD_BYTES)
            )
        return payload

    @staticmethod
    def _validate_device_id(device_id):
        if not isinstance(device_id, str) or not 1 <= len(device_id) <= 8:
            raise ProtocolError("device ID length must be 1..8")
        for character in device_id:
            valid = character.isdigit() or "A" <= character <= "Z"
            if not valid and character not in "_-":
                raise ProtocolError("invalid device ID")

    @staticmethod
    def _validate_nonnegative(value, name):
        if int(value) < 0:
            raise ProtocolError("negative {}".format(name))

    @staticmethod
    def _validate_timestamp(value):
        if value in (None, "", "NA"):
            return "NA"
        if not isinstance(value, str) or value.strip() != value:
            raise ProtocolError("invalid measurement timestamp")
        try:
            value.encode("ascii")
        except UnicodeError:
            raise ProtocolError("measurement timestamp is not ASCII")
        return value

    @staticmethod
    def _validate_event_code(value):
        if not isinstance(value, str) or not 1 <= len(value) <= 32:
            raise ProtocolError("invalid diagnostic event code")
        if any(character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
               for character in value):
            raise ProtocolError("invalid diagnostic event code")

    @staticmethod
    def _validate_event_state(value):
        if value not in ("STARTED", "ENDED", "OCCURRED"):
            raise ProtocolError("invalid diagnostic event state")

    @staticmethod
    def _encode_value(value, scale, negative_allowed=False):
        if value is None:
            return "NA"
        try:
            scaled = int(round(float(value) * scale))
        except (TypeError, ValueError, OverflowError):
            raise ProtocolError("invalid measurement value")
        if scaled < 0 and not negative_allowed:
            raise ProtocolError("negative measurement value")
        return str(scaled)

    @staticmethod
    def _decode_value(value, scale, negative_allowed=False):
        if value == "NA":
            return None
        try:
            scaled = int(value)
        except ValueError:
            raise ProtocolError("invalid measurement value")
        if scaled < 0 and not negative_allowed:
            raise ProtocolError("negative measurement value")
        return scaled if scale == 1 else scaled / scale
