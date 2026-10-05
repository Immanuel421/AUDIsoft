import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]

ADAPTER_CONTRACTS = {
    "adapters/clock.py": {
        "class": "ConfiguredUtcClock",
        "ports": {"ClockPort"},
        "methods": {"measurement_timestamp", "uptime_s"},
    },
    "adapters/sd_storage.py": {
        "class": "SdStorageAdapter",
        "ports": {"SlaveStoragePort", "MasterStoragePort"},
        "methods": {
            "next_sequence",
            "next_sequence_for",
            "save_local",
            "pending_records",
            "mark_transmitted",
            "has_received",
            "save_received",
        },
    },
    "adapters/sen66_sensor.py": {
        "class": "Sen66SensorAdapter",
        "ports": {"SensorPort"},
        "methods": {"read_measurement"},
    },
    "adapters/sx1262_radio.py": {
        "class": "Sx1262RadioAdapter",
        "ports": {"RadioPort"},
        "methods": {"send", "receive"},
    },
    "adapters/diagnostics.py": {
        "class": "DiagnosticsAdapter",
        "ports": {"DiagnosticsPort"},
        "methods": {"info", "error"},
    },
}


class AdapterContractTests(unittest.TestCase):
    def test_adapters_explicitly_implement_their_ports(self):
        for relative_path, contract in ADAPTER_CONTRACTS.items():
            with self.subTest(adapter=relative_path):
                tree = ast.parse(
                    (ROOT / relative_path).read_text(encoding="utf-8")
                )
                adapter_class = next(
                    node
                    for node in tree.body
                    if isinstance(node, ast.ClassDef)
                    and node.name == contract["class"]
                )
                base_names = {
                    base.id
                    for base in adapter_class.bases
                    if isinstance(base, ast.Name)
                }
                method_names = {
                    node.name
                    for node in adapter_class.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                self.assertTrue(contract["ports"].issubset(base_names))
                self.assertTrue(contract["methods"].issubset(method_names))


if __name__ == "__main__":
    unittest.main()
