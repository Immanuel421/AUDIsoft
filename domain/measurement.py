"""Gemeinsamer Messdatensatz fuer lokale Speicherung und Funk."""

SEN66_ERROR = 0x0001
SOIL_TEMPERATURE_ERROR = 0x0002
SOIL_MOISTURE_ERROR = 0x0004
SLAVE_SD_UNAVAILABLE = 0x0008
SLAVE_SD_WRITE_ERROR = 0x0010
MEASUREMENT_MISSING = 0x0020
TIME_UNSYNCED = 0x0040
MEASUREMENT_IMPLAUSIBLE = 0x0080

MEASUREMENT_FIELDS = (
    "air_temperature_c",
    "relative_humidity_pct",
    "co2_ppm",
    "pm1_0_ug_m3",
    "pm2_5_ug_m3",
    "pm4_0_ug_m3",
    "pm10_ug_m3",
    "voc_index",
    "nox_index",
    "soil_moisture_pct",
    "soil_temperature_c",
)


class MeasurementRecord:
    def __init__(self, device_id, sequence_number, measurement_timestamp,
                 uptime_s, values, status_flags=0, destination_id=None,
                 next_hop_id=None, hop_count=0, hop_limit=1):
        self.format_version = 1
        self.device_id = device_id
        self.sequence_number = int(sequence_number)
        self.measurement_timestamp = (
            measurement_timestamp
            if measurement_timestamp not in (None, "") else "NA"
        )
        self.uptime_s = int(uptime_s)
        self.destination_id = destination_id
        self.next_hop_id = next_hop_id
        self.hop_count = int(hop_count)
        self.hop_limit = int(hop_limit)
        self.values = {}
        for field in MEASUREMENT_FIELDS:
            self.values[field] = values.get(field)
        self.status_flags = int(status_flags)

    @property
    def origin_id(self):
        return self.device_id

    def to_dict(self):
        return {
            "format_version": self.format_version,
            "device_id": self.device_id,
            "sequence_number": self.sequence_number,
            "measurement_timestamp": self.measurement_timestamp,
            "uptime_s": self.uptime_s,
            "values": self.values,
            "status_flags": self.status_flags,
            "destination_id": self.destination_id,
            "next_hop_id": self.next_hop_id,
            "hop_count": self.hop_count,
            "hop_limit": self.hop_limit,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["device_id"], data["sequence_number"],
            data["measurement_timestamp"], data["uptime_s"],
            data["values"], data.get("status_flags", 0),
            data.get("destination_id"), data.get("next_hop_id"),
            data.get("hop_count", 0), data.get("hop_limit", 1),
        )
