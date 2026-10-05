import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CODE_PATH = ROOT / "code.py"

REQUIRED_FUNCTIONS = {
    "build_diagnostics",
    "build_shared_components",
    "build_slave",
    "build_master",
    "run_slave",
    "run_master",
    "start_configured_role",
    "main",
}


def called_functions(function):
    return {
        node.func.id
        for node in ast.walk(function)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }


class CompositionRootTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tree = ast.parse(CODE_PATH.read_text(encoding="utf-8"))
        cls.functions = {
            node.name: node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
        }

    def test_composition_root_has_explicit_builders_and_runners(self):
        self.assertTrue(REQUIRED_FUNCTIONS.issubset(self.functions))

    def test_main_delegates_component_building_and_role_selection(self):
        calls = called_functions(self.functions["main"])
        self.assertTrue({
            "build_diagnostics",
            "build_shared_components",
            "start_configured_role",
        }.issubset(calls))

    def test_role_selection_uses_role_specific_builder_and_runner(self):
        calls = called_functions(self.functions["start_configured_role"])
        self.assertTrue({
            "build_slave",
            "run_slave",
            "build_master",
            "run_master",
        }.issubset(calls))


if __name__ == "__main__":
    unittest.main()
