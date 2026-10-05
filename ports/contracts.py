"""Schlanke Port-Vertraege ohne schwere Abstraktionsbibliothek."""


class SensorPort:
    def start_measurement(self):
        """Startet einen Messzyklus ohne auf die Aufwaermzeit zu warten."""
        raise NotImplementedError

    def poll_measurement(self):
        """Liefert None solange beschaeftigt, sonst (values, status_flags)."""
        raise NotImplementedError

    def read_measurement(self):
        """Liefert (values, status_flags)."""
        raise NotImplementedError


class ClockPort:
    def measurement_timestamp(self):
        raise NotImplementedError

    def uptime_s(self):
        raise NotImplementedError

    def status_flags(self):
        """Liefert Zeit-bezogene Statusbits fuer einen Messdatensatz."""
        raise NotImplementedError

    def sleep_ms(self, milliseconds):
        raise NotImplementedError


class SlaveStoragePort:
    def next_sequence(self):
        raise NotImplementedError

    def save_local(self, record):
        raise NotImplementedError

    def pending_records(self):
        raise NotImplementedError

    def mark_transmitted(self, record):
        raise NotImplementedError

    def latest_measurement_timestamp(self, device_id):
        raise NotImplementedError


class MasterStoragePort:
    def has_received(self, device_id, sequence_number):
        raise NotImplementedError

    def save_received(self, record, metadata):
        raise NotImplementedError

    def save_missing_interval(self, device_id, metadata):
        """Speichert eine vorlaeufige NO_PACKET-Luecke fuer einen Slave."""
        raise NotImplementedError

    def next_sequence_for(self, device_id):
        raise NotImplementedError

    def save_diagnostic_event(self, event):
        """Speichert ein neues oder aktualisiertes zentrales Diagnoseereignis."""
        raise NotImplementedError

    def latest_measurement_timestamp(self, device_id):
        raise NotImplementedError


class RadioPort:
    def send(self, payload):
        raise NotImplementedError

    def receive(self, timeout_ms):
        """Liefert (payload, metadata), bei Timeout (None, {})."""
        raise NotImplementedError


class DiagnosticsPort:
    def info(self, message):
        raise NotImplementedError

    def error(self, message):
        raise NotImplementedError
