"""Persistente Warteschlange fuer weiterzuleitende Mesh-Pakete."""

import json
import os

from domain.measurement import MeasurementRecord
from ports.errors import StorageError


class RelayStorageAdapter:
    def __init__(self, mount_path="/sd"):
        self.path = mount_path + "/relay_pending.json"
        self._items = self._load()

    @staticmethod
    def key(record):
        return "D:{}:{}:{}".format(
            record.origin_id, record.destination_id, record.sequence_number
        )

    def enqueue(self, record):
        key = self.key(record)
        if key in self._items:
            return False
        self._items[key] = record.to_dict()
        self._write()
        return True

    def pending_records(self):
        for item in self._items.values():
            yield MeasurementRecord.from_dict(item)

    def mark_delivered(self, record):
        if self._items.pop(self.key(record), None) is not None:
            self._write()

    def _load(self):
        try:
            with open(self.path, "r") as source:
                value = json.load(source)
            if not isinstance(value, dict):
                raise ValueError("relay queue is invalid")
            return value
        except OSError as exc:
            if exc.args[0] == 2:
                return {}
            raise StorageError("relay queue cannot be loaded: {}".format(exc))
        except (ValueError, TypeError, KeyError) as exc:
            raise StorageError("relay queue cannot be loaded: {}".format(exc))

    def _write(self):
        temporary = self.path + ".tmp"
        try:
            with open(temporary, "w") as target:
                json.dump(self._items, target)
                target.flush()
            os.rename(temporary, self.path)
        except (OSError, ValueError, TypeError) as exc:
            raise StorageError("relay queue cannot be written: {}".format(exc))
