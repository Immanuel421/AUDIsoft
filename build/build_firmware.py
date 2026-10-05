#!/usr/bin/env python3
"""Erzeugt getrennte CircuitPython-MPY-Pakete fuer die Climate Cubes."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_PACKAGES = ("adapters", "application", "domain", "ports")
PROFILES = {
    "rp2040": {
        "circuitpython": "10.3.0",
        "devices": "C02 und C03 (Raspberry Pi Pico / RP2040)",
    },
    "rp2350": {
        "circuitpython": "10.2.1",
        "devices": "C01 und M01 (Raspberry Pi Pico 2 W / RP2350A)",
    },
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_mpy_cross(mpy_cross, source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(mpy_cross), "-o", str(target), str(source)], check=True)


def write_installation(profile, destination, compiler_version):
    details = PROFILES[profile]
    (destination / "INSTALLATION.md").write_text(
        "# {}: CircuitPython {}\n\n".format(
            profile.upper(), details["circuitpython"]
        )
        + "Dieses Paket ist ausschliesslich fuer {} bestimmt.\n\n".format(
            details["devices"]
        )
        + "## Installation\n\n"
        + "1. Vollstaendige Sicherung von `CIRCUITPY`, `config.json` und SD-Karte erstellen.\n"
        + "2. Auf `CIRCUITPY` die Ordner `adapters`, `application`, `domain` und `ports` vollstaendig durch die gleichnamigen Ordner dieses Pakets ersetzen.\n"
        + "3. `code.py` aus diesem Paket nach `CIRCUITPY/code.py` kopieren.\n"
        + "4. `config.json`, den Ordner `lib/` und die SD-Daten unveraendert lassen.\n"
        + "5. Es duerfen keine gleichnamigen `.py`- und `.mpy`-Dateien in den vier Projektordnern verbleiben.\n"
        + "6. Laufwerk sicher auswerfen und den Pico neu starten.\n\n"
        + "Erzeugt mit: `{}`\n".format(compiler_version.strip())
    )


def build(profile, mpy_cross):
    destination = ROOT / "firmware" / profile
    for package in SOURCE_PACKAGES:
        shutil.rmtree(destination / package, ignore_errors=True)

    manifest = {}
    for package in SOURCE_PACKAGES:
        for source in sorted((ROOT / package).glob("*.py")):
            relative = source.relative_to(ROOT)
            target = destination / relative.with_suffix(".mpy")
            run_mpy_cross(mpy_cross, source, target)
            manifest[str(relative)] = sha256(source)

    shutil.copy2(ROOT / "code.py", destination / "code.py")
    manifest["code.py"] = sha256(ROOT / "code.py")
    compiler_version = subprocess.check_output(
        [str(mpy_cross), "--version"], text=True, stderr=subprocess.STDOUT
    )
    (destination / "sources.json").write_text(
        json.dumps(
            {
                "profile": profile,
                "circuitpython": PROFILES[profile]["circuitpython"],
                "mpy_cross": compiler_version.strip(),
                "sources": manifest,
            },
            indent=2,
            sort_keys=True,
        ) + "\n"
    )
    write_installation(profile, destination, compiler_version)
    print("Firmware package created:", destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", choices=sorted(PROFILES))
    parser.add_argument(
        "--mpy-cross", required=True, type=Path,
        help="Passender mpy-cross derselben CircuitPython-Version wie das Zielgeraet",
    )
    args = parser.parse_args()
    if not args.mpy_cross.is_file():
        parser.error("mpy-cross wurde nicht gefunden: {}".format(args.mpy_cross))
    build(args.profile, args.mpy_cross)


if __name__ == "__main__":
    main()
