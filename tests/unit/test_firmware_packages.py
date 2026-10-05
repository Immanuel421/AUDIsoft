import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PACKAGES = ("adapters", "application", "domain", "ports")
PROFILES = {
    "rp2040": "10.3.0",
    "rp2350": "10.2.1",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_paths():
    paths = [ROOT / "code.py"]
    for package in SOURCE_PACKAGES:
        paths.extend(sorted((ROOT / package).glob("*.py")))
    return paths


class FirmwarePackageTests(unittest.TestCase):
    def test_firmware_packages_match_current_sources(self):
        expected_sources = {
            str(path.relative_to(ROOT)): sha256(path)
            for path in source_paths()
        }

        for profile, circuitpython_version in PROFILES.items():
            with self.subTest(profile=profile):
                package = ROOT / "firmware" / profile
                manifest_path = package / "sources.json"
                self.assertTrue(manifest_path.is_file())

                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual(profile, manifest["profile"])
                self.assertEqual(circuitpython_version, manifest["circuitpython"])
                self.assertEqual(expected_sources, manifest["sources"])

                for relative_path in expected_sources:
                    if relative_path == "code.py":
                        target = package / relative_path
                    else:
                        target = package / Path(relative_path).with_suffix(".mpy")
                    self.assertTrue(
                        target.is_file(),
                        "missing firmware module: {}".format(target),
                    )


if __name__ == "__main__":
    unittest.main()
