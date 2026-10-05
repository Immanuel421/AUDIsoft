import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]

HARDWARE_MODULES = {
    "board",
    "busio",
    "digitalio",
    "displayio",
    "i2cdisplaybus",
    "microcontroller",
    "sdcardio",
    "storage",
    "terminalio",
    "sx1262",
    "sx126x",
    "_sx126x",
}


def imported_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def is_hardware_module(module):
    root = module.split(".", 1)[0]
    return root in HARDWARE_MODULES or root.startswith("adafruit_")


class ArchitectureDependencyTests(unittest.TestCase):
    def assert_layer_imports(self, layer, forbidden_prefixes, hardware_forbidden):
        for path in sorted((ROOT / layer).glob("*.py")):
            with self.subTest(layer=layer, module=path.name):
                imports = imported_modules(path)
                violations = {
                    module
                    for module in imports
                    if any(
                        module == prefix or module.startswith(prefix + ".")
                        for prefix in forbidden_prefixes
                    )
                    or (hardware_forbidden and is_hardware_module(module))
                }
                self.assertEqual(
                    violations,
                    set(),
                    "{} imports forbidden dependencies: {}".format(
                        path.relative_to(ROOT),
                        ", ".join(sorted(violations)),
                    ),
                )

    def test_domain_is_independent(self):
        self.assert_layer_imports(
            "domain",
            {"application", "ports", "adapters"},
            hardware_forbidden=True,
        )

    def test_ports_are_independent(self):
        self.assert_layer_imports(
            "ports",
            {"domain", "application", "adapters"},
            hardware_forbidden=True,
        )

    def test_application_depends_only_inward(self):
        self.assert_layer_imports(
            "application",
            {"adapters"},
            hardware_forbidden=True,
        )

    def test_adapters_do_not_depend_on_application(self):
        self.assert_layer_imports(
            "adapters",
            {"application"},
            hardware_forbidden=False,
        )


if __name__ == "__main__":
    unittest.main()
