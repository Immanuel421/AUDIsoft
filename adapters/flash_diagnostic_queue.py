"""Kleine persistente Diagnosewarteschlange im CIRCUITPY-Dateisystem."""

import json
import os

from domain.protocol import DiagnosticEvent
from ports.errors import StorageError


class FlashDiagnosticQueueAdapter:
    """Keeps only compact diagnostic events; measurement data never use flash."""

    MAX_PENDING_EVENTS = 32

    def __init__(self, root_path="/diagnostics"):
        self._root_path = root_path
        self._path = root_path + "/pending.json"
        try:
            try:
                os.mkdir(root_path)
            except OSError as exc:
                if exc.args[0] != 17:
                    raise
            self._pending = self._load()
        except (OSError, ValueError, TypeError) as exc:
            raise StorageError("flash diagnostic queue unavailable: {}".format(exc))

    def queue_diagnostic_event(self, event_code, event_state, repeat_count):
        try:
            self._pending.append({
                "event_code": event_code,
                "event_state": event_state,
                "repeat_count": int(repeat_count),
            })
            if len(self._pending) > self.MAX_PENDING_EVENTS:
                del self._pending[:-self.MAX_PENDING_EVENTS]
            self._write()
        except (OSError, ValueError, TypeError) as exc:
            raise StorageError("flash diagnostic queue write failed: {}".format(exc))

    def pending_diagnostic_events(self, device_id, reference_sequence,
                                  destination_id, next_hop_id, hop_limit):
        return [DiagnosticEvent(
            device_id, destination_id, next_hop_id, reference_sequence,
            entry["event_code"], entry["event_state"],
            entry["repeat_count"], 0, hop_limit,
        ) for entry in self._pending]

    def mark_diagnostic_events_transmitted(self, events):
        try:
            del self._pending[:len(events)]
            self._write()
        except (OSError, ValueError, TypeError) as exc:
            raise StorageError("flash diagnostic queue update failed: {}".format(exc))

    def _load(self):
        try:
            with open(self._path, "r") as source:
                pending = json.load(source)
        except OSError as exc:
            if exc.args[0] == 2:
                return []
            raise
        if not isinstance(pending, list):
            raise ValueError("pending diagnostics must be a list")
        return pending

    def _write(self):
        temporary_path = self._path + ".tmp"
        with open(temporary_path, "w") as target:
            json.dump(self._pending, target)
            target.flush()
        os.rename(temporary_path, self._path)
