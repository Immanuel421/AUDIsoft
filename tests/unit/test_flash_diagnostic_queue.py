import tempfile
import unittest

from adapters.flash_diagnostic_queue import FlashDiagnosticQueueAdapter


class FlashDiagnosticQueueTests(unittest.TestCase):
    def test_event_survives_recreation_and_is_removed_after_ack(self):
        with tempfile.TemporaryDirectory() as directory:
            root = directory + "/diagnostics"
            queue = FlashDiagnosticQueueAdapter(root)
            queue.queue_diagnostic_event("F1", "STARTED", 1)

            restored = FlashDiagnosticQueueAdapter(root)
            events = restored.pending_diagnostic_events(
                "C01", 7, "M01", "M01", 1
            )
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].event_code, "F1")
            self.assertEqual(events[0].reference_sequence, 7)

            restored.mark_diagnostic_events_transmitted(events)
            self.assertEqual(
                restored.pending_diagnostic_events("C01", 8, "M01", "M01", 1),
                [],
            )


if __name__ == "__main__":
    unittest.main()
