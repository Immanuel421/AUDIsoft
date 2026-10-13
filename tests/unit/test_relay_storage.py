import io
from unittest import mock
import unittest

from adapters.relay_storage import RelayStorageAdapter
from ports.errors import StorageError


class RelayStorageTests(unittest.TestCase):
    def test_retries_transient_io_error_when_loading_queue(self):
        transient_error = OSError(5, "Input/output error")
        with mock.patch("adapters.relay_storage.open",
                        side_effect=[transient_error, io.StringIO("{}")] ) as opened:
            with mock.patch("adapters.relay_storage.time.sleep") as sleep:
                storage = RelayStorageAdapter("/sd")

        self.assertEqual({}, storage._items)
        self.assertEqual(2, opened.call_count)
        sleep.assert_called_once_with(0.2)

    def test_keeps_reporting_persistent_io_error(self):
        with mock.patch("adapters.relay_storage.open",
                        side_effect=OSError(5, "Input/output error")) as opened:
            with mock.patch("adapters.relay_storage.time.sleep"):
                with self.assertRaises(StorageError):
                    RelayStorageAdapter("/sd")

        self.assertEqual(3, opened.call_count)


if __name__ == "__main__":
    unittest.main()
